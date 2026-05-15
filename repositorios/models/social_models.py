from django.db import models
from django.conf import settings


class RepoLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='repo_likes')
    repo_github_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'repo_github_id')

    def __str__(self):
        return f"{self.user.email} → {self.repo_github_id}"


class RepoComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='repo_comments')
    repo_github_id = models.CharField(max_length=100)
    body = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.email} en {self.repo_github_id}: {self.body[:40]}"


class RepoMeta(models.Model):
    """Snapshot ligero de metadata de un repo GitHub para no re-llamar la API."""
    github_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    owner = models.CharField(max_length=100)
    owner_avatar = models.URLField(blank=True)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=60, blank=True)
    stars = models.IntegerField(default=0)
    url = models.URLField()

    def __str__(self):
        return f"{self.owner}/{self.name}"


class FavoriteRepo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    repo = models.ForeignKey(RepoMeta, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'repo')

    def __str__(self):
        return f"{self.user.email} ★ {self.repo}"


class SavedRepo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_repos')
    repo = models.ForeignKey(RepoMeta, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'repo')

    def __str__(self):
        return f"{self.user.email} 🔖 {self.repo}"


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='view_history')
    repo = models.ForeignKey(RepoMeta, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'repo')

    def __str__(self):
        return f"{self.user.email} vio {self.repo}"
