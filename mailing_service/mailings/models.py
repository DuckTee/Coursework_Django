from django.utils import timezone

from django.db import models
from django.contrib.auth.models import AbstractUser


# --- Модель "Пользователь" ---
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('manager', 'Менеджер')
    ]

    # Отключаем стандартное поле username
    username = None

    # Делаем email обязательным полем для авторизации
    email = models.EmailField(unique=True, verbose_name='Email')

    # Номер телефона
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Номер телефона',
        help_text='Введите номер телефона'
    )

    # Страна
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Страна'
    )

    # Токен
    token = models.CharField(
        max_length=100,
        verbose_name='Токен',
        blank=True,
        null=True
    )

    # Указываем email как уникальное поле для входа
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_blocked = models.BooleanField(default=False)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# --- Модель "Получатель рассылки" ---
class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылок'


# --- Модель "Управление сообщениями" ---
class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    is_published = models.BooleanField(default=False, verbose_name='Опубликовано')

    created_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages'
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']


# --- Модель "Рассылка" ---
class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Создана')
    message = models.ForeignKey('Message', on_delete=models.CASCADE)
    recipients = models.ManyToManyField('Recipient')

    created_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mailings'
    )

    def __str__(self):
        return f"Рассылка {self.id}"


# --- Модель "Попытки рассылок" ---
class Attempt(models.Model):
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE, related_name='attempts')
    date_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('success', 'Успешно'), ('fail', 'Не успешно')])
    server_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Попытка рассылки {self.mailing} от {self.date_time}'


# --- Модель "Xранениe статистики" ---
class MailingStats(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='stats')
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE)
    total_attempts = models.PositiveIntegerField(default=0)
    success_attempts = models.PositiveIntegerField(default=0)
    fail_attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Статистика рассылки {self.mailing} для {self.user}"

    class Meta:
        verbose_name = 'Статистика рассылки'
        verbose_name_plural = 'Статистика рассылок'