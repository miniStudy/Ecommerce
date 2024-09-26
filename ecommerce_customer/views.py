from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from ecommerce_app.serializers import *
from .models import *
from django.db.models import Q, F, Sum, Max, Count, Avg, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.core.paginator import Paginator
from django.contrib import messages
from datetime import date

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from rest_framework.response import Response


# Create your views here.

def page_paginators(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'data': list(page_obj),
    }

@api_view(['POST'])
def customer_create_account_function(request):
    customer_data = request.data
    form = Customer_api(data = customer_data)
    if form.is_valid():
        form.save()
        return Response({
            'status':True,
            'message': "Account has been created successfully" 
        })
    else:
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        return Response({
            'status':False,
            'message': " ".join(error_messages)
        })

@api_view(['POST'])
def customer_login_function(request):
    if request.method == 'POST':
        customer_email = request.POST['customer_email']
        customer_password = request.POST['customer_password']
        check_true = Customer.objects.filter(customer_email=customer_email, customer_password=customer_password).exists()
        if check_true:
            customer_data = Customer.objects.get(customer_email=customer_email, customer_password=customer_password)
            request.session['customer_id'] = customer_data.customer_id
            request.session['customer_fname'] = customer_data.customer_fname
            request.session['customer_logged_in'] = 'yes'
            return Response({'status': True, 'message': 'Login Successfully!'})
        else:
            messages.error(request, "Invalid email or password!")
            return Response({'status': False, 'message': 'Invalid Email or Password'})
    return Response({'status': False, 'message': 'Please use POST method'})

@api_view(['GET','PUT'])
def customer_update_account_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(Customer, pk=request.GET['pk'])
            customer_data = request.data
            form = Customer_api(data = customer_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    "status":True,
                    "message":"Your account has been updated"
                })
            else:
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")

                return Response({
                    'status':False,
                    'message': " ".join(error_messages)
                })
    else:
        if request.GET.get('pk'):
            instance = get_object_or_404(Customer, pk=request.GET['pk'])
            serializer = Customer_api(instance)
            return Response({'Instance':serializer.data})
        return Response('Somewthing went Wrong')
    
@api_view(['DELETE'])
def customer_logout_function(request):
    if request.method == 'DELETE':
        customer_id = request.GET.get('customer_id')
        if customer_id:
            customer_data = Customer.objects.get(customer_id = customer_id)
            customer_data.delete()
            return Response({'status':True, 'message':'Logout Successfully.'})
        else:
            return Response({'status':False, 'message':'Id is required for logout.'})
    else:
        return Response({'status':False, 'message':'DELETE method required.'})


