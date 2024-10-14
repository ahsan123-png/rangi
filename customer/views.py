import os
import re
from userEx.models import *
from userEx.serializers import *
from userEx.views import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Q
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.middleware.csrf import get_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail
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
         # Generate the CSRF token
        csrf_token = get_token(request)
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
        if UserEx.objects.filter(Q(username=username) | Q(email=email)).exists():
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'email already taken try another account'}, 
                    status=409
                )
            )
        if Customer.objects.filter(phone_number=phone_number).exists():
            return JsonResponse(
                bad_response(
                    request.method,
                    {'error': 'Phone number already exists'}, 
                    status=409
                )
            )
        try:
            user = UserEx.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            name=name)
            user.isCustomer = True
            user.is_active = False
            user.address = address
            user.zipCode = zip_code
            user.save()
            customer = Customer(user=user, phone_number=phone_number)
            customer.save()
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
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        'message': 'Service provider registered successfully. Please confirm your email to activate the account.',
                        'id': customer.id,
                        'username': username,
                        'email': email,
                        'phone_number': phone_number,
                        'address': address,
                        'zip_code': zip_code,
                        'csrf_token': csrf_token
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
        customers = Customer.objects.select_related('user').all()
        result = [
            {
                'id': customer.id,
                'username': customer.user.username,
                'email': customer.user.email,
                'phone_number': customer.phone_number,
                'address': customer.user.address,
                'zip_code': customer.user.zipCode,
                'profile_picture_url': customer.profile_picture.url if customer.profile_picture else None
            }
            for customer in customers
        ]
        return JsonResponse(
            good_response(
                request.method,
                {
                    'message': 'All customers fetched successfully',
                    'customers': result
                },
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
# get customers
def getCustomer(request, customer_id) -> JsonResponse:
    if request.method == 'GET':
        try:
            customer = Customer.objects.select_related('user').get(id=customer_id)
            customer_data = {
                'id': customer.id,
                'username': customer.user.username,
                'email': customer.user.email,
                'phone_number': customer.phone_number,
                'address': customer.user.address,
                'zip_code': customer.user.zipCode,
                'profile_picture_url': customer.profile_picture.url if customer.profile_picture else None
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
@csrf_exempt
def updateCustomer(request, customer_id) -> JsonResponse:
    if request.method == 'PATCH':
        try:
            customer = Customer.objects.get(id=customer_id)
            data = get_request_body(request)
            new_email = data.get('email')
            new_phone_number = data.get('phone_number')
            if new_email:
                if UserEx.objects.filter(email=new_email).exclude(id=customer.user.id).exists():
                    return JsonResponse(
                bad_response(
                request.method,
                {'error': 'Email is already taken, try another.'},
                status=400))
                customer.user.email = new_email
            if new_phone_number:
                if Customer.objects.filter(phone_number=new_phone_number).exclude(id=customer.id).exists():
                    return JsonResponse(
                bad_response(
                request.method,
                {'error': 'Phone number is already taken, try another.'}, status=400))
                customer.phone_number = new_phone_number
            customer.user.first_name = data.get('first_name', customer.user.first_name)
            customer.user.last_name = data.get('last_name', customer.user.last_name)
            customer.user.address = data.get('address', customer.user.address)
            customer.user.zipCode = data.get('zip_code', customer.user.zipCode)
            customer.user.save()
            customer.save()
            return JsonResponse(
        good_response(
        request.method,
        {'customer': {'id': customer.id, 'username': customer.user.username, 'email': customer.user.email, 'phone_number': customer.phone_number, 'address': customer.user.address, 'zip_code': customer.user.zipCode}}, status=200))
        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                request.method,
                {'error': 'Customer not found'},
                status=404))
        except Exception as e:
            return JsonResponse(
                    bad_response(
                    request.method,
                    {'error': str(e)},
                    status=500))
    return JsonResponse(
        bad_response(
        request.method,
        {'error': 'Method not allowed'},
        status=405))

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
#================= Review Operations =============================
#================= Add a Review to Service provider ==================

@csrf_exempt
def addReview(request) -> JsonResponse:
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer_id')
            service_provider_id = request.POST.get('service_provider_id')
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment')
            if not (1 <= rating <= 5):
                return JsonResponse({
                    "success": False,
                    "error": "Rating must be between 1 and 5 stars."
                }, status=400)
            customer = Customer.objects.get(id=customer_id)
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            review = Review.objects.create(
                customer=customer,
                service_provider=service_provider,
                rating=rating,
                comment=comment
            )
            images = request.FILES.getlist('images')  # Get list of images from the request
            for image in images:
                image_path = default_storage.save(f'review_images/{image.name}', image)
                ReviewImage.objects.create(review=review, image=image_path)
            return JsonResponse(
                good_response(
                    request.method,
                    {
                "success": True,
                "message": "Review added successfully!",
                "review": {
                    "rating": review.rating,
                    "comment": review.comment,
                    "timestamp": review.timestamp,
                    "images": [image.image.url for image in review.images.all()]  # Return image URLs
                }
            }, status=201
                )
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                "success": False,
                "error": "Service provider not found."
            }, status=404
                )
            )
        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                "success": False,
                "error": "Customer not found."
            }, status=404
                )
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {
                "success": False,
                "error": str(e)
            }, status=500
                )
            )
