from django.urls import path

from .views import (
    create_training_plan,
    training_plan_detail,
)


urlpatterns = [
    path('', create_training_plan, name='create_training_plan'),
    path('<int:plan_id>/', training_plan_detail, name='training_plan_detail'),
]
