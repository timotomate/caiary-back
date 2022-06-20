from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import (
    TokenVerifyView
)

urlpatterns = [
    path('me/', views.get_my_profile, name='get_my_profile'),
    path('profile/<int:user_pk>/', views.get_profile, name='get_profile'),
    path('profile/', views.get_profile_by_email, name='get_profile_by_email'),
    path('search/', views.get_profile_by_username, name='get_profile_by_username'),
    path('login/kakao/', views.kakao_login, name='kakao_login'),
    path('login/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('follow/<int:user_pk>/', views.follow_user, name='follow_user'),
    path('username/<int:user_pk>/', views.update_username, name='update_username'),
    path('list/', views.get_user_list_by_id, name='get_user_list_by_id')

]
