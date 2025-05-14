from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .forms import RegisterForm, LoginForm, TrainingForm, TrainingFilterForm, ReviewForm
from .models import Training, SportType
from django.db.models import F, ExpressionWrapper, DateTimeField, DurationField
from django.db.models.functions import Cast, Now
from django.utils import timezone
from datetime import timedelta

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
    form = TrainingFilterForm(request.GET)
    trainings = Training.objects.all()

    if form.is_valid():
        if form.cleaned_data['sport']:
            trainings = trainings.filter(sport_type=form.cleaned_data['sport'])
        if form.cleaned_data['organizer']:
            trainings = trainings.filter(organizer=form.cleaned_data['organizer'])
        if form.cleaned_data['location']:
            trainings = trainings.filter(location=form.cleaned_data['location'])
        if form.cleaned_data['date']:
            trainings = trainings.filter(date=form.cleaned_data['date'])
        """if form.cleaned_data['duration']:
            trainings = trainings.filter(duration=form.cleaned_data['duration'])"""
        if form.cleaned_data['max_participants']:
            trainings = trainings.filter(max_participants=form.cleaned_data['max_participants'])
        if form.cleaned_data['is_finished']:
            training_ids = []

            for training in trainings:
                if form.cleaned_data['is_finished'] == 'Завершенные' and training.is_finished:
                    training_ids.append(training.id)
                elif form.cleaned_data['is_finished'] == 'Незавершенные' and not training.is_finished:
                    training_ids.append(training.id)

            trainings = trainings.filter(id__in=training_ids)

        sort_field = form.cleaned_data['sort']
        if sort_field:
            if sort_field == 'sport':
                trainings = trainings.order_by('sport_type__name')
            else:
                trainings = trainings.order_by(sort_field)

    return render(request, 'training_list.html', {
        'form': form,
        'trainings': trainings
    })

def user_logout(request):
    logout(request)
    return redirect('login')  # Перенаправление на страницу входа после выхода

@login_required
def create_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training = self.get_object()
        user = self.request.user

        context['review_form'] = ReviewForm()
        context['can_review'] = (
            training.is_finished and
            user in training.participants.all() and
            not training.reviews.filter(author=user).exists()
        )
        context['has_reviewed'] = training.reviews.filter(author=user).exists()
        context['reviews'] = training.reviews.all()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        training = self.object

        if not training.is_finished or request.user not in training.participants.all():
            return redirect('training_detail', pk=training.pk)

        if training.reviews.filter(author=request.user).exists():
            # У пользователя уже есть отзыв — перенаправим с сообщением
            messages.warning(request, "Вы уже оставили отзыв.")
            return redirect('training_detail', pk=training.pk)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.training = training
            review.save()
            messages.success(request, "Отзыв успешно отправлен.")
            return redirect('training_detail', pk=training.pk)

        # Если форма невалидна — отобразим с ошибками
        context = self.get_context_data()
        context['review_form'] = form
        return self.render_to_response(context)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sport_types'] = SportType.objects.all()
        return context                        

    
class TrainingDeleteView(LoginRequiredMixin, DeleteView):
    model = Training
    template_name = 'training_confirm_delete.html'
    success_url = reverse_lazy('training_list')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.organizer != request.user:
            raise PermissionDenied("Вы не можете удалить эту тренировку")
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def join_training(request, training_id):
    training = get_object_or_404(Training, id=training_id)
    
    if training.is_full():
        messages.error(request, "Все места заняты!")
    elif request.user in training.participants.all():
        messages.info(request, "Вы уже записаны!")
    else:
        training.participants.add(request.user)
        messages.success(request, "Вы успешно записались!")

    return redirect('training_detail', pk=training.id)

@login_required
def leave_training(request, training_id):
    training = get_object_or_404(Training, id=training_id)

    if request.user in training.participants.all():
        training.participants.remove(request.user)
        messages.success(request, "Вы отменили запись.")
    else:
        messages.error(request, "Вы не записаны на эту тренировку!")

    return redirect('training_detail', pk=training.id)