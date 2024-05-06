from django.contrib import admin
from .models import PaymentRequest, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp')


@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'recipient', 'amount', 'timestamp')
