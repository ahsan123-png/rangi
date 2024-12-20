import json
from .models import *
from .serializers import *
from .views import *
from django.db.models import Avg
from django.db.models import Prefetch
from typing import Any
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
# Create your views here.
#=============== Add categories and sub-categories =============================
@csrf_exempt
def addCategory(request):
    if request.method == "POST":
        try:
            data = get_request_body(request)
            category_name = data.get("category_name")
            if not category_name:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Category name is required"},status=400 
                ))
            if Category.objects.filter(name=category_name).exists():
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Category already exists"}, status=400))
            category = Category(name=category_name)
            category.save()
            return JsonResponse({
                "message": "Category added successfully",
                "category_id": category.id,
                "category_name": category.name,
            }, status=201)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
# add subcategory to
@csrf_exempt
def addSubcategory(request):
    if request.method == "POST":
        try:
            data = get_request_body(request)
            subcategory_name = data.get("subcategory_name")
            subcategory_description = data.get("description", "")
            category_id = data.get("category_id")
            additional_price = data.get("additional_price", 0.00) 
            if not subcategory_name:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Subcategory name is required"}, status=400)
                )
            if not category_id:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Category id is required"}, status=400)
                )
            if not additional_price:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Additional price is required"}, status=400)
                )
            try:
                category = Category.objects.get(id=category_id)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Category does not exist"}, status=400)
            if Subcategory.objects.filter(name=subcategory_name).exists():
                return JsonResponse(
                    bad_response(
                        request.method,
                        {"error": "Category already exists"}, status=400))
            subcategory = Subcategory(name=subcategory_name, description=subcategory_description, category=category,additional_price=additional_price)
            subcategory.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {"message": "Subcategory added successfully",
                     "subcategory_id": subcategory.id,
                     "subcategory_name": subcategory.name,
                     "subcategory_description": subcategory.description,
                     "category_id": subcategory.category.id,
                     "category_name": subcategory.category.name,
                     "additional_price": additional_price},status=201)
                )
        except ValidationError as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": str(e)}, status=400)
                )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": str(e)}, status=500)
            )
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {"error": "Only POST requests are allowed"}, status=405)
    
        )
#===================== Category Cruds Operations =============================
#Get all categories
@csrf_exempt
def getCategories(request) -> JsonResponse:
    if request.method == 'GET':
        categories = Category.objects.all()
        result = []
        for category in categories:
            result.append({
                'id': category.id,
                'name': category.name
            })
        return JsonResponse(
            good_response(
                request.method,
                {"categories": result},status=200
            )
        )
    return JsonResponse({'error': 'Method not allowed'}, status=405)
# Get a single category
@csrf_exempt
def getCategory(request, category_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            category = Category.objects.get(id=category_id)
            provider_data = {
                'id': category.id,
                'name': category.name,
                'status': category.status,
            }
            return JsonResponse(
                good_response(request.method, 
                            {'category': provider_data}, status=200)
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(request.method, 
                             {'error': 'Category not found'}, status=404)
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(bad_response(request.method,
                                     {'error': 'Method not allowed'}, status=405))
# Update Category
@csrf_exempt
def updateCategory(request, category_id) -> JsonResponse:
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
        except ValueError:
            return JsonResponse(
                bad_response(
                    request.method, 
                             {'error': 'Invalid JSON'}, status=400)
                )
        try:
            category = Category.objects.get(id=category_id)
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                             {'error': 'Category not found'}, status=404)
            )
        category.name = data.get('name', category.name)
        category.status = data.get('status', category.status)
        category.save()
        return JsonResponse(
            good_response(request.method, 
                            {'message': 'Category updated successfully'}, status=200)
        )
    return JsonResponse(
        bad_response(request.method, 
                             {'error': 'Method not allowed'}, status=405)
    )
# Delete category
@csrf_exempt
def deleteCategory(request, category_id) -> JsonResponse:
    if request.method == 'DELETE':
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return JsonResponse(
                good_response(
                    request.method, 
                            {'message': 'Category deleted successfully'}, status=200)
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                             {'error': 'Category not found'}, status=404)
            )
    return JsonResponse(
        bad_response(request.method, 
                             {'error': 'Method not allowed'}, status=405)
    )

