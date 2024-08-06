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
from .models import person_collection

# TODO: UGLY, FIX THIS LATER!!!
base_messages = chat_session.initialize_chat_session()
chat_id = chat_session.generate_chat_id()

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
            return redirect("home")
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
def chat(request):
    # TODO: implement real session management
    username = request.user
    context = {"username": username, "chat_id": chat_id, "base_messages": base_messages}

    if request.method == "POST":
        # return render(request, "base/chat.html", context=context)
        return JsonResponse(base_messages, safe=False)
    return render(request, "base/chat.html", context=context)

# Handles the user's message
@csrf_exempt
def chatSendMessage(request):
    if request.method == 'POST':
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get("content")
        base_messages.append({"role": "user", "content": user_message})
        return JsonResponse(base_messages[-1], safe=False)

    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# Handles the agent's reply
@csrf_exempt
def chatSendResponse(request):
    base_messages.append({"role": "assistant", "content": "Hell is empty, and all the devils are here."})
    return JsonResponse(base_messages[-1:], safe=False)

# UEG code to experiment with MongoDB connections.
def add_person(request):
    records = {
        "first_name": "John",
        "last_name": "Smith",
    }
    person_collection.insert_one(records)
    return HttpResponse(f"New person is added: {records}")

def get_all_people(request):
    people = person_collection.find()
    return HttpResponse(people)