import os
import re
import csv
import argparse
from datetime import datetime

# Configuration dictionary storing settings like file paths and terminal colors
CONFIG = {
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


# Print a color-coded log message to the terminal
def log_message(message, color_key="GREEN"):
    color = CONFIG["colors"][color_key]
    reset = CONFIG["colors"]["RESET"]
    print(f"{color}{message}{reset}")


# Log error messages both to terminal and optionally a file
def log_error(message, context="", write_to_file=True):
    if write_to_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CONFIG["files"]["error_log"], "a", encoding="utf-8") as err_log:
            err_log.write(f"[{timestamp}] {message}\n")
            if context:
                err_log.write(f"Context: {context}...\n\n")

    log_message(f" {message}", "RED")


# Define and parse command line arguments using argparse
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Convert service desk data to CSV format without AI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--include-predefined", action="store_true",
                        help="Include predefined Q&A pairs in the output")
    parser.add_argument("--input", "-i", type=str, default=CONFIG["files"]["default_input"],
                        help="Input file name")
    parser.add_argument("--output", "-o", type=str, default=CONFIG["files"]["default_output"],
                        help="Output CSV file name")
    parser.add_argument("--debug", action="store_true",
                        help="Print extra debug information")
    return parser.parse_args()


# Read input file contents and return as a string
def load_input_file(filename):
    if not os.path.exists(filename):
        log_error(f"File '{filename}' not found.")
        return None

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        log_error(f"Could not read file '{filename}': {str(e)}")
        return None


# Load all text files from a directory
def load_input_directory(directory):
    if not os.path.exists(directory):
        log_error(f"Directory '{directory}' not found.")
        return None

    if not os.path.isdir(directory):
        log_error(f"'{directory}' is not a directory.")
        return None

    all_content = []
    text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]

    if not text_files:
        log_error(f"No text files found in '{directory}'.")
        return None

    log_message(f"Found {len(text_files)} text files in {directory}", "GREEN")

    for file in text_files:
        file_path = os.path.join(directory, file)
        log_message(f"Reading file: {file}", "CYAN")
        content = load_input_file(file_path)
        if content:
            all_content.append(content)

    if not all_content:
        return None

    # Join all files' content into one big string
    return "\n\n".join(all_content)


# Split raw text into separate cases by "=== Sak: ..." markers
def split_into_cases(text):
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


# Regular expression patterns for extracting messages
TIMESTAMP_PATTERN = r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]'
QUESTION_PATTERN = r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]\s*\[\s*Ekstern\s*e-post\s*\]\s*(.*)'
ANSWER_PATTERN = r'\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\]\s*(?!\[\s*Ekstern\s*e-post\s*\])(.*)'


