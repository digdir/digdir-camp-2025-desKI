import os
import re
import argparse
import csv
from datetime import datetime
from typing import List, Tuple, Optional, Dict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Main application configuration
CONFIG: Dict[str, Dict[str, str]] = {
    "files": {
        "default_input": "vault.txt",
        "default_output": "resultat.csv",
        "error_log": "error_log.txt"
    },
    "colors": {
        "CYAN": '\033[96m',
        "GREEN": '\033[92m',
        "RED": '\033[91m',
        "YELLOW": '\033[93m',
        "RESET": '\033[0m'
    }
}

# Regex patterns for text identification - COMPILED for performance
PATTERNS = {
    "timestamp": re.compile(r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]'),
    "question": re.compile(r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]\s*\[\s*Ekstern\s*e-post\s*\]\s*(.*)'),
    "answer": re.compile(r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]\s*(?!\[\s*Ekstern\s*e-post\s*\])(.*)'),
}

# For backward compatibility - compiled versions
TIMESTAMP_PATTERN = PATTERNS["timestamp"]
QUESTION_PATTERN = PATTERNS["question"]
ANSWER_PATTERN = PATTERNS["answer"]



# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def log_message(message: str, color_key: str = "GREEN") -> None:
    color = CONFIG["colors"].get(color_key, CONFIG["colors"]["GREEN"])
    reset = CONFIG["colors"]["RESET"]
    print(f"{color}{message}{reset}")


def log_error(message: str, context: str = "", write_to_file: bool = True) -> None:
    if write_to_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(CONFIG["files"]["error_log"], "a", encoding="utf-8") as err_log:
                err_log.write(f"[{timestamp}] {message}\n")
                if context:
                    err_log.write(f"Context: {context}...\n\n")
        except IOError as e:
            print(f"Kunne ikke skrive til error log: {e}")
   
    log_message(f"{message}", "RED")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Konverter service desk data til CSV format uten AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--include-predefined", 
        action="store_true",
        help="Inkluder forhåndsdefinerte spørsmål-svar par i utdataene"
    )
    parser.add_argument(
        "--input", "-i", 
        type=str, 
        default=CONFIG["files"]["default_input"],
        help="Navn på inndatafil eller mappe"
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default=CONFIG["files"]["default_output"],
        help="Navn på utdata CSV fil"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Skriv ut ekstra debug informasjon"
    )
    return parser.parse_args()

# ============================================================================
# FILE HANDLING
# ============================================================================
def load_input_file(filename: str) -> Optional[str]:
    if not os.path.exists(filename):
        log_error(f"Filen '{filename}' ble ikke funnet.")
        return None
   
    try:
        # Use larger buffer for faster reading of large files
        with open(filename, "r", encoding="utf-8", buffering=65536) as f:
            return f.read()
    except Exception as e:
        log_error(f"Kunne ikke lese filen '{filename}': {str(e)}")
        return None


def load_input_directory(directory: str) -> Optional[str]:
    if not os.path.exists(directory):
        log_error(f"Mappen '{directory}' ble ikke funnet.")
        return None

    if not os.path.isdir(directory):
        log_error(f"'{directory}' er ikke en mappe.")
        return None
        
    all_content = []
    text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    
    if not text_files:
        log_error(f"Ingen tekstfiler funnet i '{directory}'.")
        return None
    
    log_message(f"Fant {len(text_files)} tekstfiler i {directory}", "GREEN")
    
    for file in text_files:
        file_path = os.path.join(directory, file)
        log_message(f"Leser fil: {file}", "CYAN")
        content = load_input_file(file_path)
        if content:
            all_content.append(content)
    
    if not all_content:
        return None
        
    # Merge content from all files into one large string
    return "\n\n".join(all_content)

# ============================================================================
# TEXT PROCESSING
# ============================================================================
def split_into_cases(text: str) -> List[str]:
    if not text:
        return []
       
    cases = []
    current_case = ""
   
    for line in text.splitlines():
        if line.strip().startswith("=== Sak:"):
            if current_case:
                cases.append(current_case.strip())
            current_case = line + "\n"
        else:
            current_case += line + "\n"
   
    if current_case:
        cases.append(current_case.strip())
   
    return cases


