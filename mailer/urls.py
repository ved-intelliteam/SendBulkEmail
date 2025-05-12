from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.email_view_bulk, name="email_view_bulk"),
    path("followup/", views.follow_up_email_view, name="follow_up_email_view"),
]
