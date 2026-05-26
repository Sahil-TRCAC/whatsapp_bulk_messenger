from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from apps.whatsapp.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('whatsapp/', include('apps.whatsapp.urls')),
    path('contacts/', include('apps.contacts.urls')),
    path('campaigns/', include('apps.campaigns.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('dashboard/', dashboard, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
