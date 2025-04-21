from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('', views.leaderboard_view, name='leaderboard'),
    path('badges/', views.badges_view, name='badges'),
]