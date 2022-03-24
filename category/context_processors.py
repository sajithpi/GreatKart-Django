from carts.models import CartItem
from .models import Category
def media_links(request):
    try:
        links = Category.objects.all()
        cart_item_count = CartItem.objects.all().count()
        return dict(links = links,cart_item_count = cart_item_count,)
    except:
        pass

   