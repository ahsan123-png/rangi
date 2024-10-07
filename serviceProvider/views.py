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
from django.middleware.csrf import get_token
from datetime import datetime
from django.db.models import Avg
from django.db.models import Prefetch
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
        csrf_token = get_token(request)
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
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'error': 'Category or Subcategory does not exist'},
                        status=404)
                )
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
            return JsonResponse(
                good_response(
                    request.method,
                    {'message': 'Service provider registered successfully',
                     'id': service_provider.id,
                     'username': username,
                     'email': email,
                     'phone_number': phone_number,
                     'address': address,
                     'zip_code': zip_code,
                     'category': category.name,
                     'subcategory': subcategory.name,
                     'csrf_token': csrf_token
                     },
                    status=201
                )
            )
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
    csrf_token = get_token(request)
    if not (email or phone_number) or not password:
        return JsonResponse(
            bad_response(
                request.method,
                {'error': 'Email/Phone and password are required'},
                status=400
            )
        )
    if phone_number:
        phone_number = clean_phone_number(phone_number)
    try:
        user_ex = None
        if email:
            user_ex = UserEx.objects.filter(email=email).first()
        if not user_ex and phone_number:
            user_ex = UserEx.objects.filter(Q(customer__phone_number=phone_number) | Q(serviceprovider__phone_number=phone_number)).first()
        if user_ex is None:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'User not found'},
                    status=404
                )
            )
        if not user_ex.check_password(password):
            return JsonResponse(
                bad_response(request.method, 
                {'error': 'Invalid password'},
                status=401)
            )
        user_data = {
            'id': None,
            'username': user_ex.username,
            'email': user_ex.email,
            'phone_number': None,
            'address': user_ex.address,
            'zip_code': user_ex.zipCode,
            'isServiceProvider': user_ex.isServiceProvider,
            'isCustomer': user_ex.isCustomer,
            'csrf_token': csrf_token
        }
        if hasattr(user_ex, 'customer'):
            user_data['id'] = user_ex.customer.id
            user_data['phone_number'] = user_ex.customer.phone_number
        elif hasattr(user_ex, 'serviceprovider'):
            user_data['id'] = user_ex.serviceprovider.id
            user_data['phone_number'] = user_ex.serviceprovider.phone_number
        return JsonResponse(
            good_response(
                request.method,
                user_data, status=200
            )
        )
    except ValidationError as e:
        return JsonResponse(
            bad_response(
                request.method,
                {'error': str(e)},
                status=400)
        )
    except Exception as e:
        return JsonResponse(
            bad_response(request.method,
                         {'error': str(e)},
                         status=500)
        )
#===============GET All service provider============
@csrf_exempt
def getAllServiceProviders(request) -> JsonResponse:
    if request.method == 'GET':
        # Fetch all service providers with related user, category, and SPProfile in one optimized query
        service_providers = ServiceProvider.objects.select_related('user', 'category')\
                                                   .prefetch_related('spprofile')\
                                                   .annotate(average_rating=Avg('reviews__rating'))\
                                                   .all()
        result = []
        for provider in service_providers:
            # Fetch SP profile data
            try:
                sp_profile = provider.spprofile  # Access SPProfile through reverse relationship
                sp_profile_data = {
                    "base_price": float(sp_profile.base_price),
                    "introduction": sp_profile.introduction,
                    "company_founded_date": sp_profile.company_founded_date,
                    "payment_methods": sp_profile.payment_methods,
                    "services_included": [service.name for service in sp_profile.services_included.all()],
                    "profile_picture_url": sp_profile.profile_picture.url if sp_profile.profile_picture else None
                }
            except SPProfile.DoesNotExist:
                sp_profile_data = {}
            # Append service provider data to result list
            result.append({
                'id': provider.id,
                'username': provider.user.username,
                'email': provider.user.email,
                'phone_number': provider.phone_number,
                'address': provider.user.address,
                'zip_code': provider.user.zipCode,
                'company_name': provider.company_name,
                'category_id': provider.category.id,
                'category': provider.category.name,
                # 'subcategory': provider.subcategory.name,  # Assuming ServiceProvider doesn't have subcategory directly
                'average_rating': provider.average_rating if provider.average_rating is not None else 0.0,
                'number_of_people': provider.number_of_people,
                'status': provider.status,
                'sp_profile': sp_profile_data  # Add SP Profile data
            })
        return JsonResponse(
            good_response(
                request.method,
                {"all_service_provider": result},
                status=200
            )
        )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'},
            status=405
        )
    )

