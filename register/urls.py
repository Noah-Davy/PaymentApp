from django.urls import path
from .views import register, home_view, CustomLogoutView, CustomLoginView

urlpatterns = [
    path("register/", register, name="register"),
    path('home/', home_view, name='home'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('login/', CustomLoginView.as_view(), name='login'),
]

