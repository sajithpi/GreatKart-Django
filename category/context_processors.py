from .models import Category
def media_links(request):

    links = Category.objects.all()

    return dict(links = links)