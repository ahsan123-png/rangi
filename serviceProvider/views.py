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
from django.db.models import Q
# Create your views here.
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
#==================== Login for the service provider =============================
@csrf_exempt
def loginView(request):
    data = get_request_body(request)  # Fetches request body data
    # import pdb; pdb.set_trace()
    email = data.get('email')
    phone_number = data.get('phone_number')
    password = data.get('password')
    if not (email or phone_number) or not password:
        return JsonResponse({'error': 'Email/Phone and password are required'}, status=400)
    if phone_number:
        phone_number = clean_phone_number(phone_number)
    try:
        user_ex = None
        if email:
            user_ex = UserEx.objects.filter(email=email).first()
        if not user_ex and phone_number:
            user_ex = UserEx.objects.filter(Q(customer__phone_number=phone_number) | Q(serviceprovider__phone_number=phone_number)).first()
        if user_ex is None:
            return JsonResponse({'error': 'User not found'}, status=404)
        if not user_ex.check_password(password):
            return JsonResponse(
                bad_response(request.method, {'error': 'Invalid password'}, status=401)
            )
        user_data = {
            'username': user_ex.username,
            'email': user_ex.email,
            'phone_number': None,
            'address': user_ex.address,
            'zip_code': user_ex.zipCode,
            'isServiceProvider': user_ex.isServiceProvider,
            'isCustomer': user_ex.isCustomer
        }
        if hasattr(user_ex, 'customer'):
            user_data['phone_number'] = user_ex.customer.phone_number
        elif hasattr(user_ex, 'serviceprovider'):
            user_data['phone_number'] = user_ex.serviceprovider.phone_number
        return JsonResponse(
            good_response(
                request.method,
                user_data, status=200
            )
        )
    except ValidationError as e:
        return JsonResponse(
            bad_response(request.method, {'error': str(e)}, status=400)
        )
    except Exception as e:
        return JsonResponse(
            bad_response(request.method, {'error': str(e)}, status=500)
        )
#===============GET All service provider============
@csrf_exempt
def getAllServiceProviders(request) -> JsonResponse:
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
                'zip_code': provider.user.zipCode,
                'company_name': provider.company_name,
                'category': provider.category.name,
                'subcategory': provider.subcategory.name,
                'number_of_people': provider.number_of_people,
                'status': provider.status
            })
        return JsonResponse(
            good_response(
                request.method,
                {"all_service_provider": result},status=200
            )
        )
    return JsonResponse({'error': 'Method not allowed'}, status=405)
#==================update service provider employee =================
@csrf_exempt
def updateServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'PATCH': # patch is used for if we want to update all felids in the service provider
        try:
            data = get_request_body(request)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(request.method,
                             {'error': 'Service provider not found'}, status=404)
            )
        provider.user.first_name = data.get('first_name', provider.user.first_name)
        provider.user.last_name = data.get('last_name', provider.user.last_name)
        provider.user.email = data.get('email', provider.user.email)
        provider.phone_number = data.get('phone_number', provider.phone_number)
        provider.company_name = data.get('company_name', provider.company_name)
        provider.user.address = data.get('address', provider.user.address)
        provider.user.zipCode = data.get('zipCode', provider.user.zipCode)
        provider.phone_number = clean_phone_number(provider.phone_number)
        category_id = data.get('category')
        subcategory_id = data.get('subcategory')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                provider.category = category
            except ObjectDoesNotExist:
                return JsonResponse(bad_response(
                    request.method,
                    {'error': 'Category does not exist'}, status=400
                ))
        if subcategory_id:
            try:
                subcategory = Subcategory.objects.get(id=subcategory_id)
                provider.subcategory = subcategory
            except ObjectDoesNotExist:
                return JsonResponse(bad_response(
                    request.method,
                    {'error': 'Category does not exist'}, status=400
                ))
        provider.number_of_people = data.get('number_of_people', provider.number_of_people)
        provider.status = data.get('status', provider.status)
        provider.user.save()
        provider.save()
        return JsonResponse(
            good_response(request.method,
                         {'message': 'Service provider updated successfully'}, status=200)
    
        )
    return JsonResponse(
        bad_response(request.method,
                         {'error': 'Method not allowed'}, status=405)
    )
#==================== Get a single service provider =============================
@csrf_exempt
def getServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            service_provider = ServiceProvider.objects.get(id=provider_id)
            provider_data = {
                'id': service_provider.id,
                'username': service_provider.user.username,
                'email': service_provider.user.email,
                'phone_number': service_provider.phone_number,
                'address': service_provider.user.address,
                'zip_code': service_provider.user.zipCode,
                'company_name': service_provider.company_name,
                'category': service_provider.category.name,
                'subcategory': service_provider.subcategory.name,
                'number_of_people': service_provider.number_of_people,
                'status': service_provider.status
            }
            return JsonResponse(
                good_response(request.method, 
                            {'service_provider': provider_data}, status=200)
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(request.method, 
                             {'error': 'Service provider not found'}, status=404)
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(bad_response(request.method,
                                     {'error': 'Method not allowed'}, status=405))
#================== Delete Service Provider =============================
@csrf_exempt
def deleteServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'DELETE':
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
            provider.user.delete()  # This deletes both the service provider and the user.
            return JsonResponse(
                good_response(request.method, 
                             {'message': 'Service provider and user deleted successfully'}, status=200)
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(request.method, 
                             {'error': 'Service provider not found'}, status=404)
            )
    return JsonResponse(
        bad_response(request.method, 
                             {'error': 'Method not allowed'}, status=405)
    )




# @csrf_exempt
# def deleteCategory(request, category_id) -> JsonResponse:
#     if request.method == 'DELETE':
#         try:
#             category = Category.objects.get(id=category_id)
#             category.delete()
#             return JsonResponse(
#                 good_response(request.method, 
#                              {'message': 'Category deleted successfully'}, status=200)
#             )
#         except ObjectDoesNotExist:
#             return JsonResponse(
#                 bad_response(request.method, 
#                              {'error': 'Category not found'}, status=404)
#             )
#     return JsonResponse(
#         bad_response(request.method, 
#                              {'error': 'Method not allowed'}, status=405)
#     )
