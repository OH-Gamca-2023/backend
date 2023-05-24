from django.urls import path

from posts import views

urlpatterns = [
    path('', views.PostsView.as_view()),
    path('tags/', views.TagsView.as_view()),
    path('tags/<int:pk>/', views.TagDetailView.as_view()),
    path('<str:pk>/', views.PostDetailView.as_view()),
]
