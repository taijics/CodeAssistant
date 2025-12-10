try:
    import tiktoken
except Exception:
    tiktoken = None

def count_tokens(text: str, model_enc: str = "cl100k_base") -> int:
    if tiktoken:
        enc = tiktoken.get_encoding(model_enc)
        return len(enc.encode(text))
    return max(1, len(text.split()))