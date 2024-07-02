# urls.py
from django.urls import path
from .views import InventoryProductList, InventoryProductCreate, InventoryProductDetail

app_name = 'inventory'

urlpatterns = [
    path('products', InventoryProductList.as_view(), name='product_list'),
    path('products/', InventoryProductCreate.as_view(), name='product_add'),
    path('products/<int:pk>/', InventoryProductDetail.as_view(), name='product_detail'),
]
