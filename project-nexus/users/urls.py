from django.urls import path
from .views import RegisterUserAPI, LoginAPI, LogoutAPI

urlpatterns = [
    path('register/', RegisterUserAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
]