import random
import string
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