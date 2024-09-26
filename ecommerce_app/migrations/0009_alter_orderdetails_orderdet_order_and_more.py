# Generated by Django 5.1.1 on 2024-09-25 11:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0008_alter_offer_details_offer_del_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='orderDet_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to='ecommerce_app.order'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='orderDet_size_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.size'),
        ),
    ]
