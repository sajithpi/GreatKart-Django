from django.http import request
from django.shortcuts import get_object_or_404, render
from django.urls.base import reverse
from .models import Category
from store.models import Product

# Create your views here.

def store(request,category_slug=None):

    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.all().filter(category = categories, is_available = True)
        product_count = Product.objects.all().filter(category = categories, is_available = True).count()
    else:

        products = Product.objects.all().filter(is_available = True)
        product_count = Product.objects.all().count()
    context = {
        'products' : products,
        'product_count' : product_count
    }
    return render(request,'store/store.html',context)


def product_detail(request,category_slug,product_slug):

    try:
        single_product_detail = Product.objects.get(category__slug = category_slug,slug=product_slug)
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product_detail,
    }
    return render(request,'store/product_detail.html',context)