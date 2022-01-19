from datetime import date
from email import message
from itertools import product
from math import prod
from django.contrib import messages
from django.core import paginator
from django.http import request
from django.shortcuts import get_object_or_404, render,redirect
from django.urls.base import reverse

from carts.models import CartItem
from orders.models import OrderProduct
from store import forms
from store.forms import ReviewForm
from .models import Category, ReviewRating
from store.models import Product
from carts.views import get_cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.

def store(request,category_slug=None):

    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category = categories, is_available = True)
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = Product.objects.all().filter(category = categories, is_available = True).count()
    else:

        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products,6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = Product.objects.all().count()
    context = {
        'products' : paged_products,
        'product_count' : product_count
    }
    return render(request,'store/store.html',context)


def product_detail(request,category_slug,product_slug):

    try:
        single_product_detail = Product.objects.get(category__slug = category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=get_cart_id(request),product = single_product_detail).exists()
       
    #    Getting the Reviews
        try:
                 product_reviews = ReviewRating.objects.filter(product__id = single_product_detail.id, status = True)
        except:
                product_reviews = None
        
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderedProduct = OrderProduct.objects.filter(user = request.user,product__id = single_product_detail.id ).exists()
            orderedProduct = None
        except OrderProduct.DoesNotExist:
            orderedProduct = None
    else:
        orderedProduct = None
    context = {
        'single_product' : single_product_detail,
        'in_cart' : in_cart,
        'ordered_product' : orderedProduct,
        'product_reviews' : product_reviews,
    }
    return render(request,'store/product_detail.html',context)

def searchProduct(request):

    if 'keyword' in request.GET:

        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(description__icontains = keyword)
            product_count = products.count()
        else:
            products = Product.objects.order_by('-created_date').all()
            product_count = products.count()

        context = {
            'products' : products,
            'product_count' : product_count,
        }

    return render(request,'store/store.html',context)

def SubmitReview(request,product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
       try:
            review = ReviewRating.objects.get(user__id = request.user.id,product__id = product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request,"Thank You Your Review Has been Updated")
            return redirect(url)
       except ReviewRating.DoesNotExist:

            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,"ThankYou Your Review Has been Submitted")

                return redirect(url)