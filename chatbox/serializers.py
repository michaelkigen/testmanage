from rest_framework import serializers
from .models import ChatMessage
from rest_framework import serializers
from .models import ChatMessage
from django.contrib.auth.models import User

class ChatMessageWithUserInfoSerializer(serializers.ModelSerializer):
    sender_first_name = serializers.CharField(source='sender.first_name', read_only=True)
    sender_last_name = serializers.CharField(source='sender.last_name', read_only=True)
    sender_phone_number = serializers.CharField(source='sender.phone_number', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('sender', 'recipient', 'message', 'timestamp', 'sender_first_name', 'sender_last_name', 'sender_phone_number')


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('sender', 'recipient', 'message', 'timestamp')
