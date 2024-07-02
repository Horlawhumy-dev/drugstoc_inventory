from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'created_at', 'updated_at')
    list_display_links = ['id', 'name']
    list_filter = ('name',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'status', 'created_at', 'updated_at')
    list_display_links = ['id', 'owner']
    list_filter = ('owner',)
    search_fields = ('status', 'owner')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'price', 'created_at', 'updated_at')
    list_display_links = ['id']
    ordering = ('-created_at',)