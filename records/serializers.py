from rest_framework import serializers
from .models import Records, DailyRecord

class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Records
        fields ="__all__"
        
class DailyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRecord
        fields = "__all__"