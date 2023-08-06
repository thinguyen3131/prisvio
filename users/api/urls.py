from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('clone/', views.clone_user, name='clone_user'),
    path('changepassword/', views.change_password, name='change_password'),
]