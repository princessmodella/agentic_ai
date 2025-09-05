import re

def clean_text(text: str) -> str:
    """Basic cleaning of text"""
    text = re.sub(r'\s+', ' ', text)  # remove extra whitespace
    text = re.sub(r'\[[0-9]*\]', '', text)  # remove reference numbers
    text = text.strip()
    return text
