import os
from typing import Tuple

def call_llm(provider: str, model: str, prompt: str) -> Tuple[str, str]:
    """
    Returns: (response_text, provider_info)
    Supports: openai, anthropic
    """
    provider = provider.lower()
    if provider == "openai":
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = resp.choices[0].message.content
        return text, f"openai:{model}"
    elif provider == "anthropic":
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )
        text = "".join([b.text for b in msg.content if b.type == "text"])
        return text, f"anthropic:{model}"
    else:
        raise ValueError(f"Unsupported provider: {provider}")