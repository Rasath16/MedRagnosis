# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Platform

**MedRagnosis** is an AI-powered medical diagnostic tool that uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze patient medical reports. It provides preliminary diagnoses, key findings, and recommendations using the **Groq LLaMA 3.3** engine, accessible via a user-friendly Streamlit chat interface.

> **🔴 Live Demo:** [https://medragnosis.streamlit.app/](https://medragnosis.streamlit.app/)
>
> **Status:** ✅ Backend (Deployed on Render via Docker) | ✅ Frontend (Deployed on Streamlit)

---

## 🚀 Features

### 👤 For Patients
* **Secure Account Management:** Sign up and log in securely.
* **Advanced Document Upload (OCR):** Upload medical reports (PDF/TXT). Supports both digital text and **scanned image-based reports** using integrated OCR (Tesseract).
* **Conversational AI Consultant:** Chat naturally with the AI about your report. Ask follow-up questions like "What does that result mean?" or "Is this serious?" maintaining full context.
* **Smart Context:** The chat history automatically clears when you upload a new report, ensuring focused analysis.
* **Transparent Sources:** View the specific segments of your report the AI used to generate each answer.

### 👨‍⚕️ For Doctors
* **Patient Lookup:** Search for patient records by username.
* **History Review:** Access a comprehensive history of a patient's past diagnosis queries and AI responses.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit (Python) |
| **Backend** | FastAPI (Python 3.13) |
| **Containerization** | Docker |
| **OCR Engine** | Tesseract, Poppler, pdf2image |
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
│   ├── app.py           # Main UI Logic (Chat Interface)
│   └── requirements.txt # Frontend dependencies
├── server/              # FastAPI Backend Application
│   ├── auth/            # Authentication Routes & Models
│   ├── config/          # Database & Env Config
│   ├── diagnosis/       # RAG Logic (Chat History & OCR)
│   ├── models/          # Pydantic Data Models
│   ├── reports/         # File Processing & Vector Ingestion
│   └── main.py          # App Entry Point
├── uploaded_dir/        # Local storage for temp files
├── Dockerfile           # Container configuration for Render
├── requirements.txt     # Backend dependencies
└── README.md
````

-----

## ⚙️ Local Development Setup

Follow these steps to run the application locally.

### 1\. Prerequisites (System Tools)

Since the app uses OCR, you must install these tools on your machine:

  * **Mac:** `brew install tesseract poppler`
  * **Linux:** `sudo apt-get install tesseract-ocr poppler-utils`
  * **Windows:** Download and install [Tesseract](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki) and [Poppler](https://www.google.com/search?q=http://blog.alivate.com.au/poppler-windows/). Add them to your system PATH.

### 2\. Clone the Repository

```bash
git clone [https://github.com/yourusername/MedRagnosis.git](https://github.com/yourusername/MedRagnosis.git)
cd MedRagnosis
```

### 3\. Backend Setup (FastAPI)

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

### 4\. Frontend Setup (Streamlit)

1.  **Navigate to the client directory (optional, or run from root):**
    *Ensure you have the client dependencies installed.*

    ```bash
    pip install -r client/requirements.txt
    ```

2.  **Configure Client Environment:**
    Create a `.env` file inside the `client/` folder:

    ```ini
    API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
    ```

3.  **Run the Frontend:**

    ```bash
    streamlit run client/app.py
    ```

    *The UI will open at `http://localhost:8501`*

-----

## 🐳 Docker Deployment (Recommended)

This project includes a `Dockerfile` to handle system dependencies (Tesseract/Poppler) automatically.

1.  **Build the image:**
    ```bash
    docker build -t medragnosis-backend .
    ```
2.  **Run the container:**
    ```bash
    docker run -p 10000:10000 --env-file .env medragnosis-backend
    ```

-----

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **Auth** | | |
| `POST` | `/auth/signup` | Register a new user (`patient` or `doctor`). |
| `GET` | `/auth/login` | Basic Auth login. |
| **Reports** | | |
| `POST` | `/reports/upload` | Upload PDF reports (Patient only). Supports OCR. |
| **Diagnosis** | | |
| `POST` | `/diagnosis/chat` | **New:** Conversational endpoint. Accepts chat history and returns context-aware diagnosis. |
| `GET` | `/diagnosis/by_patient_name` | View diagnosis history (Doctor only). |

-----

## 🔮 Roadmap

  * [x] **Frontend Implementation:** Built with Streamlit.
  * [x] **Deployment:** Live on Render (Docker) & Streamlit Cloud.
  * [x] **OCR Support:** Handle scanned/image-based PDF reports.
  * [x] **Chat Interface:** Enable follow-up questions on the diagnosis.
  * [ ] **JWT Implementation:** Upgrade from Basic Auth to stateless tokens.
  * [ ] **Multi-File Context:** Analyze multiple reports in a single query.

-----

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact

  * **Author**: Tharusha Rasath
  * **Email**: tharusharasatml@gmail.com

<!-- end list -->

```
```
