# ============================================
# CHANDU AI LAB - ROUTER
# Stable Multi-Model Control Layer
# ============================================

import requests

OLLAMA_GENERATE_URL = "http://localhost:11434/api/generate"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

# 🔒 Locked Model Configuration
GENERAL_MODEL = "mistral"
CODE_MODEL = "codellama:34b"
REASONING_MODEL = "llama3:34b"


# ==================================================
# Model Selection
# ==================================================
def choose_model(prompt: str) -> str:
    lower_prompt = prompt.lower().strip()

    greetings = [
        "hi", "hello", "hey",
        "hi how are you", "how are you",
        "good morning", "good evening"
    ]

    if lower_prompt in greetings:
        return GENERAL_MODEL

    if any(keyword in lower_prompt for keyword in [
        "code", "python", "function", "class", "error",
        "bug", "debug", "script", "algorithm",
        "implement", "build", "create", "write",
        "integrate", "add", "module"
    ]):
        return CODE_MODEL

    if any(keyword in lower_prompt for keyword in [
        "explain deeply", "derive", "proof",
        "step by step", "why does", "theory"
    ]):
        return REASONING_MODEL

    return GENERAL_MODEL


# ==================================================
# System Prompt Builder
# ==================================================
def get_system_prompt(model_name: str) -> str:

    if model_name == CODE_MODEL:
        return """
You are a professional Python developer.

Write clean, properly formatted, multi-line Python code.

Requirements:
- The code must be complete and runnable.
- Use proper indentation (4 spaces).
- Use correct __init__ where needed.
- Include example usage under:

if __name__ == "__main__":

Do not include explanations.
Return only Python code.
"""

    elif model_name == REASONING_MODEL:
        return """
You are an analytical reasoning engine.

Rules:
- Provide structured step-by-step reasoning.
- Be precise and logical.
- Avoid fluff.
- Do not provide code unless explicitly requested.
"""

    else:
        return """
You are a friendly AI assistant.
Respond naturally and briefly.
Do not provide technical explanations unless requested.
"""


# ==================================================
# Core Response Generator (Hybrid Mode)
# ==================================================
def generate_response(
    prompt: str,
    model: str = None,
    creator_mode: bool = False
) -> str:

    model_name = model if model else choose_model(prompt)

    print("\n==============================")
    print("SELECTED MODEL:", model)
    print("FINAL MODEL USED:", model_name)
    print("CREATOR MODE:", creator_mode)
    print("==============================\n")

    system_message = get_system_prompt(model_name)

    # 🟢 USE CHAT FOR GENERAL + CODE
    if model_name in [GENERAL_MODEL, CODE_MODEL]:

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.2}
        }

        try:
            response = requests.post(
                OLLAMA_CHAT_URL,
                json=payload,
                timeout=300
            )
            response.raise_for_status()

            result = response.json()

            if "message" in result and "content" in result["message"]:
                return result["message"]["content"].strip()

            return "⚠️ Invalid chat response format."

        except Exception as e:
            return f"⚠️ Chat Error: {str(e)}"

    # 🔵 USE GENERATE FOR REASONING
    full_prompt = f"{system_message}\n\nUSER REQUEST:\n{prompt}\n\nRESPONSE:"

    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=300
        )
        response.raise_for_status()

        result = response.json()

        if "response" in result:
            return result["response"].strip()

        return "⚠️ Invalid generate response format."

    except Exception as e:
        return f"⚠️ Generate Error: {str(e)}"

    # ==================================================
    # 🔵 CREATOR MODE or CODE/REASONING → Use GENERATE
    # ==================================================
    system_message = get_system_prompt(model_name)

    full_prompt = f"{system_message}\n\nUSER REQUEST:\n{prompt}\n\nRESPONSE:"

    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }

    try:
        response = requests.post(
            OLLAMA_GENERATE_URL,
            json=payload,
            timeout=300
        )
        response.raise_for_status()

        result = response.json()

        if "response" in result:
            content = result["response"].strip()

            # Clean tokenizer artifacts
            content = content.replace("<｜begin▁of▁sentence｜>", "")
            content = content.replace("<｜end▁of▁sentence｜>", "")

            # Remove markdown fences
            content = content.replace("```python", "")
            content = content.replace("```", "")

            return content.strip()

        return "⚠️ Invalid generate response format."

    except requests.exceptions.Timeout:
        return "⚠️ Request timed out."

    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to Ollama."

    except Exception as e:
        return f"⚠️ Generate Error: {str(e)}"