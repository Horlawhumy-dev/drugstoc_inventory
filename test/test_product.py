import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from django.contrib.auth import authenticate
from inventory.models import Product, Order, OrderItem


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(email='admin@gmail.com', username='admin', password='admin123', is_staff=True)
    user.set_password('admin123')
    user.metadata = {'is_admin': True}
    user.save()
    print(f"Admin user created: {user.email}")
    return user

@pytest.fixture
def regular_user(db):
    user = User.objects.create_user(email='user@test.com', username='user', password='user123')
    user.set_password('user123')
    user.metadata = {'is_admin': False}
    user.save()
    print(f"Regular user created: {user.email}")
    return user

@pytest.fixture
def product_data():
    return {
        'name': 'Test Product',
        'description': 'Test Description',
        'quantity': 5,
        'price': 100.0
    }

@pytest.fixture
def get_token(api_client):
    def _get_token(user, password):
        response = api_client.post('/api/users/login/', {'email': user.email, 'password': password}, format='json')
        print(f"Login response data: {response.data}")
        assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.data}"
        return response.data['access']
    return _get_token

@pytest.mark.django_db
def test_regular_user_cannot_create_product(api_client, regular_user, product_data, get_token):
    token = get_token(regular_user, 'user123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = api_client.post('/api/inventory/products/add/', product_data, format='json')
    print(f"Response for regular user: {response.data}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_admin_can_create_product(api_client, admin_user, product_data, get_token):
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = api_client.post('/api/inventory/products/add/', product_data, format='json')
    print(f"Response for admin user: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == product_data['name']
    assert response.data['description'] == product_data['description']
    assert response.data['quantity'] == product_data['quantity']
    assert response.data['price'] == product_data['price']
    # Check that is_admin is True in user metadata
    assert admin_user.metadata['is_admin'] is True

@pytest.fixture
def check_password():
    def _check_password(email, password):
        user = authenticate(email=email, password=password)
        return user is not None
    return _check_password

def test_password_check(admin_user, check_password):
    assert check_password('admin@gmail.com', 'admin123') is True
    assert check_password('admin@gmail.com', 'wrongpassword') is False


@pytest.mark.django_db
def test_create_product_with_valid_data(api_client, admin_user, product_data, get_token):
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = api_client.post('/api/inventory/products/add/', product_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Product.objects.filter(name=product_data['name']).exists()

def test_unauthenticated_user_cannot_create_product(api_client, product_data):
    response = api_client.post('/api/inventory/products/add/', product_data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.django_db
def test_product_detail(api_client, admin_user, product_data, get_token):
    product = Product.objects.create(owner=admin_user, **product_data)
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = api_client.get(f'/api/inventory/products/{product.pk}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == product_data['name']
    assert response.data['description'] == product_data['description']
    assert response.data['quantity'] == product_data['quantity']
    assert response.data['price'] == product_data['price']



@pytest.mark.django_db
def test_low_stock_report(api_client, admin_user, product_data, get_token):
    # Create a product with low stock less than 10 porducts
    low_stock_product = Product.objects.create(owner=admin_user, **product_data)

    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Request the low stock report
    response = api_client.get('/api/inventory/report/stock/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['quantity'] < 10  # Assuming low stock threshold is less than 10



@pytest.mark.django_db
def test_sales_report(api_client, admin_user, product_data, get_token):
    # Assume some sales have occurred in the specified period
    period = 'day'  # Example sales period

    # Perform authentication
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Request the sales report for the specified period
    response = api_client.get(f'/api/inventory/report/sales/{period}/')
    assert response.status_code == status.HTTP_200_OK

    assert 'total_sales' not in response.data
    assert len(response.data) <= 0

def test_unauthenticated_user_cannot_access_low_stock_report(api_client):
    response = api_client.get('/api/inventory/report/stock/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED




""" Order test cases """

@pytest.mark.django_db
def test_regular_user_add_product_to_order(api_client, regular_user, product_data, get_token):
    token = get_token(regular_user, 'user123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    # Create a product first
    product = Product.objects.create(owner=regular_user, **product_data)
    
    # Create an order with the product
    order_data = {
        'items': [
            {'product': product.id, 'quantity': 1}
        ],
    }
    
    response = api_client.post('/api/inventory/orders/', order_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_admin_user_add_product_to_order(api_client, admin_user, product_data, get_token):
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    # Create a product first
    product = Product.objects.create(owner=admin_user, **product_data)
    
    # Create an order with the product
    order_data = {
        'items': [
            {'product': product.id, 'quantity': 2}
        ],
    }
    
    response = api_client.post('/api/inventory/orders/', order_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_order_detail(api_client, admin_user, product_data, get_token):
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    
    # Create a product first
    product = Product.objects.create(owner=admin_user, **product_data)
    
    # Create an order with the product
    order_data = {
        'items': [
            {'product': product.id, 'quantity': 1}
        ],
    }
    
    response = api_client.post('/api/inventory/orders/', order_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    
    # Retrieve order detail
    order_id = response.data['id']
    detail_response = api_client.get(f'/api/inventory/orders/{order_id}/')
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data['id'] == order_id
    assert len(detail_response.data) > 1  # Ensure the product is part of the order


@pytest.mark.django_db
def test_most_frequently_ordered_product(api_client, regular_user, product_data, get_token):
    token = get_token(regular_user, 'user123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Create products
    product1 = Product.objects.create(owner=regular_user, **product_data)

    # Create orders with order items
    order1 = Order.objects.create(owner=regular_user)
    order2 = Order.objects.create(owner=regular_user)

    item1 = OrderItem.objects.create(order=order1, product=product1, quantity=3, price=product1.price)
    item2 = OrderItem.objects.create(order=order2, product=product1, quantity=4, price=product1.price)

    # Call the endpoint to get the most frequently ordered product
    response = api_client.get('/api/inventory/report/order/frequent')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['product_name'] == product1.name
    assert response.data['total_quantity'] > item1.quantity

@pytest.mark.django_db
def test_no_orders_for_user(api_client, regular_user, get_token):
    token = get_token(regular_user, 'user123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    response = api_client.get('/api/inventory/report/order/frequent')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == "No frequent ordered product found."
