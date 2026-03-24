import chromadb
from chromadb.utils import embedding_functions
from config import OPENAI_API_KEY, CHROMA_HOST
from difflib import SequenceMatcher


# Initialize embedding function
embedder = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)


# Connect to Chroma server
client = chromadb.HttpClient(
    host=CHROMA_HOST,
    port=443,
    ssl=True
)


# Create or load collection
collection = client.get_or_create_collection(
    name="news_claims",
    embedding_function=embedder
)


# -------- TEXT SIMILARITY FUNCTION --------
def text_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# -------- SEARCH CLAIM --------
def search_claim(claim):

    results = collection.query(
        query_texts=[claim],
        n_results=1
    )

    if (
        results
        and results["documents"]
        and len(results["documents"][0]) > 0
        and results["distances"]
        and len(results["distances"][0]) > 0
    ):

        stored_claim = results["documents"][0][0]
        distance = results["distances"][0][0]

        similarity = text_similarity(claim, stored_claim)

        # Debug prints
        print("Vector distance:", distance)
        print("Text similarity:", similarity)
        print("Stored claim:", stored_claim)

        # Strict conditions for cache usage
        if distance < 0.25 and similarity > 0.85:
            return results["metadatas"][0][0]

    return None


# -------- STORE CLAIM --------
def store_claim(claim, metadata, claim_id):

    collection.add(
        documents=[claim],
        metadatas=[metadata],
        ids=[claim_id]
    )