#==================update service provider employee =================
@csrf_exempt
def updateServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'PATCH': # patch is used for if we want to update all felids in the service provider
        try:
            data = get_request_body(request)
        except ValueError:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Invalid request body'},
                    status=400
                )
            )
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                request.method,
                {'error': 'Service provider not found'},
                status=404)
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
                    {'error': 'Category does not exist'},
                    status=400
                ))
        if subcategory_id:
            try:
                subcategory = Subcategory.objects.get(id=subcategory_id)
                provider.subcategory = subcategory
            except ObjectDoesNotExist:
                return JsonResponse(bad_response(
                    request.method,
                    {'error': 'Category does not exist'},
                    status=400
                ))
        provider.number_of_people = data.get('number_of_people', provider.number_of_people)
        provider.status = data.get('status', provider.status)
        provider.user.save()
        provider.save()
        return JsonResponse(
            good_response(
            request.method,
            {'message': 'Service provider updated successfully'},
            status=200)
        )
    return JsonResponse(
        bad_response(
        request.method,
        {'error': 'Method not allowed'},
        status=405)
    )
#==================== Get a single service provider =============================
@csrf_exempt
def getServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            service_provider = ServiceProvider.objects.annotate(average_rating=Avg('reviews__rating')).get(id=provider_id)
            try:
                sp_profile = SPProfile.objects.get(service_provider=service_provider)
                sp_profile_data = {
                    "base_price": float(sp_profile.base_price),
                    "introduction": sp_profile.introduction,
                    "company_founded_date": sp_profile.company_founded_date,
                    "payment_methods": sp_profile.payment_methods,
                    "services_included": [service.name for service in sp_profile.services_included.all()],
                    "profile_picture_url": sp_profile.profile_picture.url if sp_profile.profile_picture else None
                }
            except SPProfile.DoesNotExist:
                sp_profile_data = {}
            provider_data = {
                'id': service_provider.id,
                'username': service_provider.user.username,
                'email': service_provider.user.email,
                'phone_number': service_provider.phone_number,
                'address': service_provider.user.address,
                'zip_code': service_provider.user.zipCode,
                'company_name': service_provider.company_name,
                'category_id': service_provider.category.id,
                'category': service_provider.category.name,
                'subcategory': service_provider.subcategory.name,
                'number_of_people': service_provider.number_of_people,
                'status': service_provider.status,
                'average_rating': service_provider.average_rating if service_provider.average_rating is not None else 0.0,
                'sp_profile': sp_profile_data
                
            }
            return JsonResponse(
                good_response(
                    request.method, 
                    {'service_provider': provider_data},
                    status=200
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                    {'error': 'Service provider not found'},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method, 
                    {'error': str(e)},
                    status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'},
            status=405
        )
    )
#================== Delete Service Provider =============================
@csrf_exempt
def deleteServiceProvider(request, provider_id) -> JsonResponse:
    if request.method == 'DELETE':
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
            provider.user.delete()  # This deletes both the service provider and the user.
            return JsonResponse(
                good_response(
                request.method, 
                {'message': 'Service provider and user deleted successfully'},
                status=200)
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                    {'error': 'Service provider not found'},
                    status=404)
            )
    return JsonResponse(
        bad_response(
                    request.method, 
                    {'error': 'Method not allowed'},
                    status=405)
    )

#================================== Update status ==========================================
@csrf_exempt
def updateServiceProviderStatus(request, id):
    if request.method == 'PATCH':
        try:
            service_provider = ServiceProvider.objects.get(id=id)
            data = get_request_body(request)
            new_status = data.get('status')
            if new_status not in ['pending', 'approved']:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'error': 'Invalid status. Status should be either "pending" or "approved".'},
                        status=400
                    )
                )
            service_provider.status = new_status
            service_provider.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                'message': 'Service provider status updated successfully.',
                'data': {
                    'username': service_provider.user.username,
                    'company_name': service_provider.company_name,
                    'status': service_provider.status
                }
            }, status=200
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {   'success': False,
                        'error': 'Service provider not found.'},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {   'success': False,
                        'error': str(e)},
                    status=500
                )
            )
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {'error': 'Method not allowed'},
                status=405
            )
        )

