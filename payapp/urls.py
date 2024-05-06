from django.urls import path


from payapp.views import create_payment_request, make_payment, handle_payment_request

urlpatterns = [
    path('create_payment_request/', create_payment_request, name='create_payment_request'),
    path('make_payment/', make_payment, name='make_payment'),
    path('payment_request/<int:request_id>/<str:action>/', handle_payment_request, name='payment_request_action'),
]

