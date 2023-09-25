from rest_framework import serializers
from .models import Reciepts

class RecieptsSerializer(serializers.Serializer):
    class Mata:
        model = Reciepts
        fields = "__all__"