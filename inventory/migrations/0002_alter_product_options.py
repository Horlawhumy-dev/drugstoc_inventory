# Generated by Django 5.0.6 on 2024-07-02 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="product",
            options={
                "permissions": [
                    ("can_add_product", "Can add product"),
                    ("can_update_product", "Can update product"),
                    ("can_delete_product", "Can delete product"),
                ]
            },
        ),
    ]