#=============Listing all service provider in the bases of category and subcategory =============
@csrf_exempt
def listServiceProviders(request):
    if request.method == 'POST':
        try:
            data = get_request_body(request)
            category_id = data.get('category_id')
            subcategory_id = data.get('subcategory_id')
            zip_code = data.get('zip_code')
            service_providers = (
                ServiceProvider.objects
                .select_related('user', 'category', 'subcategory')
                .prefetch_related(
                    Prefetch('spprofile'),  # Prefetch SP profile to get the base price
                    Prefetch('reviews')  # Prefetch reviews to calculate the average rating
                )
                .annotate(average_rating=Avg('reviews__rating'))  # Annotate the average rating from the reviews
            )
            if category_id:
                service_providers = service_providers.filter(category_id=category_id)
            if subcategory_id:
                service_providers = service_providers.filter(subcategory_id=subcategory_id)
            if zip_code:
                service_providers = service_providers.filter(user__zipCode=zip_code)
            if not service_providers.exists():
                return JsonResponse({
                    "success": False,
                    "message": "No service providers found for the given filters."
                }, status=404)
            result = []
            for sp in service_providers:
                # Get SPProfile details
                sp_profile = getattr(sp, 'spprofile', None)
                base_price = float(sp_profile.base_price) if sp_profile else 0.0

                result.append({
                    "service_provider_id": sp.id,
                    "category_id": sp.category.id,
                    "username": sp.user.username,
                    "company_name": sp.company_name,
                    "phone_number": sp.phone_number,
                    "category": sp.category.name,
                    "subcategory": sp.subcategory.name,
                    "zip_code": sp.user.zipCode,
                    "status": sp.status,
                    "number_of_people": sp.number_of_people,
                    "average_rating": sp.average_rating if sp.average_rating is not None else 0.0,  # Average rating
                    "base_price": base_price  # Base price from SPProfile
                })
            return JsonResponse({
                "success": True,
                "service_providers": result
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "Invalid JSON payload."
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
#================SP PRofile =======================
@csrf_exempt
def createSpProfile(request,service_provider_id):
    if request.method == 'POST':
        try:
            data = request.POST
            base_price = data.get('base_price')
            introduction = data.get('introduction')
            company_founded_date = data.get('company_founded_date')
            payment_methods = data.get('payment_methods')
            services_included = data.get('services_included', [])
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            company_founded_date_obj = datetime.strptime(company_founded_date, '%Y-%m-%d')
            profile_picture = request.FILES.get('profile_picture')
            company_founded_date_obj = datetime.strptime(company_founded_date, '%Y-%m-%d')
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            sp_profile, created = SPProfile.objects.update_or_create(
                service_provider=service_provider,
                defaults={
                    'base_price': base_price,
                    'introduction': introduction,
                    'company_founded_date': company_founded_date_obj,
                    'payment_methods': payment_methods,
                }
            )
            if profile_picture:
                sp_profile.profile_picture.save(profile_picture.name, profile_picture)
            sp_profile.services_included.clear()
            for subcategory_id in services_included:
                subcategory = Subcategory.objects.get(id=subcategory_id)
                sp_profile.services_included.add(subcategory)
            return JsonResponse(
                good_response(
                    request.method,
                    {
                "success": True,
                "message": "SP Profile created/updated successfully!",
                "profile": {
                    "base_price": sp_profile.base_price,
                    "introduction": sp_profile.introduction,
                    "company_founded_date": sp_profile.company_founded_date.strftime('%Y-%m-%d'),
                    "payment_methods": sp_profile.payment_methods,
                    "services_included": [subcategory.name for subcategory in sp_profile.services_included.all()],
                    "profile_picture_url": sp_profile.profile_picture.url if sp_profile.profile_picture else None,
                }
            }, status=201
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {   'success': False,
                        'error': 'Service provider not found.'},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {   'success': False,
                        'error': str(e)},
                    status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'},
            status=405
        )
    )
#================ Service Request =============================
@csrf_exempt
def createServiceRequest(request):
    if request.method == 'POST':
        try:
            data = get_request_body(request)
            service_provider_id = data.get('service_provider_id')
            category_id = data.get('category_id')
            subcategory_ids = data.get('subcategories', [])
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            category = Category.objects.get(id=category_id)
            subcategories = Subcategory.objects.filter(id__in=subcategory_ids)
            sp_profile = SPProfile.objects.get(service_provider=service_provider)
            base_price = float(sp_profile.base_price)
            total_price = base_price
            included_services_ids = sp_profile.services_included.values_list('id', flat=True)
            additional_services = []
            for subcategory in subcategories:
                if subcategory.id not in included_services_ids:
                    total_price += float(subcategory.additional_price)
                    additional_services.append(subcategory.name)
            service_request = ServiceRequest.objects.create(
                service_provider=service_provider,
                category=category,
                total_price=total_price)
            service_request.subcategories.set(subcategories)
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "message": "Service request created successfully!",
                        "service_request": {
                            "id": service_request.id,
                            "service_provider_id": service_request.service_provider.id,
                            "category_id": service_request.category.id,
                            "total_price": service_request.total_price,
                            "subcategories": [subcategory.name for subcategory in service_request.subcategories.all()]
                        }
                    },status=201))
                
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                        "error": "Service provider not found"
                    }, status=404))
        except Category.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                        "error": "Category not found"
                    }, status=404))
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                        "error": str(e)
                    }, status=500))
    return JsonResponse(
        bad_response(
            request.method,
            {
                "error": "Method not allowed"
            }, status=405))

