from django.contrib import admin
from .models import ModerationLog, MaintenanceMode


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display  = ('id', 'moderator', 'action', 'target_user', 'detail_short', 'created_at')
    list_filter   = ('action',)
    search_fields = ('moderator__email', 'target_user__email', 'detail')
    ordering      = ('-created_at',)
    readonly_fields = ('moderator', 'action', 'target_user', 'detail', 'created_at')

    @admin.display(description='Detalle')
    def detail_short(self, obj):
        return obj.detail[:60] if obj.detail else '—'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display  = ('is_active', 'message', 'activated_by', 'activated_at')
    readonly_fields = ('activated_by', 'activated_at')
