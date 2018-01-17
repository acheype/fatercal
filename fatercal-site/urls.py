from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
from django.conf import settings

urlpatterns = [
    url(r'^ajax_select/', include(ajax_select_urls)),
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^', include(admin.site.urls)),
    url(r'^fatercal/', include('fatercal.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
