from django.urls import path
from .import views

app_name = 'reservations'

urlpatterns = [
    path('reserve/', views.reserve_view, name='reserve'),
    path('submission/', views.submission_view, name='submission'),
    path('myReservations/', views.myReservations_view, name='myReservations'),
    path('staffReservations/', views.staffReservations_view, name='staffReservations'),
]
