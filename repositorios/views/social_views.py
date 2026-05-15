from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import status

from repositorios.models import RepoLike, RepoComment
from repositorios.serializers import RepoCommentSerializer


class RepoLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, repo_id):
        like, created = RepoLike.objects.get_or_create(
            user=request.user,
            repo_github_id=repo_id
        )
        if not created:
            like.delete()
            return Response({'liked': False, 'count': RepoLike.objects.filter(repo_github_id=repo_id).count()})
        return Response({'liked': True, 'count': RepoLike.objects.filter(repo_github_id=repo_id).count()}, status=status.HTTP_201_CREATED)


class RepoLikeCountView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, repo_id):
        count = RepoLike.objects.filter(repo_github_id=repo_id).count()
        liked = False
        if request.user.is_authenticated:
            liked = RepoLike.objects.filter(user=request.user, repo_github_id=repo_id).exists()
        return Response({'count': count, 'liked': liked})


class RepoCommentsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, repo_id):
        comments = RepoComment.objects.filter(repo_github_id=repo_id, parent=None)
        serializer = RepoCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, repo_id):
        serializer = RepoCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, repo_github_id=repo_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RepoCommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = RepoComment.objects.get(id=comment_id, user=request.user)
        except RepoComment.DoesNotExist:
            return Response({'error': 'No encontrado o no autorizado'}, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
