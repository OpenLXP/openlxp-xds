from django.contrib import admin

from .models import (CourseInformationMapping, XDSConfiguration,
                     XDSUIConfiguration)


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('default_user_group', 'target_xis_metadata_api',
                    'target_xse_host', 'target_xse_index', 'created',
                    'modified',)
    fieldsets = (
        ('XDS Settings', {'fields': ('default_user_group',)}),
        ('XIS Settings', {'fields': ('target_xis_metadata_api',)}),
        ('XSE Settings', {'fields': ('target_xse_host', 'target_xse_index',)}),
        ('LRS Settings', {'fields': ('lrs_endpoint',
                                     'lrs_username',
                                     'lrs_password')})
    )


@admin.register(XDSUIConfiguration)
class XDSUIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('search_results_per_page', 'xds_configuration',
                    'created', 'modified',)
    fields = [('search_results_per_page', 'xds_configuration',
               'course_img_fallback', 'ui_logo')]


@admin.register(CourseInformationMapping)
class CourseInformationMappingAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'course_description',
                    'course_url', 'course_code', 'course_startDate',
                    'course_endDate', 'course_provider',
                    'course_type', 'course_time',
                    'course_instructor', 'course_deliveryMode',
                    'course_thumbnail', 'course_derived_from',
                    'course_competency', 'course_subject',
                    'xds_ui_configuration')
    fields = ['course_title', 'course_description',
              'course_url', 'course_code', 'course_startDate',
              'course_endDate', 'course_provider',
              'course_type', 'course_time',
              'course_instructor', 'course_deliveryMode',
              'course_thumbnail', 'course_derived_from',
              'course_competency', 'course_subject',
              'xds_ui_configuration']
