from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse

from geekseat.local_settings import X_API_KEY
from rest_framework.authtoken.models import Token

from testapp.models import Customer, Item


def item_list(request):
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
            items = Item.objects.order_by('item_no')
            for item in items:
                item_id = item.item_id
                item_no = item.item_no
                item_name = item.item_name
                uom = item.uom or ''
                unit_price = item.unit_price or 0

                lists.append({
                    'item_id': item_id,
                    'item_no': item_no,
                    'item_name': item_name,
                    'uom': uom,
                    'unit_price': unit_price,
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


def item_detail(request, id):
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
            item = Item.objects.filter(item_id=id).order_by('item_no').first()
            if item:
                item_id = item.item_id
                item_no = item.item_no
                item_name = item.item_name
                uom = item.uom or ''
                unit_price = item.unit_price or 0

                data = {
                    'item_id': item_id,
                    'item_no': item_no,
                    'item_name': item_name,
                    'uom': uom,
                    'unit_price': unit_price,
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
