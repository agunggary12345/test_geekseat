import json

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from geekseat.local_settings import X_API_KEY
from rest_framework.authtoken.models import Token

from testapp.models import Customer, Item, Order, OrderDetail


def order_list(request):
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
                    username = user.username
                    customer = Customer.objects.filter(user_name=username).first()
                    if customer:
                        customer_id = customer.customer_id
                        customer_name = customer.customer_name
                        phone = customer.phone
                        email = customer.user_name
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
            orders = Order.objects.filter(customer_id=customer_id).order_by('-order_date', '-order_no')
            print(customer_id)
            for order in orders:
                print(2)
                order_id = order.order_id
                order_no = order.order_no
                order_date = order.order_date
                order_amount = order.order_amount or 0

                lists.append({
                    'order_id': order_id,
                    'order_no': order_no,
                    'order_date': order_date,
                    'order_amount': order_amount,
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'email': email,
                    'phone': phone,
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


def order_detail(request, id):
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
                    username = user.username
                    customer = Customer.objects.filter(user_name=username).first()
                    if customer:
                        customer_id = customer.customer_id
                        customer_name = customer.customer_name
                        phone = customer.phone
                        email = customer.user_name
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
            order = Order.objects.filter(order_id=id).first()
            if order:
                order_id = order.order_id
                order_no = order.order_no
                order_date = order.order_date
                order_amount = order.order_amount or 0

                details = {}
                list_details = []
                order_details = OrderDetail.objects.filter(order_id=order_id).order_by('seq')
                for order_det in order_details:
                    order_id = order_det.order_id
                    seq = order_det.seq
                    quantity = order_det.quantity or 0
                    unit_price = order_det.unit_price or 0
                    item_amount = quantity * unit_price
                    item_id = order_det.item_id

                    item_no = ""
                    item_name = ""
                    uom = ""
                    if order_det.item:
                        item_no = order_det.item.item_no
                        item_name = order_det.item.item_name
                        uom = order_det.item.uom

                    list_details.append({
                        'seq': seq,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'item_amount': item_amount,
                        'item_id': item_id,
                        'item_no': item_no,
                        'item_name': item_name,
                        'uom': uom,
                    })
                details = list_details

                data = {
                    'order_id': order_id,
                    'order_no': order_no,
                    'order_date': order_date,
                    'order_amount': order_amount,
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'email': email,
                    'phone': phone,
                    'items': details
                }

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
def order_create(request):
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
                    username = user.username
                    customer = Customer.objects.filter(user_name=username).first()
                    if customer:
                        customer_id = customer.customer_id or 0
                        customer_name = customer.customer_name
                        phone = customer.phone
                        email = customer.user_name
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

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)
            if customer_id > 0:
                if not 'order_no' in data:
                    res = {
                        'status_code': 400,
                        'message': 'Some attributes are not found!'
                    }
                    return JsonResponse(res)

                order_no = data['order_no'] or ''

                if len(order_no) == 0:
                    res = {
                        'status_code': 400,
                        'message': 'Attributes cannot be empty!'
                    }
                    return JsonResponse(res)

                try:
                    with (transaction.atomic()):
                        order = Order(order_no=order_no, customer_id=customer_id)
                        order.save()

                        data = {}
                        order = Order.objects.filter(order_id=order.order_id).first()
                        if order:
                            order_id = order.order_id
                            order_no = order.order_no
                            order_date = order.order_date
                            order_amount = order.order_amount or 0

                            data = {
                                'order_id': order_id,
                                'order_no': order_no,
                                'order_date': order_date,
                                'order_amount': order_amount,
                                'customer_id': customer_id,
                                'customer_name': customer_name,
                                'email': email,
                                'phone': phone,
                            }

                        res = {
                            'status_code': 201,
                            'data': data,
                            'message': 'Create order success.'
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
                    'status_code': 401,
                    'message': 'Unauthorized access!'
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
def order_update(request, id):
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
                    username = user.username
                    customer = Customer.objects.filter(user_name=username).first()
                    if customer:
                        customer_id = customer.customer_id or 0
                        customer_name = customer.customer_name
                        phone = customer.phone
                        email = customer.user_name
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

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)
            if customer_id > 0:
                if not 'order_no' in data:
                    res = {
                        'status_code': 400,
                        'message': 'Some attributes are not found!'
                    }
                    return JsonResponse(res)

                order_no = data['order_no'] or ''

                if len(order_no) == 0:
                    res = {
                        'status_code': 400,
                        'message': 'Attributes cannot be empty!'
                    }
                    return JsonResponse(res)

                try:
                    with (transaction.atomic()):
                        order = Order.objects.get(order_id=id)
                        order.order_no = order_no
                        order.customer_id = customer_id
                        order.save()

                        data = {}
                        order = Order.objects.filter(order_id=id).first()
                        if order:
                            order_id = order.order_id
                            order_no = order.order_no
                            order_date = order.order_date
                            order_amount = order.order_amount or 0

                            data = {
                                'order_id': order_id,
                                'order_no': order_no,
                                'order_date': order_date,
                                'order_amount': order_amount,
                                'customer_id': customer_id,
                                'customer_name': customer_name,
                                'email': email,
                                'phone': phone,
                            }

                        res = {
                            'status_code': 201,
                            'data': data,
                            'message': 'Update order success.'
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
                    'status_code': 401,
                    'message': 'Unauthorized access!'
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
def order_delete(request, id):
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

            try:
                with (transaction.atomic()):
                    order = Order.objects.get(order_id=id)
                    order.delete()

                    res = {
                        'status_code': 201,
                        'message': 'Delete order success.'
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
