from django.contrib import admin
from django.urls import include, path

from api.views import short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:hash>/', short_link_redirect),
]
