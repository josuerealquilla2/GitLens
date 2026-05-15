from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from repositorios.models import FavoriteRepo, SavedRepo, ViewHistory, RepoMeta


def _get_or_create_repo(data):
    repo, _ = RepoMeta.objects.update_or_create(
        github_id=str(data['github_id']),
        defaults={
            'name': data.get('name', ''),
            'owner': data.get('owner', ''),
            'owner_avatar': data.get('owner_avatar', ''),
            'description': data.get('description', ''),
            'language': data.get('language', ''),
            'stars': data.get('stars', 0),
            'url': data.get('url', ''),
        }
    )
    return repo


def _repo_dict(repo):
    return {
        'id': repo.github_id,
        'name': repo.name,
        'owner': repo.owner,
        'owner_avatar': repo.owner_avatar,
        'description': repo.description,
        'about': repo.description,
        'language': repo.language,
        'stars': repo.stars,
        'url': repo.url,
        'project_images': [],
    }


# ── FAVORITOS ────────────────────────────────────────
class FavoritosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favs = FavoriteRepo.objects.filter(user=request.user).select_related('repo')
        return Response([_repo_dict(f.repo) for f in favs])

    def post(self, request):
        repo = _get_or_create_repo(request.data)
        fav, created = FavoriteRepo.objects.get_or_create(user=request.user, repo=repo)
        if not created:
            fav.delete()
            return Response({'favorito': False})
        return Response({'favorito': True}, status=status.HTTP_201_CREATED)


class FavoritoCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, repo_id):
        es_fav = FavoriteRepo.objects.filter(user=request.user, repo__github_id=repo_id).exists()
        return Response({'favorito': es_fav})


# ── GUARDADOS ─────────────────────────────────────────
class GuardadosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedRepo.objects.filter(user=request.user).select_related('repo')
        return Response([_repo_dict(s.repo) for s in saved])

    def post(self, request):
        repo = _get_or_create_repo(request.data)
        saved, created = SavedRepo.objects.get_or_create(user=request.user, repo=repo)
        if not created:
            saved.delete()
            return Response({'guardado': False})
        return Response({'guardado': True}, status=status.HTTP_201_CREATED)


class GuardadoCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, repo_id):
        es_guardado = SavedRepo.objects.filter(user=request.user, repo__github_id=repo_id).exists()
        return Response({'guardado': es_guardado})


# ── HISTORIAL ─────────────────────────────────────────
class HistorialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = ViewHistory.objects.filter(user=request.user).select_related('repo')[:50]
        return Response([_repo_dict(h.repo) for h in history])

    def post(self, request):
        repo = _get_or_create_repo(request.data)
        ViewHistory.objects.update_or_create(user=request.user, repo=repo)
        return Response({'ok': True})
