from django.urls import path

from backend.posts import views

urlpatterns = [
    path('', views.PostsView.as_view()),
    path('tags/', views.TagsView.as_view()),
    path('tags/<int:pk>/', views.TagDetailView.as_view()),
    path('<str:pk>/', views.PostDetailView.as_view()),
]

app_name = 'backend.posts'