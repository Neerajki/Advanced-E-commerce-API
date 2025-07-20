# E-commerce API with Caching and Notifications
A Django REST API for an e-commerce system with user authentication, product management, order processing, caching, and real-time notifications.

## Prerequisites
- Python 
- PostgreSQL
- Redis
-Channels
-daphne

## Setup Instructions

1. **Clone the repository**:
   bash
   git clone <repository-url>
   cd ecommerce_api
   

2. **Create and activate a virtual environment**:
   bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   

3. **Install dependencies**:
   bash
   pip install -r requirements.txt
   

4. **Set up PostgreSQL**:
   - Create a database named `ecommerce_db`
   - Update database credentials in `ecommerce_api/settings.py` if needed

5. **Set up Redis**:
   - Install and run Redis server locally
   - Ensure Redis is running on `localhost:6379`

6. **Apply migrations**:
   bash
   python manage.py migrate
   

7. **Create a superuser**:
   bash
   python manage.py createsuperuser
   

8. **Run the development server**:
   bash
   daphne -b 0.0.0.0 -p 8000 config.asgi:application


9. **Test WebSocket notifications**:
   - Use a WebSocket client (e.g., `wscat`) to connect to `ws://localhost:8000/ws/orders/`
   - Example: `wscat -c ws://localhost:8000/ws/orders/ -H "Authorization: Bearer <your-jwt-token>"`

## API Endpoints
- **Authentication**:
  - POST `/api/token/` - Obtain JWT token
  - POST `/api/token/refresh/` - Refresh JWT token
- **Categories**:
  - GET/POST `/api/categories/` - List/create categories (admin only for POST)
  - GET/PUT/DELETE `/api/categories/<id>/` - Retrieve/update/delete category (admin only for PUT/DELETE)
- **Products**:
  - GET/POST `/api/products/` - List/create products (admin only for POST)
  - GET/PUT/DELETE `/api/products/<id>/` - Retrieve/update/delete product (admin only for PUT/DELETE)
  - Filter products: `/api/products/?category=<id>&price_min=<value>&price_max=<value>&stock=0`
- **Cart**:
  - GET/POST `/api/cart/` - List/add cart items (authenticated users)
  - GET/PUT/DELETE `/api/cart/<id>/` - Retrieve/update/delete cart item
- **Orders**:
  - GET/POST `/api/orders/` - List/create orders (authenticated users)
  - GET/PUT/DELETE `/api/orders/<id>/` - Retrieve/update/delete order
  - POST `/api/orders/create_from_cart/` - Create order from cart
- **Profile**:
  - GET/PUT `/api/profile/` - View/update user profile (authenticated users)

## Caching
- Product and category lists are cached in Redis for 1 hour
- Cache is invalidated when products or categories are created/updated/deleted

## Real-time Notifications
- WebSocket endpoint: `ws://localhost:8000/ws/orders/`
- Users receive notifications when order status changes
- Requires JWT token in the Authorization header

## Testing
- Use Postman or curl to test API endpoints
- Use Django admin interface for admin operations
- Use WebSocket client to test real-time notifications

## Notes
- Ensure Redis and PostgreSQL are running before starting the server
- Admin users can manage products and categories through the admin interface or API
- Regular users can only browse products, manage their cart, and place order