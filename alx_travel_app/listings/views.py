from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
import requests
import uuid
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Listing resources.
    
    Provides CRUD operations:
    - GET /api/listings/ - List all listings
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - POST /api/listings/ - Create a new listing
    - PUT /api/listings/{id}/ - Update a listing (full update)
    - PATCH /api/listings/{id}/ - Update a listing (partial update)
    - DELETE /api/listings/{id}/ - Delete a listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """
        Retrieve all bookings for a specific listing.
        GET /api/listings/{id}/bookings/
        """
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Booking resources.
    
    Provides CRUD operations:
    - GET /api/bookings/ - List all bookings
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - POST /api/bookings/ - Create a new booking
    - PUT /api/bookings/{id}/ - Update a booking (full update)
    - PATCH /api/bookings/{id}/ - Update a booking (partial update)
    - DELETE /api/bookings/{id}/ - Delete a booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        """
        Optionally filter bookings by listing_id query parameter.
        Example: /api/bookings/?listing_id=1
        """
        queryset = Booking.objects.all()
        listing_id = self.request.query_params.get('listing_id', None)
        if listing_id is not None:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a booking and initiate payment process.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        
        # Send booking confirmation email asynchronously
        from .tasks import send_booking_confirmation_email
        send_booking_confirmation_email.delay(booking.id)
        
        # Initiate payment for the booking
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='pending'
        )
        
        # Initiate payment with Chapa
        try:
            chapa_response = initiate_chapa_payment(booking, payment, request)
            if chapa_response.get('status') == 'success':
                payment.transaction_id = chapa_response.get('data', {}).get('tx_ref', '')
                payment.chapa_reference = chapa_response.get('data', {}).get('reference', '')
                payment.payment_url = chapa_response.get('data', {}).get('checkout_url', '')
                payment.save()
                
                payment_serializer = PaymentSerializer(payment)
                booking_serializer = self.get_serializer(booking)
                
                return Response({
                    'booking': booking_serializer.data,
                    'payment': payment_serializer.data,
                    'payment_url': payment.payment_url
                }, status=status.HTTP_201_CREATED)
            else:
                payment.status = 'failed'
                payment.save()
                return Response({
                    'error': 'Failed to initiate payment',
                    'details': chapa_response.get('message', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response({
                'error': 'Payment initiation failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing Payment resources.
    
    Provides read-only operations:
    - GET /api/payments/ - List all payments
    - GET /api/payments/{id}/ - Retrieve a specific payment
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify payment status with Chapa API.
        POST /api/payments/{id}/verify/
        """
        payment = self.get_object()
        
        if not payment.transaction_id:
            return Response({
                'error': 'No transaction ID found for this payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chapa_response = verify_chapa_payment(payment.transaction_id)
            
            if chapa_response.get('status') == 'success':
                payment_data = chapa_response.get('data', {})
                payment_status = payment_data.get('status', '').lower()
                
                if payment_status == 'success':
                    payment.status = 'completed'
                    payment.booking.status = 'confirmed'
                    payment.booking.save()
                    payment.save()
                    
                    # Send confirmation email asynchronously
                    from .tasks import send_payment_confirmation_email
                    send_payment_confirmation_email.delay(payment.id)
                    
                    return Response({
                        'message': 'Payment verified successfully',
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_200_OK)
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({
                        'message': 'Payment verification failed',
                        'status': payment_status,
                        'payment': PaymentSerializer(payment).data
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Failed to verify payment',
                    'details': chapa_response.get('message', 'Unknown error')
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Payment verification failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def payment_success(request):
    """
    Payment success page endpoint.
    GET /api/payments/success/
    Query params: tx_ref (transaction reference)
    """
    tx_ref = request.query_params.get('tx_ref')
    
    if not tx_ref:
        return Response({
            'message': 'Payment completed',
            'note': 'Please verify your payment using the transaction reference'
        }, status=status.HTTP_200_OK)
    
    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        return Response({
            'message': 'Payment completed successfully',
            'payment': PaymentSerializer(payment).data,
            'booking': BookingSerializer(payment.booking).data
        }, status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response({
            'message': 'Payment completed',
            'note': f'Payment with reference {tx_ref} not found. Please verify manually.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_payment_by_reference(request):
    """
    Verify payment by transaction reference.
    POST /api/payments/verify/
    Body: {"transaction_id": "tx_ref_xxx"}
    """
    transaction_id = request.data.get('transaction_id')
    
    if not transaction_id:
        return Response({
            'error': 'transaction_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(transaction_id=transaction_id)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        chapa_response = verify_chapa_payment(transaction_id)
        
        if chapa_response.get('status') == 'success':
            payment_data = chapa_response.get('data', {})
            payment_status = payment_data.get('status', '').lower()
            
            if payment_status == 'success':
                payment.status = 'completed'
                payment.booking.status = 'confirmed'
                payment.booking.save()
                payment.save()
                
                # Send confirmation email asynchronously
                from .tasks import send_payment_confirmation_email
                send_payment_confirmation_email.delay(payment.id)
                
                return Response({
                    'message': 'Payment verified successfully',
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_200_OK)
            else:
                payment.status = 'failed'
                payment.save()
                return Response({
                    'message': 'Payment verification failed',
                    'status': payment_status,
                    'payment': PaymentSerializer(payment).data
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Failed to verify payment',
                'details': chapa_response.get('message', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'Payment verification failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initiate_chapa_payment(booking, payment, request=None):
    """
    Initiate payment with Chapa API.
    
    Args:
        booking: Booking instance
        payment: Payment instance
        request: Django request object (optional)
    
    Returns:
        dict: Chapa API response
    """
    if not settings.CHAPA_SECRET_KEY:
        raise ValueError("CHAPA_SECRET_KEY is not configured")
    
    # Generate unique transaction reference
    tx_ref = f"tx_ref_{payment.id}_{uuid.uuid4().hex[:10]}"
    
    headers = {
        'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Build callback URLs
    if request:
        base_url = request.build_absolute_uri('/').rstrip('/')
    else:
        base_url = 'http://localhost:8000'  # Default for development
    
    payload = {
        'amount': str(float(booking.total_price)),
        'currency': 'ETB',
        'email': booking.guest_email,
        'first_name': booking.guest_name.split()[0] if booking.guest_name.split() else 'Guest',
        'last_name': ' '.join(booking.guest_name.split()[1:]) if len(booking.guest_name.split()) > 1 else 'User',
        'phone_number': booking.guest_phone or '0000000000',
        'tx_ref': tx_ref,
        'callback_url': f"{base_url}/api/payments/verify/",
        'return_url': f"{base_url}/api/payments/success/",
        'meta': {
            'booking_id': booking.id,
            'payment_id': payment.id
        }
    }
    
    try:
        response = requests.post(
            settings.CHAPA_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': str(e)
        }


def verify_chapa_payment(transaction_id):
    """
    Verify payment status with Chapa API.
    
    Args:
        transaction_id: Transaction reference from Chapa
    
    Returns:
        dict: Chapa API response
    """
    if not settings.CHAPA_SECRET_KEY:
        raise ValueError("CHAPA_SECRET_KEY is not configured")
    
    headers = {
        'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    verify_url = f"{settings.CHAPA_VERIFY_URL}{transaction_id}"
    
    try:
        response = requests.get(
            verify_url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': str(e)
        }
