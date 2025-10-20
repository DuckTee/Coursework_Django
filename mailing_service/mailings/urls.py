from django.urls import path
from django.views.decorators.cache import cache_page

from . import views
from .views import (
    RecipientListView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDeleteView,
    MessageListView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,
    mailing_list,
    mailing_create,
    mailing_edit,
    mailing_delete,
    attempts_list,
    send_mailing,
    home,
    user_stats,
)

urlpatterns = [
    path('', home, name='home'),

    # --- "Пользователь" ---

    # --- "Получатель рассылки" ---
    path('recipients/', cache_page(60)(RecipientListView.as_view()), name='recipient_list'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    # --- "Управление сообщениями" ---
    path('messages/', cache_page(60)(MessageListView.as_view()), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    # --- "Рассылка" ---
    path('', mailing_list, name='mailing_list'),
    path('create/', mailing_create, name='mailing_create'),
    path('edit/<int:pk>/', mailing_edit, name='mailing_edit'),
    path('delete/<int:pk>/', mailing_delete, name='mailing_delete'),
    path('send/<int:pk>/', views.send_mailing, name='send_mailing'),

    # --- "Попытки рассылок" ---
    path('attempts/<int:pk>/', attempts_list, name='attempts_list'),
    path('send/<int:pk>/', send_mailing, name='send_mailing'),

    # --- "Xранениe статистики" ---
    path('stats/', user_stats, name='user_stats'),
]