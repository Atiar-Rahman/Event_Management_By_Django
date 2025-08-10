from django.contrib import admin
from .models import Category, Participant, Event

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','description')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name','email')
    search_fields = ('name','email')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name','date','time','location','category')
    list_filter = ('category','date')
    search_fields = ('name','location')
    filter_horizontal = ('participants',)
