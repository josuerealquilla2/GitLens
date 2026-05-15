from django.contrib import admin
from repositorios.models import RepoLike, RepoComment

@admin.register(RepoLike)
class RepoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'repo_github_id', 'created_at')
    list_filter = ('repo_github_id',)

@admin.register(RepoComment)
class RepoCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'repo_github_id', 'body', 'parent', 'created_at')
    list_filter = ('repo_github_id',)
