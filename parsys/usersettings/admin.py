from django.contrib import admin
from .models import UserSettingSection, UserSetting


admin.site.register(UserSettingSection)

@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('section', 'name', 'slug', 'type', 'value')
    list_select_related = ('section',)
    list_editable = ('value',)
    list_filter = ('section',)
    ordering = ('section', 'name')




