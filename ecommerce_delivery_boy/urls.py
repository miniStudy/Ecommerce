from django.contrib import admin
from django.urls import include, path
from ecommerce_delivery_boy import views as deliveryviews

urlpatterns = [
    path('db_create_account/', deliveryviews.db_create_account_function, name= 'db_create_account'),
    path('db_login/', deliveryviews.db_login_function, name= 'db_login'),
    path('db_update_account/', deliveryviews.db_update_account_function, name= 'db_update_account'),
    path('db_update_password/', deliveryviews.db_update_password_function, name= 'db_update_password'),

    path('db_show_orders/', deliveryviews.db_show_orders_function, name= 'db_show_orders'),
    path('db_order_status/', deliveryviews.db_order_status_function, name= 'db_order_status'),
    path('db_return_order_accept/', deliveryviews.db_return_order_accept_function, name= 'db_return_order_accept'),
]
