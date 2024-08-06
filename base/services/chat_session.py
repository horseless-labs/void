import random
import string

from pymongo import errors

from .db_connection import db
# Helper functions

def generate_chat_id(length=32):
    chat_id = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    # print(f"New chat_id generated: {chat_id}")
    return chat_id

# TODO: replace with real messages
# Prototype to make sure chat turn-taking works.
def initialize_chat_session():
    base_messages = [
        {"role": "system", "content": "You are a helpful assistant" },
        {"role": "agent", "content": "What's a good way to get things done?"},
        {"role": "user", "content": "Just be brave and have no doubt."},
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

    # Will only be added to the agent's messages
    if tokens_cb != None:
        chat_message["total_tokens"] = tokens_cb.total_tokens
        chat_message["prompt_tokens"] = tokens_cb.prompt_tokens
        chat_message["completion_tokens"] = tokens_cb.completion_tokens
        chat_message["total_cost"] = tokens_cb.total_cost

    try:
        result = db.insert_one(chat_message)
        if result.inserted_id:
            print("Chat message saved successfully")
    except errors.PyMongoError as e:
        print(f"An error occurred: {e}")