from django.urls import path
from . import views

urlpatterns = [
    path('update-hostname/', views.update_hostname, name='update_hostname'),
    path('manage-resources/', views.manage_resources, name='manage_resources'),
]
