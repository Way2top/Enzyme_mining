"""
URL configuration for enzyme_2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.static import serve
from django.views.generic.base import RedirectView
from enzyme_2.settings import MEDIA_ROOT

urlpatterns = [
    path('admin_ls/', admin.site.urls),
    path('index/', include('index.urls')),  # 包括用户认证相关的路由
    path('search/', include('search.urls')),
    path('similar/', include('similar.urls')),  # 添加酶相似性搜索应用的路由
    re_path(r'^upload/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
]
