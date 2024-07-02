# urls.py
from django.urls import path
from .views import (InventoryProductList, InventoryProductCreate,
     InventoryProductDetail,OrderListCreate, OrderDetail, OrderStatusUpdate,
     LowStockReportView, SalesReportView)

app_name = 'inventory'

urlpatterns = [
    path('products', InventoryProductList.as_view(), name='product_list'),
    path('products/', InventoryProductCreate.as_view(), name='product_add'),
    path('products/<str:pk>/', InventoryProductDetail.as_view(), name='product_detail'),
    path('orders/', OrderListCreate.as_view(), name='order_list_create'),
    path('orders/<str:pk>/', OrderDetail.as_view(), name='order_detail'),
    path('orders/<str:pk>/status/', OrderStatusUpdate.as_view(), name='order_status_update'),
    path('report/stock/', LowStockReportView.as_view(), name='low-stock-report'),
    path('report/sales/<str:period>/', SalesReportView.as_view(), name='sales-report')
]