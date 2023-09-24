from rest_framework import serializers
from rest_framework.validators import ValidationError
from .models import User,Verifications
from django.contrib.auth.hashers import make_password
from .emailer import send_Verification_Email

class Verification_serializer(serializers.ModelSerializer):
    class Meta:
        model = Verifications
        fields = [ 'verification_code']
        
        
class Reset_PasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length = 20)
    new_password = serializers.CharField(max_length = 20)
    code      = serializers.CharField(max_length = 4)

class PhoneNumberCheckerSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        error_messages={
            'unique': 'The phone number already exists. Email: %(email)s'
        }
    )

    class Meta:
        model = User
        fields = ['phone_number']

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        existing_user = User.objects.filter(phone_number=phone_number).first()

        if existing_user:
            raise serializers.ValidationError(
                
                {'email': existing_user.email,
                 'message': 'phone number already exists'
                 }
            )

        return attrs

class UserSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'email', 'first_name', 'last_name','password', 'verification_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        verification_code = validated_data.pop('verification_code')
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        # Additional code for verification and saving the verification code
        Verifications.objects.create(email=user.email, verification_code=verification_code)
        return user
        

class UserLoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15,min_length = 4)
    class Meta:
        model = User
        fields = ['phone_number', 'password']
        
class Change_password_Serializer(serializers.Serializer):
    old_password = serializers.CharField(max_length = 20)
    new_password = serializers.CharField(max_length = 20)
    confirm_password = serializers.CharField(max_length = 20)
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        if new_password != confirm_password:
            raise ValidationError('passwords do not match')
        return super().validate(attrs)
    