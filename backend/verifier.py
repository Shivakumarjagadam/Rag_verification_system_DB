import hashlib
import json
from datetime import datetime
import openai

from config import OPENAI_API_KEY
from backend.google_search import google_search
from backend.rag_pipeline import build_context
from database.chroma_db import search_claim, store_claim


openai.api_key = OPENAI_API_KEY


# Generate unique ID for claim
def hash_claim(claim):

    return hashlib.sha256(
        claim.lower().strip().encode()
    ).hexdigest()


# Main verification function
def verify_claim(claim):

    claim_id = hash_claim(claim)

    # 1️⃣ Check if claim already exists in DB
    cached = search_claim(claim)

    if cached:
        cached["source_type"] = "database"
        cached["cached"] = True

        # Convert sources string back to list
        if isinstance(cached.get("sources"), str):
            cached["sources"] = json.loads(cached["sources"])

        return cached


    # 2️⃣ If not cached → Google Search
    search_results = google_search(claim)

    context = build_context(search_results)


    # 3️⃣ Send context to LLM
    prompt = f"""
You are a professional fact-checking AI.

Claim:
{claim}

Evidence:
{context}

Respond exactly in this format:

VERDICT: REAL or FAKE or UNVERIFIED
CONFIDENCE: number 0-100
EXPLANATION: 3 sentences.
"""


    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a fact checking AI."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )


    content = response.choices[0].message.content


    verdict = "UNVERIFIED"
    confidence = 50
    explanation = ""


    for line in content.split("\n"):

        if line.startswith("VERDICT"):
            verdict = line.split(":")[1].strip()

        elif line.startswith("CONFIDENCE"):
            confidence = float(line.split(":")[1].strip())

        elif line.startswith("EXPLANATION"):
            explanation = line.split(":", 1)[1].strip()


    # 4️⃣ Prepare result
    result = {
        "verdict": verdict,
        "confidence": confidence,
        "explanation": explanation,
        "sources": json.dumps(search_results),   # convert list → string for DB
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_type": "google"
    }


    # 5️⃣ Store in ChromaDB
    store_claim(claim, result, claim_id)


    # Convert sources back for UI display
    result["sources"] = search_results


    return result