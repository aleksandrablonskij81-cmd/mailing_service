from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Recipient, Message, Mailing, Attempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing as send_mailing_service


# ===== ГЛАВНАЯ СТРАНИЦА =====
def home(request):
    """Главная страница со статистикой"""
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


# ===== ПОЛУЧАТЕЛИ (CRUD) =====
class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно добавлен!')
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель успешно обновлён!')
        return super().form_valid(form)


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Получатель удалён!')
        return super().form_valid(form)


# ===== СООБЩЕНИЯ (CRUD) =====
class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно создано!')
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено!')
        return super().form_valid(form)


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение удалено!')
        return super().form_valid(form)


# ===== РАССЫЛКИ (CRUD) =====
class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        """Обновляем статус каждой рассылки перед показом"""
        mailings = Mailing.objects.all()
        for mailing in mailings:
            mailing.update_status()
        return mailings


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        """Обновляем статус при просмотре"""
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно создана!')
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно обновлена!')
        return super().form_valid(form)


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка удалена!')
        return super().form_valid(form)


# ===== ПОПЫТКИ РАССЫЛОК =====
class AttemptListView(ListView):
    model = Attempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'


# ===== ЗАПУСК РАССЫЛКИ =====
@require_POST
def send_mailing_view(request, pk):
    """Запуск рассылки вручную"""
    success, message = send_mailing_service(pk)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('mailing:mailing_detail', pk=pk)