from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('update-user/', views.updateUser, name="update-user"),
    
    path('', views.home, name="home"),
    path('chat/', views.chat, name="chat"),
    path('chat-send-message/', views.chatSendMessage, name="chat-send-message"),
    path('chat-send-response/', views.chatSendResponse, name="chat-send-response"),
]