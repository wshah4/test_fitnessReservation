from django.urls import path, include
from .import views

app_name = 'fitnessClass'

urlpatterns = [
    path('', views.schedule_view, name='schedule'),
]
