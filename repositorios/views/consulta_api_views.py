import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from repositorios.serializers import RepoFilterSerializer


class RepositoriosPopulares(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        # 🔹 validar con serializer
        serializer = RepoFilterSerializer(data=request.GET)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data_validada = serializer.validated_data

        query = data_validada.get('q')
        language = data_validada.get('language')
        stars = data_validada.get('stars')
        page = data_validada.get('page', 1)

        # 🔹 construir query
        filtros = []

        if query:
            filtros.append(query)

        if language:
            filtros.append(f"language:{language}")

        if stars:  #  IMPORTANTE
            filtros.append(f"stars:>{stars}")

        q = " ".join(filtros)

        # 🔹 petición a GitHub
        url = "https://api.github.com/search/repositories"
        params = {
            "q": q,
            "sort": "stars",
            "order": "desc",
            "per_page": 10,
            "page": page
        }

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
        except Exception:
            return Response(
                {"error": "Error al consultar GitHub"},
                status=400
            )

        datos = resp.json().get('items', [])

        repositorios = [
            {
                'name': j['name'],
                'description': j['description'],
                'avatar': j['owner']['avatar_url'],
                'creador': j['owner']['login'],
                'lenguaje': j['language'],
                'numerodeEstrellas': j['stargazers_count'],
                'urlRepos': j['html_url']
            }
            for j in datos
        ]

        return Response(repositorios)