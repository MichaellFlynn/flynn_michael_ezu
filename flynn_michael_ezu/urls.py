from django.contrib import admin
from django.urls import path, include
from .views import redirect_root_view

urlpatterns = [
    path('', redirect_root_view),
    path('admin/', admin.site.urls),
    path('', include('courseinfo.urls'))
]
