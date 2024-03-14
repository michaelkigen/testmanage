from django.shortcuts import render

from rest_framework import status,viewsets,views,mixins,generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# from rest_framework.authentication import JSONWebTokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OrderedFoodSerializer,Menu_ObjectSerializer, CartSerializer,OrderIdSerializer, CategorySerializer,Update_cart_serializer,AddCartItemSerializer,Create_Cart_Serializer,ViewCartItemserializer,Order_Serializer
from .models import Menu_Object,Categories,Cart,Add_item_to_cart,Order,Orderd_Food
from .filters import Foodfilter
from Profile.models import Profile

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils.timezone import timezone

import cloudinary
from cloudinary import api
from django.conf import settings

from records.views import recorder
import cloudinary.uploader
from rest_framework.decorators import action
from mpesa.models import PaymentTransaction

# Create your views here.
class MenuAPiView(viewsets.ModelViewSet):
    serializer_class = Menu_ObjectSerializer
    queryset = Menu_Object.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = Foodfilter
    parser_classes = (MultiPartParser,)

    @action(detail=False, methods=['POST'])
    def create_food(self, request):
        serializer = Menu_ObjectSerializer(data=request.data)
        if serializer.is_valid():
            # Upload food image to Cloudinary
            image_file = request.data.get('food_image')
            if image_file:
                cloudinary_response = cloudinary.uploader.upload(image_file)
                serializer.validated_data['food_image'] = cloudinary_response['secure_url']

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


class MenuupdateAPiView(viewsets.ModelViewSet):
    serializer_class = Menu_ObjectSerializer
    queryset = Menu_Object.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = Foodfilter
    parser_classes = (MultiPartParser,)

    @action(detail=True, methods=['PUT'])
    def update_food(self, request, pk):
        menu_object = self.get_object()
        serializer = Menu_ObjectSerializer(menu_object, data=request.data, partial=True)
        if serializer.is_valid():
            # Upload food image to Cloudinary if provided
            image_file = request.data.get('food_image')
            if image_file:
                cloudinary_response = cloudinary.uploader.upload(image_file)
                serializer.validated_data['food_image'] = cloudinary_response['secure_url']

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['DELETE'])
    def delete_food(self, request, pk):
        try:
           food = Menu_Object.objects.filter(food_id = pk)
        except Menu_Object.DoesNotExist:
            return Response({"error":"enter correct id"}, status=status.HTTP_400_BAD_REQUEST)
        food.delete()
        return Response({"success":"done"}, status=status.HTTP_200_OK)
    
class CategoriesAPiView(viewsets.ModelViewSet):
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class =CategorySerializer
    queryset=  Categories.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']    
    

'''class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
   # permission_classes = [IsAuthenticated] # Add this line

   

class AddToCartViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        cart_pk = self.kwargs['']
        return Add_item_to_cart.objects.filter(cart_id=cart_pk)
    serializer_class = AddToCartSerializer

class Add_to_cart(viewsets.ModelViewSet):
    serializer_class = AddToCartSerializer
    queryset = Add_item_to_cart.objects.all()'''
    
