import csv
import logging

from langchain.schema import Document

from app.services.chroma_service import ChromaService

logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


def load_csv_documents(csv_path: str) -> list:
    """
    Loads a CSV file where each row is a (question, answer) pair.
    Returns a list of LangChain Document objects with question as content and answer as metadata.
    """

    documents = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row['spm']
            answer = row['svar']
            doc = Document(
                page_content=question,
                metadata={'answer': answer, 'source': '2024sorted_man_7.csv-clean'},
            )
            documents.append(doc)
    print(f'Loaded {len(documents)} Q&A entries from CSV')
    return documents


chroma = ChromaService()

# Switch to CSV collection
csv_collection = 'servicedesk_qna_clean'
chroma.switch_collection(csv_collection)

# Load and add
csv_docs = load_csv_documents('./Documentation/servicedeskQuestions/2024sorted_man_7_clean.csv')
chroma.add_documents(csv_docs)

logger.info(f'Added {len(csv_docs)} FAQ entries into {csv_collection}')
