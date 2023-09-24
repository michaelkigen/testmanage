'''from django.shortcuts import render
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

def index(request):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = '0797759614'
    amount = 1
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'https://darajambili.herokuapp.com/express-payment';
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)

def stk_push_callback(request):
        data = request.body
        
        return HttpResponse("STK Push in Django")'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .mpesa import sendSTK, check_payment_status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import PaymentTransaction
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from menu.views import CheckoutView , CartViewSet
from menu.models import Cart , Add_item_to_cart
from django.db.models import Sum
from Profile.models import Profile
from users.models import User
from rest_framework import generics, permissions
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from menu.models import Order
from cloudinary import uploader
import qrcode
from PIL import Image
from menu.views import CheckoutView
from users.emailer import Orderdfood_emailer
# Create your views here.

def QR_code_generator(data,order_id):
    Logo_link = 'templates/logo.png'
    logo = Image.open(Logo_link)
    # taking base width
    basewidth = 100
    # adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_L
    )
    QRcode.add_data(data)
    print('DATA ENCODED:', data)
    # generating QR code
    QRcode.make()
    # taking color name from user
    QRcolor = 'black'
    # adding color to QR code
    QRimg = QRcode.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')
    # set size of QR code
    # pos = ((QRimg.size[0] - logo.size[0]) // 2,
    #     (QRimg.size[1] - logo.size[1]) // 2)
    # QRimg.paste(logo, pos)
    # save the QR code generated
    qr_image_name = f"{order_id}.png"
                    # Save the QR code image with the desired name
    QRimg.save(qr_image_name)
    
    uploaded_image = uploader.upload(qr_image_name)
    order = Order.objects.filter(order_id = order_id).first()
    order.qrc_image = uploaded_image['url']
    order.save()
    print('QR code generated!')
    
class Redeem_points(APIView):
    permission_classes = [AllowAny, ]
    def post(self , request):
        user = self.request.user
        profile = Profile.objects.filter(user = user).first()
        points = profile.points
        
        cart = Cart.objects.filter(user=user).first()

        if cart is None:
            return Response({"detail": "Cart not found."}, status=HTTP_404_NOT_FOUND)

        total = sum([item.quantity * item.food.price for item in cart.cart_item.all()])
        print('the total amount is: ', total)
    
        if points < 40:
            return Response({'error':'your have not reached withdrawal limit'}) 
        
        shillings = points // 5
            
        if shillings < total:
            return Response({'error':'you have insufficient point to make this order'})
        rem_shillings = int(shillings) - total
        rem_points = rem_shillings * 5
        profile.points = rem_points
        profile.save()
        
        
        checkout_view = CheckoutView()
        order_id = checkout_view.post(request).data.get('order_id')
        
        data = {
            'user' : user,
            'order_id': order_id
        }
        print('THIS IS THE DATA ;',data)
        QR_code_generator(data,order_id)
        
        order = Order.objects.get(order_id=order_id)
        orderd_food = order.ordered_food.all()
        print('ORDERED FOOD TO THE EMAIL: ', orderd_food)
        ordered_food_list = []
        first_name = user.first_name
        last_name = user.last_name
        for ordered_food_item in orderd_food:
            food = ordered_food_item.food
            quantity = ordered_food_item.quantity
            ordered_food_list.append({
                'food_name': food.food_name,
                'quantity': quantity
            })

        Orderdfood_emailer(request, user.email, first_name, last_name, ordered_food_list)
        return Response({'message':'order made'})
    

class PaymentTranactionView(ListCreateAPIView):
    def post(self, request):
        return HttpResponse("OK", status=200)
    

class SubmitView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        phone_number = data.get('phone_number')
        user = self.request.user
        cart = Cart.objects.filter(user=user).first()

        if cart is None:
            # Handle the case where the user does not have a cart
            # Return an appropriate response or raise an exception
            # For example, you can return a 404 response:
            return Response({"detail": "Cart not found."}, status=HTTP_404_NOT_FOUND)

        total = sum([item.quantity * item.food.price for item in cart.cart_item.all()])
        amount = total
        print('the total amount is: ', amount)

        entity_id = 0
        if data.get('entity_id'):
            entity_id = data.get('entity_id')

        paybill_account_number = None
        if data.get('paybill_account_number'):
            paybill_account_number = data.get('paybill_account_number')

        trans = PaymentTransaction.objects.create()
        print('TRANSACTION INSTANCE :', trans)
        transaction_id = sendSTK(phone_number, amount, entity_id, transaction_id=trans)

        # b2c()
        
        
        message = {"status": "ok", "transaction_id": transaction_id}
        return Response(message, status=HTTP_200_OK)


class CheckTransactionOnline(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        trans_id = request.data['transaction_id']
        transaction = PaymentTransaction.objects.filter(trans_id=trans_id).first()

        try:
            if transaction and transaction.checkout_request_id:
                status_response = check_payment_status(transaction.checkout_request_id)
                status = status_response.get('status')
                print('STATUS: ', status)
                message = status_response.get('message')
                
                if status == True:
                    user = request.user
                    checkout_view = CheckoutView()
                    order_id = checkout_view.post(request).data.get('order_id')
                    print('ORDER_ID :', order_id)

                    transaction.order_id = order_id
                    transaction.is_finished = True
                    transaction.is_successful = True
                    transaction.user = user
                    transaction.message = message
                    transaction.save()
                    print('SAVED TRANSACTION :', transaction)
                    
                    # GENERATION OF QR CODE
                    
                   
                    data ={
                        "user" : user,
                        "checkout_id": transaction.checkout_request_id,
                        "transaction_id": transaction.trans_id,
                        "order_id":transaction.order_id
                    } 
                    # adding URL or text to QRcode
                    QR_code_generator(data,order_id)
                    
                   #handling  points  
                    amount = transaction.amount  
                    profile = Profile.objects.get(user=user) 
                    
               
                    if amount >= 10:
                        profile.points += 5  
                        profile.save()
                   #sending email
                    
                    order = Order.objects.get(order_id=order_id)
                    orderd_food = order.ordered_food.all()
                    print('ORDERED FOOD TO THE EMAIL: ', orderd_food)
                    ordered_food_list = []
                    first_name = user.first_name
                    last_name = user.last_name
                    for ordered_food_item in orderd_food:
                        food = ordered_food_item.food
                        quantity = ordered_food_item.quantity
                        ordered_food_list.append({
                            'food_name': food.food_name,
                            'quantity': quantity
                        })

                    Orderdfood_emailer(request, user.email, first_name, last_name, ordered_food_list)
                    
                    

                      
                    
                 # Pass the transaction as a list

                return JsonResponse(status_response, status=200)
            else:
                return JsonResponse({
                    "message": "Server Error. Transaction not found",
                    "status": False
                }, status=400)
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                "message": "Server Error. Transaction not found",
                "status": False
            }, status=400)




class CheckTransaction(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        trans_id = data['transaction_id']
        try:
            transaction = PaymentTransaction.objects.filter(id=trans_id).get()
            if transaction:
                return JsonResponse({
                    "message": "ok",
                    "finished": transaction.is_finished,
                    "successful": transaction.is_successful
                },
                    status=200)
            else:
                # TODO : Edit order if no transaction is found
                return JsonResponse({
                    "message": "Error. Transaction not found",
                    "status": False
                },
                    status=400)
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                "message": "Server Error. Transaction not found",
                "status": False
            },
                status=400)


class RetryTransaction(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        trans_id = request.data['transaction_id']
        try:
            transaction = PaymentTransaction.objects.filter(id=trans_id).get()
            if transaction and transaction.is_successful:
                return JsonResponse({
                    "message": "ok",
                    "finished": transaction.is_finished,
                    "successful": transaction.is_successful
                },
                    status=200)
            else:
                response = sendSTK(
                    phone_number=transaction.phone_number,
                    amount=transaction.amount,
                    orderId=transaction.order_id,
                    transaction_id=trans_id)
                return JsonResponse({
                    "message": "ok",
                    "transaction_id": response
                },
                    status=200)

        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                "message": "Error. Transaction not found",
                "status": False
            },
                status=400)


class ConfirmView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        # save the data
       # request_data = json.dumps(request.data)
        request_data = request.data
        print("the data  is: " , request_data)
        body = request_data
        print("the body is: ",body)
        
        resultcode = body.get('stkCallback').get('ResultCode')
        # Perform your processing here e.g. print it out...
        if resultcode == 0:
            print('Payment successful')
            requestId = body.get('stkCallback').get('CheckoutRequestID')
            metadata = body.get('stkCallback').get('CallbackMetadata').get('Item')
            for data in metadata:
                if data.get('Name') == "MpesaReceiptNumber":
                    receipt_number = data.get('Value')
            transaction = PaymentTransaction.objects.get(
                checkout_request_id=requestId)
            if transaction:
                transaction.receipt_number = receipt_number
                transaction.is_finished = True
                transaction.is_successful = True
                transaction.save()

        else:
            print('unsuccessfull')
            requestId = body.get('stkCallback').get('CheckoutRequestID')
            transaction = PaymentTransaction.objects.get(
                checkout_request_id=requestId)
            if transaction:
                transaction.is_finished = True
                transaction.is_successful = False
                transaction.save()

        # Prepare the response, assuming no errors have occurred. Any response
        # other than a 0 (zero) for the 'ResultCode' during Validation only means
        # an error occurred and the transaction is cancelled
        message = {
            "ResultCode": 0,
            "ResultDesc": "The service was accepted successfully",
            "ThirdPartyTransID": "1237867865"
        }

        # Send the response back to the server
        return Response(message, status=HTTP_200_OK)

    def get(self, request):
        return Response("Confirm callback", status=HTTP_200_OK)


class ValidateView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        # save the data
        request_data = request.data

        # Perform your processing here e.g. print it out...
        print("validate data" + request_data)

        # Prepare the response, assuming no errors have occurred. Any response
        # other than a 0 (zero) for the 'ResultCode' during Validation only means
        # an error occurred and the transaction is cancelled
        message = {
            "ResultCode": 0,
            "ResultDesc": "The service was accepted successfully",
            "ThirdPartyTransID": "1234567890"
        }

        # Send the response back to the server
        return Response(message, status=HTTP_200_OK)
    
    
class PaymentTransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PaymentTransaction.objects.filter(user=user)