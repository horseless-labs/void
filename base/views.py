from django.shortcuts import render, redirect
from django.contrib import messages

# Authentication imports
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .forms import UserForm

from .services import chat_session

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
    chat_id = chat_session.generate_chat_id()
    base_messages = chat_session.initialize_chat_session()
    context = {"chat_id": chat_id, "base_messages": base_messages}
    return render(request, "base/chat.html", context=context)