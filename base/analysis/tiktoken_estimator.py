import sys
import tiktoken

def estimate_tokens(text, model="gpt-3.5-turbo", cost_per_megatoken=1.50):
    tokenizer = tiktoken.encoding_for_model(model)

    with open(file_path, 'r') as file:
        text = file.read()

    tokens = tokenizer.encode(text)
    num_tokens = len(tokens)
    cost = (num_tokens / 1000000) * cost_per_megatoken
    return num_tokens, cost

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage python estimate_tokens.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_tokens, cost = estimate_tokens(file_path)
    print(f"Estimated number of tokens: {num_tokens}")
    print(f"Estimate cost to ingest: ${cost}")