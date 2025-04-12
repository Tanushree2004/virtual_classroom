from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'institution','is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        ('User Details', {'fields': ('username', 'email', 'password')}),
        ('Roles and Status', {'fields': ('role', 'is_active')}),
    )

