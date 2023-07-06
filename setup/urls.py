from django.contrib import admin
from django.urls import include, path, re_path
from app.views import *
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/app/update/<str:model_name>/', update_data,name='update_data'),
    path('admin/app/generate/<str:model_name>/', generate_data ,name='generate_data'),
    path('admin/app/page/<str:model>/', load_page,name='load_page'),
    path('admin/app/pages/<str:model>/', load_pages,name='load_pages'),
    path('admin/app/movie/<int:id>/load/', load_movie,name='load_movie'),
    path('admin/app/season/<int:id>/load/', load_season,name='load_season'),
    path('admin/', admin.site.urls),
    path('', include('app.urls'), name='admin'),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
