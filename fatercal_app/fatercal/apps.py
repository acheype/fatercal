from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class FatercalConfig(AppConfig):
    name = 'fatercal'


# Custom django admin application to remove the application name from all urls
class FatercalAdminConfig(AdminConfig):
    default_site = 'fatercal.admin.FatercalAdminSite'