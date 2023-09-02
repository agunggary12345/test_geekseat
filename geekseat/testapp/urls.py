from django.urls import path

from .views import customer, item, order, order_detail

urlpatterns = [
    path('customer/', customer.home, name='home'),
    path('customer/register', customer.register, name='register'),
    path('customer/login', customer.customer_login, name='login'),
    path('customer/detail/<id>', customer.customer_detail, name='customer_detail'),
    path('customer/update/<id>', customer.customer_update, name='customer_update'),

    path('item/list', item.item_list, name='item_list'),
    path('item/detail/<id>', item.item_detail, name='item_detail'),

    path('order/list', order.order_list, name='order_list'),
    path('order/detail/<id>', order.order_detail, name='order_detail'),
    path('order/create', order.order_create, name='order_create'),
    path('order/update/<id>', order.order_update, name='order_update'),
    path('order/delete/<id>', order.order_delete, name='order_delete'),

    path('order_detail/list/<id>', order_detail.order_detail_list, name='order_detail_list'),
    path('order_detail/create', order_detail.order_detail_create, name='order_detail_create'),
    path('order_detail/update/<order_id>', order_detail.order_detail_update, name='order_detail_update'),
    path('order_detail/delete/<order_id>', order_detail.order_detail_delete, name='order_detail_delete'),
]
