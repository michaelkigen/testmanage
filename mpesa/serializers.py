from rest_framework import serializers
from .models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['trans_id','checkout_request_id','order_id','is_finished','is_successful','amount','phone_number','message']