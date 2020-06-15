from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic

from order.models import Order, OrderStatus
from order.tasks import add_to_cart_walmart, add_to_cart_kmart
from product.models import Product
from supplieraccount.models import SupplierAccount, SupplierCodes


@login_required()
def add_to_cart(request):
    if request.method == 'POST':
        count = request.POST['product_count']

        product = Product.objects.get(sku=request.POST['sku'])
        account = SupplierAccount.objects.get(supplier=product.supplier, usersupplieraccount__user=request.user,
                                              usersupplieraccount__is_selected_account=True)
        order = Order(product=product, user_id=request.user.id, account=account)
        order.save()
        order_status = OrderStatus(order=order, status='IN_PROGRESS')
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

    return HttpResponseRedirect((request.META.get('HTTP_REFERER') + '#' + request.POST['sku'])
                                or request.META.get('HTTP_REFERER'))


@login_required()
def display_my_orders(request, product):
    # Display only orders with status
    my_orders = Order.objects.filter(user=request.user, product=product, orderstatus__isnull=False).order_by('-order_id')
    return render(request, 'order/my_orders.html', {'my_orders': my_orders})


class StatusImageView(generic.DetailView):
    model = OrderStatus
    template_name = 'order/order_status_image_display.html'
    context_object_name = 'order_status'
