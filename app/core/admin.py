from django.contrib import admin

from core.models import SearchFilter, XDSConfiguration, XDSUIConfiguration,\
                        SearchSortOption


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_metadata_api',)
    fields = [('target_xis_metadata_api',)]


@admin.register(XDSUIConfiguration)
class XDSUIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('search_results_per_page', 'xds_configuration',)
    fields = [('search_results_per_page', 'xds_configuration',)]


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'filter_type', 'active',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'filter_type', 'active',)]


@admin.register(SearchSortOption)
class SearchSortOptionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'active',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'active',)]
