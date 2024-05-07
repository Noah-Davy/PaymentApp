import requests
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Transaction, PaymentRequest
from decimal import Decimal


"""
Utility function that interacts with the currency conversion API, reused across payment functions below, abstracted out here to ensure modularity and to remove the complexity
"""
def convert_currency(from_currency, to_currency, amount):
    try:
        response = requests.get(f"https://127.0.0.1:8000/api/conversion/{from_currency}/{to_currency}/{amount}/",
                                verify=False)
        if response.status_code == 200:
            data = response.json()
            return Decimal(data['converted_amount'])
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error converting currency: {str(e)}")


"""
If Testing on local development server change the above url to this below one that is not https or currency conversion will not work
f"http://127.0.0.1:8000/api/conversion/{from_currency}/{to_currency}/{amount}/"
"""


"""
Facilitates sending money from one user to another, error handling ensuring users can't send money to themselves and sufficent funds are available'
"""
@login_required
@transaction.atomic
def make_payment(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        if recipient_username == request.user.username:
            messages.error(request, "You cannot send a payment to yourself.")
            return redirect('home')

        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            messages.error(request, "Recipient does not exist.")
            return redirect('home')

        amount = Decimal(request.POST.get('amount'))
        sender = request.user

        if not hasattr(sender, 'wallet') or not hasattr(recipient, 'wallet'):
            messages.error(request, "Both users must have wallets to complete a transaction.")
            return redirect('home')

        sender_wallet = sender.wallet
        recipient_wallet = recipient.wallet

        if sender_wallet.currency != recipient_wallet.currency:
            try:
                converted_amount = convert_currency(sender_wallet.currency, recipient_wallet.currency, amount)
                conversion_details = f"{amount:.2f} {sender_wallet.currency} converted to {converted_amount:.2f} {recipient_wallet.currency}"
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('home')
        else:
            converted_amount = amount
            conversion_details = f"{amount:.2f} {sender_wallet.currency} (no conversion needed)"

        if sender_wallet.balance >= amount > 0:
            sender_wallet.balance -= amount
            recipient_wallet.balance += converted_amount
            sender_wallet.save()
            recipient_wallet.save()
            Transaction.objects.create(sender=sender, recipient=recipient, amount=converted_amount)
            messages.success(request, f'Payment successful! {conversion_details}')
            return redirect('home')
        else:
            messages.error(request, 'Payment failed. Insufficient funds or invalid amount.')
    return redirect('home')


"""
Manages actions for existing payment request i.e. accept or reject payment request
"""
@login_required
@transaction.atomic
def handle_payment_request(request, request_id, action):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)
    if payment_request.recipient != request.user:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')

    if payment_request.status != 'pending':
        messages.info(request, "This request has already been processed.")
        return redirect('home')

    if action == 'accept':
        if request.method == 'POST':
            sender = payment_request.requester
            recipient = request.user
            amount = payment_request.amount  # Already in the recipient's currency

            sender_wallet = sender.wallet
            recipient_wallet = recipient.wallet

            # Ensure only perform transactions in the recipient's currency
            if recipient_wallet.balance >= amount:
                sender_wallet.balance += amount
                recipient_wallet.balance -= amount
                sender_wallet.save()
                recipient_wallet.save()
                Transaction.objects.create(sender=recipient, recipient=sender, amount=amount)
                payment_request.status = 'accepted'
                payment_request.save()
                messages.success(request, 'Payment request accepted and payment made.')
            else:
                messages.error(request, 'Insufficient funds to make the payment.')
            return redirect('home')
    elif action == 'reject':
        if request.method == 'POST':
            payment_request.status = 'rejected'
            payment_request.save()
            messages.info(request, 'Payment request rejected.')
            return redirect('home')

    messages.error(request, 'Invalid action.')
    return redirect('home')

"""
Creates a payment request from one user to another, ensuring users can't request money from themselves and sufficent funds are available
"""
@transaction.atomic
@login_required
def create_payment_request(request):
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        if recipient_username == request.user.username:
            messages.error(request, "You cannot request a payment from yourself.")
            return redirect('home')

        try:
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            messages.error(request, "Recipient does not exist.")
            return redirect('home')

        amount = Decimal(request.POST.get('amount'))
        requester = request.user

        requester_wallet = requester.wallet
        recipient_wallet = recipient.wallet

        try:
            if requester_wallet.currency != recipient_wallet.currency:
                converted_amount = convert_currency(requester_wallet.currency, recipient_wallet.currency, amount)
            else:
                converted_amount = amount

            PaymentRequest.objects.create(
                requester=requester,
                recipient=recipient,
                amount=converted_amount
            )
            messages.success(request,
                             f'Payment request sent. {amount:.2f} {requester_wallet.currency} requested as {converted_amount:.2f} {recipient_wallet.currency}.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('home')
    else:
        return redirect('home')