# ============================================================================
# MAIN CLEANING FUNCTION
# ============================================================================
def clean_text(text: str) -> str:
    # Use compiled patterns for most common operations first (faster)
    # Remove case number
    text = re.sub(r'===\s*Sak:\s*[A-Za-z0-9-]+\s*===', '', text)

    # Remove timestamps
    text = TIMESTAMP_PATTERN.sub('', text)
    
    # Remove "[ Ekstern e-post ]" tag
    text = re.sub(r'\[\s*Ekstern\s*e-post\s*\]', '', text)

    # Remove mentions of "Lysningsbladet" and "Rapporter" as requested
    text = re.sub(r'(?:Lysningsbladet|Rapporter)\s*', '', text)

    # Remove contact information headers and content
    text = re.sub(r'(?i)Telefonnummer[\s:]*[\d\s+()-]+', '', text)
    text = re.sub(r'(?i)Fakturaadresse(?:[,:]|\s+)[^\n]+', '', text)
    text = re.sub(r'(?i)(?:postboks|fakturarefereanse)[^\n]+', '', text)

    # Remove sentence ending followed by name and title pattern
    text = re.sub(r'([.!?])\s+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})\.?\s+(?:Rådgiver|Seniorrådgiver|Konsulent|Direktør|Leder|Sjef)\.?\s+[A-Za-zæøåÆØÅ]+\.?', r'\1', text)

    # Remove name with title patterns (common format in Norwegian emails)
    text = re.sub(r'(?m)^([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})(?:\s*,\s*|\s+)((?:[A-ZÆØÅ][a-zæøå]+\s*)+)(?:\s*$|\s*\n)', '', text)
    
    # Add specific pattern to catch "FirstName LastName Title, Department" format
    text = re.sub(r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})(?:Seniorrådgiver|Rådgiver|Konsulent|Direktør|Leder|Sjef)(?:,?\s*[A-Za-z]+)?', '', text)
    
    # Remove adjacent name-title combinations without space (like "Tove Helen ModahlSeniorrådgiver")
    text = re.sub(r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,2})(?:Seniorrådgiver|Rådgiver|Konsulent|Direktør|Leder|Sjef)', '', text)

    # Enhanced phone number removal - including numbers after text without clear separators
    text = re.sub(r'(?<=[a-zæøå\.\?\!])\s*[:;]?\s*\d{8}\b', '', text)  # Numbers after text
    text = re.sub(r'(?<=[a-zæøå\.\?\!])\s*[:;]?\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}\b', '', text)  # Formatted numbers
    
    # Remove website URLs and phone numbers
    text = re.sub(r'(?i)(?:Telefon|Tlf|Mobil)[\s:]*[\d\s+()-]+', '', text)
    text = re.sub(r'(?i)(?:www\.)?[a-zæøå0-9][a-zæøå0-9-]{1,61}[a-zæøå0-9]\.[a-zæøå]{2,}(?:/[^\s]*)?', '', text)

    # Remove content between vertical bars (common in signatures and contact info)
    vertical_bar_pattern = r'\|[^|]*\|'
    text = re.sub(vertical_bar_pattern, '', text)
    
    # More comprehensive pattern to handle nested or multiple vertical bar sections
    multi_vertical_bar_pattern = r'\|[^|]*(?:\|[^|]*)*\|'
    text = re.sub(multi_vertical_bar_pattern, '', text)
    
    # Also handle cases with just single vertical bars as section dividers
    single_vertical_bar_divider = r'(?<=\S)\s*\|\s*(?=\S)'
    text = re.sub(single_vertical_bar_divider, ' ', text)

    # Enhanced business signature removal - matches company names and organization numbers
    business_signature = r'(?i)(?:Business\s+name|Company|Organization|Organisation|Firma)[\s:]*([\w\s&]+)(?:AS|AB|Inc|Ltd|GmbH)?[\s,]*(?:(?:Organization|Organisation|Org(?:\.|anisasjon)?\s*(?:number|nr))[\s:]*)?\d{5,12}[\s,]*(?:Thanks|Regards|Vennlig hilsen|MVH)?[\s,]*([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})[\s,]*(?:Digital|Manager|Director|CEO|CTO|Consultant|Adviser|Advisor|Rådgiver|Konsulent|Leder|Sjef)[\s\w&+]*(?:\|[^|]*){0,3}'
    text = re.sub(business_signature, '', text)

    # Remove Norwegian phone numbers with parentheses (+47) format
    parentheses_phone_pattern = r'\(\+\d{2}\)[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{0,2}'
    text = re.sub(parentheses_phone_pattern, '', text)
    
    # More comprehensive phone number pattern to catch all variants
    text = re.sub(r'(?:\(?\+\d{2}\)?|\+\d{2}|00\d{2})[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{0,2}', '', text)

    # Remove original message markers in Norwegian and related formats
    original_message_pattern = r'(?i)(?:[-]+\s*(?:Originalmelding|Original\s*melding)\s*[-]+)'
    text = re.sub(original_message_pattern, '', text)
    
    # More comprehensive pattern to catch variants of original message headers
    original_message_variants = r'(?i)(?:[-]{2,}\s*(?:Originalmelding|Original\s*melding|Opprinnelig\s*melding)\s*[-]{2,})(?:\n.*?(?=\n\n|\Z))?'
    text = re.sub(original_message_variants, '', text, flags=re.DOTALL)
    
    # Remove message separators with dates that often follow original message markers
    message_date_separator = r'(?i)(?:[-]{3,})\s*\w+\.\s+\d{1,2}\.\s+\w+\.\s+\d{4}(?:\s+\d{1,2}:\d{2})?(?:[-]{3,})'
    text = re.sub(message_date_separator, '', text)
    
    # Remove chains of dashes that might be message separators
    dash_separators = r'[-]{3,}[\s\r\n]*[-]{3,}'
    text = re.sub(dash_separators, '', text)

    # Even more flexible pattern to catch phone numbers without country code
    any_phone_format = r'\b(?:\d{2}[\s.-]*){4,5}\b'
    text = re.sub(any_phone_format, '', text)
    
    # Remove standalone digits that might be phone numbers (8-digit format common in Norway)
    standalone_digits = r'\b\d{8}\b'
    text = re.sub(standalone_digits, '', text)
    
    
    # Also catch variants with different spacing and formatting
    name_department_direct_variant = r'[A-ZÆØÅ][a-zæøåA-ZÆØÅ]+(?:\d{1,3})?\s+(?:Direkte|Telefon|Tlf)[:.]?\s*\d{3}[\s.-]?\d{2}[\s.-]?\d{3}'
    text = re.sub(name_department_direct_variant, '', text)
    
    # More general pattern to catch organization-employee-number combinations with few separators
    condensed_org_contact = r'[A-ZÆØÅ][a-zæøå]+(?:[A-ZÆØÅ][a-zæøå]+)*(?:[A-ZÆØÅ][A-Z0-9]+){0,3}\d{1,3}\s+(?:Direkte|Telefon|Tlf)[:.]?\s*\d{3}[\s.-]?\d{2}[\s.-]?\d{3}'
    text = re.sub(condensed_org_contact, '', text)

    
    # Remove digits immediately following text (could be partial phone numbers)
    text_followed_by_digits = r'(?<=[a-zæøåA-ZÆØÅ])\s*\d{6,12}\b'
    text = re.sub(text_followed_by_digits, '', text)

    # Remove Norwegian phone numbers starting with +47
    norway_phone_pattern = r'\+47\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}'
    text = re.sub(norway_phone_pattern, '', text)
    
    # More flexible pattern to catch variants with different spacing
    norway_phone_flexible = r'\+47[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{0,2}'
    text = re.sub(norway_phone_flexible, '', text)
    
    # Also catch the +47 prefix when it appears with a following space and digits
    plus47_prefix = r'\+47\s+\d[\d\s.-]+'
    text = re.sub(plus47_prefix, '', text)
    
    # Simpler pattern for catching key parts of signatures with phone numbers and domains
    simple_signature = r'(?:[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})[\s,]*(?:Digital|Manager|Director|CEO|CTO|Consultant|Adviser|Advisor|Rådgiver|Konsulent|Leder|Sjef)[\s\w&+]*(?:\+\d{1,2}[\s.()0-9]{8,15})[\s|]*(?:[\w.]+\.(?:com|no|org|net))'
    text = re.sub(simple_signature, '', text)

    # Remove subtle business signatures with partial formatting (no clear labels)
    text = re.sub(r'(?i)(?:Kind\s+)?(?:Manager|Director|Assurance|Supply Chain|Product|Digital|Business|Consultant|Advisor|Rådgiver|Konsulent|Leder|Sjef)(?:[A-Za-z\s]+)?(?:\|\s*[a-z0-9.-]+\.(?:com|no|org|net)\s*\|\s*)?', '', text)
    
    # Simpler pattern for catching key parts of signatures with phone numbers and domains
    simple_signature = r'(?:[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})[\s,]*(?:Digital|Manager|Director|CEO|CTO|Consultant|Adviser|Advisor|Rådgiver|Konsulent|Leder|Sjef)[\s\w&+]*(?:\+\d{1,2}[\s.()0-9]{8,15})[\s|]*(?:[\w.]+\.(?:com|no|org|net))'
    text = re.sub(simple_signature, '', text)
    
    # Catch domain references with vertical bars (common in signatures)
    domain_bar_pattern = r'(?i)(?:\|\s*[a-z0-9.-]+\.(?:com|no|org|net)\s*\|\s*LinkedIn)'
    text = re.sub(domain_bar_pattern, '', text)
    
    # Catch fragments of signatures with job titles and departments
    title_dept_pattern = r'(?i)(?:Digital|Product|Supply Chain|Assurance|Platforms)[A-Za-z\s&]+'
    text = re.sub(title_dept_pattern, '', text)

    # Enhanced contact information removal - improved patterns
    text = re.sub(r'(?i)(?:Kontaktinformasjon|Informasjon om innmelder)(?:[\s\S]*?)(?=\n\n|\Z)', '', text)
    
    # Enhanced address removal - comprehensive pattern for various address types
    text = re.sub(r'(?i)(?:Fakturadresse|Fakturaadresse|Fakturareferanse|Fakturarefereanse)(?:[,:]|\s+)[^\n]+', '', text)
    text = re.sub(r'(?i)(?:postboks|pb\.?|p\.?b\.?)(?:\s+\d+[A-Za-z0-9\s,./-]*)', '', text)
    text = re.sub(r'(?i)(?:Besøksadresse|Besøks-?adresse|Gateadresse|Forretningsadresse)(?:[,:]|\s+)[^\n]+', '', text)
    
    # Remove common Norwegian street address patterns
    text = re.sub(r'(?i)(?:[A-ZÆØÅ][a-zæøå]+(?:veien|gata|gaten|vegen|vei|gate|gt\.?|v\.?|plass|torg))\s+\d+\w?(?:[,\s]+\d{4}\s+[A-ZÆØÅ][a-zæøå]+)?', '', text)
    
    # Enhanced phone number removal - all formats and variants
    text = re.sub(r'(?i)(?:Telefonnummer|Telefon|Tlf\.?|Mobil|Mobilnummer|Sentralbord|Tel\.?|Phone|Mobile)[\s:]*[\d\s+()-]{8,15}', '', text)  # Standard format
    text = re.sub(r'(?<=[a-zæøå\.\?\!])\s*[:;]?\s*(?:\+\d{1,3}\s*)?(?:\d{2}\s*){4}\b', '', text)  # Formatted numbers after text
    text = re.sub(r'(?<=[a-zæøå\.\?\!])\s*[:;]?\s*(?:\+\d{1,3}\s*)?(?:\d{3}\s*){2,3}\b', '', text)  # 3-digit groupings
    text = re.sub(r'\b\d{8}\b', '', text)  # 8-digit numbers
    text = re.sub(r'\+47[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{1,2}[\s.-]*\d{0,2}', '', text)  # Norwegian numbers
    
    # Remove LinkedIn profiles and references - enhanced pattern
    text = re.sub(r'(?i)(?:linkedin\.com\/(?:in|company)\/[^\s\n]+)', '', text)
    text = re.sub(r'(?i)(?:linkedin|(?:www\.)?linkedin\.com|LinkedIn-profil).*?(?=\n|\Z)', '', text, flags=re.MULTILINE)
    
    # Remove lines with LinkedIn profiles
    text = re.sub(r'(?i)(?:linkedin|(?:www\.)?linkedin\.com).*$', '', text, flags=re.MULTILINE)
    
    # Remove feedback/rating requests
    text = re.sub(r'(?i)Hvor\s+tilfreds\s+var\s+du\s+med\s+(?:responsen|svaret)[^\n]+', '', text)
    text = re.sub(r'(?i)gi\s+oss\s+tilbakemelding[^\n]*', '', text)
    text = re.sub(r'(?i)(?:takk\s+for\s+din\s+(?:henvendelse|forespørsel)|har\s+du\s+fått\s+svar\s+på\s+det\s+du\s+lurte\s+på)[^\n]*', '', text)

    # Enhanced name removal patterns
    # 1. Names after common greetings
    text = re.sub(r'(?i)(med\s+vennlig\s+hilsen|mvh|hilsen|regards|fra)[,:]?\s*([A-ZÆØÅa-zæøå]+(?:\s+[A-ZÆØÅa-zæøå]+){1,3})', 
                  r'\1', text)
    
    # 2. Names at beginning of lines (common in emails)
    text = re.sub(r'(?m)^([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,2})[\.,!]?\s*$', '', text)
    
    # 3. Names with common titles
    text = re.sub(r'(?i)([A-ZÆØÅa-zæøå]+(?:\s+[A-ZÆØÅa-zæøå]+){1,3})\s*[,/]\s*(seniorrådgiver|rådgiver|direktør|konsulent|leder|sjef|prosjektleder|teamleder|avdelingsleder)', 
                  '', text)
    
    # 4. Common Norwegian format: Firstname Lastname <email>
    text = re.sub(r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,2})\s*<[^>]+@[^>]+>', '', text)
    
    # Remove various greeting formats - use compiled patterns first (fastest)
    text = re.sub(r'(?i)(?:med\s+vennlig\s+hilsen|mvh|vennlig\s+hilsen|beste\s+hilsen|hilsen|regards)[\s,.]*(?:$|\n)', '', text)
    text = re.sub(r'(?i)(?:\s*M\s*e\s*d\s+v\s*e\s*n\s*(?:n|l)\s*i\s*g\s*)(?:[\s,.]+h\s*i\s*l\s*s\s*e\s*n|[\s,.]+h(?:ä|a|e)l\s*s\s*(?:n|i\s*n\s*g)|[\s,.]+h\s*e\s*l\s*s\s*i\s*n\s*g)?[\s,.]*(?:$|\n)', '', text)
    
    # Then the more complex patterns
    greetings_pattern = r'(?i)(med\s+vennlig\s+hilsem|.Med\s+vennleg\s+helsing|.Med\s+vennlig\s+hilsen|med\s+vennlig\s+hilsen|mvh|vennlig\s+hilsen|}Med venlig|"Med venlig|. Med venlig|.  Med venlig|beste\s+hilsen|hilsen|regards|med\s+venleg\s+helsing)[,\.]?\s*'
    text = re.sub(greetings_pattern, '', text)
    
    # More comprehensive pattern for spaced variations and with/without punctuation
    spaced_greetings = r'(?i)(?:med[\s,.]+vennlig[\s,.]+hilsen|med[\s,.]+venlig[\s,.]+(?:hilsen|hälsning)|med[\s,.]+venleg[\s,.]+helsing)[\s,.]*(?:$|\n)'
    text = re.sub(spaced_greetings, '', text)
    
    # Handle explicitly the "Med venlig" pattern that might be broken across lines or with extra spaces
    broken_greeting = r'(?i)(?:\.?\s*Med\s+ven(?:n|l)(?:l)?ig\s*(?:\n|\r|\s)*(?:hilsen|hälsning|helsing))[\s,.]*(?:$|\n)'
    text = re.sub(broken_greeting, '', text)

    # Enhanced greeting removal patterns for all spacing variations
    
    # Super-flexible pattern for Med venlig with any spacing or line breaks
    super_flexible_greeting = r'(?i)(?:\s*M\s*e\s*d\s+v\s*e\s*n\s*(?:n|l)\s*i\s*g\s*)(?:[\s,.]+h\s*i\s*l\s*s\s*e\s*n|[\s,.]+h(?:ä|a|e)l\s*s\s*(?:n|i\s*n\s*g)|[\s,.]+h\s*e\s*l\s*s\s*i\s*n\s*g)?[\s,.]*(?:$|\n)'
    text = re.sub(super_flexible_greeting, '', text)
    
    # Pattern to catch cases with spaces before and after "Med venlig"
    spaced_med_venlig = r'(?i)(?:\s+|\n|^)[\s,.]*M\s*e\s*d[\s,.]+v\s*e\s*n\s*(?:n|l)\s*i\s*g[\s,.]+(?:h\s*i\s*l\s*s\s*e\s*n|h(?:ä|a|e)l\s*s\s*(?:n|i\s*n\s*g)|h\s*e\s*l\s*s\s*i\s*n\s*g)?[\s,.]*(?:$|\n|\s+)'
    text = re.sub(spaced_med_venlig, '', text)
    
    # Pattern to catch Med venlig with intervening spaces
    med_venlig_spaces = r'(?i)(?:\.|^|\s+)M[\s,.]*e[\s,.]*d[\s,.]*v[\s,.]*e[\s,.]*n[\s,.]*(?:n|l)[\s,.]*i[\s,.]*g[\s,.]*(?:h[\s,.]*i[\s,.]*l[\s,.]*s[\s,.]*e[\s,.]*n|h(?:ä|a|e)[\s,.]*l[\s,.]*s[\s,.]*(?:n|i[\s,.]*n[\s,.]*g)|h[\s,.]*e[\s,.]*l[\s,.]*s[\s,.]*i[\s,.]*n[\s,.]*g)?[\s,.]*(?:$|\n)'
    text = re.sub(med_venlig_spaces, '', text)
    
    # Catch greetings with excessive whitespace between or around them
    excessive_space_greeting = r'(?i)(?:^\s*|\n\s*|\.\s*)M\s+e\s+d\s+v\s+e\s+n\s+(?:n|l)\s+i\s+g(?:\s+h\s+i\s+l\s+s\s+e\s+n)?[\s,.]*(?:$|\n)'
    text = re.sub(excessive_space_greeting, '', text)
    
    # Try a completely different approach with character-by-character optional spaces
    character_spaced_greeting = r'(?i)(?:\s*M\s*)\s*(?:e\s*)\s*(?:d\s*)\s*(?:v\s*)\s*(?:e\s*)\s*(?:n\s*)\s*(?:[nl]\s*)\s*(?:i\s*)\s*(?:g\s*)'
    text = re.sub(character_spaced_greeting, '', text)
    
    # Additional pattern to catch separated signature components
    signature_fragments = r'(?i)(?<=[.?!\n])[\s,.]*(?:hilsen|med\s+(?:vennlig|venlig|venleg)\s+(?:hilsen|helsing|hälsning))[\s,.]*$'
    text = re.sub(signature_fragments, '', text)

    # Remove eFormidling conversation IDs and associated JWT/base64 data 
    # Pattern matches UUIDs followed by timestamps and status messages with JWT data
    eformidling_pattern = r'(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}){1,3}[0-9]+(?:20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[\+\-]\d{2}:\d{2})?(?:OPPRETTET|SENDT|MOTTATT|LEVERT)(?:[^<\n]{10,2000})'
    text = re.sub(eformidling_pattern, '', text)

    # Remove JWT tokens (typically long base64-encoded strings with two period separators)
    jwt_pattern = r'ey[A-Za-z0-9_-]+\.ey[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
    text = re.sub(jwt_pattern, '', text)
    
    # Remove any long base64-looking strings (may be certificates, encoded data, etc.)
    base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4}){20,}'
    text = re.sub(base64_pattern, '', text)

    # Additional pattern to catch ID-related statistics tables
    # This pattern matches lines containing authentication providers and numbers like "BankID. BankID Mobil. Buypass..."
    authentication_stats_pattern = r'(?:(?:ID|BankID|Buypass|Commfides|MinID)(?:\s+\w+)?\.?\s*)+(?:\d+[\s.]*)+(?:Sum\.?)?'
    text = re.sub(authentication_stats_pattern, '', text)
    
    # Remove common ID service statistics patterns with dot-separated columns
    id_stats_pattern = r'(?:(?:helsenorge|difi|digdir)_\w+(?:_\w+)*\.(?:\s*\d{1,3}(?:\s*\d{3})*\.?)+(?:\s*-)*){1,}'
    text = re.sub(id_stats_pattern, '', text)
    
    # Remove tabular data with numbers and authentication methods (multi-line approach)
    tabular_pattern = r'(?:Sum|Total)\.?\s*\d[\d\s.]*\n(?:\w+(?:\s+\w+)?\.?\s*(?:\d[\d\s.]*|-)+\n)+'
    text = re.sub(tabular_pattern, '', text, flags=re.MULTILINE)
    
    # Try to identify and remove names (names often appear after greetings or at end of messages)
    text = re.sub(r'(?i)(hilsen|regards|fra)[,:]?\s*[A-ZÆØÅa-zæøå]+\s+[A-ZÆØÅa-zæøå]+', '', text)
    
    # Remove email addresses - bruk kompilert mønster
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '', text)

    # Enhanced domain and sentralbord removal - bruk kompilert mønster
    text = re.sub(r'(?i)(?:www\.)?[a-zæøå0-9][a-zæøå0-9-]{1,61}[a-zæøå0-9]\.[a-zæøå]{2,}(?:/[^\s]*)?', '', text)
    
    # Enhanced stack trace pattern to handle very long ones (with "common fra" pattern)
    extensive_stack_trace = r'(?:\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[.,]\d{3}(?:\+\d{2}:\d{2})?\s+(?:ERROR|INFO|WARN|DEBUG).*?(?:\n.*?at\s+[\w$.()]+(?::\d+)?)+(?:\n\s*\.\.\.\s+\d+\s+common\s+(?:fra|frames))?)+'
    text = re.sub(extensive_stack_trace, '', text, flags=re.MULTILINE | re.DOTALL)
    
    # Enhanced JWT token pattern (base64 encoded parts with periods)
    jwt_extended_pattern = r'eyJ[A-Za-z0-9_-]+\.(?:[A-Za-z0-9_-]+\.){1,10}[A-Za-z0-9_-]+'
    text = re.sub(jwt_extended_pattern, '', text)
    
    # Developer/professional info with location (common in signatures)
    dev_location_pattern = r'(?:[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+\s*(?:\([A-Za-z]+\.?\))?)\s*(?:Developer|Programmer|Engineer|Consultant|Architect)(?:Email)?\s+[A-Za-z]+(?:[A-ZÆØÅ][a-zæøå]+)?\s*(?:[A-ZÆØÅ][a-zæøå]+)?'
    text = re.sub(dev_location_pattern, '', text)
    
    # More aggressive greeting pattern for all "Med venlig" variants
    med_venlig_pattern = r'(?i)(?:^|\s+|[.!?]\s*)Med\s+ven(?:n|l)ig\b(?:\s*|\n)[^.!?]*?(?:\n|$)'
    text = re.sub(med_venlig_pattern, '', text)
    
    # Thymeleaf/Spring expression errors
    thymeleaf_error_pattern = r'(?i)Exception\s+(?:processing|evaluating)\s+(?:template|SpringEL\s+expression):\s*"[^"]*"\s*\(template:\s*"[^"]*".*?\)'
    text = re.sub(thymeleaf_error_pattern, '', text)
    
    # Spring EL evaluation errors
    spring_el_error_pattern = r'(?i)(?:EL\d+E|SpelEvaluationException):\s*[^\n]*'
    text = re.sub(spring_el_error_pattern, '', text)
    
    # Another approach for Med venlig variants with line breaks
    broken_greeting_extended = r'(?i)(?:\.?\s*Med\s+ven(?:n|l)(?:l)?ig)(?:\s*[\n\r\s]){0,4}(?:hilsen|hälsning|helsing|hilsem)?[\s,.]*(?:$|\n)'
    text = re.sub(broken_greeting_extended, '', text)
    
    # Remove sentralbord mentions and related content
    sentralbord_pattern = r'(?i)(?:sentralbord|telefon|tlf)[^\n\d]*(?:\+\d{1,3}[\s.]?)?\d{2,3}[\s.]?\d{2,3}[\s.]?\d{2,3}[\s.]?\d{0,3}'
    text = re.sub(sentralbord_pattern, '', text)

    # Remove calendar invite patterns
    calendar_pattern = r'(?i)(?:møteinvitasjon|kalenderhendelse|kalenderinvitasjon).*?(?:start|slutt|sted|location)\s*:\s*[^\n]+'
    text = re.sub(calendar_pattern, '', text, flags=re.DOTALL)

    # Remove Norwegian ID number references
    id_number_pattern = r'\b(?:DIN|person|fødsels|org\.?|organisasjons)(?:[-\s])?(?:nummer|nr\.?)[\s:]*\d{9,11}\b'
    text = re.sub(id_number_pattern, '', text, flags=re.IGNORECASE)

    # Remove social media platform mentions and marketing terms
    social_media_pattern = r'(?i)(?:facebook|twitter|instagram|linkedin|snapchat|tiktok)(?:\s+[\w\s]+)?'
    text = re.sub(social_media_pattern, '', text)
    
    # Remove marketing material references
    marketing_pattern = r'(?i)(?:brosjyre|flyer|poster|plakat|roll-up|banner|infographic|nyhetsbrev)'
    text = re.sub(marketing_pattern, '', text)
    
    # Remove contact person references
    contact_person_pattern = r'(?i)(?:kontaktperson|kontaktperson:|kontakt(?:\s+)?person)(?:er)?(?:\s*(?:for|er|:))?\s*[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){0,2}'
    text = re.sub(contact_person_pattern, '', text)

    # Remove standard email client signatures
    outlook_sig = r'(?i)Sendt\s+fra\s+(?:min\s+)?(?:iPhone|Android|Outlook|Gmail|Yahoo|Epost|Windows\s+Mail)'
    text = re.sub(outlook_sig, '', text)

    # Remove service desk ticket references
    ticket_pattern = r'(?i)(?:sak|ticket|case|ref|reference)[\s.:#]*[A-Z0-9]+-[A-Z0-9]+'
    text = re.sub(ticket_pattern, '', text)

    # Remove Norwegian social security numbers (fødselsnummer) - various formats
    ssn_pattern = r'\b\d{6}[\s.-]?\d{5}\b'
    text = re.sub(ssn_pattern, '', text)

    # Remove attachment references
    attachment_pattern = r'(?i)(?:vedlegg|attachments?)[\s:].*?(?:\.\w{2,4}|$)'
    text = re.sub(attachment_pattern, '', text)

    # Remove Teams and chat platform artifacts
    teams_pattern = r'(?i)Fra\s+Teams\s+(?:meeting|chat|samtale).*?(?=\n\n|\Z)'
    text = re.sub(teams_pattern, '', text, flags=re.DOTALL)
    
    # Remove fragments with both domain and organization name patterns
    text = re.sub(r'[A-Za-zæøåÆØÅ]+(?:direktoratet|departementet|etaten|instituttet)\.no', '', text)

    # Enhanced signature removal after message endings
    message_ending_signature = r'(?i)(?:Hei|Ok|Takk|Kan\s+dere\s+gi\s+oss\s+et\s+svar\s+når\s+det\s+er\s+i\s+orden\??)[^\n]*([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){0,3})?(?:\s*[|↳]+\s*|\s+)?(?:senior|Senior\s+Adviser|[Rr]ådgiver|[Kk]onsulent|[Dd]irektør|[Ll]eder|[Ss]jef)[^\n]*(?:\+\d{2}\s*\d+[^\n]*)?(?:\n.*\.(?:com|no|org|net))?'
    text = re.sub(message_ending_signature, r'\1', text)
    
    # Remove specific Norwegian style signatures with arrow/pipe and department
    arrow_dept_signature = r'(?:[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){0,3})\s*[|↳]\s*(?:[A-Za-zæøåÆØÅ\s&]+)\s*\+?\d{1,2}\s*\d{5,}'
    text = re.sub(arrow_dept_signature, '', text)
    
    # Remove email headers (comprehensive pattern)
    header_pattern = r'(?:Fra|From|Sendt|Sent|Til|To|Kopi|Cc|Emne|Subject|Reply-To|Date|Dato):\s+.*?(?:@.*?)?(?=\n|\Z)'
    text = re.sub(header_pattern, '', text)

    # Remove contact information blocks
    contact_pattern = r'(?i)(?:kontor|administrasjon|besøksadresse|besøks-?adresse|postadresse|telefon|tlf)[\s:].*?\n'
    text = re.sub(contact_pattern, '', text)

    # Add to clean_text function - pattern for removing archive creator metadata
    text = re.sub(r'ARKIVSKAPER\.\s*BASEID\.\s*\d+\.\s*\d+\.', '', text)

    # Remove signature blocks (often contain names and titles)
    signature_pattern = r'(?i)(-{2,}|_{2,})\s*\n.*?(rådgiver|konsulent|direktør|leder|manager|senior|advisor|administrator|kontor|avdeling)'
    text = re.sub(signature_pattern, '', text, flags=re.DOTALL)
    
    # Remove multi-line email headers (more aggressive approach)
    header_block_pattern = r'(?:Fra|From|Sendt|Sent|Til|To|Kopi|Cc|Emne|Subject):[^\n]*(?:\n[^\n:]*(?!:)[^\n]*)*'
    text = re.sub(header_block_pattern, '', text)
    
    # Remove date/time patterns like "man. 13. jan. 2025 kl. 12:18 skrev Servicedesk :"
    date_pattern = r'\w+\.\s+\d+\.\s+\w+\.\s+\d{4}\s+kl\.\s+\d{1,2}:\d{2}\s+skrev\s+[^:]+:'
    text = re.sub(date_pattern, '', text)

    # Remove message tracking metadata timestamps, IDs and status information
    message_tracking_pattern = r'(?i)(?:Tidspunkt\s+for\s+feil|Tidspunkt\s+sendt|Timestamp):\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?'
    text = re.sub(message_tracking_pattern, '', text)
    
    # Remove Message-ID, Conversation-ID, Process-ID lines
    message_id_pattern = r'(?i)(?:Message-ID|Conversation-ID|Process-ID|Reference-ID):\s*[\w.-]+(?:[-:]\w+)*'
    text = re.sub(message_id_pattern, '', text)

    # Remove company/person with location and direct number (Norwegian format)
    text = re.sub(r'[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){0,3}\s*\|\s*\d{4}\s+[A-ZÆØÅ][a-zæøå]+\|\s*Direkte:\s*\d{3}\s*\d{2}\s*\d{3}', '', text)
    
    # Remove customer service person with specific phone format
    text = re.sub(r'[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+(?:kundeansvarlig|kundeservice|kontaktperson)(?:KFM|TEL|TLF)?:\s*\+\s*,\s*T:\s*\+\.?"', '', text)
    
    # Remove UUID-based tracking information with timestamps and status indicators - bruk kompilerte mønstre
    eformidling_complex = r'(?:\d+)?(?:20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[\+\-]\d{2}:\d{2})?(?:OPPRETTET|SENDT|MOTTATT|LEVERT)(?:[^<\n]{0,2000})'
    text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '', text)  # Remove UUIDs first
    text = re.sub(eformidling_complex, '', text)

    # Remove application logs and technical traces (Spring Boot, Java logs etc.)
    java_log_pattern = r'(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2},\d{3}(?:\+\d{2}:\d{2})?\s+\[[A-Z]+\]\s+[a-zA-Z0-9_.]+(?:\s+-\s+.+)?)'
    text = re.sub(java_log_pattern, '', text)

    # More comprehensive Spring Boot ASCII art banner
    spring_banner_pattern = r'(?:(?:\s*\.\s*____.*\n?)(?:\s*/\\\\\s*/\s*___.*\n?)?(?:\s*\(\s*\(\s*\).*\n?)?(?:\s*\\\\\/.*\n?)?(?:\s*\'.*\n?)?(?:\s*=+.*\n?)?(?:\s*::\s*Spring\s*Boot.*\n?)?)'
    text = re.sub(spring_banner_pattern, '', text, flags=re.MULTILINE)

    # Remove e-formidling status sequences with timestamps
    eformidling_status_pattern = r'\d{6,10}(?:20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[\+\-]\d{2}:\d{2})?(?:OPPRETTET|SENDT|MOTTATT|LEVERT)'
    text = re.sub(eformidling_status_pattern, '', text)

    # Remove complex log stack traces
    stack_trace_pattern = r'(?:Caused by:.*?at .*?)(?:\n\s+at .*?)*(?:\n\s*\.\.\. \d+ common .*?)?'
    text = re.sub(stack_trace_pattern, '', text, flags=re.DOTALL)

    # Remove original message headers in forwarded emails
    original_msg_pattern = r'(?:---+ Original Message ---+)(?:\n.*?)*?(?=\n\n|\Z)'
    text = re.sub(original_msg_pattern, '', text, flags=re.DOTALL)

    # Clean up signatures with pipe character and phone number
    text = re.sub(r'[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+(?:Seksjons|Avdelings)?(?:\s*\|\s*\+\d{2}\s*\d{3}\s*\d{2}\s*\d{3})(?:[A-ZÆØÅ][A-Za-zæøåÆØÅ]+(?:Dokumentsenteret)?(?:\s*i\s*\|\s*\.)?)?', '', text)

    # Remove HTML style attributes - bruk kompilerte mønstre
    text = re.sub(r'<span\s+style=\"[^\"]+\">', '', text)
    text = re.sub(r'</span>', '', text)
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove series of UUIDs and numeric sequences (common in tracking data) - allerede fjernet UUIDs over
    tracking_data_pattern = r'(?:\d{6,10}){0,5}'
    text = re.sub(tracking_data_pattern, '', text)
    
    # Remove true/false pattern sequences (common in logging and tracking)
    boolean_sequence = r'(?:true|false){2,}(?:\d+)?(?:true|false){2,}'
    text = re.sub(boolean_sequence, '', text)
    
    # Remove Status reports and service identifiers
    status_pattern = r'(?i)(?:Status|Service\s+identifier):\s*[A-ZÆØÅ_]+(?:[-_]\w+)*'
    text = re.sub(status_pattern, '', text)

    # Remove specific formats with company name and phone number (like "Sikri+47 990 86 101")
    text = re.sub(r'(?:[A-ZÆØÅ][a-zæøå]+)\+\d{2}\s*\d{3}\s*\d{2}\s*\d{3}', '', text)
    
    # Remove bullet-point separated contact info (addresses with formatting characters)
    text = re.sub(r'\s*•\s*(?:_+\s*)?(?:[A-ZÆØÅ][a-zæøå]+(?:(?:veien|gata|gaten|vegen|vei|gate|gt\.?|v\.?|plass|torg))\s+\d+\w?,?\s*\d{4}\s+[A-ZÆØÅa-zæøå]+)?', '', text)
    
    # Remove phone numbers with bullet point separators
    text = re.sub(r'\+\d{2}\s*\d{3}\s*\d{2}\s*\d{3}\s*•', '', text)
    
    # Remove standalone people names without context (like "pangilinan, , Ali Heidar, 5.")
    text = re.sub(r'(?:[A-ZÆØÅ][a-zæøå]+),\s*(?:,\s*)?(?:[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)?)(?:,\s*\d+\.?)?', '', text)
    
    # Remove contact info with underscores (like "____ Dronning Mauds gate")
    text = re.sub(r'_{2,}\s*[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,5}\s*\d+', '', text)
    
    # Remove sender/receiver information with organization numbers
    org_pattern = r'(?i)(?:Sender|Receiver|Avsender|Mottaker):\s*\d{4}:\d{9}(?:\s+[A-ZÆØÅ][A-Za-zæøåÆØÅ\s]+)?'
    text = re.sub(org_pattern, '', text)
    
    # Remove URN identifiers (commonly used in digital post)
    urn_pattern = r'urn:no:difi:[a-zA-Z0-9:._-]+(?:ver\d+\.\d+)?'
    text = re.sub(urn_pattern, '', text)

    # Remove generic thank you messages and periods at the end (common in these systems)
    thanks_pattern = r'(?i)På\s+forhånd\s+(?:tusen\s+)?takk\s+for\s+(?:hjelpen|tilbakemelding|assistanse)\.+\s*\.*'
    text = re.sub(thanks_pattern, '', text)

    # Remove contact person field headers with or without content
    contact_person_header = r'(?i)Kontaktperson:.*?(?:\n|$)'
    text = re.sub(contact_person_header, '', text)

    # Remove JSON certificate data and assertions (long arrays of numbers enclosed in double quotes)
    cert_data_pattern = r'\"alg\":\"[^\"]+\",\"x5c\":\[\[(?:\"[0-9]+\",?)+\]\]'
    text = re.sub(cert_data_pattern, '', text)

    # More general pattern for removing large numeric sequences in quotes
    numeric_sequence_pattern = r'(?:\"[0-9]+\",?){30,}'
    text = re.sub(numeric_sequence_pattern, '', text)

    # More comprehensive JSON removal (catches both error messages and certificate data)
    json_pattern = r'\{(?:[^\{\}]|\{[^\{\}]*\})*\}'
    text = re.sub(json_pattern, '', text)

    # Remove trace_id references
    trace_id_pattern = r'trace_id:?\s*[a-f0-9]{32}'
    text = re.sub(trace_id_pattern, '', text)

    # Remove certificate, assertion, and x5c fragments
    cert_fragments_pattern = r'(?:Assertion|Certificate|cert|x5c):\s*\{[^\}]*\}'
    text = re.sub(cert_fragments_pattern, '', text, flags=re.IGNORECASE)

    # Remove long quoted string arrays that look like certificate data
    quoted_array_pattern = r'(?:\[\[(?:\"[^\"]*\",?)+\]\])'
    text = re.sub(quoted_array_pattern, '', text)

    # Remove stray JSON property text
    stray_json_prop = r'(?:\"[a-zA-Z_]+\":\s*(?:\"[^\"]*\"|true|false|\d+|null)\s*,?\s*)'
    text = re.sub(stray_json_prop, '', text)
    
    # Remove organization number field headers with or without content
    org_number_header = r'(?i)(?:Virksomhetens|Organisasjonens|Selskapets)\s+organisasjonsnummer:.*?(?:\n|$)'
    text = re.sub(org_number_header, '', text)

    # Remove Norwegian phone number followed by organization department and centralized info
    phone_org_pattern = r'(?:\+\d{2}\s*)?\d{2}\s*\d{2}\s*\d{2}\s*\d{2}(?:[A-ZÆØÅ][A-Za-zæøåÆØÅ]+(?:-[A-Za-zæøåÆØÅ]+)*)+(?:\/\.[a-z]+)?(?:Sentralbord\.?)?'
    text = re.sub(phone_org_pattern, '', text)

    # Remove eInnsyn date/time code references (common format in service desk tickets)
    einnsyn_date_pattern = r'(?:\d{4}\s+\d{4}\s*:?\s*"+"?\s*eInnsyn:?\s*)'
    text = re.sub(einnsyn_date_pattern, '', text)
    
    # Remove customer service person with specific contact format (Mydland pattern)
    customer_service_pattern = r'(?:[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+\s+[A-ZÆØÅ][a-zæøå]+)(?:kundeansvarlig|kundeservice|kontaktperson)?(?:KFM|TEL|TLF)?:?\s*\+\s*,\s*T:\s*\+\.?'
    text = re.sub(customer_service_pattern, '', text)
    
    # More general pattern to catch name with title and phone format with plus signs and periods
    general_contact_pattern = r'(?:[A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,3})(?:kundeansvarlig|kundeservice|kontaktperson|rådgiver|konsulent)?(?:[,:]?\s*\+\s*[,.]*\s*T:?\s*\+[.,]*)'
    text = re.sub(general_contact_pattern, '', text)
    
    # Fix for the pattern that causes case 9115 to crash - use atomic groups or possessive quantifiers
    # Replace the problematic org_dept_pattern with a more efficient version
    org_dept_pattern = r'(?>[A-ZÆØÅ][A-Za-zæøåÆØÅ]+(?:-\s*[A-Za-zæøåÆØÅ]+)*)(?:\s+og\s+(?>[A-Za-zæøåÆØÅ]+))(?:etaten|avdeling|direktorat)?(?:IKT-tjenester)?(?:\/\.[a-z]+)?(?:Sentralbord\.?)?'
    text = re.sub(org_dept_pattern, '', text)
    
    # More efficient version of the org_ikt_pattern
    org_ikt_pattern = r'(?>[A-Za-zæøåÆØÅ]+(?:-[A-Za-zæøåÆØÅ]+)*)(?:\s+og\s+(?>[A-Za-zæøåÆØÅ]+(?:-[A-Za-zæøåÆØÅ]+)*))etatenIKT-tjenester\/\.[a-z]+Sentralbord\.?'
    text = re.sub(org_ikt_pattern, '', text)

    # More general pattern for phone numbers followed by organization names
    phone_org_general = r'(?:\+\d{2}\s*)?(?:\d{2}\s*){4,5}[A-ZÆØÅ][a-zæøå]+(?:-[A-Za-zæøå]+)*(?:\s+[A-ZÆØÅ][a-zæøå]+(?:-[A-Za-zæøå]+)*){0,3}(?:\/\.[a-z]+)?(?:Sentralbord\.?)?'
    text = re.sub(phone_org_general, '', text)
    
    # Remove case number notification template
    case_notification_pattern = r'(?i)Vi\s+takker\s+for\s+din\s+henvendelse,\s+som\s+er\s+tildelt\s+følgende\s+saksnummer:\.?\s*(?:Saksnummer\.?)?(?:\s*\([A-Z0-9-]+\))?\.?\s*(?:Henvendelsen\s+vil\s+bli\s+behandlet\s+så\s+snart\s+en\s+kundebehandler\s+er\s+ledig\.?\s*)?(?:Ønsker\s+du\s+å\s+gi\s+oss\s+flere\s+opplysninger(?:\s+kan\s+du\s+enkelt\s+benytte)?(?:\s+svar-knappen\s+\(Reply\))?.+?(?:til\s+dennehenvendelsen\.?)?)?(?:\s*Vennligst\s+ta\s+vare\s+på\s+saksnummeret(?:\s+\([A-Z0-9-]+\))?\s+ved\s+videre\s+henvendelser,?(?:\.?\s*slik\s+at\s+vi\s+kan\s+hjelpe\s+deg\s+så\s+raskt\s+som\s+mulig)?)?'
    text = re.sub(case_notification_pattern, '', text, flags=re.DOTALL)
    
    # Also add a simpler pattern to catch different variants
    simple_case_notification = r'(?i)(?:Vi\s+takker\s+for\s+din\s+henvendelse[\s\S]*?saksnummer(?:et)?(?:\s+\([A-Z0-9-]+\))?)[\s\S]*?(?:så\s+raskt\s+som\s+mulig)'
    text = re.sub(simple_case_notification, '', text, flags=re.DOTALL)

    # More comprehensive pattern to remove labeled organization numbers
    org_id_pattern = r'(?i)(?:Virksomhetens|Organisasjonens|Selskapets|Bedriftens)?\s*(?:organisasjonsnummer|orgnr|org\.nr|orgnummer)[\s:.]*\d{9}'
    text = re.sub(org_id_pattern, '', text)
    
    # Empty fields (just labels with colon or space)
    empty_fields_pattern = r'(?i)(?:Kontaktperson|Virksomheten|Organisasjonsnummer|Org\.nr)[:.]?\s*$'
    text = re.sub(empty_fields_pattern, '', text)
    
    # Remove CRM references
    text = re.sub(r'CRM:\d+', '', text)
    
    # Remove base64 image data and HTML image tags
    text = re.sub(r'<img\s+src="data:image/[^"]+"\s*/?>', '', text)
    text = re.sub(r'data:image/[a-zA-Z0-9+/=]+;base64,[a-zA-Z0-9+/=\s]+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove URL parameters (often contain unwanted metadata) - bruk kompilert
    text = re.sub(r'\?[a-zA-Z0-9%=&;_\-+.]+', '', text)
    
    # Remove multiple empty lines (replace with a single newline) - bruk kompilert
    text = re.sub(r'\n\s*\n+', '\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

# ============================================================================
# PREDFINED QUESTION-ANSWER PAIRS
# ============================================================================

def get_predefined_qa_pairs() -> List[Tuple[str, str]]:
    return [
        (
            "Vil/vil ikke at fødselsnummer skal vise i signert dokument",
            "https://signering-docs.readthedocs.io/en/latest/signert-dokument.html#how-are-signers-identified-in-a-signed-document"
        ),
        (
            "Trenger bistand til å opprette ein ID-porten integrasjon.",
            "https://docs.digdir.no/docs/idporten/oidc/oidc_func_clientreg.html"
        ),
        (
            "Jeg forsøker å logge meg inn på deres systemer som administrator for vårt selskap, AS Financiering, orgnr 911629283. Men jeg får melding om at jeg ikke har tilgang til selvbetjeningsløsningen. Er dette noe dere kan bistå meg med?",
            "https://docs.digdir.no/docs/Maskinporten/maskinporten_sjolvbetjening_web.html#tilgang-i-test--og-produksjonsmilj%C3%B8. Må få delegert tilgong i altinn"
        ),
        (
            "Finner ikkje scopet eg treng når eg skal opprette Maskinporten",
            "https://docs.digdir.no/docs/Maskinporten/maskinporten_guide_apikonsument.html#4-opprett-en-integrasjon-i-maskinporten. Bør få til svar noko slikt som dette, Scopes får din organisasjon tildelt tilgang til av API-tilbyder."
        ),
        (
            "Vil opprette ein ny SAML integrasjon. Kvar skal eg sende inn metadata?",
            "https://docs.digdir.no/docs/idporten/oidc/oidc_func_saml.html. Her bør dei få til svar at SAML blir fasa ut 01.01.26"
        ),
        (
            "Mottaker av signering får ikke varsel på epost",
            "be mottaker logge inn på https://signering.posten.no/. Dersom det er sendt signeringsoppdrag til dem så skal de finne dem der. Vi opplever at noen epostklienter av og til oppfatter varslene som søppelpost, så et tips kan være å be de som skal få varsel om signering å sjekke spamfilter/søppelpost og evt. legge til no-reply@signering.posten.no som sikker avsender i sin epostklient. "
        ),
        (
            "mottaker får ikke signeringsoppdrag",
            "I de aller fleste tilfeller er det varselet som uteblir (epostklient oppfatter varsel som spam etc), så da kan dere be mottaker logge inn på signering.posten.no. Dersom det er sendt signeringsoppdrag til dem så skal de finne dem der."
        ),
        (
            "sak/arkiv-systemet får ikke oppdatert status på signeringsoppdrag",
            "Ta kontakt med leverandør av sak/arkivsystem."
        ),
        (
            "Kan vi bruke registeret til en spørreundersøkelse?",
            "https://samarbeid.digdir.no/media/218/download. Se punkt 4.1.1.5 i veiledningen."
        ),
        (
            "Eg får feilmeldinga Invalid assertion. Client authentication failed. Invalid JWT. The client requires pre-registered jwk and no key identifier (kid) provided",
            "Feilmeldinga Invalid assertion. Client authentication failed. Invalid JWT. The client requires pre-registered jwk and no key identifier (kid) provided betyr at det er ein mismatch mellom det som er registrert for klienten i sjølvbetjeningsportalen, og det som faktisk blir brukt i forespørselen mot Maskinporten. "
        )
    ]

# ============================================================================
# QUESTION-ANSWER EXTRACTION
# ============================================================================

def smart_join(parts: List[str]) -> str:
    if not parts:
        return ""
    
    cleaned_parts = []
    cutoff_re = re.compile(r"^(.*?)(?:\bkl\.\s*\d{1,2}:\d{2}\s+skrev\s+[^:]+:).*", re.DOTALL | re.IGNORECASE)
    
    for part in parts:
        match = cutoff_re.match(part)
        if match:
            cleaned_parts.append(match.group(1).rstrip())
        else:
            cleaned_parts.append(part.rstrip())
    
    result = cleaned_parts[0]
    for part in cleaned_parts[1:]:
        if not result.rstrip().endswith(('.', '!', '?')):
            result = result.rstrip() + '. '
        else:
            result = result.rstrip() + ' '
        result += part.lstrip()
    
    return result


def extract_qa_pairs(case_text: str) -> List[Tuple[str, str]]:
    pairs = []
    lines = case_text.splitlines()
    i = 0
    current_question = []
    current_answer = []

    def flush_pair():
        """Ferdigstiller og legger til et spørsmål-svar par."""
        nonlocal current_question, current_answer
        if current_question and current_answer:
            q = clean_text(smart_join(current_question))
            a = clean_text(smart_join(current_answer))
            if q and a:
                pairs.append((q, a))
        current_question = []
        current_answer = []

    while i < len(lines):
        line = lines[i]
        question_match = QUESTION_PATTERN.match(line)
        answer_match = ANSWER_PATTERN.match(line)

        if question_match:
            if current_question and current_answer:
                flush_pair()
            current_question.append(question_match.group(1))
            i += 1
            while i < len(lines) and not TIMESTAMP_PATTERN.match(lines[i]):
                current_question.append(lines[i])
                i += 1

        elif answer_match:
            current_answer.append(answer_match.group(1))
            i += 1
            while i < len(lines) and not TIMESTAMP_PATTERN.match(lines[i]):
                current_answer.append(lines[i])
                i += 1
        else:
            i += 1

    flush_pair()
    return pairs

def process_cases(cases: List[str], debug: bool = False) -> List[Tuple[str, str]]:
    all_pairs = []
   
    for i, case in enumerate(cases):
        case_id = i + 1
        log_message(f"Processing case {case_id}/{len(cases)}...", "CYAN")
       
        try:
            pairs = extract_qa_pairs(case)
           
            if pairs:
                all_pairs.extend(pairs)
                log_message(f"Found {len(pairs)} valid question-answer pairs in case {case_id}", "GREEN")
            else:
                log_message(f"No valid question-answer pairs found in case {case_id}", "YELLOW")
               
            if debug and pairs:
                for q, a in pairs:
                    print(f"\nQuestion: {q[:50]}...")
                    print(f"Answer: {a[:50]}...")
               
        except Exception as e:
            log_error(f"Error processing case {case_id}: {str(e)}", case[:100] if case else "")
   
    return all_pairs


def remove_duplicates(pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set()
    unique_pairs = []
   
    for question, answer in pairs:
        q_clean = question.strip().replace('\n', ' ')
        a_clean = answer.strip().replace('\n', ' ')
       
        if q_clean == a_clean:
            continue 
       
        pair_tuple = (q_clean, a_clean)
        if pair_tuple not in seen:
            unique_pairs.append(pair_tuple)
            seen.add(pair_tuple)
   
    return unique_pairs

# ============================================================================
# CSV EXPORT
# ============================================================================
def save_csv(pairs: List[Tuple[str, str]], filename: str) -> bool:
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
 
            csvfile.write("spm,svar\n")
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for question, answer in pairs:
          
                if "Delivery has failed to these recipients or groups" in answer:
                    continue
                q_flat = question.replace('\n', ' ').strip()
                a_flat = answer.replace('\n', ' ').strip()
                writer.writerow([q_flat, a_flat])
        return True
    except Exception as e:
        log_error(f"Could not write to '{filename}': {str(e)}")
        return False


def save_predefined_csv(pairs: List[Tuple[str, str]], filename: str = "predefined_csv.csv") -> bool:
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
     
            csvfile.write("spm,svar\n")
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for question, answer in pairs:
                q_flat = question.replace('\n', ' ').strip()
                a_flat = answer.replace('\n', ' ').strip()
                writer.writerow([q_flat, a_flat])
        return True
    except Exception as e:
        log_error(f"Could not write to '{filename}': {str(e)}")
        return False

# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main() -> None:
    args = parse_arguments()

    # Handle predefined question-answer pairs first
    predefined_pairs = []
    if args.include_predefined:
        log_message("📚 Adding predefined question-answer pairs...", "CYAN")
        predefined_pairs = get_predefined_qa_pairs()
        log_message(f"Added {len(predefined_pairs)} predefined question-answer pairs", "GREEN")
        
        # Save predefined question-answer pairs to a separate CSV file
        if predefined_pairs and save_predefined_csv(predefined_pairs):
            log_message(f"{len(predefined_pairs)} predefined question-answer pairs saved to predefined_csv.csv", "GREEN")
    
    # Continue with normal processing
    if os.path.isdir(args.input):
        log_message(f"Reading files from '{args.input}' directory...", "CYAN")
        text = load_input_directory(args.input)
    else:
        log_message(f"Reading from file '{args.input}'...", "CYAN")
        text = load_input_file(args.input)
    
    if text is None and not predefined_pairs:
        log_error("No valid input data found. Exiting.")
        return
    
    # Process cases only if we have input text
    unique_qa_pairs = []
    total_cases = 0
    
    if text is not None:
        cases = split_into_cases(text)
        total_cases = len(cases)
        log_message(f"📦 Found {total_cases} cases.", "GREEN")
       
        if total_cases > 0:
            log_message("🚀 Starting to process cases...", "GREEN")
            qa_pairs = process_cases(cases, args.debug)
            raw_pairs_count = len(qa_pairs)
            unique_qa_pairs = remove_duplicates(qa_pairs)
            log_message(f"Found {len(unique_qa_pairs)} unique question-answer pairs from cases", "GREEN")
        else:
            log_message("⚠️ No cases found in input files.", "YELLOW")
    
    # Combine predefined first, then processed pairs
    combined_pairs = predefined_pairs + unique_qa_pairs
    
    # Save the combined pairs (predefined first, then from cases)
    if combined_pairs:
        if save_csv(combined_pairs, args.output):
            log_message(
                f"\nDone! {len(combined_pairs)} total question-answer pairs saved to {args.output}",
                "GREEN"
            )
        else:
            log_message("Could not save results.", "RED")
    else:
        log_message("No question-answer pairs to save.", "RED")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def initialize_error_log() -> None:
    if not os.path.exists(CONFIG["files"]["error_log"]):
        try:
            with open(CONFIG["files"]["error_log"], "w", encoding="utf-8") as f:
                f.write(f"# Error log created {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        except IOError as e:
            print(f"Could not create error log: {e}")


if __name__ == "__main__":
    initialize_error_log()
   
    try:
        main()
    except KeyboardInterrupt:
        log_message("\n⚠️ Process interrupted by user.", "YELLOW")
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        raise  # Re-raise for debugging if necessary