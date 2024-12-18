import asyncio

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models

# Authentication imports
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

from .forms import UserForm, MyUserCreationForm
from .services import agent_spec, vectorize, chat_session
from .models import Message, Conversation, User, TokenUsage
from .analysis import partition_blogs as pb

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
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)

            # Creates a FAISS index unique to the user.
            vectorize.open_or_create_faiss_index(user.username)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration.")
    else:
        form = MyUserCreationForm()
    
    context = {"form": form}
    return render(request, "base/login_register.html", context)

@login_required(login_url='login')
def userProfile(request, username):
    user = User.objects.get(username=username)
    context = {"user": user}
    return render(request, "base/profile.html", context=context)

# TODO: test this later, as it is currently unconnected to anything.
@login_required(login_url='login')
def updateUser(request):
    user = request.user

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", username=user.username)
    else:
        form = UserForm(instance=user)
        print(form.errors)

    return render(request, "base/update_user.html", {"form": form})

@login_required(login_url='login')
def journal(request, username):
    user = User.objects.get(username=username)
    conversation = Conversation.objects.create(user=user)

    conversation.initialize_chat(username=username)
    context = {"chat_id": conversation.chat_id}
    return render(request, "base/journal.html", context=context)

@login_required(login_url='login')
def uploadJournal(request, username):
    context = {"username": username}

    if request.method == 'POST':
        uploaded_file = request.FILES.get('text_file')
        if uploaded_file:
            file_content = uploaded_file.read().decode('utf-8')
            entries = pb.read_journal_string(file_content)
            print(entries[0])

            # file_name = default_storage.save(uploaded_file.name, ContentFile(file_content))

            # user = request.user
            for entry in entries:
                user = User.objects.get(username=username)
                print(user)
                # Currently, every one of these journal entries gets their own Conversation.
                chat_id = chat_session.generate_chat_id()
                # conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)
                conversation = Conversation.objects.create(user=user)
                conversation.initialize_journal_entry(datetime=entry[0], content=entry[1], username=username, chat_id=chat_id)
                conversation.save()

                message = Message.objects.create(
                    user=user,
                    # In this implementation, a journal entry also has a unique chat id
                    # This will make it visible in the Chat Manager
                    chat_id=chat_id,
                    role="user",
                    body=entry[1],
                )
                message.save()

            return redirect("chat-manager", username=username)
    return render(request, "base/journal_upload.html", context=context)

@csrf_exempt
def sendJournal(request, chat_id):
    if request.method == "POST":
        journal_entry = request.POST.get("journal_entry", "").strip()
        print(journal_entry)
        
        conversation, created = Conversation.objects.get_or_create(chat_id=chat_id)

        username = conversation.user.username
        user = User.objects.get(username=username)

        # Currently saving Journals the same way as Messages.
        # Might change later.
        # This way does allow a user to discuss single documents in the same way as the rest of their chats.
        message = Message.objects.create(
            user=user,
            # In this implementation, a journal entry also has a unique chat id
            # This will make it visible in the Chat Manager
            chat_id=chat_id,
            role="user",
            body=journal_entry
        )

        message.save()

        try:
            faiss_index = f"base/indices/{request.user.username}_faiss_index"
            vectorize.add_string_to_store(message.body, faiss_index)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Failed to add the message to the index.")
    
        context = {"user": request.user.username}
    # return redirect('journal', username=request.user.username)
    return redirect('redirect-journal', chat_id=chat_id)

@csrf_exempt
def redirectJournalOrChatManager(request, chat_id):
    context = {"chat_id": chat_id,
               "username": request.user.username}
    return render(request, "base/journal_redirect.html", context=context)

# A page where the user can query their own documents.
# Unsure if this will make it into the final implementation.
# It is here for testing purposes.
@login_required(login_url='login')
def ask(request, username):
    user = User.objects.get(username=username)

    # Query of the index will not be persisted; it is easier to
    # store this in the session.
    ask_convo = request.session.get("ask_convo", [])
    context = {"user": user, "conversation": ask_convo}
    return render(request, "base/query_chats.html", context=context)

@csrf_exempt
def sendFaissQuery(request, username):
    if request.method == 'POST':
        user_query = request.POST.get("message").strip()
        ask_convo = request.session.get("ask_convo", [])
        ask_convo.append({"role": "user", "content": user_query})

        request.session["ask_convo"] = ask_convo
        return redirect('send-faiss-response', username=username)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

@csrf_exempt
def sendFaissResponse(request, username):
    ask_convo = request.session.get("ask_convo")
    faiss_index = f"base/indices/{username}_faiss_index"

    # Uses ask_store(), the LLM version of search for FAISS here.
    # query_store() acts as a more raw search engine
    response = vectorize.ask_store(ask_convo[-1]["content"], faiss_index)

    ask_convo.append({"role": "agent", "content": response})
    request.session["ask_convo"] = ask_convo
    return redirect("ask", username=username)

