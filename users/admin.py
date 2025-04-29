from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id','email', 'username', 'user_type', 'is_admin', 'is_email_verified', 'is_approved')
    list_filter = ('is_admin', 'user_type', 'is_email_verified', 'is_approved')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'profile_pic', 'profile_pic_url')}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser', 'is_email_verified', 'is_approved', 'is_deleted', 'is_mute')}),
        ('User Type', {'fields': ('user_type',)}),
        ('Other', {'fields': ('device_token',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )

admin.site.register(User, UserAdmin)
