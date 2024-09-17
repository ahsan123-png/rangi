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
            category_description = data.get("description", "")
            if not category_name:
                return JsonResponse({"error": "Category name is required"}, status=400)
            category = Category(name=category_name, description=category_description)
            category.save()
            return JsonResponse({
                "message": "Category added successfully",
                "category_id": category.id,
                "category_name": category.name,
                "category_description": category.description,
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
            if not subcategory_name:
                return JsonResponse({"error": "Subcategory name is required"}, status=400)
            if not category_id:
                return JsonResponse({"error": "Category ID is required"}, status=400)
            try:
                category = Category.objects.get(id=category_id)
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Category does not exist"}, status=400)
            subcategory = Subcategory(name=subcategory_name, description=subcategory_description, category=category)
            subcategory.save()
            return JsonResponse({
                "message": "Subcategory added successfully",
                "subcategory_id": subcategory.id,
                "subcategory_name": subcategory.name,
                "subcategory_description": subcategory.description,
                "category_id": subcategory.category.id,
                "category_name": subcategory.category.name,
            }, status=201)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)





















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