#===================== Subcategory Cruds Operations =============================
@csrf_exempt
def getSubcategories(request) -> JsonResponse:
    if request.method == 'GET':
        subcategories = Subcategory.objects.all()
        result = []
        for subcategory in subcategories:
            result.append({
                'main_category_id': subcategory.category.id,
                'main_category_name': subcategory.category.name,
                'subcategory_id': subcategory.id,
                'subcategory_name': subcategory.name,
                'description': subcategory.description,
                'additional_price': subcategory.additional_price,
            })
        return JsonResponse(result, safe=False, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
# Get Category
@csrf_exempt
def getSubCategory(request, category_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            subcategory = Subcategory.objects.get(id=category_id)
            provider_data = {
                'id': subcategory.id,
                'name': subcategory.name,
                'description': subcategory.description,
                'category': {
                    'id': subcategory.category.id,  # Assuming category is a ForeignKey
                    'name': subcategory.category.name  # Adjust attributes as needed
                },
            }
            return JsonResponse(
                good_response(request.method, 
                            {'subcategory': provider_data}, status=200)
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(request.method, 
                             {'error': 'Category not found'}, status=404)
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(bad_response(request.method,
                                     {'error': 'Method not allowed'}, status=405))
#update sub category with id
@csrf_exempt
def updateSubcategory(request, subcategory_id) -> JsonResponse:
    if request.method == 'PATCH':
        try:
            data = get_request_body(request)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            subcategory = Subcategory.objects.get(id=subcategory_id)
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                             {'error': 'Subcategory not found'}, status=404)
                )
        subcategory.name = data.get('name', subcategory.name)
        subcategory.description = data.get('description', subcategory.description)
        category_id = data.get('category', subcategory.category.id)
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                subcategory.category = category
            except ObjectDoesNotExist:
                return JsonResponse(
                    bad_response(
                        request.method, 
                                 {'error': 'Category not found'}, status=404)
                )
        subcategory.save()
        return JsonResponse(
            good_response(request.method, 
                            {'message': 'Subcategory updated successfully'}, status=200)
        )
    return JsonResponse(
        bad_response(request.method, 
                             {'error': 'Method not allowed'}, status=405)
    )
# Delete subcategory
@csrf_exempt
def deleteSubCategory(request, category_id) -> JsonResponse:
    if request.method == 'DELETE':
        try:
            category = Subcategory.objects.get(id=category_id)
            category.delete()
            return JsonResponse(
                good_response(
                    request.method, 
                            {'message': 'Category deleted successfully'}, status=200)
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method, 
                             {'error': 'Category not found'}, status=404)
            )
    return JsonResponse(
        bad_response(request.method, 
                             {'error': 'Method not allowed'}, status=405)
    )
#======================== subcategory by category name =================
@csrf_exempt
def getSubcategoriesByCategory(request, category_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            category = Category.objects.get(id=category_id)
            subcategories = category.subcategories.all()
            result = []
            for subcategory in subcategories:
                result.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'description': subcategory.description,
                    'additional_price': subcategory.additional_price,
                    
                })
            return JsonResponse(
                good_response(request.method, 
                {'subcategories': result},
                status=200)
            )
        except ObjectDoesNotExist:
            return JsonResponse(
                bad_response(request.method, 
                {'error': 'Category not found'},
                status=404)
            )
        except Exception as e:
            return JsonResponse(
            bad_response(
                request.method,
                {'error': str(e)},
                status=500
            ))
    return JsonResponse(
        bad_response(
            request.method, 
            {'error': 'Method not allowed'},
            status=405)
    )
# ======================== Contact us =================
@csrf_exempt
def contactView(request):
    if request.method == 'POST':
        data= get_request_body(request)
        name=data.get('name' , None)
        phone=data.get('phone' , None)
        email=data.get('email' , None)
        subject=data.get('subject' , None)
        message=data.get('message' , None)
        if not name and (phone or email) and subject and message:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"error": "All fields are required"},
                    status=400,
                )
            )
        if phone:
            phone=clean_phone_number(phone)
        contact = ContactUs(name=name, phone=phone, email=email, subject=subject, message=message)
        contact.save()
        return JsonResponse(
            good_response(
                request.method,
                {"message": "Your message has been sent successfully",
                 "contact_id": contact.id,
                 "name": name,
                 "phone": phone,
                 "email": email,
                 "subject": subject,
                 "message": message},
                status=200,))
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {"error": "Only POST requests are allowed"},
                status=405,
            )
        )
#============ get all contacts ==============
@csrf_exempt
def getAllContacts(request):
    if request.method == 'GET':
        try:
            contacts = ContactUs.objects.only('id', 'name', 'phone', 'email', 'subject', 'message').all()
            # Prepare response
            result = [
                {
                    'contact_id': contact.id,
                    'name': contact.name,
                    'phone': contact.phone,
                    'email': contact.email,
                    'subject': contact.subject,
                    'message': contact.message,
                }
                for contact in contacts
            ]
            return JsonResponse(
                good_response(
                    request.method,
                    {"contacts": result},
                    status=200
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
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {'error': 'Method not allowed'},
                status=405
            )
        )
