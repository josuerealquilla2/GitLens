from django.urls import path
from repositorios.views.social_views import (
    RepoLikeToggleView, RepoLikeCountView, RepoCommentsView, RepoCommentDeleteView,
)
from repositorios.views.categoria_lenguajes_views import (
    ReposPopularesPublicosView, ReposTendenciasView,
)
from repositorios.views.user_collections_views import (
    FavoritosView, FavoritoCheckView, GuardadosView, GuardadoCheckView, HistorialView,
)

urlpatterns = [
    # Social
    path('<str:repo_id>/like/', RepoLikeToggleView.as_view()),
    path('<str:repo_id>/likes/', RepoLikeCountView.as_view()),
    path('<str:repo_id>/comments/', RepoCommentsView.as_view()),
    path('comments/<int:comment_id>/', RepoCommentDeleteView.as_view()),

    # Públicos
    path('populares/', ReposPopularesPublicosView.as_view()),
    path('tendencias/', ReposTendenciasView.as_view()),

    # Colecciones de usuario
    path('favoritos/', FavoritosView.as_view()),
    path('favoritos/<str:repo_id>/check/', FavoritoCheckView.as_view()),
    path('guardados/', GuardadosView.as_view()),
    path('guardados/<str:repo_id>/check/', GuardadoCheckView.as_view()),
    path('historial/', HistorialView.as_view()),
]
