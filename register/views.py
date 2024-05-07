from django.shortcuts import render, HttpResponseRedirect
from .forms import UserForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView
from django.urls import reverse_lazy
from payapp.models import Transaction, PaymentRequest
from payapp.views import convert_currency
from .models import Wallet
from django.contrib import messages


@login_required(login_url='/login/')
def home_view(request):
    received_payment_requests = PaymentRequest.objects.filter(recipient=request.user).order_by('-timestamp')
    sent_payments = Transaction.objects.filter(sender=request.user).order_by('-timestamp')
    received_payments = Transaction.objects.filter(recipient=request.user).order_by('-timestamp')

    context = {
        'account_balance': request.user.wallet.balance,
        'currency': request.user.wallet.currency,
        'received_payment_requests': received_payment_requests,
        'sent_payments': sent_payments,
        'received_payments': received_payments,

    }
    return render(request, 'home.html', context)


def register(request):
    if not request.user.is_authenticated:

        if request.method == "POST":

            form = UserForm(request.POST)

            if form.is_valid():
                user = form.save()
                currency = form.cleaned_data['currency']
                balance = float(1000)
                #Conversion to ensure wallet is initialised with 1000 gbp value equivalent
                if currency == 'EUR':
                    value = convert_currency('GBP', 'EUR', balance)
                    Wallet.objects.create(user=user, balance=value, currency='EUR')
                elif currency == 'USD':
                    value = convert_currency('GBP', 'USD', balance)
                    Wallet.objects.create(user=user, balance=value, currency='USD')
                else:
                    Wallet.objects.create(user=user, balance=balance, currency='GBP')

                messages.success(request, 'New Account Registered Successfully!')
                return HttpResponseRedirect(f'/login/')
        else:
            form = UserForm()

        return render(request, 'register.html', {'form': form})
    else:
        return HttpResponseRedirect(f'/home/')


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('home')

    def form_valid(self, form):
        # Authenticate and login the user
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
