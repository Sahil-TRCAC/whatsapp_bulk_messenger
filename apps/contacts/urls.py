from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('add/', views.contact_add, name='contact_add'),
    path('edit/<int:pk>/', views.contact_edit, name='contact_edit'),
    path('delete/<int:pk>/', views.contact_delete, name='contact_delete'),
    path('bulk-delete/', views.contact_bulk_delete, name='contact_bulk_delete'),
    path('import-csv/', views.contact_import_csv, name='contact_import_csv'),
    path('export-csv/', views.contact_export_csv, name='contact_export_csv'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('groups/delete/<int:pk>/', views.group_delete, name='group_delete'),
]
