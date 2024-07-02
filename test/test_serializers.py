import pytest
from rest_framework.exceptions import ValidationError
from inventory.models import Product, Order, OrderItem
from inventory.serializers import OrderSerializer, OrderItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_order_item_serializer():
    user = User.objects.create_user(username='testuser', email='admin@mail.com', password='password')
    product = Product.objects.create(name='Test Product', description='Test Description', quantity=100, price=10, owner=user)
    order = Order.objects.create(owner=user, status='pending')
    
    data = {
        'product': product.id,
        'quantity': 10
    }
    
    serializer = OrderItemSerializer(data=data)
    assert serializer.is_valid()
    item = serializer.save(order=order)
    
    assert item.order == order
    assert item.product == product
    assert item.quantity == 10

@pytest.mark.django_db
def test_order_serializer():
    user = User.objects.create_user(username='testuser2', email='admin2@mail.com', password='password')
    product = Product.objects.create(name='Test Product2', description='Test Description', quantity=100, price=10, owner=user)
    
    data = {
        'status': 'pending',
        'items': [
            {
                'product': product.id,
                'quantity': 10
            }
        ]
    }
    
    serializer = OrderSerializer(data=data)
    assert serializer.is_valid()
    
    order = serializer.save(owner=user)
    
    assert order.owner == user
    assert order.status == 'pending'
    assert order.items.count() == 1
    
    item = order.items.first()
    assert item.product == product
    assert item.quantity == 10
    

@pytest.mark.django_db
def test_order_serializer_invalid_product():
    user = User.objects.create_user(username='testuser3', email='admin3@mail.com', password='password')
    
    data = {
        'status': 'pending',
        'items': [
            {
                'product': 999,  # Invalid product ID
                'quantity': 10
            }
        ]
    }
    
    serializer = OrderSerializer(data=data)
    assert not serializer.is_valid()
    assert 'items' in serializer.errors


@pytest.mark.django_db
def test_order_serializer_insufficient_stock():
    user = User.objects.create_user(username='testuser4', email='admin4@mail.com', password='password')
    product = Product.objects.create(name='Test Product3', description='Test Description', quantity=5, price=10, owner=user)
    
    data = {
        'status': 'pending',
        'items': [
            {
                'product': product.id,
                'quantity': 10
            }
        ]
    }
    
    serializer = OrderSerializer(data=data)
    assert serializer.is_valid()
    
    with pytest.raises(ValidationError) as excinfo:
        serializer.save(owner=user)
    
    assert 'Insufficient stock' in str(excinfo.value)

@pytest.mark.django_db
def test_order_serializer_partial_update():
    user = User.objects.create_user(username='testuser5', email='admin5@mail.com', password='password')
    product = Product.objects.create(name='Test Product4', description='Test Description', quantity=100, price=10, owner=user)
    order = Order.objects.create(owner=user, status='pending')
    OrderItem.objects.create(order=order, product=product, quantity=10)
    
    data = {
        'status': 'completed'
    }
    
    serializer = OrderSerializer(order, data=data, partial=True)
    assert serializer.is_valid()
    
    updated_order = serializer.save()
    assert updated_order.status == 'completed'
    assert updated_order.items.count() == 1
