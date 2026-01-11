from rest_framework import serializers
from .models import Listing, Booking, Payment


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'address',
            'city',
            'state',
            'country',
            'price_per_night',
            'property_type',
            'max_guests',
            'bedrooms',
            'bathrooms',
            'amenities',
            'is_available',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        source='listing',
        queryset=Listing.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_id',
            'listing_title',
            'guest_name',
            'guest_email',
            'guest_phone',
            'check_in',
            'check_out',
            'number_of_guests',
            'total_price',
            'status',
            'special_requests',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate booking data."""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        
        if check_in and check_out:
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Check-out date must be after check-in date."
                )
        
        listing = data.get('listing')
        number_of_guests = data.get('number_of_guests')
        
        if listing and number_of_guests:
            if number_of_guests > listing.max_guests:
                raise serializers.ValidationError(
                    f"Number of guests ({number_of_guests}) exceeds maximum "
                    f"guests allowed ({listing.max_guests}) for this listing."
                )
        
        return data


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    booking_reference = serializers.CharField(source='booking.id', read_only=True)
    guest_name = serializers.CharField(source='booking.guest_name', read_only=True)
    guest_email = serializers.CharField(source='booking.guest_email', read_only=True)
    listing_title = serializers.CharField(source='booking.listing.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'booking',
            'booking_reference',
            'guest_name',
            'guest_email',
            'listing_title',
            'transaction_id',
            'amount',
            'status',
            'chapa_reference',
            'payment_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'transaction_id', 'chapa_reference', 'payment_url', 'created_at', 'updated_at']

