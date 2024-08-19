import random
import string

# Helper functions

def generate_chat_id(length=64):
    chat_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # print(f"New chat_id generated: {chat_id}")
    return chat_id

# TODO: replace with real messages
def initialize_chat_session():
    base_messages = [
        {"role": "system", "content": "You are a helpful assistant" },
        {"role": "agent", "content": "What's on your mind?"},
    ]
    return base_messages

def save_message(chat_id, user_id, username, message, timestamp, tokens_cb=None):
    chat_message = {
        "chat_id": chat_id,
        "user_id": user_id,
        "username": username,
        "message": message,
        "timestamp": timestamp,
    }

    # TODO: Add these to Messages
    # Will only be added to the agent's messages
    # Null otherwise
    if tokens_cb != None:
        chat_message["user_id"] = "agent" # TODO: think if this is a good way of doing this
        chat_message["total_tokens"] = tokens_cb.total_tokens
        chat_message["prompt_tokens"] = tokens_cb.prompt_tokens
        chat_message["completion_tokens"] = tokens_cb.completion_tokens
        chat_message["total_cost"] = tokens_cb.total_cost