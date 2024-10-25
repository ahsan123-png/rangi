import json
import os
import re
from userEx.views import *
from userEx.models import *
from userEx.serializers import *
from django.urls import reverse
from datetime import datetime
from django.db.models import Avg
from django.conf import settings
from django.db.models import Q
from django.db.models import Prefetch
from django.utils.text import slugify
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import IntegrityError
from django.core.mail import send_mail
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
        if UserEx.objects.filter(Q(username=username) | Q(email=email)).exists():
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'email already taken try another one'}, 
                    status=409
                )
            )
        if ServiceProvider.objects.filter(phone_number=phone_number).exists():
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Phone number already exists'}, 
                    status=409
                )
            )
        if UserEx.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        try:
            user = UserEx.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            name=name)
            user.is_active = False
            user.isServiceProvider = isServiceProvider
            user.address = address
            user.zipCode = zip_code
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
            send_mail(
                subject="Activate your account",
                message=f"Hi {user.first_name},\n\nPlease activate your account by clicking the link below:\n\n{activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
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
                    {'message': 'Service provider registered successfully. Please confirm your email to activate the account.',
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
            'profile_picture_url': None,
            'csrf_token': csrf_token
        }
        if hasattr(user_ex, 'customer'):
            customer = user_ex.customer
            user_data['id'] = customer.id
            user_data['phone_number'] = customer.phone_number
            if user_ex.customer.profile_picture:
                user_data['profile_picture_url'] = user_ex.customer.profile_picture.url
        elif hasattr(user_ex, 'serviceprovider'):
            service_provider = user_ex.serviceprovider
            user_data['id'] = service_provider.id
            user_data['phone_number'] = service_provider.phone_number
            if hasattr(user_ex.serviceprovider, 'spprofile') and user_ex.serviceprovider.spprofile.profile_picture:
                user_data['profile_picture_url'] = user_ex.serviceprovider.spprofile.profile_picture.url

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
        service_providers = ServiceProvider.objects\
            .select_related('user', 'category')\
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
    if request.method == 'PATCH':
        try:
            data = get_request_body(request)
        except ValueError:
            return JsonResponse(
        bad_response(request.method,
        {'error': 'Invalid request body'},
        status=400))
        try:
            provider = ServiceProvider.objects.get(id=provider_id)
        except ObjectDoesNotExist:
            return JsonResponse(
        bad_response(
        request.method,
        {'error': 'Service provider not found'},
        status=404))
        new_email = data.get('email')
        if new_email:
            if UserEx.objects.filter(email=new_email).exclude(id=provider.user.id).exists():
                return JsonResponse(
            bad_response(
            request.method,
            {'error': 'Email is already taken, try another.'},
            status=400))
            provider.user.email = new_email
        new_phone_number = data.get('phone_number')
        if new_phone_number:
            cleaned_phone_number = clean_phone_number(new_phone_number)
            if ServiceProvider.objects.filter(phone_number=cleaned_phone_number).exclude(id=provider.id).exists():
                return JsonResponse(
                bad_response(
                request.method,
                {'error': 'Phone number is already taken, try another.'},
                status=400))
            provider.phone_number = cleaned_phone_number
        provider.user.first_name = data.get('first_name', provider.user.first_name)
        provider.user.last_name = data.get('last_name', provider.user.last_name)
        provider.company_name = data.get('company_name', provider.company_name)
        provider.user.address = data.get('address', provider.user.address)
        provider.user.zipCode = data.get('zipCode', provider.user.zipCode)
        category_id = data.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                provider.category = category
            except ObjectDoesNotExist:
                return JsonResponse(bad_response(request.method, {'error': 'Category does not exist'}, status=400))
        subcategory_id = data.get('subcategory')
        if subcategory_id:
            try:
                subcategory = Subcategory.objects.get(id=subcategory_id)
                provider.subcategory = subcategory
            except ObjectDoesNotExist:
                return JsonResponse(bad_response(request.method, {'error': 'Subcategory does not exist'}, status=400))
        provider.number_of_people = data.get('number_of_people', provider.number_of_people)
        provider.status = data.get('status', provider.status)
        provider.user.save()
        provider.save()
        response_data = {
            'service_provider': {
                'id': provider.id,
                'first_name': provider.user.first_name,
                'last_name': provider.user.last_name,
                'email': provider.user.email,
                'phone_number': provider.phone_number,
                'company_name': provider.company_name,
                'address': provider.user.address,
                'zip_code': provider.user.zipCode,
                'category': provider.category.name if provider.category else None,
                'subcategory': provider.subcategory.name if provider.subcategory else None,
                'number_of_people': provider.number_of_people,
                'status': provider.status,
                'date_joined': provider.user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': provider.user.is_active
            }
        }
        return JsonResponse(
        good_response(
        request.method,
        {'message': 'Service provider updated successfully', 'data': response_data},
        status=200))
    return JsonResponse(
    bad_response(
    request.method,
    {'error': 'Method not allowed'},
    status=405))

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
            zip_code = data.get('zip_code')
            service_providers = (
                ServiceProvider.objects
                .select_related('user', 'category', 'subcategory')
                .prefetch_related(
                    Prefetch('spprofile'),
                    Prefetch('reviews')
                )
                .annotate(average_rating=Avg('reviews__rating'))
            )
            if category_id:
                service_providers = service_providers.filter(category_id=category_id)
            if zip_code:
                service_providers = service_providers.filter(user__zipCode=zip_code)
            if not service_providers.exists():
                return JsonResponse({
                    "success": False,
                    "message": "No service providers found for the given filters."
                }, status=404)
            result = []
            for sp in service_providers:
                sp_profile = getattr(sp, 'spprofile', None)
                base_price = float(sp_profile.base_price) if sp_profile else 0.0
                profile_picture_url = sp_profile.profile_picture.url if sp_profile and sp_profile.profile_picture else None
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
                    "average_rating": sp.average_rating if sp.average_rating is not None else 0.0, 
                    "base_price": base_price,
                    "profile_picture": profile_picture_url
                    
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
            data = get_request_body(request)
            base_price = data.get('base_price')
            introduction = data.get('introduction')
            company_founded_date = data.get('company_founded_date')
            payment_methods = data.get('payment_methods')
            services_included = data.get('services_included', [])
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
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
                    "sp_id": service_provider_id,
                    "base_price": sp_profile.base_price,
                    "introduction": sp_profile.introduction,
                    "company_founded_date": sp_profile.company_founded_date.strftime('%Y-%m-%d'),
                    "payment_methods": sp_profile.payment_methods,
                    "services_included": [subcategory.name for subcategory in sp_profile.services_included.all()],
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
            customer_id=data.get('customer_id')
            category_id = data.get('category_id')
            subcategories_data = data.get('subcategories', [])  
            extra_services = data.get('extra_services', [])  
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            customer = Customer.objects.get(id=customer_id)
            category = Category.objects.get(id=category_id)
            sp_profile = SPProfile.objects.get(service_provider=service_provider)
            base_price = float(sp_profile.base_price)
            total_price = base_price
            included_services_ids = sp_profile.services_included.values_list('id', flat=True)
            additional_services = []
            subcategories_details = []
            for subcategory_data in subcategories_data:
                subcategory_id = subcategory_data.get('id')
                quantity = subcategory_data.get('quantity', 1)
                try:
                    subcategory = Subcategory.objects.get(id=subcategory_id)
                except Subcategory.DoesNotExist:
                    return JsonResponse(
                        bad_response(
                            request.method,
                            {"error": f"Subcategory with id {subcategory_id} not found"},
                            status=404
                        )
                    )
                individual_price = float(subcategory.additional_price)
                individual_total = individual_price * quantity
                if subcategory.id not in included_services_ids:
                    total_price += individual_total
                    additional_services.append(subcategory.name)
                else:
                    if quantity > 1:
                        total_price += individual_total
                subcategories_details.append({
                    "subcategory_name": subcategory.name,
                    "quantity": quantity,
                    "individual_price": individual_price,
                    "individual_total": individual_total
                })
            service_request = ServiceRequest.objects.create(
                service_provider=service_provider,
                customer=customer,
                category=category,
                total_price=total_price
            )
            service_request.subcategories.set(Subcategory.objects.filter(id__in=[sub['id'] for sub in subcategories_data]))
            email_subject_to_pro = "New Service Request from Customer"
            email_subject_to_customer = "Service Request Confirmation"
            accept_link = request.build_absolute_uri(reverse('accept_request', args=[service_request.id]))
            reject_link = request.build_absolute_uri(reverse('reject_request', args=[service_request.id]))  
            email_message_to_pro = render_to_string('emails/service_provider_email.html', {
            'service_provider_name': service_provider.user.name,
            'category_name': category.name,
            'customer_name': customer.user.name,
            'customer_zip_code': customer.user.zipCode,
            'customer_address': customer.user.address,
            'customer_phone_number': customer.phone_number,
            'customer_email': customer.user.email,
            'base_price': base_price,
            'subcategories_details': subcategories_details,
            'extra_services': extra_services,
            'total_price': total_price,
            'accept_link': accept_link,
            'reject_link': reject_link
        })
# Send email to service provider (PRO)
            send_mail(
                email_subject_to_pro,
                email_message_to_pro,
                'support@api.thefixit4u.com',  # From email (change as needed)
                [service_provider.user.email],  # To email (service provider's email)
                fail_silently=False,
                html_message=email_message_to_pro
            )
            # Prepare email content for customer
            email_message_to_customer = render_to_string('emails/customer_confirmation_email.html', {
            'customer_name': customer.user.name,
            'category_name': category.name,
            'service_provider_company_name': service_provider.company_name,
            'service_provider_name': service_provider.user.name,
            'service_provider_email': service_provider.user.email,
            'service_provider_phone_number': service_provider.phone_number,
            'subcategories_details': subcategories_details,
            'extra_services': extra_services,
            'total_price': total_price,
        })
            # Send email to customer
            send_mail(
                email_subject_to_customer,
                email_message_to_customer,
                'support@api.thefixit4u.com',  # From email (change as needed)
                [customer.user.email],  # To email (customer's email)
                fail_silently=False,
                html_message=email_message_to_customer
            )
            response_data = {
                "message": "Service request created successfully! Emails sent to service provider and customer.",
                "service_request": {
                    "id": service_request.id,
                    "service_provider_id": service_provider.id,
                    "service_provider_name": service_provider.user.name,
                    "service_provider_id": service_provider.company_name,
                    "category_id": category.id,
                    "category_name": category.name,  # Category name
                    "base_price": base_price,
                    "extra_services": subcategories_details,
                    # "extra_services": extra_services,  # Include extra services in the response
                    "grand_total": total_price,
                    "customer_details": {  # Include customer details in the response
                        "name": customer.user.name,
                        "zip_code": customer.user.zipCode,
                        "address": customer.user.address,
                        "phone_number": customer.phone_number,
                        "email": customer.user.email
                    }
                }
            }
            return JsonResponse(good_response(request.method, response_data, status=201))
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": "Service provider not found"},
                    status=404
                )
            )
        except Category.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": "Category not found"},
                    status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": str(e)},
                    status=500
                )
            )
    return JsonResponse(
        bad_response(
            request.method,
            {"error": "Method not allowed"},
            status=405
        )
    )
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
            # Get the uploaded profile picture
            profile_picture = request.FILES.get('profile_picture')
            if not profile_picture:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Profile picture not provided.'},
                        status=400
                    )
                )
            serviceProvider = ServiceProvider.objects.get(id=service_provider_id)
            try:
                spProfile = SPProfile.objects.get(service_provider=serviceProvider)
            except SPProfile.DoesNotExist:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Service Provider Profile not found.'},
                        status=404
                    )
                )
            file_extension = os.path.splitext(profile_picture.name)[1]
            if file_extension not in ['.jpg', '.jpeg', '.png', '.jfif']:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Invalid profile picture format. Only .jpg, .jpeg, .png are allowed.'},
                        status=400
                    )
                )
            if spProfile.profile_picture:
                spProfile.profile_picture.delete()
            new_file_name = f"{slugify(serviceProvider.user.username)}_profile_image{file_extension}"
            spProfile.profile_picture.save(new_file_name, profile_picture)
            spProfile.save()  # Save the profile changes
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "message": "Profile picture updated successfully!",
                        "profile_picture_url": spProfile.profile_picture.url
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
