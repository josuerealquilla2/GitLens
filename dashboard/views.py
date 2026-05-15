import os
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from django.db import connection
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from Chat.models import Message
from Users.models.user_models import CustomUser, ROLE_CHOICES
from repositorios.models.social_models import RepoComment, RepoLike, FavoriteRepo, SavedRepo
from .models import ModerationLog, MaintenanceMode

staff_required = user_passes_test(
    lambda u: u.is_active and u.is_staff,
    login_url='/admin/login/'
)


# ── Helpers ───────────────────────────────────────────────────

def _log(moderator, action, target=None, detail=''):
    ModerationLog.objects.create(
        moderator=moderator, action=action, target_user=target, detail=detail
    )


def _quick_stats():
    cached = cache.get('dash_quick_stats')
    if cached:
        return cached
    now = timezone.now()
    stats = {
        'total_users':    CustomUser.objects.count(),
        'active_users':   CustomUser.objects.filter(is_active=True).count(),
        'banned_users':   CustomUser.objects.filter(is_active=False).count(),
        'new_24h':        CustomUser.objects.filter(date_joined__gte=now - timedelta(hours=24)).count(),
        'verified_users': CustomUser.objects.filter(is_verified=True).count(),
        'total_messages': Message.objects.count(),
        'total_comments': RepoComment.objects.count(),
        'total_likes':    RepoLike.objects.count(),
        'mod_actions':    ModerationLog.objects.count(),
    }
    cache.set('dash_quick_stats', stats, 60)
    return stats


def _db_stats():
    db_path = settings.DATABASES['default']['NAME']
    size_bytes = os.path.getsize(str(db_path)) if os.path.exists(str(db_path)) else 0
    with connection.cursor() as c:
        c.execute('PRAGMA page_count'); page_count = c.fetchone()[0]
        c.execute('PRAGMA page_size');  page_size  = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
        table_count = c.fetchone()[0]
    return {
        'size_mb':     round(size_bytes / 1024 / 1024, 2),
        'size_kb':     round(size_bytes / 1024, 1),
        'page_count':  page_count,
        'page_size':   page_size,
        'table_count': table_count,
    }


def _notif_counts():
    return {
        'notif_comments': RepoComment.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count(),
        'notif_new_users': CustomUser.objects.filter(
            date_joined__gte=timezone.now() - timedelta(hours=24)
        ).count(),
    }


# ── Index ─────────────────────────────────────────────────────

@staff_required
def dashboard_index(request):
    recent_users = CustomUser.objects.order_by('-date_joined')[:10]
    recent_logs  = ModerationLog.objects.select_related('moderator', 'target_user')[:8]
    maintenance  = MaintenanceMode.get()
    return render(request, 'dashboard/index.html', {
        'stats':        _quick_stats(),
        'recent_users': recent_users,
        'recent_logs':  recent_logs,
        'maintenance':  maintenance,
        'section':      'index',
        **_notif_counts(),
    })


# ── Users ─────────────────────────────────────────────────────

@staff_required
def dashboard_users(request):
    q             = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    role_filter   = request.GET.get('role', '')
    date_from     = request.GET.get('date_from', '')
    date_to       = request.GET.get('date_to', '')

    qs = CustomUser.objects.order_by('-date_joined')
    if q:
        qs = qs.filter(email__icontains=q) | qs.filter(
            nombre__icontains=q) | qs.filter(apellidos__icontains=q)
    if status_filter == 'active':
        qs = qs.filter(is_active=True)
    elif status_filter == 'banned':
        qs = qs.filter(is_active=False)
    elif status_filter == 'verified':
        qs = qs.filter(is_verified=True)
    if role_filter:
        qs = qs.filter(role=role_filter)
    if date_from:
        qs = qs.filter(date_joined__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_joined__date__lte=date_to)

    user_list = list(qs[:300])
    user_ids  = [u.id for u in user_list]
    msg_counts = {
        row['sender_id']: row['c']
        for row in Message.objects
            .filter(sender_id__in=user_ids)
            .values('sender_id').annotate(c=Count('id'))
    }
    users_data = [{'obj': u, 'msg_count': msg_counts.get(u.id, 0)} for u in user_list]

    return render(request, 'dashboard/users.html', {
        'users_data':    users_data,
        'stats':         _quick_stats(),
        'roles':         ROLE_CHOICES,
        'q':             q,
        'status_filter': status_filter,
        'role_filter':   role_filter,
        'date_from':     date_from,
        'date_to':       date_to,
        'section':       'users',
        **_notif_counts(),
    })


@staff_required
@require_POST
def toggle_user_status(request, user_id):
    target = get_object_or_404(CustomUser, id=user_id)
    if target == request.user or target.is_superuser:
        return JsonResponse({'error': 'Operación no permitida.'}, status=403)
    action_type = request.POST.get('action', 'ban')  # 'ban' | 'suspend'
    target.is_active = not target.is_active
    target.save(update_fields=['is_active'])
    _log(request.user,
         action_type if not target.is_active else 'unban',
         target,
         f"is_active → {target.is_active}")
    cache.delete('dash_quick_stats')
    return JsonResponse({'is_active': target.is_active, 'user_id': target.id})


@staff_required
@require_POST
def toggle_verified(request, user_id):
    target = get_object_or_404(CustomUser, id=user_id)
    target.is_verified = not target.is_verified
    target.save(update_fields=['is_verified'])
    _log(request.user,
         'verify' if target.is_verified else 'unverify',
         target)
    return JsonResponse({'is_verified': target.is_verified, 'user_id': target.id})


