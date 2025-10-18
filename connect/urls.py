from django.urls import path
from . import views

urlpatterns = [
    path('suggestions/', views.suggestions, name='suggestions'),
    path('friends/', views.friends_view, name='friends'),

    path('friend-requests/', views.friend_requests, name='friend_requests'),

    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
    path('cancel-request/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('decline-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),

    path('', views.home, name='home'),
]
