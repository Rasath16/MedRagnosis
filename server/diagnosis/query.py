import os
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medragnosis")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

embed_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile", groq_api_key=GROQ_API_KEY)

# 1. Chain to Rephrase Follow-up Questions 
condense_q_system = """Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

condense_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", condense_q_system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
condense_q_chain = condense_q_prompt | llm | StrOutputParser()

#  2. Chain to Answer Questions using RAG 
qa_system = """You are a medical assistant AI called MedRagnosis. 
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know. 
Keep the answer concise but professional.
ALWAYS reference the source context when making a medical claim (e.g., "According to the Blood Test (Page 1)...").
If the context does not contain the answer, explicitly say so.

Context:
{context}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)
rag_chain = qa_prompt | llm


async def chat_diagnosis_report(user: str, doc_id: str, messages: list):
    """
    Handles a full chat conversation.
    1. Rephrases the latest question based on history.
    2. Retrieves context using the rephrased question.
    3. Generates an answer using the original question + history + context.
    """
    # Extract the latest question
    latest_question = messages[-1].content
    
    # Convert incoming messages to LangChain format for history
    chat_history = []
    for msg in messages[:-1]:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))

    # 1. Condense Question (if there is history)
    if chat_history:
        standalone_question = await asyncio.to_thread(
            condense_q_chain.invoke, 
            {"chat_history": chat_history, "question": latest_question}
        )
        print(f"Rephrased Query: {standalone_question}")
    else:
        standalone_question = latest_question

    # 2. Retrieve Context (Using standalone question)
    embedding = await asyncio.to_thread(embed_model.embed_query, standalone_question)
    
    results = await asyncio.to_thread(
        index.query,
        vector=embedding,
        top_k=5,
        include_metadata=True,
        filter={"doc_id": doc_id} 
    )

    contexts = []
    sources_set = set()
    for match in results.get("matches", []):
        md = match.get("metadata", {})
        text_snippet = md.get("text") or ""
        contexts.append(text_snippet)
        sources_set.add(md.get("source"))

    if not contexts:
        return {"diagnosis": "I couldn't find relevant information in the uploaded report.", "sources": []}
    
    context_text = "\n\n".join(contexts)

    # 3. Generate Answer
    final = await asyncio.to_thread(
        rag_chain.invoke,
        {
            "context": context_text,
            "chat_history": chat_history,
            "question": latest_question
        }
    )

    return {"diagnosis": final.content, "sources": list(sources_set), "contexts": contexts}

async def longitudinal_analysis(username: str, question: str):
    """
    Searches across ALL reports belonging to a user to find trends.
    """
    embedding = await asyncio.to_thread(embed_model.embed_query, question)
    
    # Filter by 'uploader' instead of 'doc_id'
    results = await asyncio.to_thread(
        index.query,
        vector=embedding,
        top_k=10,  
        include_metadata=True,
        filter={"uploader": username} 
    )

    contexts = []
    for match in results.get("matches", []):
        md = match.get("metadata", {})
        date_str = md.get("uploaded_at", "Unknown Date") 
        text = f"[Date: {date_str}] {md.get('text', '')}"
        contexts.append(text)

    if not contexts:
        return {"diagnosis": "No records found to analyze trends.", "sources": []}
    
    context_text = "\n\n".join(contexts)
    
    # Use a specific prompt for trend analysis
    trend_prompt = f"""
    You are a medical analyst. Analyze the provided excerpts from multiple reports over time.
    Identify trends, changes in values, or recurring issues.
    
    Context History:
    {context_text}
    
    User Question: {question}
    """
    
    final = await asyncio.to_thread(llm.invoke, trend_prompt)
    
    return {"diagnosis": final.content, "sources": []}