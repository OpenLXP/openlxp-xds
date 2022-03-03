from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Organization, XDSUser


# Register your models here.
@admin.register(XDSUser)
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
                                    'user_permissions', 'organizations',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name',
                       'password1', 'password2', 'is_active', 'is_staff',
                       'groups', 'user_permissions', 'organizations',)}
         ),
    )
    filter_horizontal = ['organizations', 'groups', 'user_permissions', ]


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    search_fields = ('name', 'filter',)
    ordering = ('name',)
    list_display = ('name', 'filter',)
    fieldsets = (
        (None, {'fields': ('name', 'filter',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'filter',)}
         ),
    )
