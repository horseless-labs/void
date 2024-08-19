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

    path('submit-journal-entry/<str:username>', views.journal, name="submit-journal-entry"),

    path('chat-manager/<str:username>', views.chatManager, name="chat-manager"),
    path('create-new-chat/<str:username>', views.createNewChat, name="create-new-chat"),

    path('ask/<str:username>', views.ask, name='ask'),
    path('send-faiss-query/<str:username>', views.sendFaissQuery, name="send-faiss-query"),
    path('send-faiss-response/<str:username>', views.sendFaissResponse, name="send-faiss-response")
]