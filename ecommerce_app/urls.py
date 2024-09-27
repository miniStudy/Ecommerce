from django.contrib import admin
from django.urls import include, path
from ecommerce_app import views


urlpatterns = [
    #============================= Customer =======================================================================
    path('admin_create_account/', views.admin_create_account_function, name='admin_create_account'),
    path('admin_update_account/', views.admin_update_account_function, name='admin_update_account'),
    path('admin_delete_account/', views.admin_delete_account_function, name='admin_delete_account'),

    #============================= Customer =======================================================================
    path('show_customer/', views.show_customer_function, name='show_customer'),
    path('insert_customer/', views.insert_customer_function, name='insert_customer'),
    path('update_customer/', views.update_customer_function, name='update_customer'),
    path('delete_customer/', views.delete_customer_function, name='delete_customer'),

    #============================= Address =========================================================================
    path('show_customer_address/', views.show_customer_address_function, name='show_customer_address'),
    path('insert_customer_address/', views.insert_customer_address_function, name='insert_customer_address'),
    path('update_customer_address/', views.update_customer_address_function, name='update_customer_address'),
    path('delete_customer_address/', views.delete_customer_address_function, name='delete_customer_address'),

    #============================= Category =========================================================================
    path('show_category/', views.show_category_function, name='show_category'),
    path('insert_category/', views.insert_category_function, name='insert_category'),
    path('update_category/', views.update_category_function, name='update_category'),
    path('delete_category/', views.delete_category_function, name='delete_category'),
    
    #============================= Size ==============================================================================
    path('show_size/', views.show_size_function, name='show_size'),
    path('insert_size/', views.insert_size_function, name='insert_size'),
    path('updated_size/', views.updated_size_function, name='updated_size'),
    path('delete_size/', views.delete_size_function, name='delete_size'),

    #============================= Color =============================================================================
    path('show_color/', views.show_color_function, name='show_color'),
    path('insert_color/', views.insert_color_function, name='insert_color'),
    path('update_color/', views.update_color_function, name='update_color'),
    path('delete_color/', views.delete_color_function, name='delete_color'),

    #============================= Brand =============================================================================
    path('show_brand/', views.show_brand_function, name='show_brand'),
    path('insert_brand/', views.insert_brand_function, name='insert_brand'),
    path('update_brand/', views.update_brand_function, name='update_brand'),
    path('delete_brand/', views.delete_brand_function, name='delete_brand'),

    #============================= Product Ava ========================================================================
    path('show_product_availability/', views.show_product_availability_function, name='show_product_availability'),
    path('insert_product_availability/', views.insert_product_availability_function, name='insert_product_availability'),
    path('update_product_availability/', views.update_product_availability_function, name='update_product_availability'),
    path('delete_product_availability/', views.delete_product_availability_function, name='delete_product_availability'),

    #============================= Product ============================================================================
    path('show_product/', views.show_product_function, name='show_product'),
    path('insert_product/', views.insert_product_function, name='insert_product'),
    path('update_product/', views.update_product_function, name='update_product'),
    path('delete_product/', views.delete_product_function, name='delete_product'),
    path('show_product_details/', views.show_product_details_function, name='show_product_details'),

    #============================= Review =============================================================================
    path('show_review/', views.show_review_function, name='show_review'),
    path('insert_review/', views.insert_review_function, name='insert_review'),
    path('update_review/', views.update_review_function, name='update_review'),
    path('delete_review/', views.delete_review_function, name='delete_review'),

    #============================= Cart ===============================================================================
    path('show_cart/', views.show_cart_function, name='show_cart'),
    path('insert_cart/', views.insert_cart_function, name='insert_cart'),
    path('update_cart/', views.update_cart_function, name='update_cart'),
    path('delete_cart/', views.delete_cart_function, name='delete_cart'),

    #============================= Offer ==============================================================================
    path('show_offer/', views.show_offer_function, name='show_offer'),
    path('insert_offer/', views.insert_offer_function, name='insert_offer'),
    path('update_offer/', views.update_offer_function, name='update_offer'),
    path('delete_offer/', views.delete_offer_function, name='delete_offer'),

    #============================= Offer Details =======================================================================
    path('show_offer_details/', views.show_offer_details_function, name='show_offer_details'),
    path('insert_offer_details/', views.insert_offer_details_function, name='insert_offer_details'),
    path('update_offer_details/', views.update_offer_details_function, name='update_offer_details'),
    path('delete_offer_details/', views.delete_offer_details_function, name='delete_offer_details'),

    #============================= Order ==============================================================================
    path('show_order/', views.show_order_function, name='show_order'),
    path('insert_order/', views.insert_order_function, name='insert_order'),
    path('update_order/', views.update_order_function, name='update_order'),
    path('delete_order/', views.delete_order_function, name='delete_order'),
    path('change_order_status/', views.change_order_status_function, name='change_order_status'),

    #============================= Order Details ======================================================================
    path('show_order_details/', views.show_order_details_function, name='show_order_details'),
    path('insert_order_details/', views.insert_order_details_function, name='insert_order_details'),
    path('update_order_details/', views.update_order_details_function, name='update_order_details'),
    path('delete_order_details/', views.delete_order_details_function, name='delete_order_details'),
    path('order_analysis/', views.order_analysis, name='order_analysis'),
    
    path('order_assign/', views.order_assign_function, name='order_assign'),



    path('customer_return_order_accept', views.customer_return_order_accept_function, name='customer_return_order_accept'),

    #============================= Stock ===========================================================
    path('show_stock_details/', views.show_stock_details_function, name='show_stock_details'),
    path('insert_stock_details/', views.insert_stock_details_function, name='insert_stock_details'),
    path('delete_stock_details/', views.delete_stock_details_function, name='delete_stock_details'),

    #============================= Stock Management ===============================================
    path('show_stock_management_details/', views.show_stock_management_details_function, name='show_stock_management_details'),
]