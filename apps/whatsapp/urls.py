from django.urls import path
from . import views

urlpatterns = [
    path('', views.whatsapp_page, name='whatsapp_page'),
    path('qr/', views.whatsapp_qr, name='whatsapp_qr'),
    path('status/', views.whatsapp_status, name='whatsapp_status'),
    path('connect/', views.whatsapp_connect, name='whatsapp_connect'),
    path('disconnect/', views.whatsapp_disconnect, name='whatsapp_disconnect'),
]