#============ get by id =================
@csrf_exempt
def getContactById(request, contact_id):
    if request.method == 'GET':
        try:
            contact = ContactUs.objects.only('id', 'name', 'phone', 'email', 'subject', 'message').get(id=contact_id)
            contact_data = {
                'id': contact.id,
                'name': contact.name,
                'phone': contact.phone,
                'email': contact.email,
                'subject': contact.subject,
                'message': contact.message,
            }
            return JsonResponse(
                good_response(
                    request.method,
                    {'contact': contact_data},
                    status=200
                )
            )
        except ContactUs.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Contact not found'},
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
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {'error': 'Method not allowed'},
                status=405
            )
        )

# ================== Activation =================

User = get_user_model()

@csrf_exempt
def activate_user(request, uidb64, token) -> JsonResponse:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return JsonResponse(
                {'message': 'Account activated successfully'}, status=200)
        else:
            return JsonResponse(
                {'error': 'Invalid token or token expired'}, status=400)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse(
            {'error': 'Invalid activation link'}, status=400)

# accept request and reject request of service
@csrf_exempt
def accept_request(request, request_id):
    if request.method  == 'GET':
        try:
            service_request = get_object_or_404(ServiceRequest, id=request_id)
            if service_request.customer is None or service_request.service_provider is None:
                return JsonResponse({"error": "Customer or Service Provider is missing."}, status=400)
            service_request.status = 'Accepted'
            service_request.save()

            # Send email to customer
            customer_email = service_request.customer.user.email
            customer_name = service_request.customer.user.name
            service_provider_name = service_request.service_provider.user.name
            email_subject = "Service Request Accepted"
            email_message = f"""
            Dear {customer_name},

            Congratulations! Your service provider {service_provider_name} has accepted your request for the service: {service_request.category.name}.

            Please contact your service provider for further details.

            Regards,
            TheFixIt4U Team
            """
            send_mail(
                email_subject,
                email_message,
                'support@api.thefixit4u.com',
                [customer_email],
                fail_silently=False,
            )
            return HttpResponse(status=200)  # Success
        except Exception as e:
                return HttpResponse(status=500)  # Internal server error
    else:
        return HttpResponse(status=405)  # Method not allowed
# === reject request ===
@csrf_exempt
def reject_request(request, request_id):
    if request.method == "GET":
        try:
            service_request = get_object_or_404(ServiceRequest, id=request_id)
            service_request.status = 'Rejected'
            service_request.save()
            # Send email to customer
            customer_email = service_request.customer.user.email
            customer_name = service_request.customer.user.name
            service_provider_name = service_request.service_provider.user.name
            email_subject = "Service Request Rejected"
            email_message = f"""
            Dear {customer_name},

            Unfortunately, your service provider {service_provider_name} is unavailable and has rejected your request for the service: {service_request.category.name}.

            We apologize for the inconvenience.

            Regards,
            TheFixIt4U Team
            """
            send_mail(
                email_subject,
                email_message,
                'support@api.thefixit4u.com',
                [customer_email],
                fail_silently=False,
            )
            return HttpResponse(status=200)  # Success
        except Exception as e:
            return HttpResponse(status=500)  # Internal server error
    else:
        return HttpResponse(status=405)  # Method not allowed

# ====================== get all service provider by category id  ============
@csrf_exempt
def getServiceProvidersByCategory(request, category_id):
    if request.method == "GET":
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        service_providers = (
            ServiceProvider.objects
            .filter(category=category)
            .select_related('user', 'category', 'subcategory')
            .prefetch_related(
                Prefetch('spprofile'),
                Prefetch('reviews')
            )
            .annotate(average_rating=Avg('reviews__rating'))
        )
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
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)











# some useful tools and functions

def get_request_body(request):
    return json.loads(request.body)


def good_response(method: str, data: dict | Any, status: int = 200):
    return {
        "success": True,
        "data": data,
        "method": method,
        "status": status,
    }


def bad_response(method: str, reason: str, status: int = 403, data: dict | Any = None):
    return {
        "success": False,
        "reason": reason,
        "data": data,
        "status": status,
        "method": method,
    }
def clean_phone_number(phone_number):
    if phone_number.__contains__("+"):
        phone_number = phone_number.replace("+", "")
    if phone_number.__contains__(" "):
        phone_number = phone_number.replace(" ", "")
    if phone_number.__contains__("-"):
        phone_number = phone_number.replace("-", "")
    return phone_number


def delete_all_users():
    id_to_ignore = 1
    for item in models.UserEx.objects.all():
        if item.id == id_to_ignore:
            continue
        item.delete()