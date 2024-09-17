from django.shortcuts import render
from userEx.models import *
from userEx.serializers import *
from userEx.views import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import json
import re
# Create your views here.

@csrf_exempt
def registerCustomer(request) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = get_request_body(request)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        email = data.get('email', '')
        password = data.get('password', '')
        phone_number = data.get('phone_number', '')
        address = data.get('address', '')
        zip_code = data.get('zip_code', '')
        name = first_name + ' ' + last_name
        if '@' in email:
            username = email.split('@')[0] + str(len(first_name + last_name))
        else:
            return JsonResponse(
                bad_response(
                   request.method,
                   {'error': 'Invalid email format'}, status=400
                )
            )
        if not all([first_name, last_name, password, phone_number, email]):
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'All fields are required'}, status=400
                )
            )
        phone_number = clean_phone_number(phone_number)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Invalid email format'}, status=400
                )
            )
        if UserEx.objects.filter(username=username).exists():
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Username already exists'}, status=400
                )
            )
        try:
            user = UserEx.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, name=name)
            user.isCustomer = True
            user.address = address
            user.zipCode = zip_code
            user.save()
            customer = Customer(user=user, phone_number=phone_number)
            customer.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        'username': username,
                        'email': email,
                        'phone_number': phone_number,
                        'address': address,
                        'zip_code': zip_code
                    }
                ), status=201
            )
        except IntegrityError:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Database error'}, status=500
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': str(e)}, status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'}, status=405
        )
    )
# get all customers
@csrf_exempt
def getAllCustomers(request) -> JsonResponse:
    if request.method == 'GET':
        customers = Customer.objects.all()
        result = []
        for customer in customers:
            result.append({
                'id': customer.id,
                'username': customer.user.username,
                'email': customer.user.email,
                'phone_number': customer.phone_number,
                'address': customer.user.address,
                'zip_code': customer.user.zipCode
            })
        return JsonResponse(
            good_response(
                request.method,
                {
            'message': 'All customers fetched successfully',
            'customers': result
        }, status=200
            )
        )

    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'}, status=405
        )
    )
# get customers
@csrf_exempt
def getCustomer(request, customer_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            customer = Customer.objects.get(id=customer_id)
            customer_data = {
                'id': customer.id,
                'username': customer.user.username,
                'email': customer.user.email,
                'phone_number': customer.phone_number,
                'address': customer.user.address,
                'zip_code': customer.user.zipCode
            }
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        'customer': customer_data
                    }
                ), status=200
            )
        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Customer not found'}, status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': str(e)}, status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'}, status=405
        )
    )
# update customer
@csrf_exempt
def updateCustomer(request, customer_id) -> JsonResponse:
    if request.method == 'PATCH':
        try:
            customer = Customer.objects.get(id=customer_id)
            data = get_request_body(request)
            # Update user details
            customer.user.first_name = data.get('first_name', customer.user.first_name)
            customer.user.last_name = data.get('last_name', customer.user.last_name)
            customer.user.email = data.get('email', customer.user.email)
            customer.user.address = data.get('address', customer.user.address)
            customer.user.zipCode = data.get('zip_code', customer.user.zipCode)
            customer.user.save()
            customer.phone_number = data.get('phone_number', customer.phone_number)
            customer.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        'customer': {
                            'id': customer.id,
                            'username': customer.user.username,
                            'email': customer.user.email,
                            'phone_number': customer.phone_number,
                            'address': customer.user.address,
                            'zip_code': customer.user.zipCode
                        }
                    }
                ), status=200
            )

        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Customer not found'}, status=404
                )
            )

        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': str(e)}, status=500
                )
            )

    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'}, status=405
        )
    )
#delete customer
@csrf_exempt
def deleteCustomer(request, customer_id) -> JsonResponse:
    if request.method == 'DELETE':
        try:
            customer = Customer.objects.get(id=customer_id)
            customer.user.delete()  # This will delete both the customer and the linked user
            return JsonResponse(
                good_response(
                    request.method,
                    {'message': 'Customer deleted successfully'}
                ), status=200
            )

        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Customer not found'}, status=404
                )
            )

        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': str(e)}, status=500
                )
            )

    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'}, status=405
        )
    )
