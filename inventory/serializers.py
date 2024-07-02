# serializers.py
from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'quantity', 'price', 'created_at', 'updated_at', 'owner']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

@transaction.atomic
class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'products']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product in products_data:
            product_data = product.pop('product')
            product_instance = Product.objects.get(id=product_data['id'])
            OrderItem.objects.create(order=order, product=product_instance, **product)
        return order
