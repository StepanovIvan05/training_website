from django.urls import path
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/')),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('accounts/login/', views.user_login, name='login'),
    # path('login/', TemplateView.as_view(template_name='accounts/login.html'), name='login'),
    # path('accounts/login/', TemplateView.as_view(template_name='accounts/login.html')),
    path('trainings/', views.training_list, name='training_list'),
    path('logout/', views.user_logout, name='logout'),
    path('create-training/', views.create_training, name='create_training'),
    # Детальная страница тренировки
    path('training/<int:pk>/', views.TrainingDetailView.as_view(), name='training_detail'),
    # Редактирование тренировки
    path('training/<int:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_edit'),
    path('training/<int:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),
    path('training/<int:training_id>/join/', views.join_training, name='join_training'),
    path('training/<int:training_id>/leave/', views.leave_training, name='leave_training'),
    # Восстановление пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)