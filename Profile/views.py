from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from cloudinary.exceptions import Error
from users.models import User
from .serializers import ProfileSerializer
from .models import Profile

class ProfileView(generics.CreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        user = self.request.user
        profile = Profile.objects.get(user = user)
        # Access all the payment transactions related to the profile
        return profile


    
    def create(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Update the existing profile
        except Profile.DoesNotExist:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Create a new profile
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
  
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        # return Response({"points":str(profile.points),"transactions":str(profile.payments),"pic":serializer.data},status= status.HTTP_200_OK)
        return Response(serializer.data,status= status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.delete()
        return Response({"message":"profile picture removed "},status=status.HTTP_204_NO_CONTENT)