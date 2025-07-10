import app.utils.desensitize as de
"""
    ValidationService handles:
    1. Length control of inputs (rejects absurdly short/long queries)
    2. Detection of sensitive content (FNR, phone, email etc)
    3. Redaction of found sensitive patterns before LLM is called
"""
class ValidationService:
    def __init__(self):
        pass
        
    def detect_sensitive(self, input: str) -> list[str]:
        return de.detect_sensitive_data(input)
    
    def redact_sensitive(self, input: str) -> str:
        return de.remove_sensitive_data(input)
    
    def validate(self, input: str) -> tuple[str, list[str]]:
        if not isinstance(input, str):
            raise ValueError("Input must be a string")

        found = self.detect_sensitive(input)
        redacted = self.redact_sensitive(input) if found else input
        return redacted, found
    
    def validate_length(self, input: str) -> int:
        return de.length_detector(input)
        