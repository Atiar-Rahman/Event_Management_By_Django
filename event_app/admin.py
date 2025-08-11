from django.contrib import admin
from .models import Event, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "category", "location")
    list_filter = ("category", "date")
    search_fields = ("name", "location", "description")
    autocomplete_fields = ("category",)
    filter_horizontal = ("participants",)
