from django.shortcuts import render

from rest_framework import status,viewsets,views,mixins,generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# from rest_framework.authentication import JSONWebTokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OrderedFoodSerializer,Menu_ObjectSerializer, CartSerializer, CategorySerializer,AddToCartSerializer,Update_cart_serializer,AddCartItemSerializer,Create_Cart_Serializer,ViewCartItemserializer,Order_Serializer
from .models import Menu_Object,Categories,Cart,Add_item_to_cart,Order,Orderd_Food
from .filters import Foodfilter

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required

# Create your views here.
class MenuAPiView(viewsets.ModelViewSet):
  
    serializer_class = Menu_ObjectSerializer
    queryset=  Menu_Object.objects.filter(is_avilable = True)
    filter_backends = [DjangoFilterBackend]
    filterset_class = Foodfilter
    parser_classes = (MultiPartParser,)
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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
        orders = Order.objects.filter(user=request.user)
        if not orders:
            return Response({'detail': 'No orders found.'}, status=status.HTTP_404_NOT_FOUND)

        response_data = []
        for order in orders:
            ordered_food = Orderd_Food.objects.filter(order=order)
            ordered_food_serializer = OrderedFoodSerializer(ordered_food, many=True)
            order_serializer = Order_Serializer(order)
            order_data = {
                'order_id': order_serializer.data['order_id'],
                'status': order_serializer.data['state'],
                'created_at': order_serializer.data['created_at'],
                'total': order_serializer.data['total'],
                'qr_image':order_serializer.data['qrc_image'] ,
                'ordered_food': ordered_food_serializer.data
            }
            response_data.append(order_data)

        return Response(response_data)