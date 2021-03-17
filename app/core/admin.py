from django.contrib import admin
from core.models import XDSConfiguration


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_es_api', 'target_xis_metadata_api',)
    fields = [('target_xis_es_api', 'target_xis_metadata_api')]
