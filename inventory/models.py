from drugstoc_inventory.model_utils import BaseModelMixin
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.conf import settings


class Product(BaseModelMixin):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0) #suitable model field like float or decimal might be opted for
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
            GinIndex(fields=['search_vector']),
        ]
        permissions = [
            ("can_add_product", "Can add product"),
            ("can_update_product", "Can update product"),
            ("can_delete_product", "Can delete product")
        ]

    def __str__(self):
        return self.name



class Order(BaseModelMixin):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])


class OrderItem(BaseModelMixin):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
