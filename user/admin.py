from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number", "profile_picture")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("phone_number", "profile_picture")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "phone_number", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
