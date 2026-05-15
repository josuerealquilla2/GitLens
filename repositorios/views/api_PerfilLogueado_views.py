import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ReposPorEstrellasView(APIView):
    def get(self, request):
        stars = request.query_params.get('stars', '100')
        try:
            url = f"https://api.github.com/search/repositories?q=stars:>{stars}&sort=stars&order=desc&per_page=20"
            headers = {"Accept": "application/vnd.github+json"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json().get("items", [])
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Error al consultar GitHub", "status": response.status_code},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)