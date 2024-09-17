from django.shortcuts import render
from userEx.models import *
from userEx.serializers import *
from userEx.views import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
# Create your views here.
import json
import re

@csrf_exempt
def registerServiceProvider(request) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        email = data.get('email', '')
        password = data.get('password', '')
        isServiceProvider = data.get('isServiceProvider', False)
        company_name = data.get('company_name', '')
        phone_number = data.get('phone_number', '')
        category_id = data.get('category', '')
        subcategory_id = data.get('subcategory', '')
        number_of_people = data.get('number_of_people', '')
        status = data.get('status', 'pending')
        address = data.get('address', '')
        zip_code = data.get('zip_code', '')
        name=first_name+' '+last_name
        if '@' in email:
            username = email.split('@')[0] + str(len(first_name + last_name))
        else:
            return JsonResponse({'error': 'Invalid email format'}, status=400)
        if not all([first_name, last_name, password, phone_number, email, category_id, subcategory_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        phone_number = clean_phone_number(phone_number)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return JsonResponse({'error': 'Invalid email address'}, status=400)
        if UserEx.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        try:
            user = UserEx.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name,name=name)
            user.isServiceProvider = isServiceProvider
            user.address = address
            user.zipCode = zip_code
            user.save()
            try:
                category = Category.objects.get(id=category_id)
                subcategory = Subcategory.objects.get(id=subcategory_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Category or Subcategory does not exist'}, status=400)
            service_provider = ServiceProvider(
                user=user,
                company_name=company_name,
                phone_number=phone_number,
                category=category,
                subcategory=subcategory,
                number_of_people=number_of_people,
                status=status
            )
            service_provider.save()
            return JsonResponse({
                'message': 'Service provider registered successfully',
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'zip_code': zip_code,
                'category': category.name,
                'subcategory': subcategory.name
            }, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'Database error'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
#===============GET All service provider============
@csrf_exempt
def getServiceProviders(request) -> JsonResponse:
    if request.method == 'GET':
        service_providers = ServiceProvider.objects.all()
        result = []
        for provider in service_providers:
            result.append({
                'id': provider.id,
                'username': provider.user.username,
                'email': provider.user.email,
                'phone_number': provider.phone_number,
                'address': provider.user.address,
                'zip_code': provider.user.zip_code,
                'company_name': provider.company_name,
                'category': provider.category.name,
                'subcategory': provider.subcategory.name,
                'number_of_people': provider.number_of_people,
                'status': provider.status
            })
        return JsonResponse(result, safe=False, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
