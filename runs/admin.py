from django.contrib import admin
from .models import Run
# Register your models here.
@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ('user', 'file_name', 'distance_km', 'avg_pace', 'shoe_name', 'perceived_effort')
    search_fields = ('user__username', 'shoe_name', 'file_name')