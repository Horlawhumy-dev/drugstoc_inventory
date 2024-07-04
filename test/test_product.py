import pytest
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from django.contrib.auth import authenticate
from inventory.models import Product


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
        'quantity': 10,
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

@pytest.mark.django_db
def test_create_product_with_invalid_data(api_client, admin_user, get_token):
    token = get_token(admin_user, 'admin123')
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    invalid_data = {
        'name': 'Invalid Product',
        'description': 'Invalid Description',
        'quantity': -1,  # Invalid quantity (asuming -1 for negative)
        'price': 100.0
    }
    response = api_client.post('/api/inventory/products/add/', invalid_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    """
        response.data form like
        {
            "quantity": [
                "Ensure this value is greater than or equal to 0."
            ]
        }
    """
    assert response.data.get('quantity')[0] == 'Ensure this value is greater than or equal to 0.' #test error message as return in a list

def test_unauthenticated_user_cannot_create_product(api_client, product_data):
    response = api_client.post('/api/inventory/products/add/', product_data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
