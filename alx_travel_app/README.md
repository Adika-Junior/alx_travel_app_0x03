# ALX Travel App - Django Application

This is the main Django application package for the ALX Travel App project with integrated Chapa Payment Gateway.

## Application Structure

```
alx_travel_app/
├── listings/          # Listings app with models, serializers, and views
│   ├── models.py      # Listing, Booking, Review, and Payment models
│   ├── views.py       # API views including payment endpoints
│   ├── serializers.py # Serializers for all models
│   ├── tasks.py       # Celery tasks for background email sending
│   └── urls.py        # URL routing for listings, bookings, and payments
├── settings.py        # Django project settings with Chapa and Celery config
├── celery.py          # Celery configuration
├── urls.py            # Main URL configuration
├── wsgi.py            # WSGI configuration
└── asgi.py            # ASGI configuration
```

## Listings App

The `listings` app contains the core functionality for the travel booking system:

- **Models**: Listing, Booking, Review, and Payment models
- **Serializers**: Django REST Framework serializers for API endpoints
- **Views**: API endpoints for listings, bookings, and payment processing
- **Tasks**: Celery background tasks for sending payment confirmation emails
- **Management Commands**: Database seeding utilities

## Payment Integration

This application integrates with the Chapa Payment Gateway for secure payment processing.

### Payment Model

The `Payment` model tracks payment transactions with the following fields:
- `booking`: One-to-one relationship with Booking
- `transaction_id`: Unique transaction reference from Chapa
- `amount`: Payment amount
- `status`: Payment status (pending, completed, failed, cancelled)
- `chapa_reference`: Reference ID from Chapa API
- `payment_url`: URL for payment checkout page

### Payment Workflow

1. **Booking Creation**: When a booking is created, a payment record is automatically created with status "pending"
2. **Payment Initiation**: The system initiates payment with Chapa API and receives a payment URL
3. **Payment Processing**: User is redirected to Chapa's secure payment page
4. **Payment Verification**: After payment, the system verifies the transaction status with Chapa
5. **Confirmation**: On successful payment:
   - Payment status is updated to "completed"
   - Booking status is updated to "confirmed"
   - Confirmation email is sent asynchronously via Celery

### API Endpoints

#### Payment Endpoints

- `POST /api/bookings/` - Create a booking and initiate payment
  - Returns booking details and payment URL
  
- `GET /api/payments/` - List all payments
- `GET /api/payments/{id}/` - Retrieve a specific payment
- `POST /api/payments/{id}/verify/` - Verify payment status for a specific payment
- `POST /api/payments/verify/` - Verify payment by transaction reference
  - Body: `{"transaction_id": "tx_ref_xxx"}`

#### Other Endpoints

- `GET /api/listings/` - List all listings
- `GET /api/listings/{id}/` - Retrieve a specific listing
- `POST /api/listings/` - Create a new listing
- `GET /api/bookings/` - List all bookings
- `GET /api/bookings/{id}/` - Retrieve a specific booking

## Configuration

The application uses Django 5.2.7 with MySQL database support. Configuration is managed through `settings.py` and environment variables.

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=alx_travel_app
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Chapa API Configuration
CHAPA_SECRET_KEY=your-chapa-secret-key-here
CHAPA_API_URL=https://api.chapa.co/v1/transaction/initialize
CHAPA_VERIFY_URL=https://api.chapa.co/v1/transaction/verify/

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com

# Celery Configuration (Redis)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Setting Up Chapa API

1. Create an account at [Chapa Developer Portal](https://developer.chapa.co/)
2. Obtain your API secret key from the dashboard
3. Add the `CHAPA_SECRET_KEY` to your `.env` file
4. Use sandbox/test credentials for development

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

2. **Set Up Database**:
   ```bash
   python manage.py migrate
   ```

3. **Set Up Environment Variables**:
   - Copy `.env.example` to `.env` (if available)
   - Fill in all required environment variables

4. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Start Redis** (for Celery):
   ```bash
   redis-server
   ```

6. **Start Celery Worker** (in a separate terminal):
   ```bash
   celery -A alx_travel_app worker --loglevel=info
   ```

7. **Start Django Development Server**:
   ```bash
   python manage.py runserver
   ```

## Testing Payment Integration

### Using Chapa Sandbox

1. Use test credentials from Chapa dashboard
2. Create a booking via `POST /api/bookings/`
3. Use the returned `payment_url` to complete payment
4. Use test card numbers provided by Chapa for testing
5. Verify payment via `POST /api/payments/{id}/verify/`

### Test Payment Flow

1. **Create Booking**:
   ```bash
   POST /api/bookings/
   {
     "listing_id": 1,
     "guest_name": "John Doe",
     "guest_email": "john@example.com",
     "guest_phone": "+251900000000",
     "check_in": "2024-01-15",
     "check_out": "2024-01-20",
     "number_of_guests": 2
   }
   ```

2. **Response includes payment_url**:
   ```json
   {
     "booking": {...},
     "payment": {...},
     "payment_url": "https://checkout.chapa.co/checkout/payment/..."
   }
   ```

3. **Verify Payment** (after user completes payment):
   ```bash
   POST /api/payments/{payment_id}/verify/
   ```

## Development

This application is part of the ALX Software Engineering program travel booking project.

### Key Features

- ✅ Secure payment processing with Chapa API
- ✅ Payment transaction tracking
- ✅ Automated email confirmations via Celery
- ✅ RESTful API endpoints
- ✅ Comprehensive error handling
- ✅ Payment status verification

### Technologies Used

- Django 5.2.7
- Django REST Framework
- Chapa Payment Gateway
- Celery (for background tasks)
- Redis (Celery broker)
- MySQL (database)
- Requests (HTTP client for API calls)

