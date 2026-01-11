# ALX Travel App

A Django-based travel booking application with listings, bookings, and reviews functionality.

## Features

- **Listings**: Property listings with details such as location, price, amenities, and availability
- **Bookings**: Booking management with guest information and booking status
- **Reviews**: User reviews and ratings for listings
- **API Serializers**: Django REST Framework serializers for Listing and Booking models
- **Database Seeding**: Management command to populate the database with sample data
- **Background Jobs**: Asynchronous email notifications using Celery with RabbitMQ

## Project Structure

```
alx_travel_app/
├── alx_travel_app/
│   ├── listings/
│   │   ├── models.py          # Listing, Booking, and Review models
│   │   ├── serializers.py     # DRF serializers for Listing and Booking
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── seed.py    # Database seeding command
│   │   └── ...
│   └── ...
└── manage.py
```

## Models

### Listing
Represents a property available for booking with fields including:
- Title, description, address, city, state, country
- Price per night, property type, max guests
- Bedrooms, bathrooms, amenities
- Availability status

### Booking
Represents a booking made for a listing with:
- Foreign key relationship to Listing
- Guest information (name, email, phone)
- Check-in and check-out dates
- Number of guests, total price, status
- Special requests

### Review
Represents a review for a listing with:
- Foreign key relationship to Listing
- Reviewer information
- Rating (1-5) and comment

## Setup

### Prerequisites
- Python 3.8+
- MySQL database server
- RabbitMQ server (for background task processing)
- Virtual environment (recommended)

### Environment Setup

1. **Create and activate a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Create a `.env` file** in the project root with the following variables:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (MySQL)
DB_NAME=alx_travel_app
DB_USER=root
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=3306

# CORS Settings
CORS_ALLOW_ALL=True
```

3. **Install dependencies:**
```bash
pip install -r alx_travel_app/requirement.txt
```

4. **Create the MySQL database:**
```bash
mysql -u root -p
CREATE DATABASE alx_travel_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Seed the database with sample data:**
```bash
python manage.py seed
```

To clear existing data before seeding:
```bash
python manage.py seed --clear
```

## Celery and RabbitMQ Setup

This project uses Celery with RabbitMQ for asynchronous background task processing, specifically for sending booking confirmation emails.

### Installing RabbitMQ

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

#### macOS:
```bash
brew install rabbitmq
brew services start rabbitmq
```

#### Windows:
Download and install from [RabbitMQ Downloads](https://www.rabbitmq.com/download.html)

### Configuring RabbitMQ

1. **Start RabbitMQ server:**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start rabbitmq-server
   
   # macOS
   brew services start rabbitmq
   
   # Or manually
   rabbitmq-server
   ```

2. **Verify RabbitMQ is running:**
   ```bash
   sudo rabbitmqctl status
   ```

3. **Optional: Create a dedicated user (recommended for production):**
   ```bash
   sudo rabbitmqctl add_user alx_travel_app your_password
   sudo rabbitmqctl set_permissions -p / alx_travel_app ".*" ".*" ".*"
   ```

### Environment Variables for Celery

Add the following to your `.env` file:
```env
# Celery Configuration (RabbitMQ)
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://

# Email Configuration (for sending booking confirmation emails)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
```

**Note:** For Gmail, you'll need to use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

### Running Celery Worker

To process background tasks, you need to run a Celery worker in a separate terminal:

```bash
# Activate your virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run Celery worker
celery -A alx_travel_app worker --loglevel=info
```

The worker will process tasks like sending booking confirmation emails asynchronously.

### Running the Application

You need to run both Django and Celery:

**Terminal 1 - Django Development Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A alx_travel_app worker --loglevel=info
```

### Testing Background Tasks

When you create a booking via the API, a booking confirmation email will be sent asynchronously:

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing_id": 1,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "check_in": "2026-01-15",
    "check_out": "2026-01-20",
    "number_of_guests": 2,
    "total_price": "500.00"
  }'
