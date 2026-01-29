from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    # Use phone instead of username in the list display
    list_display = ('phone', 'full_name', 'is_staff', 'is_active')
    search_fields = ('phone', 'full_name')
    ordering = ('phone',)
    
    # These must be empty or updated because we don't have a 'username' field
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email', 'address', 'city')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password'),
        }),
    )
admin.site.register(User,CustomUserAdmin)