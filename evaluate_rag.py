import os
import asyncio
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevance,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings


from server.diagnosis.query import chat_diagnosis_report

# Load Environment Variables
from dotenv import load_dotenv
load_dotenv()

.
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4-turbo"))
evaluator_embeddings = OpenAIEmbeddings()


test_data = [
    {
        "question": "What is the patient's hemoglobin level?",
        "ground_truth": "The patient's hemoglobin level is 13.5 g/dL.",
        "doc_id": "YOUR_TEST_DOC_ID_HERE" 
    },
    {
        "question": "Does the patient show signs of anemia?",
        "ground_truth": "No, the hemoglobin and iron levels are within normal range, indicating no anemia.",
        "doc_id": "YOUR_TEST_DOC_ID_HERE"
    },
    
]

async def run_evaluation():
    print("🚀 Starting RAG Evaluation...")
    
    results_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    from collections import namedtuple
    Message = namedtuple('Message', ['role', 'content'])

    for item in test_data:
        print(f"Processing: {item['question']}...")
        
        # Simulate the API input
        messages = [Message(role="user", content=item["question"])]
        
        # Call your backend function
        response = await chat_diagnosis_report(
            user="evaluator",
            doc_id=item["doc_id"],
            messages=messages
        )
        
        # Collect data for RAGAS
        results_data["question"].append(item["question"])
        results_data["answer"].append(response["diagnosis"])
        results_data["contexts"].append(response["contexts"]) # The list of strings we added in Step 2
        results_data["ground_truth"].append(item["ground_truth"])

    # 3. CONVERT TO DATASET
    dataset = Dataset.from_dict(results_data)

    # 4. RUN RAGAS METRICS
    print("📊 Calculating Metrics (this relies on OpenAI/LLM calls)...")
    
    scores = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,      # Did the AI make things up not in the context?
            answer_relevance,  # Did it answer the actual question?
            context_precision, # Did the vector DB find relevant chunks?
            context_recall,    # Did the vector DB miss the answer?
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings
    )

    # 5. DISPLAY RESULTS
    df = scores.to_pandas()
    print("\n\n✅ EVALUATION RESULTS:")
    print(df[['question', 'faithfulness', 'answer_relevance', 'context_precision']].to_markdown())
    
    # Save to CSV for your CV/Report
    df.to_csv("rag_evaluation_report.csv", index=False)
    print("\nSaved detailed report to rag_evaluation_report.csv")

if __name__ == "__main__":
    asyncio.run(run_evaluation())