```

The email will be sent in the background without blocking the API response. Check the Celery worker logs to see the task execution.

## API Endpoints

The application provides RESTful API endpoints for managing listings and bookings. All endpoints are accessible under `/api/`.

### Base URL
```
http://localhost:8000/api/
```

### API Documentation (Swagger)
Interactive API documentation is available at:
```
http://localhost:8000/swagger/
```

### Listings Endpoints

#### List all listings
- **GET** `/api/listings/`
- Returns a list of all listings
- Query parameters: None

#### Retrieve a specific listing
- **GET** `/api/listings/{id}/`
- Returns details of a specific listing

#### Create a new listing
- **POST** `/api/listings/`
- Creates a new listing
- Required fields: `title`, `description`, `address`, `city`, `country`, `price_per_night`, `property_type`, `max_guests`, `bedrooms`, `bathrooms`

#### Update a listing (full update)
- **PUT** `/api/listings/{id}/`
- Updates all fields of a listing

#### Update a listing (partial update)
- **PATCH** `/api/listings/{id}/`
- Updates specific fields of a listing

#### Delete a listing
- **DELETE** `/api/listings/{id}/`
- Deletes a listing

#### Get bookings for a listing
- **GET** `/api/listings/{id}/bookings/`
- Returns all bookings associated with a specific listing

### Bookings Endpoints

#### List all bookings
- **GET** `/api/bookings/`
- Returns a list of all bookings
- Query parameters: `listing_id` (optional) - Filter bookings by listing ID
  - Example: `/api/bookings/?listing_id=1`

#### Retrieve a specific booking
- **GET** `/api/bookings/{id}/`
- Returns details of a specific booking

#### Create a new booking
- **POST** `/api/bookings/`
- Creates a new booking
- Required fields: `listing_id`, `guest_name`, `guest_email`, `check_in`, `check_out`, `number_of_guests`, `total_price`
- Validations:
  - Check-out date must be after check-in date
  - Number of guests cannot exceed listing's max_guests

#### Update a booking (full update)
- **PUT** `/api/bookings/{id}/`
- Updates all fields of a booking

#### Update a booking (partial update)
- **PATCH** `/api/bookings/{id}/`
- Updates specific fields of a booking

#### Delete a booking
- **DELETE** `/api/bookings/{id}/`
- Deletes a booking

## API Serializers

### ListingSerializer
Serializes Listing model with all fields for API responses.

### BookingSerializer
Serializes Booking model with:
- Listing information (title and ID)
- Guest details
- Booking dates and pricing
- Validation for check-in/check-out dates and guest limits

## Testing the API

### Using Postman

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Test GET request (List all listings):**
   - Method: GET
   - URL: `http://localhost:8000/api/listings/`

3. **Test POST request (Create a listing):**
   - Method: POST
   - URL: `http://localhost:8000/api/listings/`
   - Headers: `Content-Type: application/json`
   - Body (JSON):
     ```json
     {
       "title": "Beautiful Apartment in Downtown",
       "description": "A cozy apartment in the heart of the city",
       "address": "123 Main St",
       "city": "New York",
       "state": "NY",
       "country": "USA",
       "price_per_night": "150.00",
       "property_type": "apartment",
       "max_guests": 4,
       "bedrooms": 2,
       "bathrooms": 1,
       "amenities": "WiFi, Air Conditioning, Kitchen"
     }
     ```

4. **Test GET request (Retrieve a listing):**
   - Method: GET
   - URL: `http://localhost:8000/api/listings/1/`

5. **Test PUT request (Update a listing):**
   - Method: PUT
   - URL: `http://localhost:8000/api/listings/1/`
   - Headers: `Content-Type: application/json`
   - Body: Updated JSON data

6. **Test DELETE request (Delete a listing):**
   - Method: DELETE
   - URL: `http://localhost:8000/api/listings/1/`

Similar patterns apply for bookings endpoints at `/api/bookings/`.

### Using cURL

```bash
# List all listings
curl -X GET http://localhost:8000/api/listings/

# Create a listing
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beautiful Apartment",
    "description": "A cozy apartment",
    "address": "123 Main St",
    "city": "New York",
    "country": "USA",
    "price_per_night": "150.00",
    "property_type": "apartment",
    "max_guests": 4,
    "bedrooms": 2,
    "bathrooms": 1
  }'

# Retrieve a specific listing
curl -X GET http://localhost:8000/api/listings/1/

# Update a listing
curl -X PUT http://localhost:8000/api/listings/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title", ...}'

# Delete a listing
curl -X DELETE http://localhost:8000/api/listings/1/
```

## Management Commands

### seed
Populates the database with sample listings, bookings, and reviews.

Usage:
```bash
python manage.py seed
python manage.py seed --clear  # Clear existing data first
```

## Development

This project uses:
- Django 5.2.7
- Django REST Framework
- MySQL database
- Celery (for asynchronous task processing)
- RabbitMQ (message broker for Celery)

## License

This project is part of the ALX Software Engineering program.

