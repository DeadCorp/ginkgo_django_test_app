from django.views import generic

from order.models import Order
from product.models import Product


class ProductListView(generic.ListView):
    model = Product
    template_name = 'product/products_list.html'
    context_object_name = 'prod'
    paginate_by = 5

    def get_queryset(self):
        products = Product.objects.all()
        return ordering(products)


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'


def ordering(sets):
    # First will be display availability products with delivery
    # Next will be display products without delivery or not availability products
    # In the end will be display not found products
    sets1 = sets.exclude(name='not found')
    sets2 = sets1.filter(delivery_price='No delivery')
    sets3 = sets.filter(name='not found')
    sets_last = sets1.union(sets2)
    sets_last = sets_last.union(sets3).order_by('delivery_price', 'name')
    return sets_last
