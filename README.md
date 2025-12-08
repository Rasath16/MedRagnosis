# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Platform

**MedRagnosis** is an AI-powered medical diagnostic tool that uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze patient medical reports. It bridges the gap between AI insights and professional medical oversight by combining a patient-facing chat interface with a doctor-facing verification dashboard.

> **🔴 Live Demo:** [https://medragnosis.streamlit.app/](https://medragnosis.streamlit.app/)
>
> **Status:** ✅ Backend (Deployed on Render via Docker) | ✅ Frontend (Deployed on Streamlit)

---

## 🚀 Key Features

### 👤 For Patients

- **Secure Identity:** Sign up and log in securely using **JWT (JSON Web Token)** authentication.
- **Smart Document Upload (OCR):** Upload medical reports (PDF/TXT). The system automatically detects scanned documents and uses **Tesseract OCR** to extract text from images.
- **AI Consultation:** Chat naturally with the AI about your specific report (e.g., "What does this blood test result mean?").
- **📈 Longitudinal Trend Analysis:** Toggle between analyzing a **single report** or **all uploaded reports** to identify health trends over time (e.g., "Has my cholesterol increased over the last year?").
- **Diagnosis History:** View past AI diagnoses and see if they have been **Verified ✅** or **Rejected ❌** by a doctor.

### 👨‍⚕️ For Doctors

- **Professional Dashboard:** A specialized interface for medical professionals.
- **Patient Lookup:** Search for specific patient records by username to review their history.
- **✅ Verification Loop:** Access a **"Pending Reviews"** queue. Doctors can:
  - **Review:** Read the patient's query and the AI's generated response.
  - **Verify Source:** **Download and view the original uploaded report** directly from the dashboard to ensure accuracy.
  - **Action:** Mark diagnoses as **Verified** or **Rejected** and add professional clinical notes.

---

## 🛠 Tech Stack

| Component          | Technology            | Details                                           |
| :----------------- | :-------------------- | :------------------------------------------------ |
| **Frontend**       | Streamlit (Python)    | Custom CSS for Modern UI, Interactive Chat        |
| **Backend**        | FastAPI (Python 3.13) | Async Endpoints, Dependency Injection             |
| **Hosting**        | Render (Docker)       | Live Backend Deployment                           |
| **Authentication** | JWT (JSON Web Tokens) | Role-based access (Patient/Doctor)                |
| **Database**       | MongoDB               | User profiles, Report metadata, Diagnosis History |
| **Vector DB**      | Pinecone (Serverless) | Stores document embeddings for RAG                |
| **LLM Inference**  | Groq API              | **LLaMA 3.3-70b-versatile** (High speed/accuracy) |
| **Embeddings**     | OpenAI                | **text-embedding-3-small**                        |
| **OCR Engine**     | Tesseract, Poppler    | Handles scanned PDFs and images                   |

---

## 📂 Project Structure

```text
MedRagnosis/
├── client/              # Streamlit Frontend Application
│   ├── app.py           # Main UI Logic (Patient Chat & Doctor Dashboard)
│   └── requirements.txt # Frontend dependencies
├── server/              # FastAPI Backend Application
│   ├── auth/            # Auth Routes (JWT Handler)
│   ├── config/          # Database & Env Config
│   ├── diagnosis/       # RAG Logic, Trend Analysis & Verification
│   ├── models/          # Pydantic Data Models
│   ├── reports/         # File Processing, OCR & Vector Ingestion
│   └── main.py          # App Entry Point
├── uploaded_dir/        # Local storage for temp files
├── reset_system.py      # Utility script to wipe DB/Pinecone for fresh start
├── Dockerfile           # Container configuration for Render
├── requirements.txt     # Backend dependencies
└── README.md
```

---

## ⚙️ Local Development Setup

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

1.  **Open a new terminal and navigate to the root.**

2.  **Install Client Dependencies:**

    ```bash
    pip install -r client/requirements.txt
    ```

3.  **Configure Client Environment:**
    Create a `.env` file inside the `client/` folder:

    ```ini
    # Point this to your Render URL for live backend, or localhost for dev
    API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)
    ```

4.  **Run the Frontend:**

    ```bash
    streamlit run client/app.py
    ```

    _The UI will open at `http://localhost:8501`_

### 5\. Resetting the System (Optional)

If you need to clear all users, reports, and vectors to start fresh, run:

```bash
python reset_system.py
```

_⚠️ This deletes ALL data from MongoDB, Pinecone, and local storage._

---

## 🐳 Docker Deployment

The project includes a `Dockerfile` that handles system dependencies automatically.

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

| Method        | Endpoint                  | Description                                                   |
| :------------ | :------------------------ | :------------------------------------------------------------ |
| **Auth**      |                           |                                                               |
| `POST`        | `/auth/signup`            | Register a new user (`patient` or `doctor`).                  |
| `POST`        | `/auth/login`             | Login and receive a **JWT Access Token**.                     |
| **Reports**   |                           |                                                               |
| `POST`        | `/reports/upload`         | Upload PDF reports (Patient only). Supports OCR.              |
| `GET`         | `/reports/view/{id}`      | **Download original report** (Doctor/Uploader only).          |
| **Diagnosis** |                           |                                                               |
| `POST`        | `/diagnosis/chat`         | **Single Report RAG:** Chat with context from a specific doc. |
| `POST`        | `/diagnosis/longitudinal` | **Trend Analysis:** Analyzes all reports for a user.          |
| `GET`         | `/diagnosis/pending`      | **Doctor:** Fetch all diagnoses awaiting verification.        |
| `POST`        | `/diagnosis/verify`       | **Doctor:** Approve/Reject a diagnosis and add a note.        |
| `GET`         | `/diagnosis/my_history`   | **Patient:** Get history including verification status.       |

---

## 🔮 Future Roadmap

We plan to expand MedRagnosis with the following features:

1.  **📧 Email & SMS Notifications:** Automatically notify patients when a doctor has reviewed and verified their diagnosis.
2.  **📊 Visual Data Extraction:** Use Multimodal LLMs (like LLaVA or GPT-4o) to extract data from charts and graphs inside PDF reports, not just text.
3.  **🩺 Integration with Wearables:** Allow patients to sync data from Apple Health or Fitbit to provide real-time context to the AI (e.g., heart rate trends).
4.  **🗣️ Voice Interface:** Add speech-to-text (Whisper) for patients to ask questions verbally, making the app more accessible to the elderly.
5.  **🔒 HIPAA Compliance Auditing:** Implement strict audit logs and data masking to ensure full compliance with healthcare privacy standards.
6.  **🖼️ Medical Image Analysis:** Expand beyond text reports to analyze raw medical images (X-rays, MRIs) for preliminary anomaly detection.

---

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact

- **Author:** Tharusha Rasath
- **Email:** tharusharasatml@gmail.com

<!-- end list -->

```

```
