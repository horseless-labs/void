from datetime import datetime
import json, os

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

# Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from django.http import HttpResponse

from .forms import UserForm
from .services import agent_spec, vectorize
from .models import Message, Conversation

# TODO: get rid of this when development is done
faiss_index = "base/services/faiss_index"

def home(request):
    user = request.user
    
    if user.is_authenticated:
        return redirect('chat-manager', username=user)
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
            return redirect("chat-manager", username=username)
        else:
            messages.error(request, "Username or password does not exist.")

    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")

def registerPage(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration.")
    else:
        form = UserCreationForm()
    
    context = {"form": form}
    return render(request, "base/login_register.html", context)

# TODO: test this later, as it is currently unconnected to anything.
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(request.POST, instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)
    
    return render(request, "base/update-user.html", {"form": form})

@login_required(login_url='login')
def chat(request, chat_id):
    conversation = Conversation.objects.get(chat_id=chat_id)

    if conversation.user.username != request.user.username:
        print(conversation.user_id)
        print(request.user.username)
        return render(request, "base/403.html")

    messages = Message.objects.filter(chat_id=chat_id).order_by('created')

    context = {"username": request.user.username,
               "conversation": conversation,
               "messages": messages,
               "chat_id": chat_id}
    return render(request, "base/chat.html", context=context)

@login_required(login_url='login')
def chatManager(request, username):
    if request.user.username != username:
        return render(request, "base/403.html")

    user = User.objects.get(username=username)
    chat_ids = Message.objects.filter(user=user).distinct().values_list("chat_id", flat=True)
    context = {"user": user, "chat_ids": chat_ids}
    return render(request, "base/manage_chats.html", context=context)

@login_required(login_url='login')
def createNewChat(request, username):
    user = User.objects.get(username=username)
    conversation = Conversation.objects.create(
        user=user,
    )
    print(f"conversation.user: {conversation.user}")
    conversation.initialize_chat(username=username)
    return redirect("chat", chat_id=conversation.chat_id)

# Handles the user's message
@csrf_exempt
def chatSendMessage(request, chat_id):
    if request.method == 'POST':
        user_message = request.POST.get("message", "").strip()

        conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)
        user = User.objects.get(username=request.user)

        message = Message.objects.create(
            user=user,
            chat_id=chat_id,
            role="user",
            body=user_message
        )
        print(message)
        message.save()

        try:
            print(f"Attempting to add the message {message.body} to the default index")
            vectorize.add_string_to_store(message.body, faiss_index)
            print("Success")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Failed to add the message to the index.")

        response_data = {
            "user": user.username,
            "content": user_message,
            "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S"),
            "chat_id": conversation.chat_id
        }

        # Stores the most recent message from the user in the Django session
        request.session["mr_human_message"] = user_message
        
        return redirect('chat-send-response', chat_id=chat_id)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# Handles the agent's reply
@csrf_exempt
def chatSendResponse(request, chat_id):
    message = request.session["mr_human_message"]
    agent = agent_spec.init_agent(chat_id)
    agent_message = agent_spec.get_agent_output(agent, message, chat_id)

    conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)
    user = User.objects.get(username=request.user)

    message = Message.objects.create(
        user=None,
        chat_id=chat_id,
        role="agent",
        body=agent_message["output"]
    )
    print(message)
    message.save()

    try:
        print(f"Attempting to add the message {message.body} to the default index")
        vectorize.add_string_to_store(agent_message["output"], faiss_index)
        print("Success")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Failed to add the message to the index.")

    response_data = {
        "user": user.username,
        "content": agent_message,
        "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return redirect("chat", chat_id=chat_id)