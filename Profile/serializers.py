from rest_framework import serializers
from .models import Profile
from cloudinary import uploader
from mpesa.models import PaymentTransaction


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Profile
        fields = ('user', 'profile_pic', 'points')


    def create(self, validated_data):
        # Save the profile instance
        profile = super().create(validated_data)

        if 'profile_pic' in self.context['request'].data:
            uploaded_image = uploader.upload(self.context['request'].data['profile_pic'])
            profile.profile_pic = uploaded_image['url']
            profile.save()

        return profile
