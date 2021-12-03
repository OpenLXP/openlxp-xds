from core.models import (CourseDetailHighlight, CourseInformationMapping,
                         CourseSpotlight, Experience, InterestList,
                         SavedFilter, SearchFilter, SearchSortOption,
                         XDSConfiguration, XDSUIConfiguration, XDSUser)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(XDSConfiguration)
class XDSConfigurationAdmin(admin.ModelAdmin):
    list_display = ('target_xis_metadata_api', 'created', 'modified',)
    fields = [('target_xis_metadata_api',)]


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


@admin.register(CourseInformationMapping)
class CourseInformationMappingAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'course_description',
                    'course_url', 'xds_ui_configuration')

    fields = ['course_title', 'course_description',
              'course_url', 'xds_ui_configuration']


class XDSUserAdmin(UserAdmin):
    model = XDSUser
    search_fields = ('email', 'first_name',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('-date_joined', '-last_login')
    list_display = ('email', 'first_name',
                    'is_active', 'is_staff', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'first_name', 'last_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups',
                                    'user_permissions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_active', 'is_staff',
                       'groups', 'user_permissions')}
         ),
    )


admin.site.register(XDSUser, XDSUserAdmin)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('metadata_key_hash',)


@admin.register(InterestList)
class InterestListAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'created', 'modified',)
    fields = ['owner', 'name', 'description', 'experiences']


@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'query', 'modified',)
    fields = ['owner', 'name', 'query']
