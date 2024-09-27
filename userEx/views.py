from typing import Any
from django.shortcuts import render
import json
from django.http import JsonResponse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
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
                    'status': subcategory.status
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