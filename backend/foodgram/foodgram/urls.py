from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('api/', include('api.urls')),
    path('receipes/', include('receipes.urls')),
]
