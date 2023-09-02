import json

from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from geekseat.local_settings import X_API_KEY
from rest_framework.authtoken.models import Token

from testapp.models import Customer, Item, Order, OrderDetail
from testapp.models.raw_model import RawModel


def order_detail_list(request, id):
    if request.method == 'GET':
        try:
            api_key = None
            if request.headers and 'x-api-key' in request.headers:
                api_key = request.headers['x-api-key'] or None

            if X_API_KEY != api_key:
                res = {
                    'status_code': 401,
                    'message': 'Unauthorized access.'
                }
                return JsonResponse(res)

            api_token = None
            if 'HTTP_AUTHORIZATION' in request.META:
                api_token = request.META['HTTP_AUTHORIZATION'] or None

            api_token = api_token.split(' ')
            api_token = api_token[1]

            token = Token.objects.filter(key=api_token).first()
            if token:
                token_user_id = token.user_id or 0
                user = User.objects.get(id=token_user_id)
                if user:
                    user_id = user.id
                    customer = Customer.objects.filter(customer_id=user_id).first()
                    if customer:
                        customer_id = customer.customer_id
                    else:
                        res = {
                            'status_code': 401,
                            'message': 'Unauthorized access.'
                        }
                        return JsonResponse(res)
                else:
                    res = {
                        'status_code': 401,
                        'message': 'Token unrecognized.'
                    }
                    return JsonResponse(res)
            else:
                res = {
                    'status_code': 401,
                    'message': 'Token unrecognized.'
                }
                return JsonResponse(res)

            data = {}
            lists = []
            orders = OrderDetail.objects.filter(order_id=id).order_by('seq')
            for order in orders:
                order_id = order.order_id
                seq = order.seq
                quantity = order.quantity or 0
                unit_price = order.unit_price or 0
                item_amount = quantity * unit_price
                item_id = order.item_id

                item_no = ""
                item_name = ""
                uom = ""
                if order.item:
                    item_no = order.item.item_no
                    item_name = order.item.item_name
                    uom = order.item.uom

                lists.append({
                    'order_id': order_id,
                    'seq': seq,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'item_amount': item_amount,
                    'item_id': item_id,
                    'item_no': item_no,
                    'item_name': item_name,
                    'uom': uom,
                })
            data = lists

            res = {
                'status_code': 200,
                'data': data,
                'message': 'Ok'
            }
            return JsonResponse(res)
        except Exception as e:
            print(e)
            res = {
                'status_code': 500,
                'message': 'Internal server error. Please try again later.'
            }
            return JsonResponse(res)
    else:
        res = {
            'status_code': 404,
            'message': 'Request unavailable.'
        }
        return JsonResponse(res)


