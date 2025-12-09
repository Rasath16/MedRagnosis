import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset

# Import your backend logic
from server.diagnosis.query import chat_diagnosis_report
from server.models.db_models import ChatMessage

# Import LangChain OpenAI components for the Ragas Evaluator
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

# 1. SETUP
# ⚠️ IMPORTANT: Upload 'lipid.pdf' to your running app first!
# Then copy the doc_id from the UI or logs and paste it below.
TEST_DOC_ID = "065b6e48-bc6f-41b5-bb86-1a90697872b7" 
TEST_USERNAME = "tester" 

# 2. DEFINE YOUR TEST SET (Customized for lipid.pdf)
test_questions = [
    "What is the total cholesterol level for Mrs. Priyani Almeda?",
    "Are there any abnormal results in the lipid profile? Which ones are high?",
    "When was this sample collected and who referred the patient?",
    "What is the HDL to LDL ratio listed in the report?",
    "Based on the target levels provided, is the LDL cholesterol considered optimal?"
]

# Ground truths must be STRINGS (not lists) to avoid validation errors
ground_truths = [
    "The total cholesterol level is 165 mg/dL.",
    "Yes, there are abnormal results. The Triglycerides are 244 mg/dL (Reference: 10-200) and VLDL Cholesterol is 48.8 mg/dL (Reference: 10-41). Both are above the reference range.",
    "The sample was collected on 05 Dec, 2025. The patient was referred by Kalubowila Hospital.",
    "The HDL/LDL ratio is 0.6.",
    "Yes, the LDL cholesterol is 71.2 mg/dL. According to the target levels, LDL < 100 mg/dL is considered Optimal."
]

async def generate_responses():
    """Runs the questions through your actual RAG pipeline"""
    data_samples = {
        'question': [],
        'answer': [],
        'contexts': [],
        'ground_truth': ground_truths 
    }

    print(f"🚀 Starting evaluation on {len(test_questions)} questions...")

    for i, question in enumerate(test_questions):
        print(f"Processing ({i+1}/{len(test_questions)}): {question}")
        
        # Mock the message format your API expects
        mock_messages = [ChatMessage(role="user", content=question)]
        
        try:
            # Call your actual backend function
            response = await chat_diagnosis_report(TEST_USERNAME, TEST_DOC_ID, mock_messages)
            
            data_samples['question'].append(question)
            data_samples['answer'].append(response["diagnosis"])
            data_samples['contexts'].append(response["contexts"])
            
        except Exception as e:
            print(f"❌ Error on question '{question}': {e}")
            # If backend fails (502 error), fill with placeholder to prevent crash
            data_samples['question'].append(question)
            data_samples['answer'].append("I could not retrieve the information due to a server error.")
            data_samples['contexts'].append(["No context retrieved"])

    return data_samples

def run_evaluation():
    # 1. Generate Data
    raw_data = asyncio.run(generate_responses())
    
    # 2. Convert to HuggingFace Dataset
    dataset = Dataset.from_dict(raw_data)
    
    # 3. Define Metrics
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]

    # 4. Define the Evaluator (The Judge)
    # Ragas uses this LLM to grade your LLaMA model's answers.
    # We use GPT-3.5-turbo or GPT-4 as the "Gold Standard" judge.
    judge_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    judge_embeddings = OpenAIEmbeddings()

    print("\n🧠 Running Ragas Evaluation (this may take a minute)...")
    
    # Pass the explicit llm and embeddings to avoid 'InstructorLLM' error
    results = evaluate(
        dataset, 
        metrics=metrics, 
        llm=judge_llm, 
        embeddings=judge_embeddings
    )

    # 5. Display Results
    print("\n📊 ============ EVALUATION RESULTS ============")
    print(results)
    
    df = results.to_pandas()
    
    # Check if columns exist before printing to avoid KeyError
    cols_to_print = ['question', 'faithfulness', 'answer_relevancy', 'context_precision','context_recall']
    existing_cols = [c for c in cols_to_print if c in df.columns]
    
    print("\n📝 Detailed Breakdown:")
    print(df[existing_cols])
    
    df.to_csv("rag_evaluation_results.csv", index=False)
    print("\n✅ Results saved to 'rag_evaluation_results.csv'")

if __name__ == "__main__":
    run_evaluation()