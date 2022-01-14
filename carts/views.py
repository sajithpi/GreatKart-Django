from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from django.contrib.auth.decorators import login_required

from store.models import Product, Variation

# Create your views here.

def get_cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request,product_id):

    
    current_user = request.user
    product = Product.objects.get(id = product_id)
    product_variation = []
    #If user is authenticated
    if current_user.is_authenticated:
    
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass
    

        
        
        is_cart_item_exits = CartItem.objects.filter(product=product,user = current_user).exists()

        if is_cart_item_exits:

            cart_item = CartItem.objects.filter(product=product, user = current_user)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            print(existing_variation_list)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                cart_item_id = id[index]
                item = CartItem.objects.get(product=product,id=cart_item_id)
                item.quantity += 1
                
                item.save()
            else:
                cart_item = CartItem.objects.create(product = product, quantity = 1 , user = current_user)

                if len(product_variation) > 0 :
                    cart_item.variation.clear()    
                    cart_item.variation.add(*product_variation)
                # cart_item.quantity += 1
                    cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,

            )
            if len(product_variation) > 0 :
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
                cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('carts:cart')





    #if user not authenticated
    else:
       
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass
    

        
        try:
            cart = Cart.objects.get(cart_id = get_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = get_cart_id(request)
            )
        cart.save()
        is_cart_item_exits = CartItem.objects.filter(product=product,cart = cart).exists()

        if is_cart_item_exits:

            cart_item = CartItem.objects.filter(product=product, cart=cart)
            existing_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                existing_variation_list.append(list(existing_variation))
                id.append(item.id)
            print(existing_variation_list)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                cart_item_id = id[index]
                item = CartItem.objects.get(product=product,id=cart_item_id)
                item.quantity += 1
                
                item.save()
            else:
                cart_item = CartItem.objects.create(product = product, quantity = 1 , cart = cart)

                if len(product_variation) > 0 :
                    cart_item.variation.clear()    
                    cart_item.variation.add(*product_variation)
                # cart_item.quantity += 1
                    cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,

            )
            if len(product_variation) > 0 :
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
                cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('carts:cart')
    
def remove_cart(request,product_id,card_item_id):
    product = get_object_or_404(Product,id = product_id)
    current_user = request.user
    #If user is authenticated
    if current_user.is_authenticated:
        
        try:
            cart_item = CartItem.objects.get(product = product, user = current_user,id=card_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
        
        return redirect('carts:cart')
    #If user is not authenticated
    else:
        cart = Cart.objects.get(cart_id = get_cart_id(request))
        try:
            cart_item = CartItem.objects.get(product = product, cart = cart,id=card_item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
        except:
            pass
        
        return redirect('carts:cart')

def remove_cart_item(request,product_id,card_item_id):
    # cart = Cart.objects.get(cart_id = get_cart_id(request))
    current_user = request.user
    if current_user.is_authenticated:

        product = get_object_or_404(Product,id = product_id)
        cart_item = CartItem.objects.get(product = product,user = current_user,id=card_item_id)
        cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id = get_cart_id(request))
        product = get_object_or_404(Product,id = product_id)
        cart_item = CartItem.objects.get(product = product,cart = cart,id=card_item_id)
        cart_item.delete()

    return redirect('carts:cart')


def cart(request,total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else: 
            cart = Cart.objects.get(cart_id = get_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active = True)
       
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,

    }
    return render(request,'store/cart.html',context)


@login_required(login_url="accounts:login")
def checkout(request,total = 0, quantity = 0, cart_items = None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
           cart_items = CartItem.objects.filter(user=request.user, is_active = True)
        else: 
            cart = Cart.objects.get(cart_id = get_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart,is_active = True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,

    }
    return render(request,'store/checkout.html',context)
