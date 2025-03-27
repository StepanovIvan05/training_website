from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('trainings/', views.training_list, name='training_list'),
    path('logout/', views.user_logout, name='logout'),
    path('create-training/', views.create_training, name='create_training'),
    # Детальная страница тренировки
    path('training/<int:pk>/', views.TrainingDetailView.as_view(), name='training_detail'),
    # Редактирование тренировки
    path('training/<int:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_edit'),
    path('training/<int:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),
]