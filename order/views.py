from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from order.models import Order, OrderStatus
from order.tasks import add_to_cart_walmart, add_to_cart_kmart, add_to_cart_samsclub
from product.models import Product
from supplieraccount.models import SupplierAccount, SupplierCodes


@login_required()
def add_to_cart(request):
    if request.method == 'POST':
        count = request.POST['product_count']

        product = Product.objects.get(sku=request.POST['sku'])
        account = SupplierAccount.objects.get(id=request.POST['supplier_account_id'])
        order = Order(product=product, user_id=request.user.id, account=account)
        order.save()  # create order instance with current product user and supplier account
        order_status = OrderStatus(order=order, status='IN_PROGRESS')  # set status in_progress for created order
        order_status.save()
        parameters = {
            'count': count,
            'order_instance_id': order.id,
            'order_status_instance_id': order_status.id,
        }
        supplier = product.supplier
        if supplier in SupplierCodes.SUPPLIERS:
            supplier_name = SupplierCodes.SUPPLIERS[supplier]
            if supplier_name == 'Walmart':
                add_to_cart_walmart.delay(parameters)
            elif supplier_name == 'Kmart':
                add_to_cart_kmart.delay(parameters)
            elif supplier_name == 'SamsClub':
                add_to_cart_samsclub.delay(parameters)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER') + '#' + product.sku)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def display_my_orders(request, product):
    my_orders = Order.objects.filter(user=request.user, product=product).order_by('-order_id')
    return render(request, 'order/my_orders.html', {'my_orders': my_orders})


class StatusImageView(generic.DetailView):
    # to display images for order status
    model = OrderStatus
    template_name = 'order/order_status_image_display.html'
    context_object_name = 'order_status'
