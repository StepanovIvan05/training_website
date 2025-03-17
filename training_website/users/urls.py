from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('trainings/', views.training_list, name='training_list'),
    path('logout/', views.user_logout, name='logout'),
]