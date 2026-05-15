from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from Users.models.perfil_models import Profile
from Users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display  = ('id', 'email', 'nombre', 'apellidos', 'role', 'is_verified_badge', 'is_active', 'is_staff', 'date_joined')
    list_filter   = ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'role')
    search_fields = ('email', 'nombre', 'apellidos')
    ordering      = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')
    fieldsets = (
        ('Cuenta', {'fields': ('email', 'password')}),
        ('Datos personales', {'fields': ('nombre', 'apellidos')}),
        ('Estado', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'role')}),
        ('Fechas', {'fields': ('date_joined', 'last_login')}),
    )
    actions = ['ban_users', 'activate_users', 'verify_users']

    @admin.display(boolean=True, description='Verificado')
    def is_verified_badge(self, obj):
        return obj.is_verified

    @admin.action(description='Banear usuarios seleccionados')
    def ban_users(self, request, queryset):
        updated = queryset.exclude(is_superuser=True).update(is_active=False)
        self.message_user(request, f'{updated} usuario(s) baneado(s).')

    @admin.action(description='Activar usuarios seleccionados')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuario(s) activado(s).')

    @admin.action(description='Verificar usuarios seleccionados')
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} usuario(s) verificado(s).')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'created_at')
    search_fields = ('user__email',)
    raw_id_fields = ('user',)