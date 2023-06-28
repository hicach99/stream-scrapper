from django.contrib import admin
from django.urls import include, path, re_path
from app.views import *
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/app/page/<str:model>/', load_page,name='load_page'),
    path('admin/app/pages/<str:model>/', load_pages,name='load_pages'),
    path('admin/app/movie/<int:id>/load/', load_movie,name='load_movie'),
    path('admin/app/season/<int:id>/load/', load_season,name='load_season'),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
