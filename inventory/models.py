from drugstoc_inventory.model_utils import BaseModelMixin
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db import models


class Product(BaseModelMixin):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0) #suitable model field like float or decimal might be opted for
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