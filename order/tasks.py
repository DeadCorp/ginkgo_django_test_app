from selenium.common.exceptions import TimeoutException

from final.celery import app

from order.autoplacers import placer_walmart, placer_kmart
from order.models import OrderStatus, OrderStatusImage, Order

result_dict = {
            'price': '',
            'quantity': '',
            'screenshots': {},
            'product_status': None,
        }


@app.task(bind=True)
def add_to_cart_walmart(self, parameters_dict):
    parameters_dict = set_order_id(self, parameters_dict)
    selenium_instance = placer_walmart.AutoPlacerWalmart(**parameters_dict)
    try:
        self.result_dict = selenium_instance.run()
    except TimeoutException:
        pass
    save_status(self.result_dict, parameters_dict)


@app.task(bind=True)
def add_to_cart_kmart(self, parameters_dict):
    parameters_dict = set_order_id(self, parameters_dict)
    selenium_instance = placer_kmart.AutoPlacerKmart(**parameters_dict)
    try:
        self.result_dict = selenium_instance.run()
    except TimeoutException:
        pass
    save_status(self.result_dict, parameters_dict)


def save_status(no_empty_result_dict, parameters_dict):
    root = 'status_image/'
    order = Order.objects.filter(pk=parameters_dict['order_instance_id']) \
        .update(price=no_empty_result_dict['price'], quantity=no_empty_result_dict['quantity'],
                order_id=parameters_dict['celery_task_id'])
    upd = OrderStatus.objects.filter(pk=parameters_dict['order_status_instance_id'])\
        .update(status=no_empty_result_dict['product_status'])

    for tag, path in no_empty_result_dict['screenshots'].items():
        img = OrderStatusImage(order_status_id=parameters_dict['order_status_instance_id'],
                               status_image=root + path, tag=tag)
        img.save()


def set_order_id(self, parameters_dict):
    parameters_dict['celery_task_id'] = self.request.id
    order = Order.objects.filter(pk=parameters_dict['order_instance_id']) \
        .update(order_id=parameters_dict['celery_task_id'])
    return parameters_dict
