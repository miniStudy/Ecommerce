from datetime import timezone
from django.db import models
from datetime import date

# Create your models here.

from django.db import models

# Create your models here.
class Admin(models.Model):
    admin_id = models.BigAutoField(primary_key=True)
    admin_fname = models.CharField(max_length=55)
    admin_lname = models.CharField(max_length=55)
    admin_email = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=155)
    admin_date_joined = models.DateTimeField(auto_now_add=True)
    admin_phone = models.CharField(max_length=15, blank=True, null=True)
    admin_role = models.CharField(max_length=20, default='admin')
    admin_profile_image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    admin_otp = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return f"{self.admin_email} - {self.admin_fname} {self.admin_lname}"
    
    class Meta:
        db_table = 'Admin'

class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    customer_fname = models.CharField(max_length=55)
    customer_lname = models.CharField(max_length=55)
    customer_email = models.EmailField(unique=True)
    customer_phone = models.CharField(max_length=15, null=True, blank=True)
    customer_password = models.CharField(max_length=155)
    customer_date_joined = models.DateTimeField(auto_now_add=True)
    customer_active = models.BooleanField(default=True)
    customer_otp = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return f"{self.customer_email} {self.customer_fname} {self.customer_lname}"
    
    class Meta:
        db_table = 'Customer'


class Customer_Address(models.Model):
    address_id = models.BigAutoField(primary_key=True)
    address_customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address_customer_fname = models.CharField(max_length=255)
    address_line1 = models.TextField()
    address_line2 = models.TextField(blank=True, null=True)
    address_landmark = models.CharField(max_length=255, blank=True, null=True)
    address_country = models.CharField(max_length=155)
    address_city = models.CharField(max_length=155)
    address_state = models.CharField(max_length=155)
    address_zipcode = models.IntegerField() 
    address_phone = models.CharField(max_length=12)
    address_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.address_customer_id.customer_fname} {self.address_customer_id.customer_lname} - {self.address_city}, {self.address_state}"
    
    class Meta:
        db_table = 'Customer_Address'

class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=155)

    def __str__(self):
        return f"{self.category_name}"
    
    class Meta:
        db_table = 'Category'

class Size(models.Model):
    size_id = models.BigAutoField(primary_key=True)
    size_size = models.CharField(max_length=10)
    size_cat = models.ForeignKey(Category, on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f"{self.size_id} - {self.size_size}"
    
    class Meta:
        db_table = 'Size'

class Color(models.Model):
    color_id = models.BigAutoField(primary_key=True)
    color_color = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.color_id} - {self.color_color}"
    
    class Meta:
        db_table = 'Color'

class Brand(models.Model):
    brand_id = models.BigAutoField(primary_key=True)
    brand_name = models.CharField(max_length=155, null=True, blank=True)

    def __str__(self):
        return f"{self.brand_id} - {self.brand_name}"
    
    class Meta:
        db_table = 'Brand'
        

class Product_Availability(models.Model):
    product_ava_id = models.BigAutoField(primary_key=True)
    product_ava_area = models.CharField(max_length=155)
    product_ava_pincode = models.CharField(max_length=155)

    def __str__(self):
        return f"{self.product_ava_id} - {self.product_ava_area} - {self.product_ava_pincode}"
    
    class Meta:
        db_table = 'Product_Availability'


class Stock(models.Model):
    stock_id = models.BigAutoField(primary_key=True)
    stock_supplier = models.CharField(max_length=900)
    stock_sku = models.CharField(max_length=150)
    stock_total_order_value = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_supplier}"
    
    class Meta:
        db_table = 'Stock'

class Stock_product(models.Model):
    sp_id = models.BigAutoField(primary_key=True)
    sp_product_name = models.CharField(max_length=300)
    sp_product_code = models.CharField(max_length=10)
    sp_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sp_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    sp_sub_category = models.CharField(max_length=100, null=True, blank=True)
    sp_stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_product_data')
    
    def __str__(self):
        return f"{self.sp_product_name} - {self.sp_product_code}"

    class Meta:
        db_table = 'Stock_product'

class stock_details(models.Model):
    sd_id = models.BigAutoField(primary_key=True)
    sd_price = models.DecimalField(max_digits=20, decimal_places=2)
    sd_quantity = models.IntegerField()
    sd_size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    sd_color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    sd_product = models.ForeignKey(Stock_product, on_delete=models.CASCADE, related_name='stock_details_data')
    
    def __str__(self):
        return f"{self.sd_product.sp_product_name} - {self.sd_price} - {self.sd_quantity}"

    class Meta:
        db_table = 'stock_details'
    

