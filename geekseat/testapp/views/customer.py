import json

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

from geekseat.local_settings import X_API_KEY
from rest_framework.authtoken.models import Token

from testapp.models import Customer
from testapp.models.raw_model import RawModel
from testapp.views.general import check_email, gen_bcrypt, gen_token


@csrf_exempt
def register(request):
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

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)

            if not 'customer_name' in data or not 'address' in data or not 'phone' in data \
                    or not 'email' in data or not 'password' in data or not 'password_conf' in data:
                res = {
                    'status_code': 400,
                    'message': 'Some attributes are not found!'
                }
                return JsonResponse(res)

            customer_name = data['customer_name'] or ''
            address = data['address'] or ''
            phone = data['phone'] or ''
            email = data['email'] or ''
            password = data['password'] or ''
            password_conf = data['password_conf'] or ''

            if len(customer_name) == 0 or len(address) == 0 \
                    or len(phone) == 0 or len(email) == 0 \
                    or len(password) == 0 or len(password_conf) == 0:
                res = {
                    'status_code': 400,
                    'message': 'Attributes cannot be empty!'
                }
                return JsonResponse(res)

            if check_email(email):
                res = {
                    'status_code': 400,
                    'message': 'Invalid email!'
                }
                return JsonResponse(res)

            if password != password_conf:
                res = {
                    'status_code': 400,
                    'message': 'Password confirmation does not match!'
                }
                return JsonResponse(res)

            customer_count = Customer.objects.filter(Q(phone=phone) | Q(user_name=email)).count()
            if customer_count > 0:
                res = {
                    'status_code': 400,
                    'message': 'Your phone/email already registered.'
                }
                return JsonResponse(res)

            try:
                with transaction.atomic():
                    bpassword = gen_bcrypt(password)

                    customer = Customer(customer_name=customer_name, address=address,
                                        phone=phone, user_name=email, password=bpassword)
                    customer.save()

                    user = User.objects.create_user(username=email, email=email, password=password)
                    user.save()

                    res = {
                        'status_code': 201,
                        'message': 'Register success.'
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
def customer_login(request):
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

            if not request.body:
                res = {
                    'status_code': 400,
                    'message': 'There is no request body.'
                }
                return JsonResponse(res)

            data = json.loads(request.body)

            if not 'email' in data or not 'password' in data:
                res = {
                    'status_code': 400,
                    'message': 'Some attributes are not found!'
                }
                return JsonResponse(res)

            email = data['email'] or ''
            password = data['password'] or ''

            if len(email) == 0 or len(password) == 0:
                res = {
                    'status_code': 400,
                    'message': 'Attributes cannot be empty!'
                }
                return JsonResponse(res)

            if check_email(email):
                res = {
                    'status_code': 400,
                    'message': 'Invalid email!'
                }
                return JsonResponse(res)

            customer_id = 0
            customer_token = ''
            rows = RawModel.objects.raw("select customer_id as id from customer "
                                        "where user_name = %s and password = crypt(%s, password) limit 1",
                                        [email, password])
            for row in rows:
                customer_id = row.id

            if customer_id > 0:
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request, user)

                    # token = Token.objects.create(user=user)
                    token, created = Token.objects.get_or_create(user=user)
                    customer_token = token.key
                    # print(token.key)
                else:
                    res = {
                        'status_code': 401,
                        'message': 'Unauthorized access.'
                    }
                    return JsonResponse(res)

                res = {
                    'status_code': 200,
                    'data': {
                        'customer_id': customer_id,
                        'email': email,
                        'token': customer_token
                    },
                    'message': 'Ok'
                }
                return JsonResponse(res)
            else:
                res = {
                    'status_code': 400,
                    'message': 'Incorrect email or password!'
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


def customer_detail(request, id):
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
            customer = Customer.objects.filter(customer_id=id).first()
            if customer:
                customer_id = customer.customer_id
                customer_name = customer.customer_name
                address = customer.address
                phone = customer.phone
                email = customer.user_name

                data = {
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'address': address,
                    'phone': phone,
                    'email': email
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
def customer_update(request, id):
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

            customer_id = id or 0
            token = Token.objects.filter(key=api_token).first()
            if token:
                token_user_id = token.user_id or 0
                user = User.objects.get(id=token_user_id)
                if user:
                    user_id = user.id
                    customer = Customer.objects.filter(customer_id=id).first()
                    if customer:
                        customer_id = customer.customer_id or 0
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
                if not 'customer_name' in data or not 'address' in data or not 'phone' in data:
                    res = {
                        'status_code': 400,
                        'message': 'Some attributes are not found!'
                    }
                    return JsonResponse(res)

                customer_name = data['customer_name'] or ''
                address = data['address'] or ''
                phone = data['phone'] or ''

                if len(customer_name) == 0 or len(address) == 0 or len(phone) == 0:
                    res = {
                        'status_code': 400,
                        'message': 'Attributes cannot be empty!'
                    }
                    return JsonResponse(res)

                try:
                    with (transaction.atomic()):
                        customer = Customer.objects.get(customer_id=customer_id)
                        customer.customer_name = customer_name
                        customer.address = address
                        customer.phone = phone
                        customer.save()

                        res = {
                            'status_code': 201,
                            'message': 'Update profile success.'
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
def home(request):
    return HttpResponse("Hello world!")