# Remove case number, timestamp brackets, and email headers from text
def clean_text(text):
    # Remove case number
    text = re.sub(r'===\s*Sak:\s*[A-Za-z0-9-]+\s*===', '', text)

    # Remove timestamps
    text = re.sub(TIMESTAMP_PATTERN, '', text)

    # Remove "[ Ekstern e-post ]" tag
    text = re.sub(r'\[\s*Ekstern\s*e-post\s*\]', '', text)

    # Enhanced name removal patterns
    # 1. Names after common greetings
    text = re.sub(
        r'(?i)(med\s+vennlig\s+hilsen|mvh|hilsen|regards|fra)[,:]?\s*([A-ZÆØÅa-zæøå]+(?:\s+[A-ZÆØÅa-zæøå]+){1,3})',
        r'\1', text)

    # 2. Names at beginning of lines (common in emails)
    text = re.sub(r'(?m)^([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,2})[\.,!]?\s*$', '', text)

    # 3. Names with common titles
    text = re.sub(
        r'(?i)([A-ZÆØÅa-zæøå]+(?:\s+[A-ZÆØÅa-zæøå]+){1,3})\s*[,/]\s*(seniorrådgiver|rådgiver|direktør|konsulent|leder|sjef|prosjektleder|teamleder|avdelingsleder)',
        '', text)

    # 4. Common Norwegian format: Firstname Lastname <email>
    text = re.sub(r'([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+){1,2})\s*<[^>]+@[^>]+>', '', text)

    # Remove various greeting formats (now more comprehensive)
    greetings_pattern = r'(?i)(med\s+vennlig\s+hilsem|.Med\s+vennleg\s+helsing|.Med\s+vennlig\s+hilsen|med\s+vennlig\s+hilsen|mvh|vennlig\s+hilsen|beste\s+hilsen|hilsen|regards|med\s+venleg\s+helsing)[,\.]?\s*'
    text = re.sub(greetings_pattern, '', text)

    # Try to identify and remove names (names often appear after greetings or at end of messages)
    text = re.sub(r'(?i)(hilsen|regards|fra)[,:]?\s*[A-ZÆØÅa-zæøå]+\s+[A-ZÆØÅa-zæøå]+', '', text)

    # Remove email addresses
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '', text)

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

    # Remove CRM references
    text = re.sub(r'CRM:\d+', '', text)

    # Remove base64 image data and HTML image tags
    text = re.sub(r'<img\s+src="data:image/[^"]+"\s*/?>', '', text)
    text = re.sub(r'data:image/[a-zA-Z0-9+/=]+;base64,[a-zA-Z0-9+/=\s]+', '', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Remove URL parameters (often contain unwanted metadata)
    text = re.sub(r'\?[a-zA-Z0-9%=&;_\-+.]+', '', text)

    # Remove multiple empty lines (replace with a single newline)
    text = re.sub(r'\n\s*\n+', '\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


# Returns a list of predefined question-answer pairs. These are manually curated frequently asked questions.
def get_predefined_qa_pairs():
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


def extract_qa_pairs(case_text):
    pairs = []
    lines = case_text.splitlines()
    i = 0
    current_question = []
    current_answer = []

    def smart_join(parts):
        import re
        if not parts:
            return ""
        cleaned_parts = []

        cutoff_re = re.compile(r"^(.*?)\bkl\.\s*\d{1,2}:\d{2}\s+skrev\s+[^:]+:.*", re.DOTALL | re.IGNORECASE)
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

    def flush_pair():
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
        question_match = re.match(QUESTION_PATTERN, line)
        answer_match = re.match(ANSWER_PATTERN, line)

        if question_match:
            if current_question and current_answer:
                flush_pair()
            current_question.append(question_match.group(1))
            i += 1
            while i < len(lines) and not re.match(TIMESTAMP_PATTERN, lines[i]):
                current_question.append(lines[i])
                i += 1

        elif answer_match:
            current_answer.append(answer_match.group(1))
            i += 1
            while i < len(lines) and not re.match(TIMESTAMP_PATTERN, lines[i]):
                current_answer.append(lines[i])
                i += 1
        else:
            i += 1

    flush_pair()
    return pairs


# Process all cases and extract Q&A pairs
def process_cases(cases, debug=False):
    all_pairs = []

    for i, case in enumerate(cases):
        case_id = i + 1
        log_message(f"Processing case {case_id}/{len(cases)}...", "CYAN")

        try:
            pairs = extract_qa_pairs(case)

            if pairs:
                all_pairs.extend(pairs)
                log_message(f" Found {len(pairs)} valid Q&A pairs in case {case_id}", "GREEN")
            else:
                log_message(f"️ No valid Q&A pairs found in case {case_id}", "YELLOW")

            if debug and pairs:
                for q, a in pairs:
                    print(f"\nQuestion: {q[:50]}...")
                    print(f"Answer: {a[:50]}...")

        except Exception as e:
            log_error(f"Error processing case {case_id}: {str(e)}", case[:100] if case else "")

    return all_pairs


# Remove duplicate Q&A pairs and those with identical question and answer
def remove_duplicates(pairs):
    seen = set()
    unique_pairs = []

    for question, answer in pairs:
        q_clean = question.strip().replace('\n', ' ')
        a_clean = answer.strip().replace('\n', ' ')

        if q_clean == a_clean:
            continue  # Skip identical question-answer pairs

        pair_tuple = (q_clean, a_clean)
        if pair_tuple not in seen:
            unique_pairs.append(pair_tuple)
            seen.add(pair_tuple)

    return unique_pairs


# Save Q&A pairs to CSV file
def save_csv(pairs, filename):
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
            # Skriv header som ren tekst, ikke via csv.writer
            csvfile.write("spm,svar\n")
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            for question, answer in pairs:
                # Filtrer ut uønskede svar
                if "Delivery has failed to these recipients or groups" in answer:
                    continue
                q_flat = question.replace('\n', ' ').strip()
                a_flat = answer.replace('\n', ' ').strip()
                writer.writerow([q_flat, a_flat])
        return True
    except Exception as e:
        log_error(f"Could not write to '{filename}': {str(e)}")
        return False


# Save predefined Q&A pairs to a separate CSV file
def save_predefined_csv(pairs, filename="predefined_csv.csv"):
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as csvfile:
            # Write header as plain text
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


# Modify the main function to check if the input is a file or directory
def main():
    args = parse_arguments()

    # Handle predefined Q&A pairs first
    predefined_pairs = []
    if args.include_predefined:
        log_message(" Adding predefined Q&A pairs...", "CYAN")
        predefined_pairs = get_predefined_qa_pairs()
        log_message(f"Added {len(predefined_pairs)} predefined Q&A pairs", "GREEN")

        # Save predefined Q&A pairs to a separate CSV file
        if predefined_pairs and save_predefined_csv(predefined_pairs):
            log_message(f" {len(predefined_pairs)} predefined Q&A pairs saved to predefined_csv.csv", "GREEN")

    # Continue with regular processing
    if os.path.isdir(args.input):
        log_message(f" Reading files from '{args.input}' directory...", "CYAN")
        text = load_input_directory(args.input)
    else:
        log_message(f" Reading from file '{args.input}'...", "CYAN")
        text = load_input_file(args.input)

    if text is None and not predefined_pairs:
        log_error("No valid input data found. Exiting.")
        return

    # Process cases only if we have input text
    unique_qa_pairs = []
    if text is not None:
        cases = split_into_cases(text)
        num_cases = len(cases)
        log_message(f" Found {num_cases} cases.", "GREEN")

        if num_cases > 0:
            log_message("🚀 Starting to process cases...", "GREEN")
            qa_pairs = process_cases(cases, args.debug)
            unique_qa_pairs = remove_duplicates(qa_pairs)
            log_message(f"Found {len(unique_qa_pairs)} unique Q&A pairs from cases", "GREEN")
        else:
            log_message("⚠ No cases found in the input files.", "YELLOW")

    # Combine predefined first, then processed pairs
    combined_pairs = predefined_pairs + unique_qa_pairs

    # Save the combined pairs (predefined first, then from cases)
    if combined_pairs:
        if save_csv(combined_pairs, args.output):
            log_message(
                f"\n Done! {len(combined_pairs)} total Q&A pairs saved to {args.output}",
                "GREEN"
            )
    else:
        log_message(" No Q&A pairs to save.", "RED")


# Main entry point for the script
if __name__ == "__main__":
    if not os.path.exists(CONFIG["files"]["error_log"]):
        with open(CONFIG["files"]["error_log"], "w", encoding="utf-8") as f:
            f.write(f"# Error log created {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    try:
        main()
    except KeyboardInterrupt:
        log_message("\n⚠ Process interrupted by user.", "YELLOW")
    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")