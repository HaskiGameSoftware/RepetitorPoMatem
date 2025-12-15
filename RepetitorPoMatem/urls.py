from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('homepage.urls', namespace='homepage')),
    path('service/', include('service.urls', namespace='service')),
    path('about/', include('about.urls', namespace='about')),
    path('contacts/', include('contacts.urls', namespace='contacts')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
]