class Stock_management(models.Model):
    sm_id = models.BigAutoField(primary_key=True)
    sm_product_name = models.CharField(max_length=300)
    sm_product_code = models.CharField(max_length=10)
    sm_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    sm_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    sm_sub_category = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.sm_product_name} - {self.sm_product_code}"

    class Meta:
        db_table = 'Stock_management'


class stock_manage_details(models.Model):
    smd_id = models.BigAutoField(primary_key=True)
    smd_price = models.DecimalField(max_digits=20, decimal_places=2)
    smd_quantity = models.IntegerField()
    smd_size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    smd_color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    smd_product = models.ForeignKey(Stock_management, on_delete=models.CASCADE, related_name='stock_management_data')

    def __str__(self):
        return f"{self.smd_product.sm_product_name} - {self.smd_price} - {self.smd_quantity}"

    class Meta:
        db_table = 'stock_manage_details'


class Product(models.Model):
    class Product_Choices(models.TextChoices):
        InStock = 'InStock', 'InStock'
        OutOfStock = 'OutOfStock', 'OutOfStock'
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=155)
    product_mrp = models.FloatField()
    product_cost = models.FloatField()
    product_selling_price = models.FloatField()
    product_desc = models.TextField(null=True,blank=True)
    product_stock = models.IntegerField()
    product_color = models.ManyToManyField(Color, max_length=55)
    product_status = models.CharField(
        max_length=55,
        choices=Product_Choices.choices,
        default=Product_Choices.InStock,
    )
    product_img1 = models.ImageField(upload_to='uploads/')
    product_img2 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img3 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img4 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img5 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img6 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img7 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_img8 = models.ImageField(upload_to='uploads/', null=True, blank=True)
    product_size = models.ManyToManyField(Size, blank=True)
    product_ava = models.ManyToManyField(Product_Availability, blank=True)
    product_brand = models.ForeignKey(Brand, on_delete=models.CASCADE,null=True,blank=True)
    product_cat = models.ForeignKey(Category, on_delete=models.CASCADE,null=True,blank=True)
    product_returnable = models.BooleanField(default=True, null=True, blank=True)
    product_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} - {self.product_selling_price}"
    
    class Meta:
        db_table = 'Product'


class Review(models.Model):
    review_id = models.BigAutoField(primary_key= True)
    review_date = models.DateTimeField(auto_now_add=True)
    review_customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    review_product = models.ForeignKey(Product, related_name='product_reviews', on_delete=models.CASCADE, null=True, blank=True)
    review_review = models.CharField(max_length=255, null=True, blank=True)
    review_rating = models.FloatField()
    review_img = models.CharField(null=True, blank=True, max_length=550)

    def __str__(self):
        return f"{self.review_product.product_name} - {self.review_rating}"
    
    class Meta:
        db_table = 'Review'
    

class Cart(models.Model):
    cart_id = models.BigAutoField(primary_key=True)
    cart_product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    cart_price = models.FloatField()
    cart_quantity = models.IntegerField()
    cart_size = models.ForeignKey(Size, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cart_product_id.product_name} - {self.cart_price}"
    
    class Meta:
        db_table = 'Cart' 


class Offer(models.Model):
    offer_id = models.BigAutoField(primary_key=True)
    offer_name = models.CharField(max_length=155)
    offer_discount = models.IntegerField()
    offer_starting_date = models.DateField()
    offer_ending_date = models.DateField()
    offer_expired = models.BooleanField(default=False)
    offer_image = models.ImageField(upload_to='uploads/', null=True,blank=True)

    def save(self, *args, **kwargs):
        # Automatically mark offer as expired if the ending date is in the past
        if self.offer_ending_date < date.today():
            self.offer_expired = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.offer_name} - {self.offer_discount}"
    
    class Meta:
        db_table = 'Offer' 

class Offer_Details(models.Model):
    offer_del_id = models.BigAutoField(primary_key=True)
    offer_del_offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='offerdata')
    offer_del_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offer_product_data')

    def __str__(self):
        return f"{self.offer_del_offer.offer_name} - {self.offer_del_product.product_name}"

    class Meta:
        db_table = 'Offer_Details' 


