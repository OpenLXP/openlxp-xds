from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import XDSUser


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