# Retrieve All Reviews for a Service Provider
@csrf_exempt
def getReviewsByServiceProvider(request, service_provider_id):
    if request.method == 'GET':
        try:
            service_provider = ServiceProvider.objects.get(id=service_provider_id)
            reviews = Review.objects.filter(service_provider=service_provider).select_related('customer')
            review_data = []
            for review in reviews:
                review_data.append({
                    "id": review.id,
                    'customer': review.customer.user.username,
                    'rating': review.rating,
                    'comment': review.comment,
                    'timestamp': review.timestamp,
                    'images': [image.image.url for image in review.images.all()]
                })
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "reviews": review_data
                    }
                ), status=200
            )
        except ServiceProvider.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": "Service provider not found."}
                ), status=404
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": str(e)}
                ), status=500
            )
    return JsonResponse(
        bad_response(
            request.method,
            {"success": False, "error": "Method not allowed."}, status=405
        )
    )
# Update a Review
@csrf_exempt
def updateReview(request, review_id):
    if request.method == 'PATCH':
        try:
            review = Review.objects.get(id=review_id)
            data = get_request_body(request)
            rating = data.get('rating')
            if rating is not None:
                rating = int(rating)
                if not (1 <= rating <= 5):
                    return JsonResponse(
                        bad_response(
                            request.method,
                            {"success": False, "error": "Rating must be between 1 and 5."}
                        ), status=400
                    )
                review.rating = rating
            review.comment = data.get('comment', review.comment)
            review.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "message": "Review updated successfully!",
                        "review": {
                            "rating": review.rating,
                            "comment": review.comment,
                            "timestamp": review.timestamp
                        }
                    }
                ), status=200
            )
        except Review.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": "Review not found."}
                ), status=404
            )
        except ValueError:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": "Invalid rating value. Rating must be an integer."}
                ), status=400
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": str(e)}
                ), status=500
            )
    return JsonResponse(
        bad_response(
            request.method,
            {"success": False, "error": "Method not allowed."}, status=405
        )
    )

# Delete a Review
@csrf_exempt
def deleteReview(request, review_id):
    if request.method == 'DELETE':
        try:
            review = Review.objects.get(id=review_id)
            review.delete()
            return JsonResponse(
                good_response(
                    request.method,
                    {"success": True, "message": "Review deleted successfully!"}
                ), status=200
            )
        except Review.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": "Review not found."}
                ), status=404
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": str(e)}
                ), status=500
            )
    return JsonResponse(
        bad_response(
            request.method,
            {"success": False, "error": "Method not allowed."}, status=405
        )
    )
#============ add profile picture =================
@csrf_exempt
def addProfilePicture(request, customer_id):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=customer_id)
            profile_picture = request.FILES.get('profile_picture')
            if not profile_picture:
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Profile picture not provided.'},
                        status=400
                    )
                )
            allowed_extensions = ['.jpg', '.jpeg', '.png' , 'jfif']
            if not profile_picture.name.endswith(tuple(allowed_extensions)):
                return JsonResponse(
                    bad_response(
                        request.method,
                        {'success': False, 'error': 'Invalid profile picture format. Only JPEG, JPG, and PNG files are allowed.'},
                        status=400
                    )
                )
            #delete profile picture if it exists save new profile picture
            if customer.profile_picture:
                default_storage.delete(customer.profile_picture.name)
            fileExtension = os.path.splitext(profile_picture.name)[1] 
            newFileName = f"{slugify(customer.user.username)}_profile_image{fileExtension}" 
            customer.profile_picture.save(newFileName, profile_picture)
            customer.save()
            return JsonResponse(
                good_response(
                    request.method,
                    {
                        "success": True,
                        "message": "Profile picture added successfully!",
                        "profile_picture_url": customer.profile_picture.url
                    }
                ), status=201
            )
        except Customer.DoesNotExist:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": "Customer not found."}
                ), status=404
            )
        except Exception as e:
            return JsonResponse(
                bad_response(
                    request.method,
                    {"success": False, "error": str(e)}
                ), status=500
            )
    else:
        return JsonResponse(
            bad_response(
                request.method,
                {"success": False, "error": "Method not allowed."}, status=405
            )
        )