@csrf_exempt
def order_detail_create(request):
    if request.method == 'POST':
        try:
            api_key = None
            if request.headers and 'x-api-key' in request.headers:
                api_key = request.headers['x-api-key'] or None

            if X_API_KEY != api_key:
                res = {
                    'status_code': 401,
                    'message': 'Unauthorized access.'
                }
                return JsonResponse(res)

            api_token = None
            if 'HTTP_AUTHORIZATION' in request.META:
                api_token = request.META['HTTP_AUTHORIZATION'] or None

            api_token = api_token.split(' ')
            api_token = api_token[1]

            token = Token.objects.filter(key=api_token).first()
            if token:
                token_user_id = token.user_id or 0
                user = User.objects.get(id=token_user_id)
                if user:
                    user_id = user.id
                else:
                    res = {
                        'status_code': 401,
                        'message': 'Token unrecognized.'
                    }
                    return JsonResponse(res)
            else:
                res = {
                    'status_code': 401,
                    'message': 'Token unrecognized.'
                }
                return JsonResponse(res)

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)

            if not 'order_id' in data or not 'item_id' in data or not 'quantity' in data:
                res = {
                    'status_code': 400,
                    'message': 'Some attributes are not found!'
                }
                return JsonResponse(res)

            order_id = data['order_id']
            item_id = data['item_id'] or None
            quantity = data['quantity'] or 0

            if item_id is None or quantity == 0:
                res = {
                    'status_code': 400,
                    'message': 'Attributes cannot be empty!'
                }
                return JsonResponse(res)

            try:
                with (transaction.atomic()):
                    order = Order.objects.filter(order_id=order_id).first()
                    if order is None:
                        res = {
                            'status_code': 400,
                            'message': 'Order has not been made.'
                        }
                        return JsonResponse(res)

                    seq = 1
                    cursor = connection.cursor()
                    cursor.execute('SELECT max(seq) FROM order_detail where order_id = %s', [order_id])
                    row = cursor.fetchone()
                    if row[0]:
                        seq = row[0] + 1

                    cursor.close()

                    item_no = ''
                    item_name = ''
                    uom = ''
                    unit_price = 0
                    item = Item.objects.filter(item_id=item_id).first()
                    if item:
                        item_no = item.item_no
                        item_name = item.item_name
                        uom = item.uom
                        unit_price = item.unit_price or 0

                    order_det = OrderDetail(order_id=order_id, seq=seq, item_id=item_id, quantity=quantity, unit_price=unit_price)
                    order_det.save()

                    item_amount = quantity * unit_price

                    RawModel.objects.raw(
                        "update orders "
                        "set order_amount = coalesce((select coalesce(sum(coalesce(quantity, 0) * coalesce(unit_price, 0)), 0) "
                        "                   from order_detail where order_id = %s), 0) "
                        "where order_id = %s", [order_id, order_id])

                    data = {
                        'order_id': order_id,
                        'seq': seq,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'item_amount': item_amount,
                        'item_no': item_no,
                        'item_name': item_name,
                        'uom': uom,
                    }

                    res = {
                        'status_code': 201,
                        'data': data,
                        'message': 'Create order detail success.'
                    }
                    return JsonResponse(res)
            except Exception as e:
                print(e)
                res = {
                    'status_code': 500,
                    'message': 'Internal server error. Please try again later.'
                }
                return JsonResponse(res)

        except Exception as e:
            print(e)
            res = {
                'status_code': 500,
                'message': 'Internal server error. Please try again later.'
            }
            return JsonResponse(res)
    else:
        res = {
            'status_code': 404,
            'message': 'Request unavailable.'
        }
        return JsonResponse(res)


@csrf_exempt
def order_detail_update(request, order_id):
    if request.method == 'PUT':
        try:
            api_key = None
            if request.headers and 'x-api-key' in request.headers:
                api_key = request.headers['x-api-key'] or None

            if X_API_KEY != api_key:
                res = {
                    'status_code': 401,
                    'message': 'Unauthorized access.'
                }
                return JsonResponse(res)

            api_token = None
            if 'HTTP_AUTHORIZATION' in request.META:
                api_token = request.META['HTTP_AUTHORIZATION'] or None

            api_token = api_token.split(' ')
            api_token = api_token[1]

            token = Token.objects.filter(key=api_token).first()
            if token:
                token_user_id = token.user_id or 0
                user = User.objects.get(id=token_user_id)
                if user:
                    user_id = user.id
                else:
                    res = {
                        'status_code': 401,
                        'message': 'Token unrecognized.'
                    }
                    return JsonResponse(res)
            else:
                res = {
                    'status_code': 401,
                    'message': 'Token unrecognized.'
                }
                return JsonResponse(res)

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)

            if not 'seq' in data or not 'item_id' in data or not 'quantity' in data:
                res = {
                    'status_code': 400,
                    'message': 'Some attributes are not found!'
                }
                return JsonResponse(res)

            seq = data['seq'] or 0
            item_id = data['item_id'] or None
            quantity = data['quantity'] or 0

            if item_id is None or quantity == 0:
                res = {
                    'status_code': 400,
                    'message': 'Attributes cannot be empty!'
                }
                return JsonResponse(res)

            try:
                with (transaction.atomic()):
                    order = Order.objects.filter(order_id=order_id).first()
                    if order is None:
                        res = {
                            'status_code': 400,
                            'message': 'Order has not been made.'
                        }
                        return JsonResponse(res)

                    item_no = ''
                    item_name = ''
                    uom = ''
                    unit_price = 0
                    item = Item.objects.filter(item_id=item_id).first()
                    if item:
                        item_no = item.item_no
                        item_name = item.item_name
                        uom = item.uom
                        unit_price = item.unit_price or 0

                    order_det = OrderDetail.objects.get(order_id=order_id, seq=seq)
                    order_det.order_id = order_id
                    order_det.seq = seq
                    order_det.item_id = item_id
                    order_det.quantity = quantity
                    order_det.unit_price = unit_price
                    order_det.save()

                    item_amount = quantity * unit_price

                    RawModel.objects.raw(
                        "update orders "
                        "set order_amount = coalesce((select coalesce(sum(coalesce(quantity, 0) * coalesce(unit_price, 0)), 0) "
                        "                   from order_detail where order_id = %s), 0) "
                        "where order_id = %s", [order_id, order_id])

                    data = {
                        'order_id': order_id,
                        'seq': seq,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'item_amount': item_amount,
                        'item_no': item_no,
                        'item_name': item_name,
                        'uom': uom,
                    }

                    res = {
                        'status_code': 201,
                        'data': data,
                        'message': 'Update order detail success.'
                    }
                    return JsonResponse(res)
            except Exception as e:
                print(e)
                res = {
                    'status_code': 500,
                    'message': 'Internal server error. Please try again later.'
                }
                return JsonResponse(res)

        except Exception as e:
            print(e)
            res = {
                'status_code': 500,
                'message': 'Internal server error. Please try again later.'
            }
            return JsonResponse(res)
    else:
        res = {
            'status_code': 404,
            'message': 'Request unavailable.'
        }
        return JsonResponse(res)


