import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User
from inventory.models import Product

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(email='admin@gmail.co', username='admin', password='admin123', is_staff=True)

@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username='user',email='user@test.co', password='user123')

@pytest.fixture
def product_data():
    return {
        'name': 'Test Product',
        'description': 'Test Description',
        'quantity': 10,
        'price': 100.0
    }

@pytest.mark.django_db
def test_admin_can_create_product(api_client, admin_user, product_data):
    url = reverse('product_add')
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(url, product_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == product_data['name']
    assert response.data['description'] == product_data['description']
    assert response.data['quantity'] == product_data['quantity']
    assert response.data['price'] == product_data['price']

# @pytest.mark.django_db
# def test_non_admin_cannot_create_product(api_client, regular_user, product_data):
#     url = reverse('product_add')
#     api_client.force_authenticate(user=regular_user)
#     response = api_client.post(url, product_data, format='json')
#     assert response.status_code == status.HTTP_403_FORBIDDEN

# @pytest.mark.django_db
# def test_create_product_with_invalid_data(api_client, admin_user, product_data):
#     url = reverse('product_add')
#     api_client.force_authenticate(user=admin_user)
#     invalid_data = product_data.copy()
#     invalid_data['price'] = -100  # Invalid price
#     response = api_client.post(url, invalid_data, format='json')
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert 'price' in response.data

# @pytest.mark.django_db
# def test_unauthenticated_user_cannot_create_product(api_client, product_data):
#     url = reverse('product_add')
#     response = api_client.post(url, product_data, format='json')
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
