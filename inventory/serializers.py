# serializers.py
import logging
from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction
from django.db.models import Sum


# Set up logging
logger = logging.getLogger(__name__)

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)

    def get_owner(self, obj):
        return obj.owner.name
        
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'quantity', 'price', 'created_at', 'updated_at', 'owner']

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.name

    def get_total_price(self, obj):
        total_price = sum(item.quantity * item.product.price for item in obj.items.all())
        return total_price

    class Meta:
        model = Order
        fields = ['id', 'owner', 'status', 'items', 'total_price', 'created_at', 'updated_at']

    #rollback if any transaction fails
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        total_order_price = self.process_order_items(order, items_data)
        
        order.save()
        return order

    def process_order_items(self, order, items_data):
        total_order_price = 0

        for item_data in items_data:
            product_id = item_data['product'].id
            order_quantity = item_data['quantity']

            # Retrieve the product object
            try:
                product_obj = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

            if product_obj.quantity < order_quantity:
                raise serializers.ValidationError(f"Insufficient stock for product {product_obj.name}.")

            unit_price = product_obj.price
            item_price = order_quantity * unit_price
            total_order_price += item_price

            OrderItem.objects.create(order=order, product=product_obj, quantity=order_quantity)

            product_obj.quantity -= order_quantity
            product_obj.save()