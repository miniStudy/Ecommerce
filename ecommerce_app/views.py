from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from ecommerce_app.serializers import *
from .models import *
from .forms import *
from django.db.models import Q, F, Sum, Max, Count, Avg, OuterRef, Exists
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.core.paginator import Paginator
from django.contrib import messages

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from rest_framework.response import Response


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


@api_view(['GET'])
def order_analysis(request):
    total_sales_amount = Order.objects.aggregate(total_sales=Sum('order_amount'))
    total_tax_amount = Order.objects.aggregate(total_tax=Sum('order_tax_amount'))
    total_delivery_charge = Order.objects.aggregate(total_delivery=Sum('order_delivery_charge'))

    total_tax_plus_delivery = total_tax_amount['total_tax'] + total_delivery_charge['total_delivery']

    total_cost_amount = OrderDetails.objects.aggregate(total_cost=Sum(F('orderDet_product__product_cost') * F('orderDet_quantity')))

    total_profit_amount = total_sales_amount['total_sales'] - total_cost_amount['total_cost']

    net_profit_amount = total_profit_amount - total_tax_plus_delivery

    master_products = OrderDetails.objects.values('orderDet_product__product_id', 'orderDet_product__product_name').annotate(total_amount=Sum('orderDet_price'), total_quantity = Sum('orderDet_quantity')).order_by('-total_amount')[:10]

    citywise_sales_amount = Order.objects.values('order_address_id__address_city').annotate(
    city_sales=Sum('order_amount')).order_by('-city_sales')

    statewise_sales_amount = Order.objects.values('order_address_id__address_state').annotate(
    state_sales=Sum('order_amount')).order_by('-state_sales')

    monthly_sales = Order.objects.annotate(order_month=TruncMonth('order_date')).values('order_month').annotate(total_sales=Sum('order_amount')).order_by('order_month')

    yearly_sales = Order.objects.annotate(order_year=TruncYear('order_date')).values('order_year').annotate(total_sales=Sum('order_amount')).order_by('order_year')

    return Response({'master_products':master_products, 'total_sales_amount':total_sales_amount, 'total_cost_amount':total_cost_amount, 'total_profit_amount':total_profit_amount, 'net_profit_amount':net_profit_amount, 'citywise_sales_amount':citywise_sales_amount,'statewise_sales_amount':statewise_sales_amount, 'monthly_sales':monthly_sales, 'yearly_sales':yearly_sales})
    

