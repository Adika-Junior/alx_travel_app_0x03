"""
Management command to seed the database with sample listings data.
Usage: python manage.py seed
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from alx_travel_app.listings.models import Listing, Booking, Review


class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Review.objects.all().delete()
            Booking.objects.all().delete()
            Listing.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create sample listings
        listings_data = [
            {
                'title': 'Cozy Beachfront Apartment',
                'description': 'Beautiful apartment with stunning ocean views. Perfect for a relaxing getaway.',
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'state': 'Florida',
                'country': 'United States',
                'price_per_night': Decimal('150.00'),
                'property_type': 'apartment',
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'amenities': 'WiFi, Air Conditioning, Beach Access, Parking',
                'is_available': True,
            },
            {
                'title': 'Luxury Mountain Villa',
                'description': 'Spacious villa nestled in the mountains with breathtaking views and modern amenities.',
                'address': '456 Mountain View Road',
                'city': 'Aspen',
                'state': 'Colorado',
                'country': 'United States',
                'price_per_night': Decimal('350.00'),
                'property_type': 'villa',
                'max_guests': 8,
                'bedrooms': 4,
                'bathrooms': 3,
                'amenities': 'WiFi, Fireplace, Hot Tub, Mountain View, Parking',
                'is_available': True,
            },
            {
                'title': 'Downtown Modern Condo',
                'description': 'Stylish condo in the heart of the city, close to restaurants and nightlife.',
                'address': '789 City Center Avenue',
                'city': 'New York',
                'state': 'New York',
                'country': 'United States',
                'price_per_night': Decimal('200.00'),
                'property_type': 'condo',
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'amenities': 'WiFi, Air Conditioning, Gym Access, Rooftop Terrace',
                'is_available': True,
            },
            {
                'title': 'Rustic Cabin Retreat',
                'description': 'Charming cabin surrounded by nature, perfect for a peaceful escape.',
                'address': '321 Forest Lane',
                'city': 'Portland',
                'state': 'Oregon',
                'country': 'United States',
                'price_per_night': Decimal('120.00'),
                'property_type': 'cabin',
                'max_guests': 6,
                'bedrooms': 3,
                'bathrooms': 2,
                'amenities': 'WiFi, Fireplace, Hiking Trails, Pet Friendly',
                'is_available': True,
            },
            {
                'title': 'Elegant Family House',
                'description': 'Large family home with garden, perfect for groups and families.',
                'address': '654 Garden Street',
                'city': 'Los Angeles',
                'state': 'California',
                'country': 'United States',
                'price_per_night': Decimal('280.00'),
                'property_type': 'house',
                'max_guests': 10,
                'bedrooms': 5,
                'bathrooms': 3,
                'amenities': 'WiFi, Garden, BBQ Area, Parking, Pet Friendly',
                'is_available': True,
            },
        ]

        created_listings = []
        for listing_data in listings_data:
            listing, created = Listing.objects.get_or_create(
                title=listing_data['title'],
                defaults=listing_data
            )
            if created:
                created_listings.append(listing)
                self.stdout.write(
                    self.style.SUCCESS(f'Created listing: {listing.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Listing already exists: {listing.title}')
                )

        # Create sample bookings
        if created_listings:
            bookings_data = [
                {
                    'listing': created_listings[0],
                    'guest_name': 'John Doe',
                    'guest_email': 'john.doe@example.com',
                    'guest_phone': '+1-555-0101',
                    'check_in': timezone.now().date() + timedelta(days=7),
                    'check_out': timezone.now().date() + timedelta(days=10),
                    'number_of_guests': 2,
                    'total_price': Decimal('450.00'),
                    'status': 'confirmed',
                    'special_requests': 'Late check-in requested',
                },
                {
                    'listing': created_listings[1],
                    'guest_name': 'Jane Smith',
                    'guest_email': 'jane.smith@example.com',
                    'guest_phone': '+1-555-0102',
                    'check_in': timezone.now().date() + timedelta(days=14),
                    'check_out': timezone.now().date() + timedelta(days=21),
                    'number_of_guests': 6,
                    'total_price': Decimal('2450.00'),
                    'status': 'pending',
                    'special_requests': '',
                },
                {
                    'listing': created_listings[2],
                    'guest_name': 'Bob Johnson',
                    'guest_email': 'bob.johnson@example.com',
                    'guest_phone': '+1-555-0103',
                    'check_in': timezone.now().date() + timedelta(days=30),
                    'check_out': timezone.now().date() + timedelta(days=32),
                    'number_of_guests': 2,
                    'total_price': Decimal('400.00'),
                    'status': 'confirmed',
                    'special_requests': 'Anniversary celebration',
                },
            ]

            for booking_data in bookings_data:
                booking = Booking.objects.create(**booking_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created booking: {booking.guest_name} - '
                        f'{booking.listing.title}'
                    )
                )

            # Create sample reviews
            reviews_data = [
                {
                    'listing': created_listings[0],
                    'reviewer_name': 'Alice Williams',
                    'reviewer_email': 'alice.williams@example.com',
                    'rating': 5,
                    'comment': 'Amazing place! The view was breathtaking and the location was perfect.',
                },
                {
                    'listing': created_listings[0],
                    'reviewer_name': 'Charlie Brown',
                    'reviewer_email': 'charlie.brown@example.com',
                    'rating': 4,
                    'comment': 'Great apartment, very clean and well-maintained. Would stay again!',
                },
                {
                    'listing': created_listings[1],
                    'reviewer_name': 'Diana Prince',
                    'reviewer_email': 'diana.prince@example.com',
                    'rating': 5,
                    'comment': 'Absolutely stunning villa! The mountain views are incredible.',
                },
                {
                    'listing': created_listings[2],
                    'reviewer_name': 'Edward Norton',
                    'reviewer_email': 'edward.norton@example.com',
                    'rating': 4,
                    'comment': 'Perfect location in the city center. Modern and comfortable.',
                },
            ]

            for review_data in reviews_data:
                review = Review.objects.create(**review_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created review: {review.reviewer_name} - '
                        f'{review.listing.title} ({review.rating}/5)'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDatabase seeding completed successfully!\n'
                f'Created: {len(created_listings)} listings, '
                f'{Booking.objects.count()} bookings, '
                f'{Review.objects.count()} reviews'
            )
        )