class CartViewSet(viewsets.ModelViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Require authentication for all actions

    def get_queryset(self):
        user = self.request.user  # Get the currently logged-in user
        return Cart.objects.filter(user=user)
  

class AddToCartViewSet(viewsets.ModelViewSet):
    
    http_method_names = ['get','post','patch','delete']
    
    def get_queryset(self):
        user = self.request.user
        cart_id = user.cart.cart_id
        return Add_item_to_cart.objects.filter(cart_id = cart_id )

    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        
        elif self.request.method == 'PATCH':
            return Update_cart_serializer
        
        return ViewCartItemserializer
    
    def get_serializer_context(self):
        user = self.request.user
        cart_id = user.cart.cart_id
        return {'cart_id': cart_id}
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart_id = instance.cart_id

        super().destroy(request, *args, **kwargs)

        remaining_items = Add_item_to_cart.objects.filter(cart_id=cart_id)
        serializer = self.get_serializer(remaining_items, many=True)
        return Response(serializer.data)

    
class CheckoutView(views.APIView):
    def post(self, request):
        # Perform the payment process here
        # If the payment is successful, continue to the next step

        cart = request.user.cart
        order = cart.create_order()
        
        serializer = Order_Serializer(order)
        return Response(serializer.data)
    
    def get(self, request):
        print("START 1!")
        orders = Order.objects.filter(user=request.user)
        print("START 2! ",orders)
        if not orders:
            return Response({'detail': 'No orders found.'}, status=status.HTTP_404_NOT_FOUND)
        print("START 3!")
        response_data = []
        for order in orders:
            ordered_food = Orderd_Food.objects.filter(order=order)
            print("START 4!")
            ordered_food_serializer = OrderedFoodSerializer(ordered_food, many=True)
            print("START 5!")
            order_serializer = Order_Serializer(order)
            print("START 6!")
            orderId = order_serializer.data['order_id']
            trans = PaymentTransaction.objects.filter(order_id = orderId).first()
            
      
            print("START 7!")
            if trans:
                print("START 7! ", trans.trans_id)
                order_data = {
                    'order_id': order_serializer.data['order_id'],
                    'trans_id': trans.trans_id,
                    'status': order_serializer.data['state'],
                    'created_at': order_serializer.data['created_at'],
                    'total': order_serializer.data['total'],
                    'qr_image':order_serializer.data['qrc_image'] ,
                    'reciept':order_serializer.data['reciept'] ,
                    'scanned_time':order_serializer.data['scaned_time'] ,
                    'payment_mode':order_serializer.data['payment_mode'],
                    'ordered_food': ordered_food_serializer.data
                }
                print(order_data)  
                response_data.append(order_data)
            else:
                order_data = {
                    'order_id': order_serializer.data['order_id'],
                    'status': order_serializer.data['state'],
                    'created_at': order_serializer.data['created_at'],
                    'total': order_serializer.data['total'],
                    'qr_image':order_serializer.data['qrc_image'] ,
                    'reciept':order_serializer.data['reciept'] ,
                    'scanned_time':order_serializer.data['scaned_time'] ,
                    'payment_mode':order_serializer.data['payment_mode'],
                    'ordered_food': ordered_food_serializer.data
                }
                print(order_data)  
                response_data.append(order_data)

        return Response(response_data)
    

class ProcessOrderView(views.APIView):
    def post(self, request, format=None):
        serializer = OrderIdSerializer(data=request.data)
        user = self.request.user
        user_profile = Profile.objects.get(user= user)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            user = self.request.user
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            ordered_food_items = order.ordered_food.all()
            
            for ordered_food in ordered_food_items:
                if not ordered_food.food.is_avilable:
                    # Convert food price to points in a 1:10 ratio
                    points_to_add = ordered_food.food.price * 5
                    
                    # Update user's profile with points
                    user_profile = Profile.objects.get(user= user)
                    user_profile.points += int(points_to_add)
                    user_profile.save()
            
            return Response({'detail': 'Order processed successfully.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class OrdererdFood(views.APIView):
    def get(self, request, pk):
        try:
            order = Order.objects.filter(order_id=pk).first()
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if order.state == 'c':
            return Response({'error': 'already scanned.','scanned time':order.scaned_time}, status=status.HTTP_404_NOT_FOUND)

        ordered_food = Orderd_Food.objects.filter(order=order)
        ordered_food_serializer = OrderedFoodSerializer(ordered_food, many=True)
        order_serializer = Order_Serializer(order)
        food = ordered_food_serializer.data
        user=order_serializer.data['user']
        
        response_data = {
            'order_id': order_serializer.data['order_id'],
            'status': order_serializer.data['state'],
            'created_at': order_serializer.data['created_at'],
            'qr_image': order_serializer.data['qrc_image'],
            'scanned_time': order_serializer.data['scaned_time'],
            'user': user,
            'ordered_food': food
        }
        cloudinary_storage_config = settings.CLOUDINARY_STORAGE
        cloudinary.config(
            cloud_name=cloudinary_storage_config['CLOUD_NAME'],
            api_key=cloudinary_storage_config['API_KEY'],
            api_secret=cloudinary_storage_config['API_SECRET']
        )
        public_id = order.qrc_image
        api.delete_resources([public_id])
        current_time = datetime.now(timezone.utc)
        order.scaned_time = current_time
        order.qrc_image = ""
        order.state = 'c'
        order.save()
        recorder(food,user)
        return Response(response_data)
