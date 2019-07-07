from . import views
from django.urls import path
from django.contrib.auth import logout
urlpatterns = [

    path('login', views.userlogin),
    path('logout', views.userlogout),
    path('log_index', views.log_index),

]