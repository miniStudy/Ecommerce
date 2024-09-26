from django.contrib import admin
from django.urls import include, path
from ecommerce_customer import views as customerviews


urlpatterns = [
    path('customer_create_account/', customerviews.customer_create_account_function, name='customer_create_account'),
    path('customer_login/', customerviews.customer_login_function, name='customer_login'),
    path('customer_logout/', customerviews.customer_logout_function, name='customer_logout'),
    path('deactivate_customer/', customerviews.deactivate_customer_function, name='deactivate_customer'),
    path('customer_update_password/', customerviews.customer_update_password_function, name='customer_update_password'),
    path('customer_update_account/', customerviews.customer_update_account_function, name='customer_update_account'),


    path('show_customer_address/', customerviews.show_customer_address_function, name='show_customer_address'),
    path('customer_address/', customerviews.customer_address_function, name='customer_address'),
    path('customer_update_address/', customerviews.customer_update_address_function, name='customer_update_address'),
    path('customer_delete_address/', customerviews.customer_delete_address_function, name='customer_delete_address'),

    path('customer_add_cart/', customerviews.customer_add_cart_function, name='customer_add_cart'),
    path('customer_view_cart/', customerviews.customer_view_cart_function, name='customer_view_cart'),
    path('customer_update_cart/', customerviews.customer_update_cart_function, name='customer_update_cart'),
    path('customer_delete_cart/', customerviews.customer_delete_cart_function, name='customer_delete_cart'),

    path('customer_add_wishlist/', customerviews.customer_add_wishlist_function, name='customer_add_wishlist'),
    path('customer_view_wishlist/', customerviews.customer_view_wishlist_function, name='customer_view_wishlist'),
    path('customer_delete_wishlist/', customerviews.customer_delete_wishlist_function, name='customer_delete_wishlist'),

    path('show_products/', customerviews.show_products_function, name='show_products'),
    path('show_product_details/', customerviews.show_product_details_function, name='show_product_details'),

    path('customer_checkout/', customerviews.customer_checkout_function, name='customer_checkout'),

    path('customer_add_order/', customerviews.customer_add_order_function, name='customer_add_order'),
    path('order_cancled/', customerviews.order_cancled_function, name='order_cancled'),

    path('customer_add_review', customerviews.customer_add_review_function, name='customer_add_review'),
    path('customer_delete_review', customerviews.customer_delete_review_function, name='customer_delete_review'),

    path('customer_return_order/', customerviews.customer_return_order_function, name='customer_return_order'),
    

]