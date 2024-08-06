from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('update-user/', views.updateUser, name="update-user"),
    
    path('', views.home, name="home"),
    path('chat/<str:chat_id>', views.chat, name="chat"),
    path('chat-send-message/<str:chat_id>', views.chatSendMessage, name="chat-send-message"),
    path('chat-send-response/<str:chat_id>', views.chatSendResponse, name="chat-send-response"),

    path('chat-manager/<int:user_id>', views.chatManager, name="chat-manager")
]