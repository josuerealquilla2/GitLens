
from django.urls import path

from Users.views.login_views import LoginView
from Users.views.perfil_view import MyProfileView, PublicProfileView
from Users.views.register_views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('yo',MyProfileView.as_view(), name='mi perfil '),
    path('<str:email>',PublicProfileView.as_view(), name=' perfil-amigo'),
]