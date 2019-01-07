from rest_framework.routers import DefaultRouter
from django.urls import path

from voting_app import views, apiviews


app_name = 'polls'


router = DefaultRouter()
router.register(r'', apiviews.PollViewSet, basename='poll')
# router.register(r'<int:pk>/', apiviews.ChoiceViewSet)

urlpatterns = [
    # path('', views.poll_list, name='poll_list'),
    # path('<int:pk>/', views.poll_detail, name='poll_detail'),
    # path('', apiviews.PollList.as_view(), name='poll_list'),
    # path('<int:pk>/', apiviews.PollDetail.as_view(), name='poll_detail'),
    path('create/', apiviews.CreatePoll.as_view(), name='create_poll'),
    path('<int:pk>/choices/', apiviews.ChoiceList.as_view(), name='choice-list'),
    path('<int:pk>/choices/<int:choice_pk>/', apiviews.ChoiceDetail.as_view(), name='choice-detail'),
]


urlpatterns += router.urls