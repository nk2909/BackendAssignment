from django.contrib import admin
from django.urls import path
from .views import (
    PostListAPIView,
    PostDetailAPIView,
    UserLoginView,
    UserView,
    UserRegisterView,
)

urlpatterns = [
    path("post/", PostListAPIView.as_view()),
    path("post/<uuid:pk>/", PostDetailAPIView.as_view()),
    path("register/", UserRegisterView.as_view()),
    path("users/<int:pk>/", UserView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("users/", UserView.as_view()),
]
