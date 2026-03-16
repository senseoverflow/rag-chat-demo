"""
Simple LLM call using Gemini. Takes a prompt and returns the model's text response.
"""

import google.generativeai as genai


def configure(api_key: str) -> None:
    genai.configure(api_key=api_key)


def generate(api_key: str, prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Send prompt to Gemini and return the generated text.
    """
    configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    if response.text:
        return response.text.strip()
    raise ValueError("Empty or blocked response from model")
