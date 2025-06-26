import re

SENSITIVE_PATTERNS = {
    r'\b\d{11}\b': 'FNR',  # Norwegian national ID
    r'\b\d{6}[- ]?\d{5}\b': 'DNR',  # D-number
    r'\b\d{9}\b': 'ORGNR',  # Organization number
    r'\b\d{4} \d{2} \d{5}\b': 'ACCOUNT',  # Bank account number
    r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b': 'CARD',  # Credit card number
    r'\b\d{8}\b': 'PHONE',  # Phone number
    r'[\w\.-]+@[\w\.-]+\.\w+': 'EMAIL',  # Email
    r'https?://[^\s]+': 'URL',  # URLs
    r'\b[A-Z]{2}\d{6}\b': 'PASSPORT',  # Passport number (simplified)
    r'\b\d{2}[-/]\d{2}[-/]\d{4}\b': 'DATE',  # Date formats
    r'\b[\wæøåÆØÅ.\- ]{2,},?\s+\d{4,5}\s+[A-ZÆØÅ][\wæøåÆØÅ]+': 'ADDRESS',  # Simplified address
}


def detect_sensitive_data(text: str) -> list[str]:
    """Detect types of sensitive data in the input text."""
    found = set()
    for pattern, label in SENSITIVE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.add(label)
    return list(found)


def remove_sensitive_data(text: str) -> str:
    """Replace sensitive data in the input text with redacted labels."""
    for pattern, label in SENSITIVE_PATTERNS.items():
        text = re.sub(pattern, f'[REDACTED_{label}]', text, flags=re.IGNORECASE)
    return text
