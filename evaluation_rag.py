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

# Import your existing backend logic
# Ensure you are running this from the root folder
from server.diagnosis.query import chat_diagnosis_report
from server.models.db_models import ChatMessage

load_dotenv()

# 1. SETUP: You need a valid Doc ID from a file you uploaded
# Upload a PDF via the UI, check the logs or UI for the doc_id, and paste it here.
TEST_DOC_ID = "PASTE_YOUR_DOC_ID_HERE" 
TEST_USERNAME = "tester" 

# 2. DEFINE YOUR TEST SET
# Questions relevant to the specific medical report you uploaded
test_questions = [
    "What is the patient's cholesterol level?",
    "Are there any abnormalities in the blood count?",
    "What date was this report generated?",
    "Does the patient show signs of anemia?"
]

# (Optional) Ground truths improve accuracy metrics like Context Recall
# If you don't have them, Ragas will calculate what it can without them.
ground_truths = [
    ["The total cholesterol is 185 mg/dL."],
    ["Yes, the white blood cell count is slightly elevated."],
    ["The report is dated October 12, 2023."],
    ["No, hemoglobin levels are within normal range."]
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
        # context_precision, # (Requires ground_truth)
        # context_recall     # (Requires ground_truth)
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