# Base chat interface. Starts here, then routes to chatSendMessage() and chatSendResponse()
@login_required(login_url='login')
def chat(request, chat_id):
    conversation = Conversation.objects.get(chat_id=chat_id)
    print(chat_id)
    print(conversation)
    print(conversation.user)
    print(request.user.username)

    if conversation.user.username != request.user.username:
        print(conversation.user_id)
        print(request.user.username)
        return render(request, "base/403.html")

    messages = Message.objects.filter(chat_id=chat_id).order_by('created')
    for message in messages:
        print(f"ID: {message.id}")
        print(f"User: {message.user}")
        print(f"Role: {message.get_role_display()}")  # Uses choices to display the human-readable role
        print(f"Chat ID: {message.chat_id}")
        print(f"Body: {message.body}")
        print(f"Created: {message.created}")
        print(f"Updated: {message.updated}")
        print("-" * 40)  # Separator for readability

    context = {"username": request.user.username,
               "conversation": conversation,
               "messages": messages,
               "chat_id": chat_id}
    return render(request, "base/chat.html", context=context)

# View that shows the viewer a list of their chats.
@login_required(login_url='login')
def chatManager(request, username):
    if request.user.username != username:
        return render(request, "base/403.html")

    user = User.objects.get(username=username)
    chat_ids = Message.objects.filter(user=user).distinct().values_list("chat_id", flat=True)
    context = {"user": user, "chat_ids": chat_ids}

    return render(request, "base/manage_chats.html", context=context)

# This is referred to in base/manage_chats.html
# It only feels redundant. Grab a coffee.
@login_required(login_url='login')
def createNewChat(request, username):
    user = User.objects.get(username=username)

    conversation = Conversation.objects.create(
        user=user,
    )
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

        message.save()

        try:
            faiss_index = f"base/indices/{request.user.username}_faiss_index"
            vectorize.add_string_to_store(message.body, faiss_index)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Failed to add the message to the index.")

        response_data = {
            "user": user.username,
            "content": user_message,
            "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S"),
            "chat_id": conversation.chat_id
        }

        # TODO: review code to determine if this is redundant. There is also one in chatSendResponse()
        # Stores the most recent message from the user in the Django session
        request.session["mr_human_message"] = user_message
        
        # return redirect('chat-send-response', chat_id=chat_id)
        return JsonResponse(response_data)
    return JsonResponse({"error": "Only POST method is allowed"}, status=405)

# Handles the agent's reply
@csrf_exempt
def chatSendResponse(request, chat_id):
    # Check the user's total spending
    # NOTE: this is implemented in this way because this is a demonstration; a recruiter shouldn't
    #       use too many tokens.
    # NOTE: this could be fleshed out to manage users to e.g. better manage large numbers of users,
    #       help prevent the formation of parasocial relationships, etc.
    # TODO: expand this in monetized production
    user = User.objects.get(username=request.user)
    total_spent = TokenUsage.objects.filter(user=user).aggregate(models.Sum('total_cost'))['total_cost__sum'] or 0

    if total_spent >= 0.01:
        return JsonResponse({"error": "Token usage limit exceeded"}, status=401)
    
    message = request.session["mr_human_message"]
    agent, tt_cb = agent_spec.init_agent(chat_id)
    # agent_message = await agent_spec.get_agent_output(agent, message, chat_id)
    agent_message = asyncio.run(agent_spec.get_agent_output(agent, message, chat_id))
    print(f"tt_cb from chatSendResponse(): {tt_cb.get_tokens_info()}")
    tokens_used, response_tokens, cost = tt_cb.get_tokens_info()

    user = User.objects.get(username=request.user)

    message = Message.objects.create(
        user=None,
        chat_id=chat_id,
        role="agent",
        body=agent_message["output"]
    )

    message.save()

    tokens = TokenUsage.objects.create(
        user=user,
        conversation=Conversation.objects.get(chat_id=chat_id),
        tokens_used=tokens_used,
        # response_tokens=response_tokens,
        total_cost=cost
    )
    tokens.save()

    try:
        faiss_index = f"base/indices/{request.user.username}_faiss_index"
        vectorize.add_string_to_store(agent_message["output"], faiss_index)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Failed to add the message to the index.")

    response_data = {
        "user": user.username,
        "content": agent_message,
        "timestamp": message.created.strftime("%Y-%m-%d %H:%M:%S"),
        "chat_id": chat_id
    }
    
    return JsonResponse(response_data)

def recruiterView(request):
    return render(request, "base/recruiters.html")