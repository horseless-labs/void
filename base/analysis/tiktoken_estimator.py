import sys
import tiktoken

def estimate_tokens(text, model="gpt-3.5-turbo"):
    tokenizer = tiktoken.encoding_for_model(model)

    with open(file_path, 'r') as file:
        text = file.read()

    tokens = tokenizer.encode(text)
    return len(tokens)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage python estimate_tokens.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_tokens = estimate_tokens(file_path)
    print(f"Estimated number of tokens: {num_tokens}")