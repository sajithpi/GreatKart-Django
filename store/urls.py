from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('',views.store,name="store"),
    path('category/<slug:category_slug>/',views.store,name="products_by_category"),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail,name="product_detail"),
    path('search/',views.searchProduct,name="search"),
    path('submit_review/<int:product_id>/',views.SubmitReview,name="submit_review"),
    path('apply/',views.product_detailed_search,name="product_detailed_search"),
]
