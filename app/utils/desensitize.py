import re

# Patterns to detect different types of sensitive data
SENSITIVE_PATTERNS = {
    r'\b\d{11}\b': 'FNR',  # Norwegian national ID
    r'\b\d{6}[- ]?\d{5}\b': 'DNR',  # D-numbers
    r'\b\d{4} \d{2} \d{5}\b': 'ACCOUNT',  # Bank account number
    r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b': 'CARD',  # Credit card number
    r'\b[A-Z]{2}\d{6}\b': 'PASSPORT',  # Passport number (simplified)
}


# Detect types of sensitive data in the input text
def detect_sensitive_data(text: str) -> list[str]:
    """Detect types of sensitive data in the input text."""
    found = set()
    for pattern, label in SENSITIVE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.add(label)
    return list(found)


# Replace sensitive data in the input text with redacted labels
def remove_sensitive_data(text: str) -> str:
    """Replace sensitive data in the input text with redacted labels."""
    for pattern, label in SENSITIVE_PATTERNS.items():
        text = re.sub(pattern, f'[REDACTED_{label}]', text, flags=re.IGNORECASE)
    return text
