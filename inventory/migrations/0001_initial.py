# Generated by Django 5.0.6 on 2024-07-02 08:20

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import drugstoc_inventory.model_utils
from django.conf import settings
from django.db import migrations, models
from django.contrib.postgres.search import SearchVector
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Value



def create_product_owner_group(apps, schema_editor):
    CustomUser = apps.get_model('users', 'User')
    Product = apps.get_model('inventory', 'Product')
    
    product_owner_group, created = Group.objects.get_or_create(name='Admin')
    
    product_content_type = ContentType.objects.get_for_model(Product)
    
    permissions = [
        Permission.objects.get_or_create(
            codename='can_add_product',
            name='Can add product',
            content_type=product_content_type,
        )[0],
        Permission.objects.get_or_create(
            codename='can_update_product',
            name='Can update product',
            content_type=product_content_type,
        )[0],
        Permission.objects.get_or_create(
            codename='can_delete_product',
            name='Can delete product',
            content_type=product_content_type,
        )[0]
    ]
    
    product_owner_group.permissions.add(*permissions)

# def add_search_vector(apps, schema_editor):
#     Product = apps.get_model('inventory', 'Product')
#     Product.objects.update(search_vector=SearchVector('title', 'description'))

# def add_search_vector(apps, schema_editor):
#     Product = apps.get_model('inventory', 'Product')
#     User = apps.get_model(settings.AUTH_USER_MODEL)

#     for product in Product.objects.select_related('owner').all():
#         if product.owner:
#             search_vector = SearchVector(
#                 'name', 
#                 'description', 
#                 Value(product.owner.name, output_field=CharField()),
#                 Value(product.owner.email, output_field=CharField())
#             )
#             product.search_vector = search_vector
#             product.save()



class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=drugstoc_inventory.model_utils.generate_id,
                        editable=False,
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="active"
                    ),
                ),
                ("name", models.CharField(max_length=200, unique=True)),
                ("description", models.TextField()),
                ("quantity", models.IntegerField(default=0)),
                ("price", models.IntegerField(default=0)),
                (
                    "search_vector",
                    django.contrib.postgres.search.SearchVectorField(
                        blank=True, null=True
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["name"], name="inventory_p_name_f6a6a1_idx"),
                    models.Index(
                        fields=["owner"], name="inventory_p_owner_i_cbbddf_idx"
                    ),
                    django.contrib.postgres.indexes.GinIndex(
                        fields=["search_vector"], name="inventory_p_search__08c329_gin"
                    ),
                ],
            },
        ),
        migrations.RunPython(create_product_owner_group),
        # migrations.RunPython(add_search_vector)
    ]