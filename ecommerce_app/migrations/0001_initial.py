# Generated by Django 5.1.1 on 2024-09-21 12:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('admin_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('admin_fname', models.CharField(max_length=55)),
                ('admin_lname', models.CharField(max_length=55)),
                ('admin_email', models.EmailField(max_length=254, unique=True)),
                ('admin_password', models.CharField(max_length=155)),
                ('admin_date_joined', models.DateTimeField(auto_now_add=True)),
                ('admin_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('admin_role', models.CharField(default='admin', max_length=20)),
                ('admin_profile_image', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('admin_otp', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Admin',
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('brand_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('brand_name', models.CharField(blank=True, max_length=155, null=True)),
            ],
            options={
                'db_table': 'Brand',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=155)),
            ],
            options={
                'db_table': 'Category',
            },
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('color_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('color_color', models.CharField(max_length=55)),
            ],
            options={
                'db_table': 'Color',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('customer_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('customer_fname', models.CharField(max_length=55)),
                ('customer_lname', models.CharField(max_length=55)),
                ('customer_email', models.EmailField(max_length=254, unique=True)),
                ('customer_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('customer_password', models.CharField(max_length=155)),
                ('customer_date_joined', models.DateTimeField(auto_now_add=True)),
                ('customer_active', models.BooleanField(default=True)),
                ('customer_otp', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='delivery_boy',
            fields=[
                ('db_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('db_name', models.CharField(max_length=55)),
                ('db_email', models.EmailField(max_length=254, unique=True)),
                ('db_password', models.CharField(max_length=55)),
                ('db_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('db_address', models.TextField()),
                ('db_otp', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'delivery_boy',
            },
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('offer_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('offer_name', models.CharField(max_length=155)),
                ('offer_discount', models.IntegerField()),
                ('offer_starting_date', models.DateField()),
                ('offer_ending_date', models.DateField()),
            ],
            options={
                'db_table': 'Offer',
            },
        ),
        migrations.CreateModel(
            name='Product_Availability',
            fields=[
                ('product_ava_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('product_ava_area', models.CharField(max_length=155)),
                ('product_ava_pincode', models.CharField(max_length=155)),
            ],
            options={
                'db_table': 'Product_Availability',
            },
        ),
        migrations.CreateModel(
            name='Customer_Address',
            fields=[
                ('address_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('address_customer_fname', models.CharField(max_length=255)),
                ('address_line1', models.TextField()),
                ('address_line2', models.TextField(blank=True, null=True)),
                ('address_landmark', models.CharField(blank=True, max_length=255, null=True)),
                ('address_country', models.CharField(max_length=155)),
                ('address_city', models.CharField(max_length=155)),
                ('address_state', models.CharField(max_length=155)),
                ('address_zipcode', models.IntegerField()),
                ('address_phone', models.CharField(max_length=12)),
                ('address_default', models.BooleanField(default=False)),
                ('address_customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
            ],
            options={
                'db_table': 'Customer_Address',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('order_code', models.CharField(max_length=55)),
                ('order_payment_mode', models.CharField(max_length=155)),
                ('order_amount', models.FloatField()),
                ('order_tax_amount', models.FloatField()),
                ('order_delivery_charge', models.FloatField(blank=True, null=True)),
                ('order_paid', models.BooleanField(default=False)),
                ('order_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('order_delivered_date', models.DateField(blank=True, null=True)),
                ('order_note', models.CharField(blank=True, max_length=550, null=True)),
                ('order_address_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer_address')),
                ('order_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
            ],
            options={
                'db_table': 'Order',
            },
        ),
        migrations.CreateModel(
            name='OrderDetails',
            fields=[
                ('orderDet_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('orderDet_price', models.FloatField()),
                ('orderDet_quantity', models.IntegerField()),
                ('orderDet_size_id', models.IntegerField()),
                ('orderDet_status', models.CharField(choices=[('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected'), ('O', 'OutForDelivery'), ('D', 'Delivered'), ('C', 'Cancelled')], default='P', max_length=1)),
                ('orderDet_color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.color')),
                ('orderDet_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
                ('orderDet_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.order')),
            ],
            options={
                'db_table': 'OrderDetails',
            },
        ),
        migrations.CreateModel(
            name='assign_orders',
            fields=[
                ('assign_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('assign_order_todo', models.CharField(choices=[('For_Delivery', 'For_Delivery'), ('For_Returning', 'For_Returning')], default='For_Delivery', max_length=15)),
                ('assign_date', models.DateField(auto_now_add=True, null=True)),
                ('assign_db_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.delivery_boy')),
                ('assign_orderDet_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.orderdetails')),
            ],
            options={
                'db_table': 'assign_orders',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('product_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=155)),
                ('product_mrp', models.FloatField()),
                ('product_cost', models.FloatField()),
                ('product_selling_price', models.FloatField()),
                ('product_desc', models.CharField(max_length=355)),
                ('product_stock', models.IntegerField()),
                ('product_status', models.CharField(choices=[('InStock', 'InStock'), ('OutOfStock', 'OutOfStock')], default='InStock', max_length=55)),
                ('product_img1', models.ImageField(upload_to='uploads/')),
                ('product_img2', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img3', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img4', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img5', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img6', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img7', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_img8', models.ImageField(blank=True, null=True, upload_to='uploads/')),
                ('product_returnable', models.BooleanField(blank=True, default=True, null=True)),
                ('product_active', models.BooleanField(default=True)),
                ('product_brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.brand')),
                ('product_cat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.category')),
                ('product_color', models.ManyToManyField(max_length=55, to='ecommerce_app.color')),
                ('product_ava', models.ManyToManyField(blank=True, to='ecommerce_app.product_availability')),
            ],
            options={
                'db_table': 'Product',
            },
        ),
        migrations.AddField(
            model_name='orderdetails',
            name='orderDet_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product'),
        ),
        migrations.CreateModel(
            name='Offer_Details',
            fields=[
                ('offer_del_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('offer_del_offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.offer')),
                ('offer_del_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product')),
            ],
            options={
                'db_table': 'Offer_Details',
            },
        ),
        migrations.CreateModel(
            name='Return',
            fields=[
                ('return_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('return_reason', models.TextField()),
                ('return_request_date', models.DateTimeField(auto_now_add=True)),
                ('return_status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Returned', 'Returned')], default='Pending', max_length=10)),
                ('return_payment_amount', models.FloatField()),
                ('return_payment_paid', models.BooleanField(default=False)),
                ('return_date', models.DateTimeField(blank=True, null=True)),
                ('return_address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer_address')),
                ('return_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
                ('return_orderdetails', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.orderdetails')),
                ('return_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product')),
            ],
            options={
                'db_table': 'Return',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('review_date', models.DateTimeField(auto_now_add=True)),
                ('review_review', models.CharField(blank=True, max_length=255, null=True)),
                ('review_rating', models.FloatField()),
                ('review_img', models.CharField(blank=True, max_length=550, null=True)),
                ('review_customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
                ('review_product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product')),
            ],
            options={
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('size_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('size_size', models.CharField(max_length=10)),
                ('size_cat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.category')),
            ],
            options={
                'db_table': 'Size',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_size',
            field=models.ManyToManyField(blank=True, to='ecommerce_app.size'),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('cart_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cart_price', models.FloatField()),
                ('cart_quantity', models.IntegerField()),
                ('cart_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
                ('cart_product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product')),
                ('cart_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.size')),
            ],
            options={
                'db_table': 'Cart',
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('wishlist_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('wishlist_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.customer')),
                ('wishlist_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce_app.product')),
            ],
            options={
                'db_table': 'Wishlist',
            },
        ),
    ]
