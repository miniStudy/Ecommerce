# Generated by Django 5.1.1 on 2024-09-21 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='return',
            name='return_product',
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='orderDet_status',
            field=models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected'), ('O', 'OutForDelivery'), ('D', 'Delivered'), ('RET', 'RETURNED'), ('C', 'Cancelled')], default='P', max_length=3),
        ),
    ]
