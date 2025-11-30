
# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Backend

**MedRagnosis** is an AI-powered API service designed to assist in medical diagnostics. It utilizes a **Retrieval-Augmented Generation (RAG)** architecture to analyze patient-uploaded medical reports (PDFs) and generate preliminary diagnoses using the **Groq LLaMA 3.3** engine.

> **Status:** ✅ Backend API (Active) | 🚧 Frontend (In Development)

---

## 🚀 Features

* **Role-Based Authentication:** Secure Basic Auth system distinguishing between **Patients** (uploaders) and **Doctors** (viewers).
* **Medical Document Processing:**
    * PDF upload and parsing.
    * Automated text chunking and vectorization using **OpenAI Embeddings**.
    * Vector storage in **Pinecone**.
* **AI-Driven Diagnosis:**
    * Context-aware answering using **Groq (LLaMA 3.3-70b)**.
    * Generates diagnoses, key findings, and recommended next steps based *only* on the uploaded report context.
* **Diagnosis History:**
    * Patients receive immediate AI feedback.
    * Doctors can query historical diagnosis records for specific patients via MongoDB.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | FastAPI (Python 3.13) |
| **Database** | MongoDB (User data, Diagnosis history) |
| **Vector DB** | Pinecone (Serverless) |
| **LLM Inference** | Groq API (LLaMA 3.3-70b-versatile) |
| **Embeddings** | OpenAI (text-embedding-3-small) |
| **Orchestration** | LangChain |
| **PDF Parsing** | PyPDF / LangChain Community |

---

## 📂 Project Structure

```text
MedRagnosis/
├── server/
│   ├── auth/            # Authentication logic (Routes & Models)
│   ├── config/          # Database connection setup
│   ├── diagnosis/       # RAG logic (Querying Pinecone & Groq)
│   ├── models/          # Pydantic DB models
│   ├── reports/         # PDF processing and Vector Store ingestion
│   └── main.py          # FastAPI Application Entry Point
├── uploaded_dir/        # Local storage for uploaded PDFs
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
````

-----

## ⚙️ Setup & Installation

### 1\. Clone the Repository

```bash
git clone [https://github.com/yourusername/MedRagnosis.git](https://github.com/yourusername/MedRagnosis.git)
cd MedRagnosis
```

### 2\. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Configure Environment Variables

Create a `.env` file in the root directory. You must provide keys for MongoDB, Pinecone, OpenAI, and Groq.

```ini
# Database
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net
DB_NAME=MedRagnosis

# Vector Database (Pinecone)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=medragnosis-index
PINECONE_ENV=us-east-1

# AI Models
OPENAI_API_KEY=your_openai_api_key   # Used for Embeddings
GROQ_API_KEY=your_groq_api_key       # Used for LLaMA 3.3 Inference

# System
UPLOAD_DIR=./uploaded_dir
```

### 5\. Run the Server

```bash
uvicorn server.main:app --reload
```

*The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)*

-----

## 📡 API Endpoints

### 🔐 Authentication

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/signup` | Register a new user (`role`: "patient" or "doctor"). |
| `GET` | `/auth/login` | Basic Auth login. Returns user details. |

### 📄 Reports (Patient Only)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/reports/upload` | Upload PDF medical reports. Triggers vectorization. Returns a `doc_id`. |

### 🩺 Diagnosis

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/diagnosis/from_report` | **(Patient)** Ask for a diagnosis based on a specific `doc_id`. |
| `GET` | `/diagnosis/by_patient_name` | **(Doctor)** View diagnosis history for a specific patient. |

-----

## 🔮 Roadmap

  * [ ] **Frontend Implementation:** Build user interface (React or Streamlit).
  * [ ] **JWT Implementation:** Upgrade from Basic Auth to stateless JWT tokens.
  * [ ] **Multi-File Context:** Allow diagnosis based on multiple uploaded reports simultaneously.

-----

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact

  * **Author**: Tharusha Rasath
  * **Email**: tharusharasatml@gmail.com

<!-- end list -->

```
```
