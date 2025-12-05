import os
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medragnosis")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

embed_model = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)

prompt = PromptTemplate.from_template(
    """
You are a medical assistant. Using only the provided context (portions of the user's report), produce:
1) A concise probable diagnosis (1-2 lines)
2) Key findings from the report (bullet points)
3) Recommended next steps (tests/treatments) — label clearly as suggestions, not medical advice.

Context:
{context}

User question:
{question}
""")

rag_chain = prompt | llm

async def diagnosis_report(user: str, doc_id: str, question: str):
    # embed question
    embedding = await asyncio.to_thread(embed_model.embed_query, question)
    
    # --- FIX: Apply filter directly in Pinecone query ---
    results = await asyncio.to_thread(
        index.query,
        vector=embedding,
        top_k=5,
        include_metadata=True,
        filter={"doc_id": doc_id}  # Only search chunks belonging to THIS document
    )
    # ----------------------------------------------------

    # Collect contexts
    contexts = []
    sources_set = set()
    for match in results.get("matches", []):
        md = match.get("metadata", {})
        # We don't need the manual check anymore, but it's safe to keep or remove
        text_snippet = md.get("text") or ""
        contexts.append(text_snippet)
        sources_set.add(md.get("source"))

    if not contexts:
        return {"diagnosis": "Unable to analyze report. No relevant text found.", "explanation": "No report content indexed for this doc_id"}
    
    # limit context length
    context_text = "\n\n".join(contexts[:5])

    # final call the rag chain
    final = await asyncio.to_thread(rag_chain.invoke, {"context": context_text, "question": question})

    return {"diagnosis": final.content, "sources": list(sources_set)}