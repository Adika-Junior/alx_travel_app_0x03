from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'city', 'country', 'price_per_night', 'property_type', 'is_available', 'created_at']
    list_filter = ['property_type', 'is_available', 'city', 'country']
    search_fields = ['title', 'description', 'address', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'listing', 'check_in', 'check_out', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['guest_name', 'guest_email', 'listing__title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer_name', 'listing', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer_name', 'listing__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'chapa_reference', 'booking__guest_name', 'booking__guest_email']
    readonly_fields = ['created_at', 'updated_at']
