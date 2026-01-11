from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment, Booking


@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Send booking confirmation email to the customer.
    
    Args:
        booking_id: ID of the Booking instance
    """
    try:
        booking = Booking.objects.get(id=booking_id)
        
        subject = f'Booking Confirmation - Booking #{booking.id}'
        
        message = f"""
Dear {booking.guest_name},

Thank you for your booking! We have received your reservation request.

Booking Details:
- Booking Reference: #{booking.id}
- Property: {booking.listing.title}
- Address: {booking.listing.address}, {booking.listing.city}, {booking.listing.country}
- Check-in: {booking.check_in}
- Check-out: {booking.check_out}
- Number of Guests: {booking.number_of_guests}
- Total Price: ETB {booking.total_price}
- Status: {booking.get_status_display()}

We will process your booking and send you a payment confirmation shortly.

If you have any questions or special requests, please don't hesitate to contact us.

Best regards,
ALX Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.guest_email],
            fail_silently=False,
        )
        
        return f"Booking confirmation email sent to {booking.guest_email}"
    except Booking.DoesNotExist:
        return f"Booking with ID {booking_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send payment confirmation email to the customer.
    
    Args:
        payment_id: ID of the Payment instance
    """
    try:
        payment = Payment.objects.get(id=payment_id)
        booking = payment.booking
        
        subject = f'Payment Confirmation - Booking #{booking.id}'
        
        message = f"""
Dear {booking.guest_name},

Thank you for your payment! Your booking has been confirmed.

Booking Details:
- Booking Reference: #{booking.id}
- Property: {booking.listing.title}
- Check-in: {booking.check_in}
- Check-out: {booking.check_out}
- Number of Guests: {booking.number_of_guests}
- Total Amount Paid: ETB {payment.amount}
- Transaction ID: {payment.transaction_id}

We look forward to hosting you!

Best regards,
ALX Travel App Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.guest_email],
            fail_silently=False,
        )
        
        return f"Confirmation email sent to {booking.guest_email}"
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found"
    except Exception as e:
        return f"Error sending email: {str(e)}"