# ============== Update user Profile details =================
@csrf_exempt
def updateSpProfile(request, service_provider_id):
    if request.method == 'PATCH':  
        try:
            data = get_request_body(request)
            base_price = data.get('base_price')
            introduction = data.get('introduction')
            company_founded_date = data.get('company_founded_date')
            payment_methods = data.get('payment_methods')
            services_included = data.get('services_included', [])
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            try:
                sp_profile = SPProfile.objects.get(service_provider=service_provider)
            except SPProfile.DoesNotExist:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'SP Profile not found.'},
                        status=404
                    )
                )
            if base_price is not None:
                sp_profile.base_price = base_price
            if introduction is not None:
                sp_profile.introduction = introduction
            if company_founded_date:
                company_founded_date_obj = datetime.strptime(company_founded_date, '%Y-%m-%d')
                sp_profile.company_founded_date = company_founded_date_obj
            if payment_methods is not None:
                sp_profile.payment_methods = payment_methods
            if services_included:
                sp_profile.services_included.clear()
                for subcategory_id in services_included:
                    subcategory = Subcategory.objects.get(id=subcategory_id)
                    sp_profile.services_included.add(subcategory)
            sp_profile.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "message": "SP Profile updated successfully!",
                        "profile": {
                            "base_price": sp_profile.base_price,
                            "introduction": sp_profile.introduction,
                            "company_founded_date": sp_profile.company_founded_date.strftime('%Y-%m-%d'),
                            "payment_methods": sp_profile.payment_methods,
                            "services_included": [subcategory.name for subcategory in sp_profile.services_included.all()],
                        }
                    },
                    status=200
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'success': False, 'error': 'Service provider not found.'},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'success': False, 'error': str(e)},
                    status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'},
            status=405
        )
    )

#================== update PRO Profile image ===================
@csrf_exempt
def updateSpProfilePicture(request, service_provider_id):
    if request.method == "POST":
        try:
            profile_picture = request.FILES.get('profile_picture')
            if not profile_picture:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Profile picture not provided.'},
                        status=400
                    )
                )
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            try:
                sp_profile = SPProfile.objects.get(service_provider=service_provider)
            except SPProfile.DoesNotExist:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'SP Profile not found.'},
                        status=404
                    )
                )
            sp_profile.profile_picture.save(profile_picture.name, profile_picture)
            sp_profile.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "message": "Profile picture updated successfully!",
                        "profile_picture_url": sp_profile.profile_picture.url
                    },
                    status=200
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'success': False, 'error': 'Service provider not found.'},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'success': False, 'error': str(e)},
                    status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {'error': 'Method not allowed'},
            status=405
        )
    )

