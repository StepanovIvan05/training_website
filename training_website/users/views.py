from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .forms import RegisterForm, LoginForm, TrainingForm
from .models import Training

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('training_list')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def training_list(request):
    trainings = Training.objects.all()
    return render(request, 'training_list.html', {'trainings': trainings})

def user_logout(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа после выхода

@login_required
def create_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            training = form.save(commit=False)
            training.organizer = request.user  # Привязываем текущего пользователя
            training.save()
            return redirect('training_list')  # Перенаправление после успешного сохранения
    else:
        form = TrainingForm()
    
    return render(request, 'create_training.html', {'form': form})

class TrainingDetailView(DetailView):
    model = Training
    template_name = 'training_detail.html'
    context_object_name = 'training'

class TrainingUpdateView(LoginRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingForm
    template_name = 'training_edit.html'
    success_url = reverse_lazy('training_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != request.user:
            raise PermissionDenied("Вы не можете редактировать эту тренировку")
        return super().dispatch(request, *args, **kwargs)
    
class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = Training
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('training_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != request.user:
            raise PermissionDenied("Вы не можете удалить эту тренировку")
        return super().dispatch(request, *args, **kwargs)