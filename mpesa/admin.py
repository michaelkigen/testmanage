# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

from django.contrib import admin
from .models import PaymentTransaction, Wallet


class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("phone_number","user", "order_id", "amount", "is_finished", "is_successful",
                    "trans_id", "checkout_request_id", "date_created", "date_modified", "receipt_number")

admin.site.register(PaymentTransaction, PaymentTransactionAdmin)

admin.site.register(Wallet)