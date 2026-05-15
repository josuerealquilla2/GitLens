from rest_framework import generics, permissions , status
from Users.models.perfil_models import Profile
from Users.serializers.perfil_serializer import ProfileSerializer
from rest_framework.response import Response

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile



class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get(self,request, email ,**kwargs):
        try:
            
            profile = Profile.objects.select_related('user').get(user__email=email)
            serializer = self.get_serializer(profile)

            return Response(serializer.data)
        except Profile.DoesNotExist:
            print('no encontrado')
            return Response({"error": "Perfil no encontrado"}, status=status.HTTP_404_NOT_FOUND)