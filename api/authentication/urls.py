from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import change_password, delete_account, login, register, logout


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('change-password/', change_password, name='change_password'),
    path('delete/', delete_account, name='delete_account'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
