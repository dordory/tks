# apps/member/urls.py
from django.urls import path
from . import views

app_name = "member"

urlpatterns = [
    path("users/", views.user_list_view, name="user_list"),
]
