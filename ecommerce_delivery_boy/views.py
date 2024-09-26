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
def db_create_account_function(request):
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
    
@api_view(['GET','POST'])
def db_login_function(request):
    if request.method == 'POST':
        db_email = request.POST['db_email']
        db_password = request.POST['db_password']
        check_true = delivery_boy.objects.filter(db_email=db_email, db_password=db_password).exists()
        if check_true:
            db_data = delivery_boy.objects.get(db_email=db_email, db_password=db_password)
            request.session['db_id'] = db_data.db_id
            request.session['db_name'] = db_data.db_name
            request.session['db_logged_in'] = 'Yes'
            return Response({'status':True, 'message': 'Login Successfully!'})
        else:
            messages.error(request, "Invalid email or password!")
            return Response({'status': False, 'message': 'Invalid Email or Password'})
        
    return Response({'status': False, 'message': 'Use POST method'})

@api_view(['GET', 'POST'])
def db_update_account_function(request):
    if request.method == 'POST':
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


@api_view(['POST'])    
def db_update_password_function(request):
    if request.method == 'POST':
        db_id = request.GET.get('db_id')

        old_password = request.data.get('old_password')
        new_password1 = request.data.get('new_password1')
        new_password2 = request.data.get('new_password2')

        db_data = delivery_boy.objects.get(db_id=db_id)
        if db_data.db_password == old_password:
            if new_password1 == new_password2:
                db_data.db_password = new_password1
                db_data.save()
                return Response({'status': True, 'message': 'Password has been updated successfully!'})
            else:
                return Response({'status': False, 'message': 'New passwords do not match, please try again!'})
        else:
            return Response({'status': False, 'message': 'Old password is incorrect, please try again!'})


@api_view(['GET'])
def db_show_orders_function(request):
    db_id = request.GET.get('db_id')
    delivery_status = request.GET.get('delivery_status')
    if not delivery_status or not db_id:
        return Response({'status': False, 'message': 'delivery_status and db_id both are required'}, status=400)

    db_orders = assign_orders.objects.filter(assign_orderDet_id__orderDet_status = delivery_status, assign_db_id__db_id = db_id).values('assign_id', 'assign_db_id__db_name','assign_orderDet_id__orderDet_id', 'assign_orderDet_id__orderDet_order__order_code', 'assign_orderDet_id__orderDet_order__order_address_id__address_line1', 'assign_orderDet_id__orderDet_order__order_payment_mode', 'assign_orderDet_id__orderDet_order__order_amount', 'assign_orderDet_id__orderDet_order__order_tax_amount', 'assign_orderDet_id__orderDet_order__order_delivery_charge', 'assign_orderDet_id__orderDet_status', 'assign_orderDet_id__orderDet_order__order_paid', 'assign_orderDet_id__orderDet_order__order_date', 'assign_orderDet_id__orderDet_order__order_delivered_date', 'assign_orderDet_id__orderDet_order__order_note', 'assign_orderDet_id__orderDet_customer__customer_fname', 'assign_orderDet_id__orderDet_customer__customer_lname', 'assign_orderDet_id__orderDet_customer__customer_email', 'assign_orderDet_id__orderDet_customer__customer_phone')



    context={'data': db_orders,'status':True}
    return Response(context)


@api_view(['POST'])
def db_order_status_function(request):
    if request.GET.get('orderDet_id'):
        orderDet_id = request.GET.get('orderDet_id')
        db_order = OrderDetails.objects.get(orderDet_id = orderDet_id)

        
        db_order.orderDet_status = OrderDetails.OrderDetStatus.DELIVERED
        db_order.save()
        return Response({'status':True, 'message':'Status Updated successfully'})
    else:
        return Response({'status':False, 'message': 'orderDet_id is required'})


@api_view(['POST'])       
def db_return_order_accept_function(request):
    return_id = request.POST.get('return_id')
    return_status = request.POST.get('return_status')

    return_data = Return.objects.get(return_id=return_id)
    if return_status == 'ACCEPTED':
        return_data.return_status = Return.ReturnStatus.ACCEPTED
        return_data.save()
        return Response({'status':True, 'message': 'Return has been accepted successfully'})
    
    elif return_status == 'REJECTED':
        return_data.return_status = Return.ReturnStatus.REJECTED
        return_data.save()
        return Response({'status':True, 'message': 'Return has been rejected successfully'})
    
    else:
        return Response({'status': False, 'message': 'Invalid return status'}, status=status.HTTP_400_BAD_REQUEST)