@api_view(['POST'])    
def customer_update_password_function(request):
    if request.method == 'POST':
        old_password = request.data.get('old_password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        customer_id = request.GET.get('customer_id')
        customer = Customer.objects.get(customer_id=customer_id)
        if customer.customer_password == old_password:
            if new_password1 == new_password2:
                customer.customer_password = new_password1
                customer.save()
                return Response({'status': True, 'message': 'Password has been updated successfully!'})
            else:
                return Response({'status': False, 'message': 'New passwords do not match, please try again!'})
        else:
            return Response({'status': False, 'message': 'Old password is incorrect, please try again!'})
    else:
        return Response({'status': False, 'message': 'POST method required!'})
    
@api_view(['GET'])
def show_customer_address_function(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return Response({'status':False, 'message':'customer_id is required'})
    customer_address_data = Customer_Address.objects.filter(address_customer_id__customer_id = customer_id).all().values('address_id', 'address_customer_id__customer_fname', 'address_customer_fname', 'address_line1', 'address_landmark', 'address_country', 'address_city', 'address_zipcode', 'address_phone')
    context = {
        'data':customer_address_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        customer_address_data = Customer_Address.objects.filter(
            Q(address_customer_fname__icontains=query) |
            Q(address_line1__icontains=query) |
            Q(address_landmark__icontains=query) |
            Q(address_country__icontains=query) |
            Q(address_city__icontains=query) |
            Q(address_state__icontains=query) |
            Q(address_zipcode__icontains=query) |
            Q(address_phone__icontains=query)).values('address_id', 'address_customer_id__customer_fname', 'address_customer_fname', 'address_line1', 'address_landmark', 'address_country', 'address_city', 'address_zipcode', 'address_phone') 
        context.update({'data':customer_address_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def customer_address_function(request):
    customer_address_data = request.data 
    form = Customer_insert_Address_api(data = customer_address_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Address has been added successfully'
        })
    else:
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")
                
        return Response({
            'status':False,
            'message': " ".join(error_messages)
        })
    
@api_view(['GET','POST'])
def customer_update_address_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Customer_Address, pk=request.GET['pk'])
            customer_address_data = request.data 
            form = Customer_Address_api(data = customer_address_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Address has been updated successfully'
                })
            else:
                error_messages = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                return Response({
                'status':False,
                'message': " ".join(error_messages)
                })
            
    if request.GET.get('pk'):
        instance = get_object_or_404(Customer_Address, pk=request.GET['pk'])
        serializer = Customer_Address_api(instance)
        return Response({'Instance':serializer.data})
    
    return Response({'Status':False, 'message':'Pass the pk(customer id)'})
    
@api_view(['DELETE'])
def customer_delete_address_function(request):
    if request.GET.get('pk'):
        try:
            customer_address = get_object_or_404(Customer_Address, pk=request.GET['pk'])
            customer_address.delete()
            return Response({
                "status": True,
                "message": "Customer Address has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })
    return Response({'status':False, 'message':'pk is required'})

    

@api_view(['POST'])
def customer_add_cart_function(request):
    if request.method == 'POST':
        cart_product_id = request.data.get('cart_product_id')
        cart_customer_id = request.data.get('cart_customer_id')
        size_id = request.data.get('size_id')
        price = request.data.get('price')
        quantity = request.data.get('quantity')

        if not (cart_product_id and cart_customer_id and size_id and price and quantity):
            return Response({'status': False, 'message': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)


        product = Product.objects.get(product_id=cart_product_id)
        customer = Customer.objects.get(customer_id=cart_customer_id)
        size = Size.objects.get(size_id=size_id)

        new_cart_item = Cart(
            cart_product_id=product,
            cart_customer=customer,
            cart_size=size,
            cart_price=price,
            cart_quantity=quantity
        )
        new_cart_item.save()
        return Response({'status': True, 'message': 'Item added to cart successfully.'})

@api_view(['GET']) 
def customer_view_cart_function(request):
    customer_id = request.GET.get('customer_id')
    # if not customer_id:
    #     return Response({'status': False, 'message': 'customer_id is required'}, status=400)
    if not customer_id:
        return Response({'status': False, 'message': 'customer_id is required'}, status=400)

    customer_cart_data = Cart.objects.filter(cart_customer__customer_id=customer_id).values('cart_id','cart_product_id__product_id','cart_customer__customer_id','cart_price','cart_quantity','cart_size__size_size','cart_size__size_id', 'cart_product_id__product_name', 'cart_product_id__product_img1', 'cart_product_id__product_brand__brand_name','cart_product_id__product_brand__brand_id',  'cart_product_id__product_mrp', 'cart_product_id__product_cat__category_name')

    context={'data': customer_cart_data, 'status':True}
    customer_cart_data = Cart.objects.filter(cart_customer__customer_id=customer_id).values('cart_id','cart_product_id__product_name','cart_customer__customer_id','cart_price','cart_quantity','cart_size')

    context={'data': customer_cart_data,'status':True}
    return Response(context)

@api_view(['GET','POST'])       
def customer_update_cart_function(request):
    if request.method == 'POST':
        cart_id = request.data.get('cart_id')
        cart_quantity = request.data.get('cart_quantity')
        cart_size = request.data.get('cart_size')
        if not cart_id:
            return Response({'status': False, 'message': 'cart_id is required'}, status=400)
        
        if cart_quantity is None or cart_size is None:
            return Response({'status': False, 'message': 'cart_quantity and cart_size are required'}, status=400)


        update_cart = Cart.objects.get(cart_id=cart_id)
        update_cart.cart_quantity = cart_quantity
        size = Size.objects.get(size_id=cart_size)
        update_cart.cart_size = size
        update_cart.save()
        return Response({'status': True, 'message': 'Cart has been updated successfully.'})
    return Response({'status':False, 'message':'Use Post Method'})
        
@api_view(['DELETE'])
def customer_delete_cart_function(request):
    if request.method == 'DELETE':
        cart_id = request.data.get('cart_id')
        try:
            cart_item = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            return Response({'status': False, 'message': 'Cart item not found.'})
        
        cart_item.delete()
        return Response({'status': True, 'message': 'Cart item deleted successfully.'})

@api_view(['GET'])
def customer_view_wishlist_function(request):
    customer_id = request.GET.get('customer_id')
    if not customer_id:
        return Response({'status':False, 'message':'customer_id is required'})
    
    customer_wishlist = Wishlist.objects.filter(wishlist_customer__customer_id = customer_id).values('wishlist_id','wishlist_product__product_name','wishlist_product__product_mrp','wishlist_product__product_selling_price','wishlist_product__product_img1','wishlist_product__product_brand','wishlist_product__product_cat')
    return Response({'Status':True, 'data':customer_wishlist})

@api_view(['POST'])   
def customer_add_wishlist_function(request):
    if request.method == 'POST':
        whishlist_customer_id = request.data.get('whishlist_customer_id')
        wishlist_product_id = request.data.get('wishlist_product_id')

        if not whishlist_customer_id:
            return Response({'status': False, 'message': 'whishlist_customer_id is required'})

        if not wishlist_product_id:
            return Response({'status': False, 'message': 'wishlist_product_id is required'})

        customer = Customer.objects.get(customer_id = whishlist_customer_id)
        product = Product.objects.get(product_id = wishlist_product_id)

        new_wishlist_items = Wishlist(wishlist_customer=customer, wishlist_product=product)
        new_wishlist_items.save()

        return Response({'status':True, 'message': 'Item added to wishlist successfully.'})
    
@api_view(['DELETE'])
def customer_delete_wishlist_function(request):
    if request.method == 'DELETE':
        wishlist_id = request.GET.get('wishlist_id')
        if not wishlist_id:
            return Response({'status':False, 'message':'wishlist_id is required'})
        
        try:
            wishlist = Wishlist.objects.get(wishlist_id=wishlist_id)
        except Wishlist.DoesNotExist:
            return Response({'status': False, 'message': 'Cart item not found.'})
        
        wishlist.delete()
        return Response({'status':True, 'message':'wishlist deleted successfully'})


    

@api_view(['GET'])
def show_products_function(request):
    product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava', 'product_reviews').all().annotate(
        average_rating=Avg('product_reviews__review_rating'),
        average_rating_count=Count('product_reviews__review_rating'))
    serializer = Product_show_api(product_data, many = True)
    context = {
        'data':serializer.data,
        'status': True
    }

    if request.GET.get('get_color'):
        get_color = request.GET.get('get_color')
        product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava').filter(product_color__color_id = get_color)
        serializer = Product_show_api(product_data, many = True)
        context.update({'data':serializer.data, 'status': True})

    if request.GET.get('get_cat'):
        get_cat = request.GET.get('get_cat')
        product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava').filter(product_cat__category_id = get_cat)
        serializer = Product_show_api(product_data, many = True)
        context.update({'data':serializer.data, 'status': True})

    
    if request.GET.get('get_brand'):
        get_brand = request.GET.get('get_brand')
        product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava').filter(product_brand__brand_id = get_brand)
        serializer = Product_show_api(product_data, many = True)
        context.update({'data':serializer.data, 'status': True})

    
    if request.GET.get('get_size'):
        get_size = request.GET.get('get_size')
        product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava').filter(product_size__size_id = get_size)
        serializer = Product_show_api(product_data, many = True)
        context.update({'data':serializer.data, 'status': True})
    
    products_filter_az = Product.objects.all().order_by('product_name')
    products_filter_za = Product.objects.all().order_by('-product_name')

    if request.GET.get('min_price') and request.GET.get('max_price'):
        min_price = request.GET.get('min_amount')
        max_price = request.GET.get('max_amount')

        product_data = Product.objects.filter(product_selling_price__gte=min_price, product_selling_price__lte=max_price).order_by('-product_selling_price')
        serializer = Product_show_api(product_data, many = True)
        context.update({'data':serializer.data, 'status': True})

    query = request.GET.get('searchhere', '')
    if query:
        product_data = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_mrp__icontains=query) |
            Q(product_selling_price__icontains=query) |
            Q(product_desc__icontains=query) |
            Q(product_stock__icontains=query) |
            Q(product_color__color_name__icontains=query) |  # Assuming product_color has a related field color_name
            Q(product_status__icontains=query) |
            Q(product_size__size_size__icontains=query) |  # Assuming product_size has a related field size_size
            Q(product_brand__brand_name__icontains=query)  # Assuming product_brand has a related field brand_name
        )
        
        filtered_serializer = Product_show_api(product_data, many=True)
        context.update({'data': filtered_serializer.data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['GET'])
def show_product_details_function(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return Response({'status': False, 'message': 'Pass the product_id'}, status=400)

    product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava').get(product_id=product_id)
    serializer = Product_show_api(product_data)
    context = {
        'data':serializer.data,
        'status': True
    }
    return Response({'status': True, 'data': context})


@api_view(['GET'])
def customer_checkout_function(request):
    customer_id = request.GET.get('customer_id')
    
    cart_items = Cart.objects.filter(cart_customer__customer_id=customer_id)

    subtotal_amount = 0
    for item in cart_items:
        offer_details = Offer_Details.objects.filter(offer_del_product=item.cart_product_id, offer_del_offer__offer_starting_date__lte=date.today(), offer_del_offer__offer_ending_date__gte=date.today()).first()
        
        if offer_details:
            discount = offer_details.offer_del_offer.offer_discount
            discounted_price = item.cart_price * (1 - discount / 100)
            item_total = discounted_price * item.cart_quantity
        else:
            item_total = item.cart_price * item.cart_quantity
        
        subtotal_amount += item_total
    
    delivery_amount = 70

    tax_amount = subtotal_amount*18/100

    final_amount = subtotal_amount + delivery_amount + tax_amount

    context = {'subtotal_amount': subtotal_amount, 'delivery_amount': delivery_amount, 'tax_amount':tax_amount, 'final_amount': final_amount}
    return Response({
        'status': True,
        'data':context    
    })

def order_cancled_function(request):
    order_id = request.data.get('order_id')
    order = Order.objects.get(order_id=order_id)

    if order.order_status in [Order.OrderStatus.PENDING, Order.OrderStatus.ACCEPTED, Order.OrderStatus.OutForDelivery]:
        order.order_status = Order.OrderStatus.CANCELLED
        order.save()
        return Response({'status': True, 'message': 'Order has been cancelled successfully.'})
    elif order.order_status == Order.OrderStatus.DELIVERED:
        return Response({'status': False, 'message': 'Order has already been delivered and cannot be cancelled.'})
    else:
        return Response({'status': False, 'message': 'Order cannot be cancelled.'})

@api_view(['POST']) 
def customer_add_order_function(request):
    customer_id = request.data.get('customer_id')
    order_code = request.data.get('order_code')
    order_address_id = request.data.get('order_address_id')
    order_payment_mode = request.data.get('order_payment_mode')
    order_amount = request.data.get('order_amount')
    order_tax_amount = request.data.get('order_tax_amount', 0)
    order_delivery_charge = request.data.get('order_delivery_charge', 0)
    order_note = request.data.get('order_note', '')

    product_id = request.data.get('product_id')
    price = request.data.get('orderDet_price')
    quantity = request.data.get('orderDet_quantity')
    size_id = request.data.get('orderDet_size_id')
    color_id = request.data.get('color_id')



    product = Product.objects.get(product_id=product_id)
    color = Color.objects.get(color_id=color_id)

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        print(customer)
    except Customer.DoesNotExist:
        return Response({'status': False, 'message': 'Customer does not exist.'})
    try:
        address = Customer_Address.objects.get(address_id=order_address_id)
    except Customer_Address.DoesNotExist:
        return Response({'status': False, 'message': 'Address does not exist.'})

    new_order = Order(
        order_code=order_code,
        order_address_id=address,
        order_payment_mode=order_payment_mode,
        order_amount=order_amount,
        order_tax_amount=order_tax_amount,
        order_delivery_charge=order_delivery_charge,
        order_note=order_note,
        order_customer=customer
    )

    new_order.save()
    order_details = OrderDetails.objects.create(
            orderDet_product=product,
            orderDet_price=price,
            orderDet_quantity=quantity,
            orderDet_size_id=size_id,
            orderDet_customer=customer,
            orderDet_order=new_order,
            orderDet_color=color
        )
    order_details.save()
    
    return Response({'status': True, 'message': 'Order added successfully!', 'order_id': new_order.order_id})

@api_view(['POST'])
def customer_add_review_function(request):
    if request.method == 'POST':
        review_date = request.data.get('review_date')
        review_customer = request.data.get('review_customer')
        review_product = request.data.get('review_product')
        review_review = request.data.get('review_review')
        review_rating = request.data.get('review_rating')
        review_img = request.data.get('review_img')

        try:
            customer = Customer.objects.get(customer_id = review_customer)
        except Customer.DoesNotExist:
            return Response({'status': False, 'message': 'Customer does not exist.'})
        try:
            product = Product.objects.get(product_id = review_product)
        except Product.DoesNotExist:
            return Response({'status': False, 'message': 'Product does not exist.'})

        new_review = Review(
            review_date = review_date,
            review_customer = customer,
            review_product = product,
            review_review = review_review,
            review_rating = review_rating,
            review_img = review_img
        )
        new_review.save()
        return Response({'status': True, 'message': 'Your review for the product has been saved. Thank you!'})
    else:
        return Response({'status': False, 'message': 'POST request required!'})

@api_view(['DELETE'])
def customer_delete_review_function(request):
    if request.method == 'DELETE':
        review_id = request.GET.get('review_id')
        customer_id = request.GET.get('customer_id')

        if review_id:
            review_data = Review.objects.get(review_id=review_id, review_customer__customer_id = customer_id)
            review_data.delete()
            return Response({'status': True, 'message': 'Your review has been deleted successfully!'})
        else:
            return Response({'status': False, 'message': 'Review id required'})
    else:
        return Response({'status': False, 'message': 'POST request required!'})


@api_view(['GET'])
def deactivate_customer_function(request):
    if request.GET.get('customer_id'):
        customer_id = request.GET.get('customer_id')
        customer = get_object_or_404(Customer, customer_id=customer_id)
        customer.customer_active = False
        customer.save()
        return Response({'status':True, 'message':f'Customer {customer.customer_fname} has been deactivated.'})
    else:
        return Response({'status':False, 'message':'GET method required'})
    
@api_view(['POST'])
def customer_return_order_function(request):
    try:
        # Extract data from the request
        customer_id = request.data.get('customer_id')
        orderdetails_id = request.data.get('orderdetails_id')
        product_id = request.data.get('product_id')
        return_reason = request.data.get('return_reason')
        return_payment_amount = request.data.get('return_payment_amount')
        address_id = request.data.get('address_id')

        # Fetch the necessary objects from the database
        customer = Customer.objects.get(pk=customer_id)
        orderdetails = OrderDetails.objects.get(pk=orderdetails_id)
        product = Product.objects.get(pk=product_id)
        address = Customer_Address.objects.get(pk=address_id)

        # Create a new return entry
        return_entry = Return.objects.create(
            return_customer=customer,
            return_orderdetails=orderdetails,
            return_product=product,
            return_reason=return_reason,
            return_payment_amount=return_payment_amount,
            return_address=address
        )
        return_entry.save()

        return Response({"status":True, "message": "Return request successfully created"})

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
    except OrderDetails.DoesNotExist:
        return Response({"error": "Order details not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except Customer_Address.DoesNotExist:
        return Response({"error": "Customer address not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET']) 
def customer_show_order_function(request):
    customer_id = request.GET.get('customer_id')
    order_data = Order.objects.filter(order_customer_customer_id = customer_id).values('order_id', 'order_code', 'order_address_id', 'order_address_idaddress_line1', 'order_address_idaddress_landmark', 'order_address_idaddress_country', 'order_address_idaddress_city', 'order_address_idaddress_state', 'order_address_idaddress_country', 'order_address_idaddress_zipcode', 'order_address_idaddress_phone', 'order_payment_mode', 'order_status', 'order_delivered_date', 'order_payment_mode', 'order_tax_amount', 'order_delivery_charge', 'order_paid', 'order_amount', 'order_date', 'order_customer_customer_id')

    order_details_data = OrderDetails.objects.filter(orderDet_customer_customer_id = customer_id).values('orderDet_id', 'orderDet_productproduct_name', 'orderDet_productproduct_mrp', 'orderDet_productproduct_selling_price', 'orderDet_productproduct_desc', 'orderDet_productproduct_stock', 'orderDet_productproduct_colorcolor_color', 'orderDet_productproduct_status', 'orderDet_productproduct_img1', 'orderDet_productproduct_avaproduct_ava_area', 'orderDet_productproduct_brand_brand_name', 'orderDet_price', 'orderDet_quantity')
    context = {
        'data':order_data,
        'data2': order_details_data,
        'status': True
    }
    return Response(context)    
    
