from django.urls import path
from . import views

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('compose/', views.campaign_compose, name='campaign_compose'),
    path('<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('<int:pk>/launch/', views.campaign_launch, name='campaign_launch'),
    path('<int:pk>/pause/', views.campaign_pause, name='campaign_pause'),
    path('<int:pk>/resume/', views.campaign_resume, name='campaign_resume'),
    path('<int:pk>/cancel/', views.campaign_cancel, name='campaign_cancel'),
    path('<int:pk>/delete/', views.campaign_delete, name='campaign_delete'),
    path('<int:pk>/recipients/', views.campaign_recipients, name='campaign_recipients'),
    path('<int:pk>/export-logs/', views.campaign_export_logs, name='campaign_export_logs'),
]
