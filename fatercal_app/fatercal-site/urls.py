"""fatercal-site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
from django.conf import settings
from django.views.generic.base import RedirectView

from fatercal.admin import fatercal_admin

urlpatterns = [
    path('ajax_select/', include(ajax_select_urls)),
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', fatercal_admin.urls),
    path('admin/', include('fatercal.urls')),
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('login/', RedirectView.as_view(url='/admin/login/', permanent=False), name='login')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
