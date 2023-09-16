"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from .views import *
from backend.data.views import LinkView

api_urls = [
    path('', api_root),
    path('auth/', include('backend.auth.urls', namespace='auth')),
    path('user/', include('backend.users.urls', namespace='user')),
    path('status/', StatusView.as_view(), name='status'),
    path('disciplines/', include('backend.disciplines.urls', namespace='disciplines')),
    path('calendar/', include('backend.kalendar.urls', namespace='calendar')),
    path('posts/', include('backend.posts.urls', namespace='posts')),
    path('ciphers/', include('backend.ciphers.urls', namespace='ciphers')),
    path('data/', include('backend.data.urls', namespace='data')),
]

urlpatterns = [
    path(r'admin/mdeditor/upload/', csrf_exempt(UploadView.as_view()), name='mdeditor_upload'),
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('link/<str:key>/', LinkView.as_view(), name='link'),
    path('', home, name='home')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT / 'public')
