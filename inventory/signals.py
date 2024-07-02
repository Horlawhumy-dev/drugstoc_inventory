from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from django.db.models import Value
from .models import Product

@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):

    # Concatenate fields and define the output_field explicitly
    search_vector = SearchVector('title', 'description')
    
    # Perform the update on the new news search vector
    Product.objects.filter(pk=instance.pk).update(search_vector=search_vector)
