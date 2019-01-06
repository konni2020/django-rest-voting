from django.urls import path

from voting_app import views


app_name = 'polls'

urlpatterns = [
    path('', views.poll_list, name='poll_list'),
    path('<int:pk>/', views.poll_list, name='poll_detail'),
]