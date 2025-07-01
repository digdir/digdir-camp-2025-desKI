import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from azure.ai.inference import ChatCompletionsClient
from langchain_huggingface import HuggingFaceEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage, SystemMessage

#  Load environment variables from .env
load_dotenv()
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_MODEL = os.getenv('AZURE_MODEL')

# 1. Initialize the embedding model
embedding_model = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-base')

# 2. Connect to local ChromaDB
collection = Chroma(
    persist_directory='app/db/chroma_db',
    embedding_function=embedding_model,
    collection_name='dig_docs',
)

# 3. Get the user query
user_query = input('<Hva trenger du hjelp til av DigDir?\n\n')

# 4. Retrieve relevant document chunks and metadata from ChromaDB
results = collection.similarity_search_with_relevance_scores(user_query, k=3)

# 5. If no results were found, exit with a message
if not results:
    print(' Fant ingen relevante tekstbiter.')
    exit()

# 6. Split results into text and metadata
combined_chunks = []
used_sources = set()

for doc, _score in results:
    source = doc.metadata.get('source', 'ukjent fil')
    page = doc.metadata.get('page', 'ukjent side')
    used_sources.add(f'{source}, side {page}')
    combined = f'[Kilde: {source}, side {page}]\n{doc.page_content}'
    combined_chunks.append(combined)

# 7. Combine retrieved context to send to the model
retrieved_context = '\n\n'.join(combined_chunks)

# 8. Build prompt
prompt = f"""
Du er en hjelpsom DigDir-assistent. Du svarer på spørsmål basert på denne dokumentasjonen og ingenting annet.
Svar på norsk om spørsmålet er på norsk, svar på engelsk om svaret er på engelsk. Om du ikke vet svaret, skriv: "Eg hakje peiling".
Svar konsist, men med relevante detaljer fra kildene. Ikke gjett. Ikke legg til informasjon som ikke står i dokumentasjonen.
Du er en ein chatbot som skal svare presist og effektivt, ikkje noe "jeg" eller "hmm"

--- Dokumentasjon ---
{retrieved_context}
----------------------

Spørsmål: {user_query}
Svar:
"""

# 9. Create Azure client
client = ChatCompletionsClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_API_KEY),
    api_version='2024-05-01-preview',
)

# 10. Send the prompt to the model
response = client.complete(
    messages=[
        SystemMessage(content='Du er en hjelpsom DigDir-assistent.'),
        UserMessage(content=prompt),
    ],
    model=AZURE_MODEL,
    max_tokens=1024,
    temperature=0.3,
)

# 11. Display the model's answer
print('\n\n---------------------\n\n')
print(response.choices[0].message.content)

# 12. Display which document sources were used
print('\n\n🗂  Brukte kilder:\n')
for source in sorted(used_sources):
    print('-', source)
