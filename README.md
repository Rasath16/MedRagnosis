# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Platform

**MedRagnosis** is an AI-powered medical diagnostic tool that uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze patient medical reports. It provides preliminary diagnoses, key findings, and recommendations using the **Groq LLaMA 3.3** engine, accessible via a user-friendly Streamlit interface.

> **🔴 Live Demo:** [https://medragnosis.streamlit.app/](https://medragnosis.streamlit.app/)
>
> **Status:** ✅ Backend (Deployed on Render) | ✅ Frontend (Deployed on Streamlit)

---

## 🚀 Features

### 👤 For Patients
* **Secure Account Management:** Sign up and log in securely.
* **Document Upload:** Upload medical reports (PDF/TXT) directly to the system.
* **AI Diagnosis:** Receive instant analysis, potential diagnoses, and actionable advice based *strictly* on your uploaded report.
* **Transparent Sources:** View the specific segments of your report the AI used to generate the answer.

### 👨‍⚕️ For Doctors
* **Patient Lookup:** Search for patient records by username.
* **History Review:** Access a comprehensive history of a patient's past diagnosis queries and AI responses.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit (Python) |
| **Backend** | FastAPI (Python 3.13) |
| **Deployment** | Render (Backend), Streamlit Cloud (Frontend) |
| **Database** | MongoDB (User data & Diagnosis history) |
| **Vector DB** | Pinecone (Serverless) |
| **LLM Inference** | Groq API (LLaMA 3.3-70b-versatile) |
| **Embeddings** | OpenAI (text-embedding-3-small) |
| **Orchestration** | LangChain |

---

## 📂 Project Structure

```text
MedRagnosis/
├── client/              # Streamlit Frontend Application
│   ├── app.py           # Main UI Logic
│   └── requirements.txt # Frontend dependencies
├── server/              # FastAPI Backend Application
│   ├── auth/            # Authentication Routes & Models
│   ├── config/          # Database & Env Config
│   ├── diagnosis/       # RAG Logic (Pinecone & Groq)
│   ├── models/          # Pydantic Data Models
│   ├── reports/         # File Processing & Vector Ingestion
│   └── main.py          # App Entry Point
├── uploaded_dir/        # Local storage for temp files
├── requirements.txt     # Backend dependencies
└── README.md
````

-----

## ⚙️ Local Development Setup

Follow these steps to run the application locally.

### 1\. Clone the Repository

```bash
git clone [https://github.com/yourusername/MedRagnosis.git](https://github.com/yourusername/MedRagnosis.git)
cd MedRagnosis
```

### 2\. Backend Setup (FastAPI)

1.  **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate   # Linux/Mac
    # .venv\Scripts\activate    # Windows
    ```

2.  **Install Backend Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory:

    ```ini
    # Database
    MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net
    DB_NAME=MedRagnosis

    # AI Services
    PINECONE_API_KEY=your_pinecone_key
    PINECONE_INDEX_NAME=medragnosis-index
    OPENAI_API_KEY=your_openai_key
    GROQ_API_KEY=your_groq_key

    # System
    UPLOAD_DIR=./uploaded_dir
    ```

4.  **Run the Server:**

    ```bash
    uvicorn server.main:app --reload
    ```

    *The Backend API will run at `http://127.0.0.1:8000`*

### 3\. Frontend Setup (Streamlit)

1.  **Navigate to the client directory (optional, or run from root):**
    *Ensure you have the client dependencies installed. If they differ from root, install them:*

    ```bash
    pip install -r client/requirements.txt
    ```

2.  **Configure Client Environment:**
    Create a `.env` file inside the `client/` folder (or ensure your main `.env` has this if running from root with modified paths):

    ```ini
    API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
    ```

    *(Note: For the live app, this points to the Render backend URL)*

3.  **Run the Frontend:**

    ```bash
    streamlit run client/app.py
    ```

    *The UI will open at `http://localhost:8501`*

-----

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **Auth** | | |
| `POST` | `/auth/signup` | Register a new user (`patient` or `doctor`). |
| `GET` | `/auth/login` | Basic Auth login. |
| **Reports** | | |
| `POST` | `/reports/upload` | Upload PDF reports (Patient only). Returns `doc_id`. |
| **Diagnosis** | | |
| `POST` | `/diagnosis/from_report` | Get AI diagnosis for a specific document. |
| `GET` | `/diagnosis/by_patient_name` | View diagnosis history (Doctor only). |

-----

## 🔮 Roadmap

  * [x] **Frontend Implementation:** Built with Streamlit.
  * [x] **Deployment:** Live on Render & Streamlit Cloud.
  * [ ] **JWT Implementation:** Upgrade from Basic Auth to stateless tokens.
  * [ ] **Multi-File Context:** Analyze multiple reports in a single query.
  * [ ] **Chat Interface:** Enable follow-up questions on the diagnosis.

-----

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact

  * **Author**: Tharusha Rasath
  * **Email**: tharusharasatml@gmail.com

<!-- end list -->

```
```
