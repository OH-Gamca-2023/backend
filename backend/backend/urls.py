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

from . import settings
from .views import *

api_urls = [
    path('auth/', include('auth.urls')),
    path('user/', include('users.urls')),
    path('status/', StatusView.as_view(), name='status'),
    path('disciplines/', include('disciplines.urls')),
    path('calendar/', include('kalendar.urls')),
    path('posts/', include('posts.urls')),
    path('ciphers/', include('ciphers.urls')),
    path('data/', include('data.urls'))
]


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('jet/', include('jet.urls', 'jet')),
    # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('api/', include(api_urls)),
    path('', home, name='home'),
    path(r'mdeditor/', include('mdeditor.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

