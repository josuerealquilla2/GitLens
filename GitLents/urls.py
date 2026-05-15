"""
URL configuration for GitLents project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static

from repositorios.views.consulta_api_views import RepositoriosPopulares
from repositorios.views.api_PerfilLogueado_views import ReposPorEstrellasView
from repositorios.views.categoria_lenguajes_views import ReposPorLenguajeView

urlpatterns = [
   path('admin/', admin.site.urls),
   path('api/users/', include('Users.urls')),
   path('api/repos/', include('repositorios.urls')),
   path('api/friends/', include('Friends.urls')),
   path('api/chat/',    include('Chat.urls')),
   path('panel/',       include('dashboard.urls')),


# path('api/repositorios/populares/',RepositoriosPopulares.as_view()),

   #  path('api/repositorios/',ReposPorEstrellasView.as_view()),
   #path('api/', ReposPorEstrellasView.as_view()),,
   path('api/repositorios/', ReposPorLenguajeView.as_view()),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
