from datetime import datetime
from .serializers import UserSerializer, UserLoginSerializer, PhoneNumberCheckerSerializer , Change_password_Serializer ,Verification_serializer,Reset_PasswordSerializer,UserDetailedSerializer
from .models import User, Verifications
from .emailer import generate_verification_code 


from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password , make_password
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,viewsets
#from rest_framework.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import RefreshToken
from .models import TokenBlacklist

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class PasswordChecker(APIView):
    def post(self , request):
        password = request.data.get('password')
        user = self.request.user
        matchcheck= check_password(password, user.password)
        if not matchcheck :
            return Response({'error':'you enterd a wrong password'},status= status.HTTP_400_BAD_REQUEST)
        return Response({'message':'correct password'}, status= status.HTTP_202_ACCEPTED)
        


class SendVerificationCode(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        print(phone_number)

        # Validate input parameters

        try:
            # Check if a verification record already exists for the phone number
            verification_record = Verifications.objects.get(phone_number=phone_number)
            verification_record.delete()
        except Verifications.DoesNotExist:
            pass  # No existing record, proceed

        verification_code = generate_verification_code()
        print(verification_code)

        # Save verification code to the database
        verifications = Verifications.objects.create(
            phone_number=phone_number,
            verification_code=verification_code,
            verification_code_sent=datetime.now(timezone.utc)
        )
        print('code saved')

        # Send SMS using Twilio
        try:
            print('step 1')
            account_sid = "AC94d634c48c7f12dfb8f6af8f0b1614c2"
            auth_token = "98636a4a87699fd0951f2c06ddd3a21f"
            client = Client(account_sid, auth_token)
            print('step 2')
            message = client.messages.create(
                body=f"Your Verification code is {verification_code}.",
                from_='+13343842451',
                to=phone_number
            )
            print('step 3')
        except TwilioRestException as e:
            print(f"Twilio error: {e}")
            # Handle the exception or return an error response
            error_message = str(e.msg) if e.msg else 'Failed to send the SMS. Please try again later.'

            
            return Response({'error': error_message, 'status': e.code, 'code':verification_code }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Verification code has been sent', 'verification_code': verification_code})


class Verify_Code(APIView):
    def post(self, request):
        serializer = Verification_serializer(data= request.data)
        phone_number = serializer.data.get('phone_number')
        verfication_code = serializer.data.get('verification_code')
        verify = Verifications.objects.filter(phone_number = phone_number)
        if verify is None:
            return Response({'message':'code not found'})
        
        if verify.verification_code != verfication_code:
            return Response({'message': 'invalid code'},
                            status=status.HTTP_400_BAD_REQUEST)
            
        sent_time = verify.verification_code_sent
        current_time = datetime.now(timezone.utc)
        delta = current_time - sent_time
        
        if abs(delta.total_seconds()) > 60:
            Verifications.objects.filter(phone_number = phone_number).delete()
            return Response({'message': 'Verification code has expired. Please request a new code.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        verify.delete()    
        return True
               
        
class Delete_code_db(APIView):
    def post( self , request):
        phone_number = request.data.get('phone_number')
        Verifications.objects.filter(phone_number = phone_number).delete()
        return Response({'message':'verification deleted'}, status= status.HTTP_200_OK)

class CheckTokenView(APIView):
    parser_classes = [IsAuthenticated]
    def get(self, request):
        return Response({'message': 'Token is valid'}, status=status.HTTP_200_OK)

class TokenRefreshView(APIView):
    authentication_classes =  [IsAuthenticated]
    def post(self, request):
        # refresh_token = request.COOKIES.get('refresh_token')

        # if not refresh_token:
        #     return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token = request.COOKIES.get('refresh_token')
            refresh = RefreshToken(str(refresh_token))
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    
    refresh['email'] = user.email
    refresh['first_name'] = user.first_name
    refresh['last_name'] = user.last_name
    refresh['phone_number'] = user.phone_number
    refresh['is_admin'] = user.is_admin
    refresh['is_staff'] = user.is_staff
    refresh['is_ccare'] = user.is_ccare
    return refresh 

class User_registration(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        verification_code = request.data.get('verification_code')
        phone_number = request.data.get('phone_number')
        

        try:
            verification = Verifications.objects.get(phone_number=phone_number)
            print(f' the V code is:{verification.verification_code}')
            if verification_code != verification.verification_code:
                return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    
        except Verifications.DoesNotExist:
            return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        sent_time = verification.verification_code_sent
        current_time = datetime.now(timezone.utc)
        delta = current_time - sent_time
        if abs(delta.total_seconds()) > 60:
            Verifications.objects.filter(phone_number = phone_number).delete()
            return Response({'message': 'Verification code has expired. Please request a new code.'},
                            status=status.HTTP_400_BAD_REQUEST)
     
        user = serializer.save()
        user.is_verified = True
        user.save()
        Verifications.objects.filter(phone_number = phone_number).delete()
        

        token = get_tokens_for_user(user)
        refresh_token = str(token)
        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'data': serializer.data,
            'access_token': str(token.access_token),
            'message': 'Registered successfully'
        }
        return response
    
    def get(self, request):
        user = User.objects.all()
        serializer = UserDetailedSerializer(user,many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailedSerializer(user)
        return Response(serializer.data ,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailedSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserDetailedSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)



class Login_View(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = str(serializer.data.get('phone_number'))
        password = str(serializer.data.get('password'))

        user = authenticate(request, phone_number=phone_number, password=password)
        
        if user is None:
            return Response({'errors': {'non_field_errors': ['phone_number or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

        # Ensure authentication was successful before proceeding
        if user.is_authenticated:
            details = User.objects.get(phone_number=phone_number)
            token = get_tokens_for_user(user)
            access_token = str(token.access_token)

            response = Response()
            response.set_cookie(key='refresh_token', value=token, httponly=True)
            response.data = {
                'phone': str(phone_number),
                'email': str(details.email),
                'name': str(details.first_name),
                'access_token': str(access_token),
                'msg': 'Logged in Successfully'
            }
            return response
        else:
            return Response({'errors': {'non_field_errors': ['Authentication failed']}}, status=status.HTTP_401_UNAUTHORIZED)

    


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            access_token = request.data.get('access_token')

            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()

                # Blacklist the access token by adding it to the TokenBlacklist model
                if access_token:
                    token_blacklist, _ = TokenBlacklist.objects.get_or_create(token=access_token)
                    token_blacklist.save()

                response = Response({'detail': 'Logout successful'})
                response.delete_cookie('refresh_token')
                return response
            else:
                return Response({'detail': 'No refresh token found'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

class PhoneNumberCheckerView(APIView):
    serializer_class = PhoneNumberCheckerSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception= True):
            return Response({'message': 'Phone number unregisterd.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
class Change_password_View(APIView):
    
    def post(self,request,format= None):
        serializer = Change_password_Serializer(data= request.data)
        serializer.is_valid(raise_exception=True)   
        user = request.user
        password = user.password
        old_password = serializer.data.get('old_password')
        confirm = check_password( old_password ,password)
        if confirm == False:
            return Response({'message':'enter correct old password'}, status=status.HTTP_400_BAD_REQUEST)
        new_password = serializer.data.get('new_password')
        user.set_password(new_password)
        user.save()
        return Response({'message':'password changed'}, status=status.HTTP_200_OK)
        
class RestetPassword_View(APIView):
    def post(self ,request , format = None):
        serializer =  Reset_PasswordSerializer(data= request.data)
        serializer.is_valid(raise_exception= True)
        phone_number = serializer.data.get('phone_number')
        new_password = serializer.data.get('new_password')
        
        user = User.objects.filter(phone_number = phone_number ).first()
        
        if user is None:
            return Response({'message':'account with this number does not exist'}, status= status.HTTP_400_BAD_REQUEST)
        
        
        email = user.email
        code = serializer.data.get('code')
        try:
            verification = Verifications.objects.get(email=email)
            print(f' the V code is:{verification.verification_code}')
            if code != verification.verification_code:
                return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    
        except Verifications.DoesNotExist:
            return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
            
        sent_time = verification.verification_code_sent
        current_time = datetime.now(timezone.utc)
        delta = current_time - sent_time
        
        if abs(delta.total_seconds()) > 120:
            Verifications.objects.filter(email = email).delete()
            return Response({'message': 'Verification code has expired. Please request a new code.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        verification.delete() 
        user.set_password(new_password) 
        user.save()  
        return Response({'message': 'password updated'},
                            status=status.HTTP_200_OK)
