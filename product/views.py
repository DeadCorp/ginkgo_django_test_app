from django.views import generic

from product.models import Product


class ProductListView(generic.ListView):
    model = Product
    template_name = 'product/products_list.html'
    context_object_name = 'prod'
    paginate_by = 5

    def get_queryset(self):
        return Product.objects.all().order_by('delivery_price')


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
