"""
URL configuration for Eagles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('brand_data/', views.get_brand_data, name='brand_data'),
    path('get_brand/<str:brand_name>/', views.show_release_id, name='brand_release_id'),
    path('get_db/<str:company_name>/', views.show_databases_url, name='db_url'),
    path('display_brand_data/', views.display_brand_data, name='display_brand_data'),
    path('hostname_updater/', include('hostname_updater.urls')),
]
