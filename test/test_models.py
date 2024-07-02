import pytest
from django.contrib.auth import get_user_model
from inventory.models import Product, Order, OrderItem

User = get_user_model()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='password123',
        email='testuser@example.com'
    )

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='adminuser',
        password='adminpassword',
        email='admin@example.com'
    )

@pytest.mark.django_db
def test_product_creation(user):
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        quantity=100,
        price=10,
        owner=user
    )
    
    assert product.name == 'Test Product'
    assert product.description == 'Test Description'
    assert product.quantity == 100
    assert product.price == 10
    assert product.owner == user


@pytest.mark.django_db
def test_order_creation(user):
    order = Order.objects.create(owner=user, status='pending')
    
    assert order.owner == user
    assert order.status == 'pending'
    assert order.items.count() == 0


@pytest.mark.django_db
def test_order_item_creation(user):
    product = Product.objects.create(
        name='Test Product',
        description='Test Description',
        quantity=100,
        price=10,
        owner=user
    )
    order = Order.objects.create(owner=user, status='pending')
    order_item = OrderItem.objects.create(order=order, product=product, quantity=10)
    
    assert order_item.order == order
    assert order_item.product == product
    assert order_item.quantity == 10
