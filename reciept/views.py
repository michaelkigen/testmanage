from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import RecieptsSerializer
from .models import Reciepts
# Create your views here.
class RecieptAPIviewset(ModelViewSet):
    serializer_class = RecieptsSerializer
    queryset = Reciepts.objects.all()
    