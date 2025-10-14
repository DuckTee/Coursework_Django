from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, Attempt, MailingStats, CustomUser
from .forms import RecipientForm, MessageForm, MailingForm
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import EmailSendError

from .utils import UserAccessMixin, ManagerAccessMixin
from ..mailing_service import settings


def home(request):
    # Подсчет общего количества рассылок
    total_mailings = Mailing.objects.count()

    # Подсчет активных рассылок (статус 'Запущена')
    active_mailings = Mailing.objects.filter(status='Запущена').count()

    # Подсчет уникальных получателей
    unique_recipients = Recipient.objects.count()

    return render(request, 'home.html', {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients
    })

# --- "Пользователь" ---
class UserMailingListView(UserAccessMixin):
    def get_queryset(self):
        return Mailing.objects.filter(created_by=self.request.user)

class ManagerMailingListView(ManagerAccessMixin):
    def get_queryset(self):
        return Mailing.objects.all()

class UserRecipientListView(UserAccessMixin):
    def get_queryset(self):
        return Recipient.objects.filter(created_by=self.request.user)

class ManagerRecipientListView(ManagerAccessMixin):
    def get_queryset(self):
        return Recipient.objects.all()

class UserList(ManagerAccessMixin):
    def get_queryset(self):
        return CustomUser.objects.all()

class BlockUserView(ManagerAccessMixin):
    def post(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        user.is_blocked = True
        user.save()
        return redirect('user_list')


# --- "Получатель рассылки" ---
class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

class RecipientCreateView(CreateView):
    # Создание
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipient_list')

class RecipientUpdateView(UpdateView):
    # Редактирование
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('recipient_list')

class RecipientDeleteView(DeleteView):
    # Удаление
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('recipient_list')


# --- "Управление сообщениями" ---
class MessageListView(ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class MessageCreateView(CreateView):
    # Создание
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('message_list')


class MessageUpdateView(UpdateView):
    # Редактирование
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('message_list')


class MessageDeleteView(DeleteView):
    # Удаление
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


# --- "Рассылка" ---
def mailing_list(request):
    mailings = Mailing.objects.all()
    return render(request, 'mailings/mailing_list.html', {'mailings': mailings})

def mailing_create(request):
    # Создание
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mailing_list')
    else:
        form = MailingForm()
    return render(request, 'mailings/mailing_form.html', {'form': form})

def mailing_edit(request, pk):
    # Редактирование
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        form = MailingForm(request.POST, instance=mailing)
        if form.is_valid():
            form.save()
            return redirect('mailing_list')
    else:
        form = MailingForm(instance=mailing)
    return render(request, 'mailings/mailing_form.html', {'form': form})

def mailing_delete(request, pk):
    # Удаление
    mailing = get_object_or_404(Mailing, pk=pk)
    if request.method == 'POST':
        mailing.delete()
        return redirect('mailing_list')
    return render(request, 'mailings/mailing_confirm_delete.html', {'mailing': mailing})


def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    recipients = mailing.recipients.all()

    for recipient in recipients:
        send_mail(
            mailing.message.subject,
            mailing.message.body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient.email],
            fail_silently=False,
        )

    return redirect('mailing_list')


# --- "Попытки рассылок" ---
def attempts_list(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    attempts = mailing.attempts.all().order_by('-date_time')
    return render(request, 'mailings/attempts_list.html', {
        'attempts': attempts,
        'mailing': mailing
    })


def send_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    recipients = mailing.recipients.all()

    try:
        for recipient in recipients:
            try:
                send_mail(
                    mailing.message.subject,
                    mailing.message.body,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient.email],
                    fail_silently=False
                )
                # Успешная попытка
                Attempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='Письмо успешно отправлено'
                )
            except Exception as e:
                # Ошибка при отправке конкретному получателю
                Attempt.objects.create(
                    mailing=mailing,
                    status='fail',
                    server_response=str(e)
                )
    except Exception as e:
        # Общая ошибка при отправке
        Attempt.objects.create(
            mailing=mailing,
            status='fail',
            server_response=f'Критическая ошибка: {str(e)}'
        )

    return redirect('mailing_list')


# --- "Xранениe статистики" ---
def update_mailing_stats(mailing):
    attempts = Attempt.objects.filter(mailing=mailing)
    total = attempts.count()
    success = attempts.filter(status='success').count()
    fail = attempts.filter(status='fail').count()

    MailingStats.objects.update_or_create(
        mailing=mailing,
        defaults={
            'total_attempts': total,
            'success_attempts': success,
            'fail_attempts': fail
        }
    )


def user_stats(request):
    user = request.user
    stats = MailingStats.objects.filter(user=user).annotate(
        total_mailings=Count('mailing')
    )

    total_success = stats.aggregate(Sum('success_attempts'))['success_attempts__sum'] or 0
    total_fail = stats.aggregate(Sum('fail_attempts'))['fail_attempts__sum'] or 0
    total_attempts = stats.aggregate(Sum('total_attempts'))['total_attempts__sum'] or 0

    context = {
        'stats': stats,
        'total_success': total_success,
        'total_fail': total_fail,
        'total_attempts': total_attempts
    }
    return render(request, 'stats/user_stats.html', context)