class Order(models.Model):
    class OrderPayment(models.TextChoices):
        UPI = 'UPI', 'UPI'  
        COD = 'COD', 'COD'
        CC = 'CC', 'CC'
        DC = 'DC', 'DC'

    order_id = models.BigAutoField(primary_key=True)
    order_code = models.CharField(max_length=55)
    order_address_id = models.ForeignKey(Customer_Address, on_delete=models.CASCADE)
    order_payment_mode = models.CharField(max_length=155)
    order_amount = models.FloatField()
    order_tax_amount = models.FloatField()
    order_delivery_charge = models.FloatField(blank=True, null=True)
    order_paid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    order_delivered_date = models.DateField(null=True, blank=True)
    order_note = models.CharField(max_length=550, null=True, blank=True)
    order_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.order_customer.customer_fname} - {self.order_address_id.address_city}"
    
    class Meta:
        db_table = 'Order' 


class OrderDetails(models.Model):
    class OrderDetStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACCEPTED = 'Accepted', 'Accepted'
        REJECTED = 'Rejected', 'Rejected'
        OutForDelivery = 'OutForDelivery', 'OutForDelivery'
        DELIVERED = 'Delivered', 'Delivered'
        RETURNED = 'Returned', 'Returned'
        CANCELLED = 'Cancelled', 'Cancelled'
    orderDet_id = models.BigAutoField(primary_key=True)
    orderDet_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    orderDet_price = models.FloatField()
    orderDet_quantity = models.IntegerField()
    orderDet_size_id = models.ForeignKey(Size, on_delete=models.CASCADE)
    orderDet_status = models.CharField(max_length=15,choices=OrderDetStatus.choices,default=OrderDetStatus.PENDING)
    orderDet_customer = models.ForeignKey(Customer, on_delete=models.CASCADE,blank=True,null=True)
    orderDet_order = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True,null=True, related_name='order_details')
    orderDet_color = models.ForeignKey(Color, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.orderDet_id} {self.orderDet_product.product_name} - {self.orderDet_price} - {self.orderDet_status}"
    
    class Meta:
        db_table = 'OrderDetails'

class Wishlist(models.Model):
    wishlist_id = models.BigAutoField(primary_key=True)
    wishlist_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    wishlist_product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.wishlist_customer.customer_fname} - {self.wishlist_product.product_name}"
    
    class Meta:
        db_table = 'Wishlist'

class delivery_boy(models.Model):
    db_id = models.BigAutoField(primary_key=True)
    db_name = models.CharField(max_length=55)
    db_email = models.EmailField(unique=True)
    db_password = models.CharField(max_length=55)
    db_phone = models.CharField(max_length=15, blank=True, null=True)
    db_address = models.TextField()
    db_otp = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.db_email} {self.db_name}"
    
    class Meta:
        db_table = 'delivery_boy'

class assign_orders(models.Model):
    class OrderWork(models.TextChoices):
        For_Delivery = 'For_Delivery', 'For_Delivery'
        For_Returning = 'For_Returning', 'For_Returning'

    assign_id = models.BigAutoField(primary_key=True)
    assign_db_id = models.ForeignKey(delivery_boy, on_delete=models.CASCADE)
    assign_orderDet_id = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    assign_order_todo = models.CharField(max_length=15,choices=OrderWork.choices,default=OrderWork.For_Delivery)
    assign_date = models.DateField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return f"{self.assign_db_id.db_name} - {self.assign_orderDet_id.orderDet_order.order_code} - {self.assign_orderDet_id.orderDet_order.order_customer}"
    
    class Meta:
        db_table = 'assign_orders' 


class Return(models.Model):
    class ReturnStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACCEPTED = 'Accepted', 'Accepted'
        REJECTED = 'Rejected', 'Rejected'
        RETURNED = 'Returned', 'Returned'
        
    return_id = models.BigAutoField(primary_key=True)
    return_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    return_orderdetails = models.ForeignKey(OrderDetails, on_delete=models.CASCADE)
    return_reason = models.TextField() 
    return_request_date = models.DateTimeField(auto_now_add=True)
    return_status = models.CharField(max_length=10,choices=ReturnStatus.choices,default=ReturnStatus.PENDING)
    return_payment_amount = models.FloatField()
    return_payment_paid = models.BooleanField(default=False)
    return_address = models.ForeignKey(Customer_Address, on_delete=models.CASCADE)
    return_date = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return f"Return Request for {self.return_product.product_name} by {self.return_customer.customer_fname} - {self.return_customer.customer_lname}"

    class Meta:
        db_table = 'Return'