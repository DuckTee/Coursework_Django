from django import forms
from .models import Recipient, Message, Mailing


# --- Форма "Получатель рассылки" ---
class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }


# --- Форма "Управление сообщениями" ---
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body', 'is_published']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 15, 'cols': 80}),
        }


# --- Форма "Рассылка" ---
class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }