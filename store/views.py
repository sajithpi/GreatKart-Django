from django.core import paginator
from django.http import request
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse

from carts.models import CartItem
from .models import Category
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
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product_detail,
        'in_cart' : in_cart,
    }
    return render(request,'store/product_detail.html',context)