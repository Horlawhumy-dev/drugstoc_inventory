from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'created_at', 'updated_at')
    list_display_links = ['id', 'name']
    list_filter = ('name',)
    search_fields = ('title', 'description')
    ordering = ('-created_at',)