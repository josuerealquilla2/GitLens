from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from Users.serializers import RegisterSerializer

@method_decorator(csrf_exempt, name='dispatch')

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post (self,request):
        print(request.data)
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            print("bien")
            try:
                user = serializer.save()
                print(user)
                return Response({"success":True},status=status.HTTP_201_CREATED)
            except BaseException as e:
                print(serializer.errors)
                return Response({"success":False},status=status.HTTP_400_BAD_REQUEST)
        else:
            #print(serializer.errors)
            #errores=[]
            #for clave , valor  in serializer.errors.items():
            #    for value in valor:
            #        errores.append(str(value))
            #print(errores)
            print(serializer.errors)
            return Response(serializer.errors, status=400)
           # return Response({"errorsBackend":errores},status=status.HTTP_400_BAD_REQUEST)