@staff_required
@require_POST
def set_role(request, user_id):
    target   = get_object_or_404(CustomUser, id=user_id)
    new_role = request.POST.get('role', 'user')
    valid    = [r[0] for r in ROLE_CHOICES]
    if new_role not in valid:
        return JsonResponse({'error': 'Rol no válido.'}, status=400)
    old_role = target.role
    target.role = new_role
    target.save(update_fields=['role'])
    _log(request.user, 'role_change', target, f"{old_role} → {new_role}")
    return JsonResponse({'role': target.role, 'user_id': target.id})


@staff_required
@require_POST
def toggle_staff(request, user_id):
    target = get_object_or_404(CustomUser, id=user_id)
    if target == request.user:
        return JsonResponse({'error': 'No puedes modificar tu propio staff.'}, status=403)
    target.is_staff = not target.is_staff
    target.save(update_fields=['is_staff'])
    return JsonResponse({'is_staff': target.is_staff, 'user_id': target.id})


# ── Content ───────────────────────────────────────────────────

@staff_required
def dashboard_content(request):
    comments  = RepoComment.objects.select_related('user').order_by('-created_at')[:200]
    avatars   = (CustomUser.objects
                 .filter(profile__image__isnull=False)
                 .exclude(profile__image='')
                 .select_related('profile')
                 .order_by('-id')[:50])
    mod_logs  = ModerationLog.objects.filter(
        action__in=['delete_comment', 'delete_message']
    ).select_related('moderator', 'target_user')[:50]

    return render(request, 'dashboard/content.html', {
        'comments':  comments,
        'avatars':   avatars,
        'mod_logs':  mod_logs,
        'likes':     RepoLike.objects.count(),
        'favorites': FavoriteRepo.objects.count(),
        'saved':     SavedRepo.objects.count(),
        'stats':     _quick_stats(),
        'section':   'content',
        **_notif_counts(),
    })


@staff_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(RepoComment, id=comment_id)
    target  = comment.user
    detail  = f"repo:{comment.repo_github_id} | {comment.body[:80]}"
    comment.delete()
    _log(request.user, 'delete_comment', target, detail)
    return JsonResponse({'deleted': True, 'comment_id': comment_id})


# ── Mod log ───────────────────────────────────────────────────

@staff_required
def dashboard_logs(request):
    logs = ModerationLog.objects.select_related('moderator', 'target_user').all()[:300]
    return render(request, 'dashboard/logs.html', {
        'logs':    logs,
        'stats':   _quick_stats(),
        'section': 'logs',
        **_notif_counts(),
    })


# ── System ────────────────────────────────────────────────────

@staff_required
def dashboard_system(request):
    maintenance = MaintenanceMode.get()
    db          = _db_stats()

    # Leer últimas líneas del log de Django si existe
    error_lines = []
    for handler in __import__('logging').getLogger('django').handlers:
        if hasattr(handler, 'baseFilename') and os.path.exists(handler.baseFilename):
            try:
                with open(handler.baseFilename, 'r', encoding='utf-8', errors='ignore') as f:
                    error_lines = f.readlines()[-60:]
            except Exception:
                pass
            break

    # API keys (solo nombres, nunca valores)
    api_keys = {
        'GITHUB_TOKEN':     '✓ configurado' if settings.GITHUB_TOKEN else '✗ no configurado',
        'DJANGO_SECRET_KEY': '✓ desde entorno' if os.environ.get('DJANGO_SECRET_KEY') else '⚠ hardcodeada',
        'DJANGO_DEBUG':      str(settings.DEBUG),
    }

    return render(request, 'dashboard/system.html', {
        'maintenance':  maintenance,
        'db':           db,
        'error_lines':  error_lines,
        'api_keys':     api_keys,
        'stats':        _quick_stats(),
        'section':      'system',
        **_notif_counts(),
    })


@staff_required
@require_POST
def toggle_maintenance(request):
    m = MaintenanceMode.get()
    m.is_active    = not m.is_active
    m.activated_by = request.user if m.is_active else None
    m.activated_at = timezone.now() if m.is_active else None
    m.save()
    return JsonResponse({'is_active': m.is_active})


# ── Stats JSON ────────────────────────────────────────────────

@staff_required
def stats_data(request):
    cached = cache.get('dash_chart_data')
    if cached:
        return JsonResponse(cached, safe=False)

    today = timezone.now().date()
    days  = [today - timedelta(days=i) for i in range(6, -1, -1)]

    msg_by_day = {
        row['day']: row['c']
        for row in Message.objects
            .filter(timestamp__date__gte=days[0])
            .annotate(day=TruncDate('timestamp'))
            .values('day').annotate(c=Count('id'))
    }
    cmt_by_day = {
        row['day']: row['c']
        for row in RepoComment.objects
            .filter(created_at__date__gte=days[0])
            .annotate(day=TruncDate('created_at'))
            .values('day').annotate(c=Count('id'))
    }

    data = {
        'labels':   [d.strftime('%d/%m') for d in days],
        'messages': [msg_by_day.get(d, 0) for d in days],
        'comments': [cmt_by_day.get(d, 0) for d in days],
        'totals': {
            'users':    CustomUser.objects.count(),
            'active':   CustomUser.objects.filter(is_active=True).count(),
            'messages': Message.objects.count(),
            'comments': RepoComment.objects.count(),
        },
    }
    cache.set('dash_chart_data', data, 300)
    return JsonResponse(data)


# ── Animations toggle ─────────────────────────────────────────

@staff_required
@require_POST
def toggle_animations(request):
    current = request.session.get('no_animations', False)
    request.session['no_animations'] = not current
    return JsonResponse({'no_animations': not current})
