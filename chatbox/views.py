from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatMessage
from .serializers import ChatMessageSerializer,ChatMessageWithUserInfoSerializer
from users.models import User
from django.db.models import Q

from rest_framework import permissions

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated
    
    def post(self, request, format=None):
        sender = request.user  # Get the current logged-in user
        recipient_id = request.data.get('recipient')

        try:
            recipient = User.objects.get(phone_number=recipient_id)
        except User.DoesNotExist:
            return Response({'error': 'Recipient does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        message = request.data.get('message')
        chat_message = ChatMessage.objects.create(sender=sender, recipient=recipient, message=message)
        return Response({'message': 'Sent.'}, status=status.HTTP_200_OK)



class GetMessagesView(APIView):
    def get(self, request, format=None):
        user = request.user
        messages = ChatMessage.objects.filter(Q(sender=user) | Q(recipient=user))
        serializer = ChatMessageWithUserInfoSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)