@csrf_exempt
def order_detail_delete(request, order_id):
    if request.method == 'DELETE':
        try:
            api_key = None
            if request.headers and 'x-api-key' in request.headers:
                api_key = request.headers['x-api-key'] or None

            if X_API_KEY != api_key:
                res = {
                    'status_code': 401,
                    'message': 'Unauthorized access.'
                }
                return JsonResponse(res)

            api_token = None
            if 'HTTP_AUTHORIZATION' in request.META:
                api_token = request.META['HTTP_AUTHORIZATION'] or None

            api_token = api_token.split(' ')
            api_token = api_token[1]

            token = Token.objects.filter(key=api_token).first()
            if token:
                token_user_id = token.user_id or 0
                user = User.objects.get(id=token_user_id)
                if user:
                    user_id = user.id
                else:
                    res = {
                        'status_code': 401,
                        'message': 'Token unrecognized.'
                    }
                    return JsonResponse(res)
            else:
                res = {
                    'status_code': 401,
                    'message': 'Token unrecognized.'
                }
                return JsonResponse(res)

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)

            if not 'seq' in data:
                res = {
                    'status_code': 400,
                    'message': 'Some attributes are not found!'
                }
                return JsonResponse(res)

            seq = data['seq'] or 0
            if seq == 0:
                res = {
                    'status_code': 400,
                    'message': 'Attributes cannot be empty!'
                }
                return JsonResponse(res)

            try:
                with (transaction.atomic()):
                    order = Order.objects.filter(order_id=order_id).first()
                    if order is None:
                        res = {
                            'status_code': 400,
                            'message': 'Order has not been made.'
                        }
                        return JsonResponse(res)

                    order_det = OrderDetail.objects.get(order_id=order_id, seq=seq)
                    order_det.delete()

                    RawModel.objects.raw(
                        "update orders "
                        "set order_amount = coalesce((select coalesce(sum(coalesce(quantity, 0) * coalesce(unit_price, 0)), 0) "
                        "                   from order_detail where order_id = %s), 0) "
                        "where order_id = %s", [order_id, order_id])

                    res = {
                        'status_code': 201,
                        'message': 'Delete order detail success.'
                    }
                    return JsonResponse(res)
            except Exception as e:
                print(e)
                res = {
                    'status_code': 500,
                    'message': 'Internal server error. Please try again later.'
                }
                return JsonResponse(res)
        except Exception as e:
            print(e)
            res = {
                'status_code': 500,
                'message': 'Internal server error. Please try again later.'
            }
            return JsonResponse(res)
    else:
        res = {
            'status_code': 404,
            'message': 'Request unavailable.'
        }
        return JsonResponse(res)
