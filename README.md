````markdown
# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Platform

**MedRagnosis** is an AI-powered medical diagnostic tool that uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze patient medical reports. It bridges the gap between AI insights and professional medical oversight by combining a patient-facing chat interface with a doctor-facing verification dashboard.

> **🔴 Live Demo:** [https://medragnosis.streamlit.app/](https://medragnosis.streamlit.app/)
>
> **Status:** ✅ Backend (Deployed on Render via Docker) | ✅ Frontend (Deployed on Streamlit)

---

## 🚀 Key Features

### 👤 For Patients

- **Secure Identity:** Sign up and log in securely using **JWT (JSON Web Token)** authentication.
- **Advanced Document Upload (OCR):** Upload medical reports (PDF/TXT). The system automatically detects scanned documents and uses **Tesseract OCR** to extract text from images.
- **AI Consultation:** Chat naturally with the AI about your specific report.
- **📈 Longitudinal Trend Analysis:** Unlike standard RAG, MedRagnosis allows you to toggle between analyzing a **single report** or **all uploaded reports** to identify health trends over time (e.g., "Has my cholesterol increased over the last year?").
- **Diagnosis History:** View past AI diagnoses. Crucially, patients can see if a specific AI insight has been **Verified ✅** or **Rejected ❌** by a doctor, along with professional notes.

### 👨‍⚕️ For Doctors

- **Doctor Dashboard:** A specialized interface for medical professionals.
- **Patient Lookup:** Search for specific patient records by username to review their history.
- **✅ Verification Loop:** Access a **"Pending Reviews"** queue. Doctors can review the AI's generated diagnosis against the patient's query and mark it as:
  - **Verified:** The AI analysis is medically sound.
  - **Rejected:** The AI analysis is incorrect or dangerous.
- **Annotation:** Add professional notes to any diagnosis, which become immediately visible to the patient.

---

## 🛠 Tech Stack

| Component            | Technology                    | Details                                           |
| :------------------- | :---------------------------- | :------------------------------------------------ |
| **Frontend**         | Streamlit (Python)            | Custom CSS for Modern UI                          |
| **Backend**          | FastAPI (Python 3.13)         | Async Endpoints                                   |
| **Authentication**   | JWT (JSON Web Tokens)         | Role-based access (Patient/Doctor)                |
| **Containerization** | Docker                        | Multi-stage build with OCR dependencies           |
| **OCR Engine**       | Tesseract, Poppler, pdf2image | For scanned PDF processing                        |
| **Database**         | MongoDB                       | User profiles, Report metadata, Diagnosis History |
| **Vector DB**        | Pinecone (Serverless)         | Stores document embeddings                        |
| **LLM Inference**    | Groq API                      | **LLaMA 3.3-70b-versatile**                       |
| **Embeddings**       | OpenAI                        | **text-embedding-3-small**                        |
| **Orchestration**    | LangChain                     | Context retrieval & Query rewriting               |

---

## 📂 Project Structure

```text
MedRagnosis/
├── client/              # Streamlit Frontend Application
│   ├── app.py           # UI Logic (Patient Chat & Doctor Dashboard)
│   └── requirements.txt # Frontend dependencies
├── server/              # FastAPI Backend Application
│   ├── auth/            # Auth Routes (JWT Handler)
│   ├── config/          # Database & Env Config
│   ├── diagnosis/       # RAG Logic, Trend Analysis & Verification
│   ├── models/          # Pydantic Data Models
│   ├── reports/         # File Processing, OCR & Vector Ingestion
│   └── main.py          # App Entry Point
├── uploaded_dir/        # Local storage for temp files
├── Dockerfile           # Container configuration for Render
├── requirements.txt     # Backend dependencies
└── README.md
```
````

---

## ⚙️ Local Development Setup

Follow these steps to run the application locally.

### 1\. Prerequisites (System Tools)

Since the app uses OCR, you must install these tools on your machine:

- **Mac:** `brew install tesseract poppler`
- **Linux:** `sudo apt-get install tesseract-ocr poppler-utils`
- **Windows:** Download and install [Tesseract](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki) and [Poppler](https://www.google.com/search?q=http://blog.alivate.com.au/poppler-windows/). Add them to your system PATH.

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

    # Auth
    SECRET_KEY=your_super_secret_key

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

    _The Backend API will run at `http://127.0.0.1:8000`_

### 4\. Frontend Setup (Streamlit)

1.  **Navigate to the client directory (optional, or run from root):**
    _Ensure you have the client dependencies installed._

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

    _The UI will open at `http://localhost:8501`_

---

## 🐳 Docker Deployment

The project includes a `Dockerfile` that handles system dependencies (Tesseract/Poppler) automatically.

1.  **Build the image:**
    ```bash
    docker build -t medragnosis-backend .
    ```
2.  **Run the container:**
    ```bash
    docker run -p 10000:10000 --env-file .env medragnosis-backend
    ```

---

## 📡 API Endpoints

| Method        | Endpoint                  | Description                                                              |
| :------------ | :------------------------ | :----------------------------------------------------------------------- |
| **Auth**      |                           |                                                                          |
| `POST`        | `/auth/signup`            | Register a new user (`patient` or `doctor`).                             |
| `POST`        | `/auth/login`             | Login and receive a **JWT Access Token**.                                |
| **Reports**   |                           |                                                                          |
| `POST`        | `/reports/upload`         | Upload PDF reports (Patient only). Supports OCR fallback.                |
| **Diagnosis** |                           |                                                                          |
| `POST`        | `/diagnosis/chat`         | **Single Report RAG:** Chat with context from a specific document.       |
| `POST`        | `/diagnosis/longitudinal` | **Trend Analysis:** Analyzes all reports belonging to a user for trends. |
| `GET`         | `/diagnosis/pending`      | **Doctor:** Fetch all diagnoses awaiting verification.                   |
| `POST`        | `/diagnosis/verify`       | **Doctor:** Approve/Reject a diagnosis and add a note.                   |
| `GET`         | `/diagnosis/my_history`   | **Patient:** Get history including doctor verification status.           |

---

## 🔮 Roadmap

- [x] **OCR Support:** Handle scanned/image-based PDF reports.
- [x] **Doctor Verification Loop:** Active dashboard for doctors to validate AI outputs.
- [x] **Longitudinal Analysis:** Multi-file trend detection.
- [ ] **Email Notifications:** Notify patients when a doctor reviews their diagnosis.
- [ ] **Visual Data Parsing:** Extract charts and graphs from reports using Vision models.

---

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact

- **Author**: Tharusha Rasath
- **Email**: tharusharasatml@gmail.com

<!-- end list -->

```

```
