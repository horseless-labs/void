from datetime import datetime
import json

from django.shortcuts import render, redirect
from django.contrib import messages

# Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from django.http import HttpResponse

from .forms import UserForm
from .services import chat_session
from .models import Message, Conversation

# TODO: UGLY, FIX THIS LATER!!!
# base_messages = chat_session.initialize_chat_session()
# chat_id = chat_session.generate_chat_id()
# conversation = None

def home(request):
    return render(request, "base/home.html")

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist.")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            conversation = Conversation.objects.create()
            conversation.initialize_chat(username=username)
            # conversation.save()
            # print(conversation)
            return redirect("chat", chat_id=conversation.chat_id)
        else:
            messages.error(request, "Username or password does not exist.")

    context = {"page": page}
    return render(request, "base/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect("home")

def registerPage(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
        else:
            messages.error(request, "An error occurred during registration.")
    
    context = {"form": form}
    return render(request, "base/login_register.html", context)

# TODO: test this later, as it is currently unconnected to anything.
def updateUser(request):
    user = request.user
    form = UserForm(request.POST, instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    
    return render(request, "base/update-user.html", {"form": form})

# TODO: come back to this after handling login/registration
def chat(request, chat_id):
    # TODO: implement real session management
    conversation = Conversation.objects.get(chat_id=chat_id)
    messages = Message.objects.filter(conversation=conversation).order_by('created')

    context = {"username": request.user.username,
               "conversation": conversation,
               "messages": messages,
               "chat_id": chat_id}
    return render(request, "base/chat.html", context=context)

def chatManager(request, pk):
    # Needs to take the user_id, run a query for all chat_ids associated with that user,
    # then pass those chat_ids into manage_chats.html
    user = User.objects.get(id=pk)
    context = {"user": user}
    return render(request, "base/manage_chats.html", context=context)

# Handles the user's message
@csrf_exempt
def chatSendMessage(request, chat_id):
    if request.method == 'POST':
        user_message = request.POST.get("message", "").strip()

        conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)
        user = User.objects.get(username=request.user)

        message = Message.objects.create(
            user=user,
            conversation=conversation,
            role="user",
            body=user_message
        )
        print(message)
        message.save()

        response_data = {
            "user": user.username,
            "content": user_message,
            "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S"),
            "chat_id": conversation.chat_id
        }
        
        # return JsonResponse(response_data, safe=False, status=201)
        return redirect('chat-send-response', chat_id=chat_id)
        # return redirect('chat', chat_id=chat_id)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# Handles the agent's reply
@csrf_exempt
def chatSendResponse(request, chat_id):
    agent_message = "I'm sorry, Dave. I'm afraid I can't do that."

    conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)
    user = User.objects.get(username=request.user)

    message = Message.objects.create(
        user=None,
        conversation=conversation,
        role="agent",
        body=agent_message
    )
    print(message)
    message.save()

    response_data = {
        "user": user.username,
        "content": agent_message,
        "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return redirect("chat", chat_id=chat_id)