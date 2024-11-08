from core.models import (CourseDetailHighlight, CourseSpotlight, Experience,
                         InterestList, SavedFilter, SearchFilter,
                         SearchSortOption, SearchField)
from django.contrib import admin


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'filter_type', 'active', 'created', 'modified',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'filter_type', 'active',)]


@admin.register(SearchField)
class SearchFieldAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'field_name', 'xds_ui_configuration',
                    'active', 'created', 'modified',)
    fields = [('display_name', 'field_name', 'xds_ui_configuration',
               'active',)]


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


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('metadata_key_hash',)


@admin.register(InterestList)
class InterestListAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'public', 'created', 'modified',)
    fields = ['owner', 'public', 'name',
              'description', 'experiences', 'subscribers', ]
    filter_horizontal = ['subscribers', ]


@admin.register(SavedFilter)
class SavedFilterAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'query', 'modified',)
    fields = ['owner', 'name', 'query']
