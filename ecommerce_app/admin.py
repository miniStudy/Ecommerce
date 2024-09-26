from django.contrib import admin
from ecommerce_app.models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Customer_Address)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Brand)
admin.site.register(Product_Availability)
admin.site.register(Cart)
admin.site.register(Offer)
admin.site.register(Offer_Details)
admin.site.register(Order)
admin.site.register(OrderDetails)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(delivery_boy)
admin.site.register(assign_orders)