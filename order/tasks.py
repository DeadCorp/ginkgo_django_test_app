import time

from final.celery import app

from order.autoplacers import placer_walmart, placer_kmart, placer_samsclub
from order.models import OrderStatus, OrderStatusImage, Order


@app.task(bind=True)
def add_to_cart_samsclub(self, parameters_dict):
    parameters_dict = set_order_id(self, parameters_dict)
    time.sleep(25)
    selenium_instance = placer_samsclub.AutoPlacerSamsClub(**parameters_dict)
    time.sleep(25)
    result_dict = selenium_instance.run()
    time.sleep(25)
    save_status(result_dict, parameters_dict)


@app.task(bind=True)
def add_to_cart_walmart(self, parameters_dict):
    parameters_dict = set_order_id(self, parameters_dict)
    selenium_instance = placer_walmart.AutoPlacerWalmart(**parameters_dict)
    result_dict = selenium_instance.run()
    save_status(result_dict, parameters_dict)


@app.task(bind=True)
def add_to_cart_kmart(self, parameters_dict):
    parameters_dict = set_order_id(self, parameters_dict)
    selenium_instance = placer_kmart.AutoPlacerKmart(**parameters_dict)
    result_dict = selenium_instance.run()
    save_status(result_dict, parameters_dict)


def save_status(result_dict, parameters_dict):
    root = 'status_image/'
    order = Order.objects.filter(pk=parameters_dict['order_instance_id']) \
        .update(price=result_dict['price'], quantity=result_dict['quantity'],
                order_id=parameters_dict['celery_task_id'])
    upd = OrderStatus.objects.filter(pk=parameters_dict['order_status_instance_id'])\
        .update(status=result_dict['order_status'])

    for tag, path in result_dict['screenshots'].items():
        img = OrderStatusImage(order_status_id=parameters_dict['order_status_instance_id'],
                               status_image=root + path, tag=tag)
        img.save()


def set_order_id(self, parameters_dict):
    # set order id  - current celery task id
    parameters_dict['celery_task_id'] = self.request.id
    order = Order.objects.filter(pk=parameters_dict['order_instance_id']) \
        .update(order_id=parameters_dict['celery_task_id'])
    return parameters_dict
