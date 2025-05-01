
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.email_view_bulk,name='email_view_bulk'),
]
