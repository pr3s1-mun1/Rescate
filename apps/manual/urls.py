from django.urls import path
from . import views

urlpatterns = [
    path('vista/', views.manual_home, name='manual_home'),
]