import re

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w.,\- ]', '', text)
    return text.strip()
