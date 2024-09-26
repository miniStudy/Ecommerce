from rest_framework import serializers
from ecommerce_app.models import *

class Admin_api(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ('__all__')

class Customer_api(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('__all__')

class Customer_Address_api(serializers.ModelSerializer):
    address_customer_id = Customer_api(many=False)

    class Meta:
        model = Customer_Address
        fields = ('__all__')

class Customer_insert_Address_api(serializers.ModelSerializer):
    address_customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), many=False)

    class Meta:
        model = Customer_Address
        fields = ('__all__')


class Category_api(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')

class Size_api(serializers.ModelSerializer):
    # size_cat = Category_api(many = False)
    size_cat = Category_api(read_only=True)
    class Meta:
        model = Size
        fields = ('__all__')

class Size_insert_api(serializers.ModelSerializer):
    size_cat = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=False)
    class Meta:
        model = Size
        fields = ('__all__')        

class Color_api(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('__all__')

class Brand_api(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('__all__')

class Product_Availability_api(serializers.ModelSerializer):
    class Meta:
        model = Product_Availability
        fields = ('__all__')


class Review_for_product_api(serializers.ModelSerializer):
    review_customer = Customer_api(many = False)
    class Meta:
        model = Review
        fields = ('__all__')

class Product_show_api(serializers.ModelSerializer):
    product_color = Color_api(many=True)  # Use nested serializer for colors
    product_size = Size_api(many=True)  # Use nested serializer for sizes
    product_brand = Brand_api(many=False)  # Use nested serializer for brand
    product_cat = Category_api(many=False)  # Use nested serializer for category
    product_ava = Product_Availability_api(many=True)  # Use nested serializer for availability
    product_reviews = Review_for_product_api(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    average_rating_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('__all__')

    def get_average_rating(self, obj):
        return obj.average_rating if obj.average_rating is not None else 0    

    def get_average_rating_count(self, obj):
        # Fetch the annotated 'average_rating_count' value from the queryset
        return obj.average_rating_count if obj.average_rating_count is not None else 0    


class Product_insert_api(serializers.ModelSerializer):
    product_color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), many=True)
    product_size = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), many=True)
    product_brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), many=False)
    product_cat = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=False)
    product_ava = serializers.PrimaryKeyRelatedField(queryset=Product_Availability.objects.all(), many=True)
    product_img1 = serializers.ImageField(required=False)  # Add the image field

    class Meta:
        model = Product
        fields = ('__all__')    
     

class Review_api(serializers.ModelSerializer):
    review_customer = Customer_api(many = False)
    review_product = Product_show_api(many = False)
    class Meta:
        model = Review
        fields = ('__all__')

class Cart_api(serializers.ModelSerializer):
    cart_product_id = Product_show_api(many = False)
    cart_customer = Customer_api(many = False)
    cart_size = Size_api(many = False)
    class Meta:
        model = Cart
        fields = ('__all__')



class Offer_api(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('__all__')

class Offer_Details_insert_api(serializers.ModelSerializer):
    offer_del_offer = serializers.PrimaryKeyRelatedField(queryset=Offer.objects.all(), many=False)
    offer_del_product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=False)
    class Meta:
        model = Offer_Details
        fields = ('__all__')


class Offer_Details_api(serializers.ModelSerializer):
    offer_del_offer = Offer_api(many = False)
    offer_del_product = Product_show_api(many = False)
    class Meta:
        model = Offer_Details
        fields = ('__all__')

class Order_api(serializers.ModelSerializer):
    order_address_id = Customer_Address_api(many = False)
    order_customer = Customer_api(many = False)
    class Meta:
        model = Order
        fields = ('__all__')

class OrderDetails_api(serializers.ModelSerializer):
    orderDet_product = Product_show_api(many = False)
    orderDet_customer = Customer_api(many = False)
    orderDet_address = Customer_Address_api(many = False)
    orderDet_order = Order_api(many = False)
    orderDet_color = Color_api(many = False)
    class Meta:
        model = OrderDetails
        fields = ('__all__')

class Wishlist_api(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('__all__')

class delivery_boy_api(serializers.ModelSerializer):
    class Meta:
        model = delivery_boy
        fields = ('__all__')

class assign_orders_api(serializers.ModelSerializer):
    assign_db_id = delivery_boy_api(many = False)
    assign_orderDet_id = Order_api(many = False)
    class Meta:
        model = assign_orders
        fields = ('__all__')
