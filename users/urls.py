from django.urls import path
from .views import QuestionListView, RegistrationView, UserDetailView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='questions'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='user-detail'),
]
