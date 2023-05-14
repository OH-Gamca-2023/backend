from django.urls import path

from posts import views

urlpatterns = [
    path('', views.PostListAPIView.as_view()),
    path('<str:pk>/', views.PostDetailAPIView.as_view()),
    path('tags/', views.TagListAPIView.as_view()),
]
