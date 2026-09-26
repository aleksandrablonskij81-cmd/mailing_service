from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Recipient, Message, Mailing, Attempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing as send_mailing_service


# ===== ГЛАВНАЯ СТРАНИЦА =====
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now(),
        status=Mailing.STATUS_STARTED
    ).count()
    total_recipients = Recipient.objects.count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'total_recipients': total_recipients,
    }
    return render(request, 'mailing/home.html', context)


def is_manager(user):
    return user.groups.filter(name='Менеджер').exists()


# ===== ПОЛУЧАТЕЛИ =====
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Получатель успешно добавлен!')
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def dispatch(self, request, *args, **kwargs):
        recipient = self.get_object()
        if recipient.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете редактировать чужого получателя.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно обновлён!')
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def dispatch(self, request, *args, **kwargs):
        recipient = self.get_object()
        if recipient.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете удалить чужого получателя.')
        return super().dispatch(request, *args, **kwargs)


# ===== СООБЩЕНИЯ =====
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        if message.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете редактировать чужое сообщение.')
        return super().dispatch(request, *args, **kwargs)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def dispatch(self, request, *args, **kwargs):
        message = self.get_object()
        if message.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете удалить чужое сообщение.')
        return super().dispatch(request, *args, **kwargs)


# ===== РАССЫЛКИ =====
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if is_manager(self.request.user):
            mailings = Mailing.objects.all()
        else:
            mailings = Mailing.objects.filter(owner=self.request.user)

        for mailing in mailings:
            mailing.update_status()
        return mailings


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if mailing.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете редактировать чужую рассылку.')
        return super().dispatch(request, *args, **kwargs)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def dispatch(self, request, *args, **kwargs):
        mailing = self.get_object()
        if mailing.owner != request.user and not is_manager(request.user):
            raise PermissionDenied('Вы не можете удалить чужую рассылку.')
        return super().dispatch(request, *args, **kwargs)


# ===== ПОПЫТКИ =====
class AttemptListView(LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Attempt.objects.all()
        return Attempt.objects.filter(mailing__owner=self.request.user)


# ===== ЗАПУСК РАССЫЛКИ =====
@require_POST
def send_mailing_view(request, pk):
    success, message = send_mailing_service(pk)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('mailing:mailing_detail', pk=pk)


# ===== ОТКЛЮЧЕНИЕ РАССЫЛКИ (МЕНЕДЖЕР) =====
@require_POST
def toggle_mailing_view(request, pk):
    if not is_manager(request.user):
        raise PermissionDenied('Только менеджер может отключать рассылки.')

    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_disabled = not mailing.is_disabled
    mailing.save()
    status = 'отключена' if mailing.is_disabled else 'включена'
    messages.success(request, f'Рассылка {status}.')
    return redirect('mailing:mailing_detail', pk=pk)


# ===== СПИСОК ПОЛЬЗОВАТЕЛЕЙ (МЕНЕДЖЕР) =====
from django.contrib.auth import get_user_model

User = get_user_model()


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'mailing/user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not is_manager(request.user):
            raise PermissionDenied('Только менеджер может смотреть список пользователей.')
        return super().dispatch(request, *args, **kwargs)


@require_POST
def toggle_user_active_view(request, pk):
    if not is_manager(request.user):
        raise PermissionDenied('Только менеджер может блокировать пользователей.')

    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'Вы не можете заблокировать себя.')
        return redirect('mailing:user_list')

    user.is_active = not user.is_active
    user.save()
    status = 'разблокирован' if user.is_active else 'заблокирован'
    messages.success(request, f'Пользователь {user.username} {status}.')
    return redirect('mailing:user_list')