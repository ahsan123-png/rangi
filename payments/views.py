from django.shortcuts import render
import json
import os
import re
from userEx.views import *
from userEx.models import *
from userEx.serializers import *
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
#============== view =====================
@csrf_exempt
def addSubscriptionPlan(request):
    if request.method == 'POST':
        data = get_request_body(request)
        plan_id = data.get('plan_id')
        customer_id = data.get('customer_id')
        pro_id = data.get('pro_id')
        duration = data.get('duration')
        if not plan_id or not duration:
            return JsonResponse({"error": "Both plan_id and duration (monthly/yearly) are required."}, status=404)
        if duration not in ['monthly', 'yearly']:
            return JsonResponse({"error": "Invalid duration. It must be 'monthly' or 'yearly'."}, status=400)
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({"error": "Subscription plan not found."}, status=404)
        user = None
        price = plan.price
        if duration=="yearly":
            price = plan.price * 12
            # 5%discount
            # price =  price * 0.05
        if customer_id:
            try:
                user = Customer.objects.get(id=customer_id).user
            except Customer.DoesNotExist:
                return JsonResponse({"error": "Customer not found."}, status=404)
            if plan_id in [4, 5, 6]:
                return JsonResponse({"error": "Customers cannot subscribe to service provider plans."}, status=400)    
        elif pro_id:
            try:
                user = ServiceProvider.objects.get(id=pro_id).user
            except ServiceProvider.DoesNotExist:
                return JsonResponse({"error": "Pro not found."}, status=404)
            if plan_id in [1, 2, 3]:
                return JsonResponse({"error": "Service providers cannot subscribe to customer plans."}, status=400)
        else:
            return JsonResponse({"error": "Either customer_id or pro_id is required."}, status=400)
        if UserSubscription.objects.filter(user=user, plan=plan).exists():
            return JsonResponse({"error": "User is already subscribed to this plan."}, status=400)
        start_date = timezone.now()
        if duration == 'monthly':
            end_date = start_date + timedelta(days=30)
        elif duration == 'yearly':
            end_date = start_date + timedelta(days=365)
        user_subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            start_date=start_date,
            end_date=end_date
        )
        user_subscription.save()
        return JsonResponse({
            "message": "Subscription added successfully.",
            "user_id": user.id,
            "user": user.username,
            "plan": plan.name,
            "duration": duration,
            "price": price,
            "start_date": start_date,
            "end_date": end_date
        }, status=201)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
# ================= Check Subscription Method ===================

def check_subscription_status(request):
    user = request.user
    try:
        subscription = UserSubscription.objects.filter(user=user).latest('start_date')
        if subscription.end_date > timezone.now():
            return JsonResponse({
                'is_active': True,
                'plan_name': subscription.plan.name,
                'end_date': subscription.end_date
            })
        else:
            return JsonResponse({'is_active': False, 'message': 'Subscription expired'})
    except UserSubscription.DoesNotExist:
        return JsonResponse({'is_active': False, 'message': 'No active subscription'})
# ================ Cancel subscription =============================
def cancel_subscription(request):
    user = request.user
    try:
        subscription = UserSubscription.objects.filter(user=user).latest('start_date')
        if subscription.end_date > timezone.now():
            subscription.end_date = timezone.now()  # Cancel immediately
            subscription.save()
            user.is_subscribed = False
            user.save()
            return JsonResponse({'message': 'Subscription canceled'})
        else:
            return JsonResponse({'error': 'No active subscription to cancel'})
    except UserSubscription.DoesNotExist:
        return JsonResponse({'error': 'No active subscription'})
# ==================== Get all plains ====================================
def list_subscription_plans(request):
    plan_type = request.GET.get('plan_type')  # 'customer' or 'service_provider'
    if plan_type not in ['customer', 'service_provider']:
        return JsonResponse({'error': 'Invalid plan type'}, status=400)
    
    plans = SubscriptionPlan.objects.filter(plan_type=plan_type)
    plan_list = [{
        'id': plan.id,
        'name': plan.name,
        'description': plan.description,
        'price': plan.price,
        'duration': plan.duration,
        'tier': plan.tier
    } for plan in plans]
    
    return JsonResponse(plan_list)
