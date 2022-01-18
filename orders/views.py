from ast import Or
from datetime import datetime
import json
import re
from django.shortcuts import render
from carts.models import CartItem
import datetime

from carts.views import cart
from django.shortcuts import redirect

from orders.models import Order, Payment
from store.models import Product
from .forms import OrderForm
from .models import OrderProduct, Payment
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import JsonResponse
# Create your views here.

def Place_Order(request,total=0,quantity=0):

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_item_count = cart_items.count()
    
    if cart_item_count <=0 :
        redirect('store:store')

    grand_total = 0
    tax = 0 
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity) 
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':

        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the information from user billing section
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered = False, order_number=order_number)

            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
             }


            return render(request,'orders/payment.html',context)
            # return redirect('carts:checkout')

        else:
        #  return redirect('carts:checkout')
            print(form.errors)
    return render(request,'accounts/dashboard.html')

def Payments(request):

    body = json.loads(request.body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['OrderID'])
    print(body)
    #Store Transaction Details inside payment model
    payment = Payment(
        user = request.user,
        payment_id = body['TransactionID'],
        payment_method = body['PaymentMethod'],
        amount_paid = order.order_total,
        status = body['Status'],
       
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the cart items to order product table

    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id = item.id)
        print('cart item id:',cart_item.id)
        product_variataion = cart_item.variation.all()
        print('product_variation:',product_variataion)
        order_product = OrderProduct.objects.get(id = order_product.id)
        order_product.variation.set(product_variataion)
        order_product.save()


    #Reduce the number of quantities of sold products

        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    #Clear the cart

    cart_item = CartItem.objects.filter(user = request.user)
    cart_item.delete()

    #Send Order Recieve

    mail_subject = 'Thank You For Your Order'
    message = render_to_string('orders/order_recieved_email.html',{
                'user' : request.user,
                'order' : order,



            })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()
    messages.success(request,"A Mail Has been Sented to Your Email")

    #Send order number and transaction id to sendData using jsonresponse
    data = {
        'order_number' : order.order_number,
        'Trans_ID' : payment.payment_id,

    }

    return JsonResponse(data)

def Order_Complete(request):

    order_number = request.GET.get('Order_Number')
    transaction_id = request.GET.get('Payment_ID')
    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        payment = Payment.objects.get(payment_id = transaction_id)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        sub_total = 0

        for item in ordered_products:
            sub_total += item.product_price * item.quantity
        
    
        context = {
            'order' : order,
            'ordered_products' : ordered_products,
            'order_number' : order.order_number,
            'transaction_id' : payment.payment_id,
            'payment' : payment,
            'sub_total' : sub_total,
          
           
        }

        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store:store')
