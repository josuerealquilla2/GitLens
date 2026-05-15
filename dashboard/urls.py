from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                                        views.dashboard_index,    name='index'),
    path('usuarios/',                               views.dashboard_users,    name='users'),
    path('contenido/',                              views.dashboard_content,  name='content'),
    path('logs/',                                   views.dashboard_logs,     name='logs'),
    path('sistema/',                                views.dashboard_system,   name='system'),

    # AJAX — usuarios
    path('usuarios/<int:user_id>/toggle/',          views.toggle_user_status, name='toggle_user'),
    path('usuarios/<int:user_id>/verified/',        views.toggle_verified,    name='toggle_verified'),
    path('usuarios/<int:user_id>/role/',            views.set_role,           name='set_role'),
    path('usuarios/<int:user_id>/staff/',           views.toggle_staff,       name='toggle_staff'),

    # AJAX — contenido
    path('contenido/<int:comment_id>/delete/',      views.delete_comment,     name='delete_comment'),

    # AJAX — sistema
    path('sistema/mantenimiento/',                  views.toggle_maintenance, name='toggle_maintenance'),
    path('toggle-animations/',                      views.toggle_animations,  name='toggle_animations'),

    # JSON
    path('stats/data/',                             views.stats_data,         name='stats_data'),
]
