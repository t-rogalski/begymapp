from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import delete_account, login, register, logout


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('delete/', delete_account, name='delete_account'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
