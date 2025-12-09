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


from server.diagnosis.query import chat_diagnosis_report
from server.models.db_models import ChatMessage

load_dotenv()

TEST_DOC_ID = "PASTE_YOUR_DOC_ID_HERE" 
TEST_USERNAME = "tester" 


test_questions = [

    "What is the total cholesterol level for Mrs. Priyani Almeda?",
    
    "Are there any abnormal results in the lipid profile? Which ones are high?",
    
    "When was this sample collected and who referred the patient?",
    
    "What is the HDL to LDL ratio listed in the report?",
    
    "Based on the target levels provided, is the LDL cholesterol considered optimal?"
]

ground_truths = [
    # A1
    ["The total cholesterol level is 165 mg/dL."],
    
    ["Yes, there are abnormal results. The Triglycerides are 244 mg/dL (Reference: 10-200) and VLDL Cholesterol is 48.8 mg/dL (Reference: 10-41). Both are above the reference range."],

    ["The sample was collected on 05 Dec, 2025. The patient was referred by Kalubowila Hospital."],
    
    ["The HDL/LDL ratio is 0.6."],
    
    ["Yes, the LDL cholesterol is 71.2 mg/dL. According to the target levels, LDL < 100 mg/dL is considered Optimal."]
]

async def generate_responses():
    """Runs the questions through your actual RAG pipeline"""
    data_samples = {
        'question': [],
        'answer': [],
        'contexts': [],
        'ground_truth': ground_truths # Remove this line if you didn't define ground_truths
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
            data_samples['contexts'].append(response["contexts"]) # The list of strings we added in Step 1
            
        except Exception as e:
            print(f"❌ Error on question '{question}': {e}")
            # Fill with empty data to keep lists aligned
            data_samples['question'].append(question)
            data_samples['answer'].append("Error")
            data_samples['contexts'].append([""])

    return data_samples

def run_evaluation():
    # 1. Generate Data
    raw_data = asyncio.run(generate_responses())
    
    # 2. Convert to HuggingFace Dataset (Required by Ragas)
    dataset = Dataset.from_dict(raw_data)
    
    # 3. Select Metrics
    # Note: Using OpenAI GPT-3.5/4 for evaluation is standard best practice,
    # even if your RAG uses LLaMA. Ensure OPENAI_API_KEY is in .env
    metrics = [
        faithfulness,      # Is the answer derived from the context? (Hallucination check)
        answer_relevancy,  # Does the answer actually address the user's question?
        context_precision, # (Requires ground_truth)
        context_recall     # (Requires ground_truth)
    ]

    print("\n🧠 Running Ragas Evaluation (this may take a minute)...")
    results = evaluate(dataset, metrics=metrics)

    # 4. Display Results
    print("\n📊 ============ EVALUATION RESULTS ============")
    print(results)
    
    # Convert to Pandas for easier reading
    df = results.to_pandas()
    print("\n📝 Detailed Breakdown:")
    print(df[['question', 'faithfulness', 'answer_relevancy']])
    
    # Save to CSV for your portfolio
    df.to_csv("rag_evaluation_results.csv", index=False)
    print("\n✅ Results saved to 'rag_evaluation_results.csv'")

if __name__ == "__main__":
    run_evaluation()