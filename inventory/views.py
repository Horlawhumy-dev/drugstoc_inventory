# views.py
import logging
from django.contrib.postgres.search import SearchQuery, SearchRank
from django_filters import rest_framework as filters
from django.db import transaction
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, F
from datetime import datetime, timedelta
from .models import Product, Order, OrderItem
from users.permissions import IsAdminOrReadOnly
from .serializers import ProductSerializer, OrderSerializer, LowStockProductSerializer, SalesReportSerializer
from django.db import transaction
from users.authentication import CustomJWTAuthentication

# Set up logging
logger = logging.getLogger(__name__)

class InventoryProductList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        logger.info(f"User {request.user.id} requested product list")
        products = Product.objects.all()
        
        # Apply pagination
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

class InventoryProductCreate(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]

    def post(self, request):
        logger.info(f"User {request.user.id} is attempting to create a new product")
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            logger.info(f"User {request.user.id} successfully created product {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning(f"User {request.user.id} failed to create product: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryProductDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        logger.info(f"User {request.user.id} requested details for product {pk}")
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        logger.info(f"User {request.user.id} is attempting to update product {pk}")
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.id} successfully updated product {pk}")
            return Response(serializer.data)
        logger.warning(f"User {request.user.id} failed to update product {pk}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        logger.info(f"User {request.user.id} is attempting to delete product {pk}")
        product = self.get_object(pk)
        product.delete()
        logger.info(f"User {request.user.id} successfully deleted product {pk}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'created_at']



class OrderListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request):
        logger.info(f"User {request.user.id} requested their order list")
        orders = Order.objects.filter(owner=request.user)
        
        filterset = OrderFilter(request.GET, queryset=orders)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        
        orders = filterset.qs
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"User {request.user.id} is attempting to create a new order")
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            
            serializer.save(owner=request.user)
            logger.info(f"User {request.user.id} successfully created order {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"User {request.user.id} failed to create order: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDetail(APIView):
    """
        View to get order detail by owner
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CustomJWTAuthentication]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk, owner=self.request.user)
        except Order.DoesNotExist:
            logger.error(f"User {self.request.user.id} attempted to access non-existent order {pk}")
            return None

    def get(self, request, pk):
        logger.info(f"User {request.user.id} requested details for order {pk}")
        order = self.get_object(pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def delete(self, request, pk):
        logger.info(f"User {request.user.id} is attempting to delete order {pk}")
        order = self.get_object(pk)
        if order:
            order.delete()
            logger.info(f"User {request.user.id} successfully deleted order {pk}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        logger.warning(f"User {request.user.id} attempted to delete non-existent order {pk}")
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

class OrderStatusUpdate(APIView):
    """
        View to update order status by Admin
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]

    def patch(self, request, pk):
        logger.info(f"User {request.user.id} is attempting to update the status of order {pk}")

        with transaction.atomic():
            order = self.get_order_object(pk)
            if not order:
                return Response(status=status.HTTP_404_NOT_FOUND)

            order_status = self.get_status_from_request(request)
            if not order_status:
                return Response({'error': 'Invalid order status'}, status=status.HTTP_400_BAD_REQUEST)

            updated_order = self.update_order_status(order, order_status)
            if not updated_order:
                return Response({'error': 'Failed to update status'}, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"User {request.user.id} successfully updated status of order {pk} to {order_status}")
            serializer = OrderSerializer(updated_order)
            return Response(serializer.data)

    def get_order_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            logger.error(f"User {self.request.user.id} attempted to update non-existent order {pk}")
            return None

    def get_status_from_request(self, request):
        status = request.data.get('status')
        if status not in [choice[0] for choice in Order.STATUS_CHOICES]:
            logger.warning(f"User {self.request.user.id} provided invalid status {status}")
            return None
        return status

    def update_order_status(self, order, status):
        order.status = status
        try:
            order.save()
            return order
        except Exception as e:
            logger.error(f"Failed to update status for order {order.id}: {str(e)}")
            return None


class LowStockReportView(APIView):
    """
        Should be accessed by an admin but GET is part of SAFE METHODS for all
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]
    def get(self, request):
        low_stock_products = Product.objects.filter(quantity__lt=10)
        serializer = LowStockProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)

class SalesReportView(APIView):
    """
        Should be accessed by an admin but GET is part of SAFE METHODS for all
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    authentication_classes = [CustomJWTAuthentication]
    def get(self, request, period='day'):
        now = datetime.now()

        start_project = None

        #match case would have been better but its only supported by python3.8+

        if period == 'day':
            start_date = now - timedelta(days=1)
        elif period ==  'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            return Response({'error': 'Invalid period specified.'}, status=status.HTTP_400_BAD_REQUEST)

        sales_data = OrderItem.objects.filter(
            order__created_at__gte=start_date
        ).values(
            date=F('order__created_at__date')
        ).annotate(
            total_sales=Sum(F('quantity') * F('price'))
        )

        serializer = SalesReportSerializer(sales_data, many=True)
        return Response(serializer.data)



class ProductSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.AllowAny]
    authentication_classes = [CustomJWTAuthentication]

    """
        This will only functional with postgres database connection
    """

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            logger.warning("Search query not provided.")
            return Response({"error": "Please provide a search query!"}, status=status.HTTP_400_BAD_REQUEST)

        search_query = SearchQuery(query)
        search_rank = SearchRank('search_vector', search_query)

        results = Product.objects.filter(search_vector=search_query)\
            .annotate(rank=search_rank)\
            .order_by('-rank', '-created_at')

        serializer = ProductSerializer(results, many=True)
        logger.info(f"Search results returned for query: {query}.")
        return Response(serializer.data)

    
from django.db.models import Sum

class FrequentOrderedProductView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        #returns the first instance of most frequent 9by quantity summation) ordered item product in the past
        with transaction.atomic():
            most_frequent_product = (
                OrderItem.objects
                    .filter(order__owner=user)
                    .values('product')
                    .annotate(total_quantity=Sum('quantity'))
                    .order_by('total_quantity') #highest quantity down to least
                    .first()
            ) 
            if most_frequent_product:
                product = Product.objects.get(id=most_frequent_product['product'])
                serializer = ProductSerializer(product)
                return Response(
                    {
                        "product_name": serializer.data.get('name'),
                        "total_quantity": serializer.data.get('quantity')
                    }
                )
            else:
                return Response({"detail": "No frequent ordered product found."}, status=404)

        