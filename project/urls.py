from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Loanapp.views import landing_page, about_us, contact_us, courses

urlpatterns = [
    path('', landing_page, name='home'),
    path('aboutus', about_us, name='about_us'),
    path('contactus', contact_us, name='contact_us'),
    path('courses', courses, name='courses'),
    path('admin/', admin.site.urls),
    path('api/v1/loanapp/', include('Loanapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 