from django.contrib import admin

from core.models import XDSConfiguration


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_metadata_api', 'search_results_per_page',)
    fields = [('target_xis_metadata_api', 'search_results_per_page')]
