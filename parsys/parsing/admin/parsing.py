from django.contrib import admin
from ..models import Parsing


@admin.register(Parsing)
class ParsingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type', 'start', 'finish', 'duration', 'completed')
    list_filter = ('type', 'completed')

    actions = ('delete_selected', )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
