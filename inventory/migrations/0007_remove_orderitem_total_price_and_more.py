# Generated by Django 5.0.6 on 2024-07-02 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0006_rename_price_orderitem_total_price_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="total_price",
        ),
        migrations.RemoveField(
            model_name="orderitem",
            name="total_quantity",
        ),
    ]