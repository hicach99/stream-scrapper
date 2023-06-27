"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from app.views import *
urlpatterns = [
    path('admin/app/page/<str:model>/', load_page,name='load_page'),
    path('admin/app/pages/<str:model>/', load_pages,name='load_pages'),
    path('admin/app/movie/<int:id>/load/', load_movie,name='load_movie'),
    path('admin/app/season/<int:id>/load/', load_season,name='load_season'),
    path('admin/', admin.site.urls),
    path('', include('app.urls'))
]
