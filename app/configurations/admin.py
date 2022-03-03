from django.contrib import admin

from .models import (CourseInformationMapping, XDSConfiguration,
                     XDSUIConfiguration)


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_metadata_api', 'target_xse_host',
                    'target_xse_index', 'created', 'modified',)
    fieldsets = (
        ('XIS Settings', {'fields':
                          ('target_xis_metadata_api',)}),
        ('XSE Settings', {'fields':
                          ('target_xse_host', 'target_xse_index',)}))


@admin.register(XDSUIConfiguration)
class XDSUIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('search_results_per_page', 'xds_configuration',
                    'created', 'modified',)
    fields = [('search_results_per_page', 'xds_configuration',
               'course_img_fallback')]


@admin.register(CourseInformationMapping)
class CourseInformationMappingAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'course_description',
                    'course_url', 'xds_ui_configuration')

    fields = ['course_title', 'course_description',
              'course_url', 'xds_ui_configuration']