@api_view(['POST'])
def admin_create_account_function(request):
    if request.method == 'POST':
        form = AdminForm(request.data)
        if form.is_valid():
            form.save()
            return Response({
                'status': True,
                'message':'Account has been created successfully. Now you can login!'
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
        return Response({'status':False, 'message':'POST method is required'})

@api_view(['GET'])
def show_admin_profile_function(request):
    if request.GET.get('admin_id'):
        admin_id = int(request.GET.get('admin_id'))
        admin_data = Admin.objects.get(admin_id=admin_id)
        admin_data = Admin_api(admin_data)
        context = {'data': admin_data.data, 'status':True}
        return Response(context)
    else:
        return Response({'status':False})
    
def admin_show_account_function(request):
    admin_data = Admin.objects.all().values('admin_id', 'admin_fname', 'admin_lname', 'admin_email', 'admin_phone', 'admin_role', 'admin_profile_image')
    context = {'data': admin_data, 'status':True}
    return Response(context)

@api_view(['GET','PUT'])
def admin_update_account_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(Admin, pk=request.GET['pk'])
            admin_data = request.data
            form = Admin_api(data = admin_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    "status":True,
                    "message":"Your account has been updated successfully"
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
            instance = get_object_or_404(Admin, pk=request.GET['pk'])
            serializer = Admin_api(instance)
            return Response({'Instance':serializer.data})
        return Response('Somewthing went Wrong')

@api_view(['DELETE'])
def admin_delete_account_function(request):
    if request.GET.get('pk'):
        try:
            admin = get_object_or_404(Admin, pk=request.GET['pk'])
            admin.delete()
            return Response({
                "status": True,
                "message": "Admin has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })

@api_view(['GET'])
def show_customer_function(request):
    customer_data = Customer.objects.all().values('customer_id','customer_fname','customer_lname','customer_email')
    context={'data': customer_data,'status':True}
    query = request.GET.get('searchhere', '')
    if query:
        customer_data = Customer.objects.filter(
            Q(customer_fname__icontains=query) |
            Q(customer_lname__icontains=query) |
            Q(customer_email__icontains=query)).values('customer_id','customer_fname','customer_lname','customer_email') 
          
        context.update({'data':customer_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)


@api_view(['POST'])
def insert_customer_function(request):
    customer_data = request.data
    form = Customer_api(data = customer_data)
    print(form)
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
    

    
@api_view(['GET','PUT'])
def update_customer_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(Customer, pk=request.GET['pk'])
            customer_data = request.data
            form = Customer_api(data = customer_data, instance = instance, partial = True)
            check = Customer.objects.filter(customer_id = instance.pk).count()
            if check:
                email = Customer.objects.filter(customer_email = customer_data.get('customer_email')).count()
                if email < 2:
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
                    return Response({'status':False, 'message':'This email id is already used'})
            else:
                return Response({
                            'status':False,
                            'message': "No user found"
                        })
    else:
        if request.GET.get('pk'):
            instance = get_object_or_404(Customer, pk=request.GET['pk'])
            serializer = Customer_api(instance)
            return Response({'Instance':serializer.data})
        return Response('Somewthing went Wrong')
             

@api_view(['DELETE'])
def delete_customer_function(request):
    if request.GET.get('pk'):
        try:
            customer = get_object_or_404(Customer, pk=request.GET['pk'])
            customer.delete()
            return Response({
                "status": True,
                "message": "Customer has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })


@api_view(['GET'])
def show_customer_address_function(request):
    customer_address_data = Customer_Address.objects.all().values('address_id', 'address_customer_id__customer_id', 'address_customer_fname', 'address_line1', 'address_landmark', 'address_country', 'address_city', 'address_zipcode', 'address_phone')
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
            Q(address_phone__icontains=query)).values('address_id', 'address_customer_id__customer_id', 'address_customer_fname', 'address_line1', 'address_landmark', 'address_country', 'address_city', 'address_zipcode', 'address_phone') 
        context.update({'data':customer_address_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_customer_address_function(request):
    customer_address_data = request.data 
    form = Customer_Address_api(data = customer_address_data)
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
def update_customer_address_function(request):
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

@api_view(['DELETE'])
def delete_customer_address_function(request):
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


@api_view(['GET'])
def show_category_function(request):
    category_data = Category.objects.all().values('category_id', 'category_name')
    context = {
        'data':category_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        category_data = Category.objects.filter(
            Q(category_name__icontains=query)).values('category_id', 'category_name')
        context.update({'data':category_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_category_function(request):
    category_data = request.data
    form = Category_api(data = category_data)
    check = Category.objects.filter(category_name = request.data.get('category_name')).exists()
    if not check:
        if form.is_valid():
                form.save()
                return Response({
                    'Status':True,
                    'Message': 'Category has been added successfully'
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
        return Response({'status':False, 'messgae':'This category already exists'})

@api_view(['GET','POST','PUT'])
def update_category_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(Category, pk=request.GET['pk'])
            category_data = request.data 
            form = Category_api(data = category_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Category has been updated successfully'
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
        instance = get_object_or_404(Category, pk=request.GET['pk'])
        serializer = Category_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_category_function(request):
    if request.GET.get('pk'):
        try:
            category = get_object_or_404(Category, pk=request.GET['pk'])
            category.delete()
            return Response({
                "status": True,
                "message": "Category has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })
        


@api_view(['GET'])
def show_size_function(request):
    size_data = Size.objects.all().values('size_id', 'size_size', 'size_cat__category_name', 'size_cat__category_id')
    context = {
        'data': size_data,
        'status': True
    }
    query = request.GET.get('searchhere', '')
    if query:
        size_data = Size.objects.filter(
            Q(size_size__icontains=query)).values('size_id', 'size_size', 'size_cat__category_name', 'size_cat__category_id')
        context.update({'data':size_data})
    
    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST','GET'])
def insert_size_function(request):

    category = Category.objects.all().values('category_id','category_name')
    if request.method == 'GET':
        return Response({
                'status':True,
                'category': category
            })
    if request.method == 'POST':
        size_data = request.data 
        print(size_data)
        form = Size_insert_api(data = size_data)
        print(form)

    size_data = request.data 
    form = Size_api(data = size_data)
    check = Size.objects.filter(size_size = request.data.get('size_size'), size_cat = request.data.get('size_cat')).exists()
    if not check:
        if form.is_valid():
            form.save()
            return Response({
                'status': True,
                'message': 'Size has been added successfully'
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

        return Response({
                'status':False,
                'message': "Method is not Post"
            }) 
        return Response({'Status':False, 'message':'This Size already exists'})

@api_view(['GET','POST'])
def updated_size_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Size, pk=request.GET['pk'])
            size_data = request.data 
            form = Size_insert_api(data = size_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Size has been updated successfully'
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
        instance = get_object_or_404(Size, pk=request.GET['pk'])
        serializer = Size_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_size_function(request):
    if request.GET.get('pk'):
        try:
            size = get_object_or_404(Size, pk=request.GET['pk'])
            size.delete()
            return Response({
                "status": True,
                "message": "Size has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })    



@api_view(['GET'])
def show_color_function(request):
    color_data = Color.objects.all().values('color_id', 'color_color')
    context = {
        'data': color_data,
        'status': True
    }
    query = request.GET.get('searchhere', '')
    if query:
        color_data = Color.objects.filter(
            Q(color_color__icontains=query)).values('color_id', 'color_color')
        context.update({'data':color_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_color_function(request):
    color_data = request.data 
    form = Color_api(data = color_data)
    check = Color.objects.filter(color_color = request.data.get('color_color')).exists()
    if not check:
        if form.is_valid():
            form.save()
            return Response({
                'status': True,
                'message': 'Color has been added successfully'
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
        return Response({'Status':False, 'message':'This Color already exists'})

@api_view(['GET','POST'])
def update_color_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Color, pk=request.GET['pk'])
            color_data = request.data 
            form = Color_api(data = color_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Color has been updated successfully'
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
        instance = get_object_or_404(Color, pk=request.GET['pk'])
        serializer = Color_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_color_function(request):
    if request.GET.get('pk'):
        try:
            color = get_object_or_404(Color, pk=request.GET['pk'])
            color.delete()
            return Response({
                "status": True,
                "message": "Color has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })    



@api_view(['GET'])
def show_brand_function(request):
    brand_data = Brand.objects.all().values('brand_id', 'brand_name')
    context = {
        'data':brand_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        brand_data = Brand.objects.filter(
            Q(brand_name__icontains=query)).values('brand_id', 'brand_name')
        context.update({'data':brand_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_brand_function(request):
    brand_data = request.data 
    form = Brand_api(data = brand_data)
    check = Brand.objects.filter(brand_name = request.data.get('brand_name')).exists()
    if not check:
        if form.is_valid():
            form.save()
            return Response({
                'status': True,
                'message': 'Brand has been added successfully'
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
        return Response({'Status':False, 'message':'This Brand already exists'})

    
@api_view(['GET','PUT'])
def update_brand_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(Brand, pk=request.GET['pk'])
            brand_data = request.data 
            form = Brand_api(data = brand_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Brand has been updated successfully'
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
        instance = get_object_or_404(Brand, pk=request.GET['pk'])
        serializer = Brand_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_brand_function(request):
    if request.GET.get('pk'):
        try:
            brand = get_object_or_404(Brand, pk=request.GET['pk'])
            brand.delete()
            return Response({
                "status": True,
                "message": "Brand has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })    



@api_view(['GET'])
def show_product_availability_function(request):
    product_ava_data = Product_Availability.objects.all().values('product_ava_id', 'product_ava_area', 'product_ava_pincode')
    context = {
        'data':product_ava_data,
        'status':True
    }
    if request.GET.get('get_product'):
        get_product = request.GET.get('get_product')
        product_ava_data = Product_Availability.objects.all().values('product_ava_id', 'product_ava_area', 'product_ava_pincode').filter(product_ava_id = get_product)
        context.update({'data':product_ava_data, 'status':True})

    query = request.GET.get('searchhere', '')
    if query:
        product_ava_data = Product_Availability.objects.filter(
            Q(product_ava_area__icontains=query) |
            Q(product_ava_pincode__icontains=query)).values('product_ava_id', 'product_ava_area', 'product_ava_pincode')
        context.update({'data':product_ava_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_product_availability_function(request):
    prod_ava_data = request.data 
    form = Product_Availability_api(data = prod_ava_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Product Availability has been added successfully'
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
def update_product_availability_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Product_Availability, pk=request.GET['pk'])
            prod_ava_data = request.data 
            form = Product_Availability_api(data = prod_ava_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Product Availability has been updated successfully'
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
        instance = get_object_or_404(Product_Availability, pk=request.GET['pk'])
        serializer = Product_Availability_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_product_availability_function(request):
    if request.GET.get('pk'):
        try:
            product_ava = get_object_or_404(Product_Availability, pk=request.GET['pk'])
            product_ava.delete()
            return Response({
                "status": True,
                "message": "Product Availability has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            })     



@api_view(['GET'])
def show_product_function(request):
    # Fetch all products with related fields
    product_data = Product.objects.prefetch_related('product_size', 'product_color', 'product_ava','product_reviews','offer_product_data').annotate(
        average_rating=Avg('product_reviews__review_rating'),total_reviews=Count('product_reviews__review_rating')
    ).all()

    # Handle filters from query parameters
    if request.GET.get('get_color'):
        get_color = request.GET.get('get_color')
        product_data = product_data.filter(product_color__color_id=get_color)

    if request.GET.get('get_cat'):
        get_cat = request.GET.get('get_cat')
        product_data = product_data.filter(product_cat__category_id=get_cat)

    if request.GET.get('get_brand'):
        get_brand = request.GET.get('get_brand')
        product_data = product_data.filter(product_brand__brand_id=get_brand)

    if request.GET.get('get_size'):
        get_size = request.GET.get('get_size')
        product_data = product_data.filter(product_size__size_id=get_size)

    # Handle search functionality
    query = request.GET.get('searchhere', '')
    if query:
        product_data = product_data.filter(
            Q(product_name__icontains=query) |
            Q(product_mrp__icontains=query) |
            Q(product_selling_price__icontains=query) |
            Q(product_desc__icontains=query) |
            Q(product_stock__icontains=query) |
            # Q(product_color__color_name__icontains=query) |
            Q(product_status__icontains=query) |
            # Q(product_size__size_size__icontains=query) |
            Q(product_brand__brand_name__icontains=query)
        )

    
    paginator = Paginator(product_data, 5)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    products_list = []
    for product in page_obj:
        inoffer = None
        price_after_offer = None
        for offer in product.offer_product_data.all():
            inoffer = offer.offer_del_offer.offer_name
            price_after_offer = product.product_mrp - (offer.offer_del_offer.offer_discount * product.product_mrp / 100)

        products_list.append({
            'product_id': product.product_id,
            'product_name': product.product_name,
            'product_mrp': product.product_mrp,
            'product_selling_price': product.product_selling_price,
            'product_desc': product.product_desc,
            'product_stock': product.product_stock,
            'product_status': product.product_status,
            'product_img1': product.product_img1.url if product.product_img1 else None,
            'product_img2': product.product_img2.url if product.product_img2 else None,
            'product_color': [{"color_color": color.color_color,"color_id": color.color_id} for color in product.product_color.all()],
            'product_size': [{"size_size": size.size_size,"size_id":size.size_id,"size_cat_id":size.size_cat.category_id,"size_cat_name":size.size_cat.category_name} for size in product.product_size.all()],
            'product_brand': {
                'brand_id': product.product_brand.brand_id,
                'brand_name': product.product_brand.brand_name
            } if product.product_brand else None,
            'product_cat': {
                'category_id': product.product_cat.category_id,
                'category_name': product.product_cat.category_name
            } if product.product_cat else None,
            'product_ava': [{"product_ava_id": ava.product_ava_id,'product_ava_area':ava.product_ava_area,'product_ava_pincode':ava.product_ava_pincode} for ava in product.product_ava.all()],
            'average_rating': round(product.average_rating,2) if product.average_rating is not None else 0,
            'total_reviews': product.total_reviews if product.total_reviews is not None else 0, 
            'inoffer': inoffer,
            'price_after_offer': price_after_offer,
        })

    offers_list = Offer.objects.all().values('offer_id','offer_name')    

    return Response({
        'data': products_list,
        'status': True,
        'total_pages' : paginator.num_pages,
        'offers_list': offers_list,
    })


@api_view(['GET'])
def show_product_details_function(request):
    if request.GET.get('product_id'):
        product_id = request.GET.get('product_id')
        product_detail = Product.objects.filter(product_id = product_id).prefetch_related('product_size', 'product_color', 'product_ava','product_reviews','offer_product_data').annotate(
        average_rating=Avg('product_reviews__review_rating')  # Calculate average rating
        ).all()
        
        if request.GET.get('get_color'):
            get_color = request.GET.get('get_color')
            product_detail = product_detail.filter(product_color__color_id=get_color)

        if request.GET.get('get_cat'):
            get_cat = request.GET.get('get_cat')
            product_detail = product_detail.filter(product_cat__category_id=get_cat)

        if request.GET.get('get_brand'):
            get_brand = request.GET.get('get_brand')
            product_detail = product_detail.filter(product_brand__brand_id=get_brand)

        if request.GET.get('get_size'):
            get_size = request.GET.get('get_size')
            product_detail = product_detail.filter(product_size__size_id=get_size)

        query = request.GET.get('searchhere', '')
        if query:
            product_detail = product_detail.filter(
                Q(product_name__icontains=query) |
                Q(product_mrp__icontains=query) |
                Q(product_selling_price__icontains=query) |
                Q(product_desc__icontains=query) |
                Q(product_stock__icontains=query) |
                Q(product_color__color_name__icontains=query) |
                Q(product_status__icontains=query) |
                Q(product_size__size_size__icontains=query) |
                Q(product_brand__brand_name__icontains=query)
            )

        paginator = Paginator(product_detail, 5)
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)
        products_list = []
        for product in page_obj:
            inoffer = None
            price_after_offer = None
            for offer in product.offer_product_data.all():
                inoffer = offer.offer_del_offer.offer_name
                price_after_offer = product.product_mrp - (offer.offer_del_offer.offer_discount * product.product_mrp / 100)

            products_list.append({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'product_mrp': product.product_mrp,
                'product_selling_price': product.product_selling_price,
                'product_desc': product.product_desc,
                'product_stock': product.product_stock,
                'product_status': product.product_status,
                'product_img1': product.product_img1.url if product.product_img1 else None,
                'product_img2': product.product_img2.url if product.product_img2 else None,
                'product_img3': product.product_img3.url if product.product_img3 else None,
                'product_img4': product.product_img4.url if product.product_img4 else None,
                'product_img5': product.product_img5.url if product.product_img5 else None,
                'product_img6': product.product_img6.url if product.product_img6 else None,
                'product_img7': product.product_img7.url if product.product_img7 else None,
                'product_img8': product.product_img8.url if product.product_img8 else None,
                'product_color': [{"color_color": color.color_color,"color_id": color.color_id} for color in product.product_color.all()],
                'product_size': [{"size_size": size.size_size,"size_id":size.size_id,"size_cat_id":size.size_cat.category_id,"size_cat_name":size.size_cat.category_name} for size in product.product_size.all()],
                'product_brand': {
                    'brand_id': product.product_brand.brand_id,
                    'brand_name': product.product_brand.brand_name
                } if product.product_brand else None,
                'product_reviews':[{'review_id':Review.review_id, 'review_date':Review.review_date, 'review_review':Review.review_review,'customer_id':Review.review_customer.customer_id, 'customer_name':"{} {}".format(Review.review_customer.customer_fname, Review.review_customer.customer_lname), 'review_rating':Review.review_rating, 'review_img':Review.review_img if Review.review_img else None} for Review in product.product_reviews.all()],
                'product_cat': {
                    'category_id': product.product_cat.category_id,
                    'category_name': product.product_cat.category_name
                } if product.product_cat else None,
                'product_ava': [{"product_ava_id": ava.product_ava_id,'product_ava_area':ava.product_ava_area,'product_ava_pincode':ava.product_ava_pincode} for ava in product.product_ava.all()],
                'average_rating': product.average_rating if product.average_rating is not None else 0,
                'inoffer': inoffer,
                'price_after_offer': price_after_offer,
                
            })

        return Response({
            'data': products_list,
            'status': True,
            'Total Pages':paginator.num_pages
        })
    
    return Response({
        'status': False,
        'message': 'product_id is required'
    })

@api_view(['GET', 'POST'])
def insert_product_function(request):
    if request.method == 'GET':
        brand_data = Brand.objects.values('brand_id', 'brand_name')
        color_data = Color.objects.values('color_id', 'color_color')
        size_data = Size.objects.values('size_id', 'size_size')
        product_ava_data = Product_Availability.objects.values('product_ava_id', 'product_ava_area')
        category_data = Category.objects.values('category_id', 'category_name')
        context = {
            'brand_data':brand_data,
            'color_data':color_data,
            'size_data':size_data,
            'product_ava_data':product_ava_data,
            'category_data':category_data
        }
        return Response({'data':context})
    
    product_data = request.data
    print(product_data)
    form = Product_insert_api(data = product_data)
    check = Product.objects.filter(product_name = request.data.get('product_name')).exists()
    if not check:
        if form.is_valid():
            form.save()
            return Response({
                'status': True,
                'message': 'Product has been added successfully'
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
        return Response({'status':False, 'message':'This product already exists'})

    
@api_view(['GET','POST'])
def update_product_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Product, pk=request.GET['pk'])
            product_data = request.data 
            form = Product_insert_api(data = product_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Product has been updated successfully'
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
        instance = get_object_or_404(Product, pk=request.GET['pk'])
        serializer = Product_show_api(instance)
        return Response({'Instance':serializer.data})
    
@api_view(['DELETE'])
def delete_product_function(request):
    if request.GET.get('pk'):
        try:
            product = get_object_or_404(Product, pk=request.GET['pk'])
            product.delete()
            return Response({
                "status": True,
                "message": "Product has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }) 


@api_view(['GET'])
def show_review_function(request):
    review_data = Review.objects.all().values('review_id', 'review_date', 'review_customer__customer_fname', 'review_customer__customer_id' , 'review_product__product_name','review_product__product_id', 'review_review', 'review_rating', 'review_img')
    context = {
        'data': review_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        review_data = Review.objects.filter(
            Q(review_date__icontains=query) |
            Q(review_review__icontains=query) |
            Q(review_rating__icontains=query)).values('review_id', 'review_date', 'review_customer__customer_fname', 'review_product__product_name', 'review_review', 'review_rating', 'review_img')
        context.update({'data':review_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_review_function(request):
    review_data = request.data 
    form = Review_api(data = review_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Review has been added successfully'
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
def update_review_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Review, pk=request.GET['pk'])
            review_data = request.data 
            form = Review_api(data = review_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Review has been updated successfully'
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
        instance = get_object_or_404(Review, pk=request.GET['pk'])
        serializer = Review_api(instance)
        return Response({'Instance':serializer.data})
    
@api_view(['DELETE'])
def delete_review_function(request):
    if request.GET.get('pk'):
        try:
            review = get_object_or_404(Review, pk=request.GET['pk'])
            review.delete()
            return Response({
                "status": True,
                "message": "Review has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }) 



@api_view(['GET'])
def show_cart_function(request):
    cart_data = Cart.objects.all().values('cart_id', 'cart_product_id', 'cart_customer__customer_fname', 'cart_customer__customer_id', 'cart_price', 'cart_quantity', 'cart_size__size_size', 'cart_size__size_id')
    context = {
        'data': cart_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        cart_data = Cart.objects.filter(
            Q(cart_price__icontains=query) |
            Q(cart_quantity__icontains=query)).values('cart_id', 'cart_product_id', 'cart_customer__customer_fname', 'cart_customer__customer_id', 'cart_price', 'cart_quantity', 'cart_size__size_size', 'cart_size__size_id')
        context.update({'data':cart_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_cart_function(request):
    cart_data = request.data 
    form = Cart_api(data = cart_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Cart has been added successfully'
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
def update_cart_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Cart, pk=request.GET['pk'])
            cart_data = request.data 
            form = Cart_api(data =cart_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Cart has been updated successfully'
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
        instance = get_object_or_404(Cart, pk=request.GET['pk'])
        serializer = Cart_api(instance)
        return Response({'Instance':serializer.data})
    
@api_view(['DELETE'])
def delete_cart_function(request):
    if request.GET.get('pk'):
        try:
            cart = get_object_or_404(Cart, pk=request.GET['pk'])
            cart.delete()
            return Response({
                "status": True,
                "message": "Cart has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }) 



@api_view(['GET'])
def show_offer_function(request):
    offer_data = Offer.objects.all().values('offer_id', 'offer_name', 'offer_discount', 'offer_starting_date', 'offer_ending_date')
    context = {
        'data': offer_data,
        'status':True
    }
    query = request.GET.get('searchhere', '')
    if query:
        offer_data = Offer.objects.filter(
            Q(offer_name__icontains=query) |
            Q(offer_discount__icontains=query) |
            Q(offer_starting_date__icontains=query) |
            Q(offer_ending_date__icontains=query)).values('offer_id', 'offer_name', 'offer_discount', 'offer_starting_date', 'offer_ending_date')
        context.update({'data':offer_data})

    paginators_data = page_paginators(context['data'], request)
    context.update({'data':paginators_data['data'],'total_pages':paginators_data['total_pages']})
    return Response(context)

@api_view(['POST'])
def insert_offer_function(request):
    offer_data = request.data 
    form = Offer_api(data = offer_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Offer has been added successfully'
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
def update_offer_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Offer, pk=request.GET['pk'])
            offer_data = request.data 
            form = Offer_api(data =offer_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Offer has been updated successfully'
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
        instance = get_object_or_404(Offer, pk=request.GET['pk'])
        serializer = Offer_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_offer_function(request):
    if request.GET.get('pk'):
        try:
            offer = get_object_or_404(Offer, pk=request.GET['pk'])
            offer.delete()
            return Response({
                "status": True,
                "message": "Offer has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }) 
        



@api_view(['GET'])
def show_offer_details_function(request):
    if request.GET.get('offerId'):
        offerid = request.GET.get('offerId')
        offer_details_data = Offer.objects.prefetch_related('offerdata__offer_del_product').filter(offer_id = offerid)
        paginator = Paginator(offer_details_data, 10)
        page_number = request.GET.get('page',1)
        page_obj = paginator.get_page(page_number)
        offerdatas = []
        
        for offer in page_obj:
            offer_dict = {
                'offer_id': offer.offer_id,
                'offer_name': offer.offer_name,
                'products': [],
                'offer_discount': offer.offer_discount,
                'offer_starting_date': offer.offer_starting_date,
                'offer_ending_date': offer.offer_ending_date,
                'offer_expired': offer.offer_expired,
                'offer_image':offer.offer_image.url
            }

            for offer_detail in offer.offerdata.all():
                product = offer_detail.offer_del_product
                after_offer_price = product.product_mrp - ((product.product_mrp * offer.offer_discount) / 100)
                offer_dict['products'].append({
                    'offer_detail_id': offer_detail.offer_del_id,
                    'product_name': product.product_name,
                    'product_mrp':product.product_mrp,
                    'product_cost':product.product_cost,
                    'product_selling_price':product.product_selling_price,
                    'product_stock':product.product_stock,
                    'product_img1':product.product_img1.url,
                    'after_offer_price':after_offer_price,
                    
                })
            offerdatas.append(offer_dict)
        print(offerdatas)
                
                
        context = {
            'data': offerdatas,
            'status': True,
            'total_pages':paginator.num_pages,
            'status': True,
        }
        return Response(context)
    else:
        return Response({'status':False,'message':'Get method is allowed'})

    
    

@api_view(['POST'])
def insert_offer_details_function(request):
    product_id = int(request.data.get('product_id'))
    offer_id = int(request.data.get('offer_id'))
    product = Product.objects.get(product_id=product_id)
    offer = Offer.objects.get(offer_id=offer_id)
    insert = Offer_Details.objects.create(offer_del_offer=offer,offer_del_product=product)
    insert.save()
    return Response({'message': 'Offer added to product successfully!','status':True})

    
@api_view(['GET','POST'])
def update_offer_details_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Offer_Details, pk=request.GET['pk'])
            offer_det_data = request.data 
            form = Offer_Details_api(data =offer_det_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Offer Details has been updated successfully'
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
        instance = get_object_or_404(Offer_Details, pk=request.GET['pk'])
        serializer = Offer_Details_api(instance)
        return Response({'Instance':serializer.data})
    
@api_view(['DELETE'])
def delete_offer_details_function(request):
    if request.GET.get('pk'):
        try:
            offer_det = get_object_or_404(Offer_Details, pk=request.GET['pk'])
            offer_det.delete()
            return Response({
                "status": True,
                "message": "Offer Details has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }) 
    else:
        return Response({
            'status': False,
            'message': 'Give Id for Delete'
        })    


@api_view(['GET'])
def show_order_function(request):


    if request.GET.get('Pending'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.PENDING  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('Accepted'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.ACCEPTED  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('Rejected'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.REJECTED  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('OutForDelivery'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.OutForDelivery  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('Delivered'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.DELIVERED  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('Returned'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.RETURNED  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     

    elif request.GET.get('Cancelled'):
        pending_order_details = OrderDetails.objects.filter(
        orderDet_order=OuterRef('order_id'),  # Reference to the current Order's ID
        orderDet_status=OrderDetails.OrderDetStatus.CANCELLED  # Filter for pending status
        )
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').annotate(
            has_thiss=Exists(pending_order_details)  # Annotate with a boolean indicating if there are pending order details
        ).filter(has_thiss=True) 
     
    else:
        order_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').all()
    
    query = request.GET.get('searchhere', '')
    if query:
        order_data = order_data.filter(
            Q(order_code__icontains=query) |
            Q(order_payment_mode__icontains=query) |
            Q(order_amount__icontains=query) |
            Q(order_tax_amount__icontains=query) |
            Q(order_delivery_charge__icontains=query) |
            Q(order_paid__icontains=query) |
            Q(order_date__icontains=query) |
            Q(order_delivered_date__icontains=query) |
            Q(order_note__icontains=query))

    paginator = Paginator(order_data, 5)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    order_list = []
    for order in page_obj:
        order_list.append({
            'order_id': order.order_id,
            'order_code': order.order_code,
            'Address': {"address_id": order.order_address_id.address_id, "customer_fname":order.order_address_id.address_customer_fname, "address_line1":order.order_address_id.address_line1, "address_line2":order.order_address_id.address_line2 if order.order_address_id.address_line2 is not None else 0, "landmark":order.order_address_id.address_landmark, "country":order.order_address_id.address_country, "city":order.order_address_id.address_city, "state":order.order_address_id.address_state, "zipcode":order.order_address_id.address_zipcode, "phone":order.order_address_id.address_phone},
            'Customer_details': {"customer_id": order.order_customer.customer_id,"customer_name": "{} {}".format( order.order_customer.customer_fname,  order.order_customer.customer_lname), "customer_email": order.order_customer.customer_email},
            "order_payment_mode":order.order_payment_mode,
            "order_amount": order.order_amount, 
            "order_tax_amount":order.order_tax_amount,
            "order_delivery_charge":order.order_delivery_charge,
            "order_paid":order.order_paid,
            "order_date":order.order_date,
            "order_delivered_date":order.order_delivered_date,
            "order_note":order.order_note,
            'order_product': [{
                    "orderdet_id":data.orderDet_id,
                    "product_id": data.orderDet_product.product_id,
                    'product_name': data.orderDet_product.product_name,
                    'product_price': data.orderDet_price,
                    'orderDet_quantity': data.orderDet_quantity,
                    'product_status': data.orderDet_status,
                    'product_brand': data.orderDet_product.product_brand.brand_name,
                    'product_size': data.orderDet_size_id.size_size,
                    'product_size_id': data.orderDet_size_id.size_id,
                    'product_color': data.orderDet_color.color_color,
                    'product_color_id': data.orderDet_color.color_id,
                    'product_img1': data.orderDet_product.product_img1.url,
                    'product_cat': data.orderDet_product.product_cat.category_name,
                    'product_returnable': data.orderDet_product.product_returnable,
                } for data in order.order_details.all()]
        })

    return Response({
            'data': order_list,
            'status': True,
            'Total Pages':paginator.num_pages
        })

@api_view(['POST'])
def insert_order_function(request):
    order_data = request.data 
    form = Order_api(data = order_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Order has been added successfully'
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
def update_order_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(Order, pk=request.GET['pk'])
            order_data = request.data 
            form = Order_api(data =order_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Order has been updated successfully'
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
        instance = get_object_or_404(Order, pk=request.GET['pk'])
        serializer = Order_api(instance)
        return Response({'Instance':serializer.data})

@api_view(['DELETE'])
def delete_order_function(request):
    if request.GET.get('pk'):
        try:
            order = get_object_or_404(Order, pk=request.GET['pk'])
            order.delete()
            return Response({
                "status": True,
                "message": "Order has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
            }) 

@api_view(['GET'])
def change_order_status_function(request):
    if request.GET.get('orderDet_id') and request.GET.get('orderDet_status'):
        orderDet_id = request.GET.get('orderDet_id')
        orderDet_status = request.GET.get('orderDet_status')
        try:
            order_data = OrderDetails.objects.get(orderDet_id=orderDet_id)
            if orderDet_status == 'ACCEPTED':
                order_data.orderDet_status = OrderDetails.OrderDetStatus.ACCEPTED
            elif orderDet_status == 'OutForDelivery':
                order_data.orderDet_status = OrderDetails.OrderDetStatus.OutForDelivery
            elif orderDet_status == 'DELIVERED':
                order_data.orderDet_status = OrderDetails.OrderDetStatus.DELIVERED
            elif orderDet_status == 'Rejected':
                order_data.orderDet_status = OrderDetails.OrderDetStatus.REJECTED
            elif orderDet_status == 'RETURNED':
                order_data.orderDet_status = OrderDetails.OrderDetStatus.RETURNED
            else:
                order_data.orderDet_status = OrderDetails.OrderDetStatus.CANCELLED
            order_data.save()
            return Response({'status': True, 'message': 'Order status updated successfully.'})
        except OrderDetails.DoesNotExist:
            return Response({'status': False, 'message': 'Order not found or not in PENDING status.'})
    else:
        return Response({'status': False, 'message': 'GET method required with orderDet_id and orderDet_status.'})


@api_view(['GET'])
def show_order_details_function(request):
    print("hello")
    if request.GET.get('order_id'):
        order_id = request.GET.get('order_id')
        OrderDetails_data = Order.objects.prefetch_related('order_address_id', 'order_customer', 'order_details').get(order_id=order_id)

        order_dict = {}
        order_dict.update({
                # order data
                'orderDet_id': OrderDetails_data.order_id,
                'order_code': OrderDetails_data.order_code,
                'order_payment_mode': OrderDetails_data.order_payment_mode,
                'order_amount': OrderDetails_data.order_amount,
                'order_tax_amount': OrderDetails_data.order_tax_amount,
                'order_delivery_charge': OrderDetails_data.order_delivery_charge,
                'order_paid': OrderDetails_data.order_paid,
                'order_date': OrderDetails_data.order_date,
                'order_note': OrderDetails_data.order_note,
                'customer_id': OrderDetails_data.order_customer.customer_id,
                'customer_fname': OrderDetails_data.order_customer.customer_fname,
                'customer_lname': OrderDetails_data.order_customer.customer_lname,
                'customer_email': OrderDetails_data.order_customer.customer_email,
                'customer_phone': OrderDetails_data.order_customer.customer_phone,

                # Address Data
                'order_address_id': OrderDetails_data.order_address_id.address_id,
                'address_customer_fname': OrderDetails_data.order_address_id.address_customer_fname,
                'address_line1': OrderDetails_data.order_address_id.address_line1,
                'address_line2': OrderDetails_data.order_address_id.address_line2,
                'address_landmark': OrderDetails_data.order_address_id.address_landmark,
                'address_country': OrderDetails_data.order_address_id.address_country,
                'address_city': OrderDetails_data.order_address_id.address_city,
                'address_state': OrderDetails_data.order_address_id.address_state,
                'address_zipcode': OrderDetails_data.order_address_id.address_zipcode,
                'address_phone': OrderDetails_data.order_address_id.address_phone,

                # product and orderdetail data
                'orderDet_product': [{
                    "product_id": data.orderDet_product.product_id,
                    'product_name': data.orderDet_product.product_name,
                    'product_price': data.orderDet_price,
                    'orderDet_quantity': data.orderDet_quantity,
                    'product_status': data.orderDet_status,
                    'product_brand': data.orderDet_product.product_brand.brand_name,
                    'product_size': data.orderDet_size_id.size_size,
                    'product_size_id': data.orderDet_size_id.size_id,
                    'product_color': data.orderDet_color.color_color,
                    'product_color_id': data.orderDet_color.color_id,
                    'product_img1': data.orderDet_product.product_img1.url,
                    'product_cat': data.orderDet_product.product_cat.category_name,
                    'product_returnable': data.orderDet_product.product_returnable,
                    'product_active': data.orderDet_product.product_active,
                } for data in OrderDetails_data.order_details.all()],
                
            })
        return Response({
       
            'status': True,
            'data': order_dict,
        })
    
    return Response({'status': False, 'message': 'order_id is required'})


@api_view(['POST'])
def insert_order_details_function(request):
    order_det_data = request.data 
    form = OrderDetails_api(data = order_det_data)
    if form.is_valid():
        form.save()
        return Response({
            'status': True,
            'message': 'Order Details has been added successfully'
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
def update_order_details_function(request):
    if request.method == 'POST':
        if request.GET.get('pk'):
            instance = get_object_or_404(OrderDetails, pk=request.GET['pk'])
            order_det_data = request.data 
            form = OrderDetails_api(data = order_det_data, instance = instance, partial = True)
            if form.is_valid():
                form.save()
                return Response({
                    'status': True,
                    'message': 'Order Details has been updated successfully'
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
        instance = get_object_or_404(OrderDetails, pk=request.GET['pk'])
        serializer = OrderDetails_api(instance)
        return Response({'Instance':serializer.data})
    
@api_view(['DELETE'])
def delete_order_details_function(request):
    if request.GET.get('pk'):
        try:
            order_det.delete()
            order_det = get_object_or_404(OrderDetails, pk=request.GET['pk'])
            return Response({
                "status": True,
                "message": "Order Details has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "error": str(e)
    })
        

@api_view(['GET', 'POST'])
def order_assign_function(request):
    if request.GET.get('orderDet_id'):
        orderDet_id = request.GET.get('orderDet_id')

        orderDet_data = OrderDetails.objects.get(orderDet_id=orderDet_id)

        if request.GET.get('db_id'):
            db_id = request.GET.get('db_id')
            if request.GET.get('for_return'):
                assign_order_todo = assign_orders.OrderWork.For_Returning
            else:
                assign_order_todo = assign_orders.OrderWork.For_Delivery

            db_data = delivery_boy.objects.get(db_id= db_id)
            assign_order = assign_orders.objects.create(assign_db_id = db_data, assign_orderDet_id = orderDet_data, assign_order_todo = assign_order_todo)
            assign_order.save()
            return Response({'status':True, 'message':'Delivery boy is been assigned'})
        return Response({'status':False, 'message':'db_id is required'})
    return Response({'status':False, 'message':'orderDet_id'})



@api_view(['GET', 'POST'])       
def customer_return_order_accept_function(request):
    return_id = request.GET.get('return_id')
    return_status = request.GET.get('return_status')

    return_data = Return.objects.get(return_id=return_id)
    if return_status == 'ACCEPTED':
        return_data.return_status = Return.ReturnStatus.ACCEPTED
        return_data.save()
        return Response({'status':True, 'message': 'Return has been accepted successfully'})
    
    elif return_status == 'REJECTED':
        return_data.return_status = Return.ReturnStatus.REJECTED
        return_data.save()
        return Response({'status':True, 'message': 'Return has been rejected successfully'})
    
    elif return_status == 'RETURNED':
        return_data.return_status = Return.ReturnStatus.RETURNED
        return_data.save()
        return Response({'status':True, 'message': 'Return has been returned successfully'})
    
    else:
        return Response({'status': False, 'message': 'Invalid return status'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])    
def show_stock_details_function(request):
    stock_data = Stock.objects.prefetch_related('stock_product_data').all()

    query = request.GET.get('searchhere', '')
    if query:
        stock_data = stock_data.filter(
            Q(stock_supplier__icontains=query) |
            Q(stock_sku__icontains=query) |
            Q(stock_total_order_value__icontains=query) |
            Q(created_at__icontains=query))
        
    paginator = Paginator(stock_data, 10)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    stock_list = []
    for stock in page_obj:
        stock_list.append({'stock_id':stock.stock_id,
                           'stock_supplier':stock.stock_supplier,
                           'stock_sku':stock.stock_sku,
                           'stock_total_order_value':stock.stock_total_order_value,
                           'created_at':stock.created_at,
                            'stock_products': [
                                {'sp_id':data.sp_id, 
                                 'sp_product_name': data.sp_product_name, 
                                 'sp_product_code': data.sp_product_code, 
                                 'sp_category':data.sp_category.category_name,
                                 'sp_category_id':data.sp_category.category_id, 
                                 'sp_sub_category':data.sp_sub_category,
                                 'stock_products_details': [{'sd_id':pd.sd_id, 'sd_price':pd.sd_price, 'sd_quantity':pd.sd_quantity,'sd_size_id':pd.sd_size.size_id, 'sd_size':pd.sd_size.size_size, 'sd_id':pd.sd_color.color_id, 'sd_color':pd.sd_color.color_color} for pd in data.stock_details_data.all()]
                                 } for data in stock.stock_product_data.all()]
                        })
    context = {'status':True, 'data':stock_list, 'total_pages':paginator.num_pages}
    return Response(context)

@api_view(['GET', 'POST'])    
def insert_stock_details_function(request):
    data = {
            "stock_supplier": "Track N Trace",
            "stock_sku": "100",
            "stock_total_order_value": 10000.0,
            "stock_products": [
                {
                    "sp_product_name": "GPS",
                    "sp_product_code": "101",
                    "sp_category": "Watches",
                    "sp_brand_id": 1,
                    "sp_category_id": 8,
                    "sp_sub_category": 'Track',
                    "stock_products_details": [
                        {
                            "sd_id": 1,
                            "sd_price": 3500.0,
                            "sd_quantity": 10,
                            "sd_size_id": 1,
                            "sd_size": "L",
                            "sd_color_id": 1,
                            "sd_color": "black"
                        }
                    ]
                }
            ]
        }

    stock_data = Stock.objects.create(stock_supplier=data['stock_supplier'], stock_sku = data['stock_sku'],stock_total_order_value=data['stock_total_order_value'])

    for x in data['stock_products']:
        sp_category_id = Category.objects.get(category_id=x['sp_category_id'])
        sp_brand_id = Brand.objects.get(brand_id=x['sp_brand_id'])

        stock_product_data = Stock_product.objects.create(sp_product_name=x['sp_product_name'], sp_product_code=x['sp_product_code'], sp_category=sp_category_id, sp_brand=sp_brand_id, sp_sub_category=x['sp_sub_category'], sp_stock = stock_data)

        stock_management_data = Stock_management.objects.create(sm_product_name=x['sp_product_name'], sm_product_code=x['sp_product_code'], sm_category=sp_category_id, sm_brand=sp_brand_id, sm_sub_category=x['sp_sub_category'])
        

        for y in x['stock_products_details']:
            sd_size_id = Size.objects.get(size_id=y['sd_size_id'])
            print(sd_size_id)
            sd_color_id = Color.objects.get(color_id=y['sd_color_id'])
            print(sd_color_id)

            stock_details_data = stock_details.objects.create(sd_price=y['sd_price'], sd_quantity=y['sd_quantity'], sd_size=sd_size_id, sd_color=sd_color_id, sd_product=stock_product_data)

            stock_management_details_data = stock_manage_details.objects.create(smd_price=y['sd_price'], smd_quantity=y['sd_quantity'], smd_size=sd_size_id, smd_color=sd_color_id, smd_product=stock_management_data)

    return Response({'message' :'datasaved','stock_id':stock_data.stock_id})


@api_view(['DELETE'])
def delete_stock_details_function(request):
    if request.GET.get('pk'):
        try:
            stock_det = get_object_or_404(Stock, pk=request.GET['pk'])
            stock_det.delete()
            return Response({
                "status": True,
                "message": "Stock has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }) 
    else:
        return Response({
            'status': False,
            'message': 'Give pk for Delete'
        }) 


@api_view(['GET']) 
def show_stock_management_details_function(request):
    stock_management = Stock_management.objects.prefetch_related('stock_management_data').all()

    query = request.GET.get('searchhere', '')
    if query:
        stock_management = stock_management.filter(
            Q(sm_product_name__icontains=query) |
            Q(sm_product_code__icontains=query) |
            Q(sm_sub_category__icontains=query))
        
    paginator = Paginator(stock_management, 10)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    stock_management_list = []
    for stock_manage in page_obj:
        stock_management_list.append({
            'sm_id': stock_manage.sm_id,
            'sm_product_name': stock_manage.sm_product_name,
            'sm_product_code':stock_manage.sm_product_code,
            'sm_category_id':stock_manage.sm_category.category_id,
            'sm_category':stock_manage.sm_category.category_name,
            'sm_brand_id':stock_manage.sm_brand.brand_id,
            'sm_brand':stock_manage.sm_brand.brand_name,
            'sm_sub_category':stock_manage.sm_sub_category,
            'stock_manage':[
                {'smd_id':data.smd_id, 'smd_price':data.smd_price, 'smd_quantity':data.smd_quantity, 'smd_size_id': data.smd_size.size_id, 'smd_size': data.smd_size.size_size, 'smd_color_id': data.smd_color.color_color, 'smd_color':data.smd_color.color_color} for data in stock_manage.stock_management_data.all()
            ]
        })
    context = {'data':stock_management_list}  
    return Response(context)


@api_view(['DELETE'])
def delete_stock_management_details_function(request):
    if request.GET.get('pk'):
        try:
            stock_manage_det = get_object_or_404(Stock_management, pk=request.GET['pk'])
            stock_manage_det.delete()
            return Response({
                "status": True,
                "message": "Stock Management has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }) 
    else:
        return Response({
            'status': False,
            'message': 'Give pk for Delete'
        })
    

@api_view(['GET']) 
def show_delivery_boy_function(request):
    db_data = delivery_boy.objects.all().values('db_id', 'db_name', 'db_email', 'db_phone', 'db_address')

    query = request.GET.get('searchhere', '')
    if query:
        db_data = db_data.filter(
            Q(db_name__icontains=query) |
            Q(db_email__icontains=query) |
            Q(db_address__icontains=query))
        
    paginator = Paginator(db_data, 10)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    db_show_list = []
    for db in page_obj:
        db_show_list.append({
            'db_id': db['db_id'],
            'db_name': db['db_name'],
            'db_email': db['db_email'],
            'db_phone': db['db_phone'],
            'db_address': db['db_address'],
        })
    context = {'data':db_show_list}  
    return Response(context)



@api_view(['POST'])
def insert_delivery_boy_function(request):
    db_data = request.data
    form = delivery_boy_api(data = db_data)
    if form.is_valid():
        form.save()
        return Response({'status':True, 'message':'account has been created successfully'})
    else:
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        return Response({
            'status':False,
            'message': " ".join(error_messages)
        })
    


@api_view(['GET', 'PUT'])
def update_delivery_boy_function(request):
    if request.method == 'PUT':
        if request.GET.get('pk'):
            instance = get_object_or_404(delivery_boy, pk=request.GET['pk'])
            db_data = request.data
            form = delivery_boy_api(data = db_data, instance=instance, partial = True)
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
            return Response({'status':False, 'message':'pk is required'})
    else:
        if request.GET.get('pk'):
            instance = get_object_or_404(delivery_boy, pk=request.GET['pk'])
            serializer = delivery_boy_api(instance)
            return Response({'instance':serializer.data})
        return Response({'status':False, 'message':'pk is required'})
    


@api_view(['DELETE'])
def delete_delivery_boy_function(request):
    if request.GET.get('pk'):
        try:
            db_delete = get_object_or_404(delivery_boy, pk=request.GET['pk'])
            db_delete.delete()
            return Response({
                "status": True,
                "message": "Delevery Boy has been deleted successfully"
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }) 
    else:
        return Response({
            'status': False,
            'message': 'Give pk for Delete'
        })