"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse
import os

def robots_txt(request):
    file_path = os.path.join(settings.BASE_DIR, 'robots.txt')
    try:
        with open(file_path, 'r') as f:
            return HttpResponse(f.read(), content_type="text/plain")
    except FileNotFoundError:
        return HttpResponse("User-agent: *\nDisallow:", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('maps.urls')),
    path('robots.txt', robots_txt),
]

from django.urls import re_path
from django.views.static import serve

# 2. Ép Django phục vụ file Media (ảnh người dùng up) ngay cả khi đã tắt DEBUG (lên mạng)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
