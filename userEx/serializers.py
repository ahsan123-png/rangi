from .models import *
from rest_framework import serializers
class UserExSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEx
        fields = ['username',
                 'password',
                 'isServiceProvider',
                 'isCustomer',
                 'address',
                 'zipCode',
                 'name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = UserEx.objects.create_user(**validated_data)
        return user
    
    class ServiceProviderSerializer(serializers.ModelSerializer):
        class Meta:
            model = ServiceProvider
            fields = ['user',
             'company_name',
             'phone_number',
             'category',
             'subcategory',
             'number_of_people',
             'status']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['user', 
                'phone_number']