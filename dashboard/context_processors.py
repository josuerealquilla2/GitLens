from django.utils import timezone
from datetime import timedelta


def animations_flag(request):
    if not request.path.startswith('/panel/'):
        return {}
    from Users.models.user_models import CustomUser
    from repositorios.models.social_models import RepoComment
    from .models import MaintenanceMode
    now = timezone.now()
    try:
        maint = MaintenanceMode.get()
        maintenance_active = maint.is_active
    except Exception:
        maintenance_active = False
    return {
        'dash_no_animations':  request.session.get('no_animations', False),
        'maintenance_status':  maintenance_active,
        'notif_new_users':     CustomUser.objects.filter(
            date_joined__gte=now - timedelta(hours=24)).count(),
        'notif_comments':      RepoComment.objects.filter(
            created_at__gte=now - timedelta(hours=24)).count(),
    }
