from rest_framework import serializers
from .models import Review,NotifY,OveralReview

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id','product','user','rating','comment','created_at']
        extra_kwargs = {'review_id': {'read_only': True},'created_at': {'read_only': True},'overal_rating': {'read_only': True},'user': {'read_only': True}}
        
class OveralratingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OveralReview
        fields = ['product','overal_rating']
        extra_kwargs = {'product': {'read_only': True},'overal_rating': {'read_only': True}}
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifY
        fields = ['message','posted_time']
        extra_kwargs = {'posted_time': {'read_only': True}}
        