from django.contrib import admin

from core.models import (CourseDetailHighlight, CourseSpotlight, SearchFilter,
                         SearchSortOption, XDSConfiguration,
                         XDSUIConfiguration)


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_metadata_api', 'created', 'modified',
        'target_xis_composite_ledger_api')
    fields = [('target_xis_metadata_api', 'target_xis_composite_ledger_api')]


@admin.register(XDSUIConfiguration)
class XDSUIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('search_results_per_page', 'xds_configuration',
                    'created', 'modified',)
    fields = [('search_results_per_page', 'xds_configuration',
               'course_img_fallback')]


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'filter_type', 'active', 'created', 'modified',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'filter_type', 'active',)]


@admin.register(SearchSortOption)
class SearchSortOptionAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'active', 'created', 'modified',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'active',)]


@admin.register(CourseDetailHighlight)
class CourseDetailHighlightAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'active', 'highlight_icon', 'rank', 'created', 'modified',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'active', 'highlight_icon', 'rank',)]


@admin.register(CourseSpotlight)
class CourseSpotlightAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'active',)
