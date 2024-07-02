# urls.py
from django.urls import path
from .views import (InventoryProductList, InventoryProductCreate,
     InventoryProductDetail,OrderListCreate, OrderDetail, OrderStatusUpdate)

app_name = 'inventory'

urlpatterns = [
    path('products', InventoryProductList.as_view(), name='product_list'),
    path('products/', InventoryProductCreate.as_view(), name='product_add'),
    path('products/<int:pk>/', InventoryProductDetail.as_view(), name='product_detail'),
    path('orders/', OrderListCreate.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetail.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdate.as_view(), name='order_status_update'),
]