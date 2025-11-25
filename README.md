# 🏥 MedRagnosis – RAG-Enhanced Medical Diagnosis Engine(In progress)

**Medical Report Diagnosis** is a full-stack, AI-powered system designed to assist both patients and doctors. It allows patients to securely upload medical reports and receive preliminary diagnoses using a Retrieval-Augmented Generation (RAG) architecture, while providing doctors with a dashboard to review patient records.

The application features a **FastAPI** backend and a **Streamlit** frontend, integrating **MongoDB** for data storage and **Pinecone** for vector embeddings.

-----

## 🏗️ System Architecture & Workflow

The application follows a microservices architecture with a clear separation between the frontend, backend, and database layers.

### Workflow Overview

1.  **User Authentication**: Users sign up or log in via the Streamlit frontend. The FastAPI backend authenticates credentials and issues a token.
2.  **Report Processing**: When a patient uploads a report, the backend extracts text and creates vector embeddings using the Google Embedding Model, storing them in Pinecone.
3.  **RAG Diagnosis**:
      * The patient asks a question.
      * The system retrieves relevant report sections from Pinecone.
      * A prompt combining the question and context is sent to the Groq LLM (LLaMA 3) to generate a diagnosis.
4.  **Doctor Review**: Doctors can query the MongoDB database to retrieve and review the diagnosis history for specific patients.

### RAG Architecture

The Retrieval-Augmented Generation (RAG) pattern ensures diagnoses are based on specific report content rather than just the model's pre-trained knowledge, reducing hallucinations.

-----

## 🚀 Core Features

  * **Role-Based Access Control (RBAC)**: Distinct functionality for "Patient" and "Doctor" roles.
  * **PDF Report Upload**: Supports uploading and processing of medical reports in PDF format.
  * **Text Extraction & Chunking**: automated processing of PDF content.
  * **AI Diagnosis Generation**: Uses **Groq LLaMA 3** for fast, context-aware responses.
  * **Vector Storage**: Utilizes **Pinecone** for efficient storage and retrieval of report embeddings.
  * **Diagnosis History**: Stores all interactions in **MongoDB**, allowing doctors to review past diagnoses.

-----

## 🛠 Tech Stack

  * **Frontend**: Streamlit
  * **Backend Framework**: FastAPI
  * **Database**: MongoDB (User data, Diagnosis records)
  * **Vector DB**: Pinecone
  * **LLM API**: Groq (LLaMA 3)
  * **Orchestration**: LangChain
  * **Language**: Python 3.10+

-----

## 📂 Project Structure

```text
medicalReportDiagnosis/
├── assets/                  # Images and documentation assets
├── client/
│   ├── app.py               # Streamlit frontend application
│   ├── .env                 # Client-side environment variables
│   ├── requirements.txt     # Frontend dependencies
├── server/
│   ├── main.py              # FastAPI entry point
│   ├── auth/                # Authentication routes and models
│   ├── config/              # Database configuration
│   ├── diagnosis/           # Diagnosis logic and RAG implementation
│   └── reports/             # File upload and vector store logic
├── .env                     # Server-side environment variables
├── requirements.txt         # Backend dependencies
└── .gitignore
```

-----

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/snsupratim/MedicalReportDiagnosis.git
cd MedicalReportDiagnosis
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory and add the following keys:

```env
MONGO_URI=your_mongodb_uri
DB_NAME=rbac-diagnosis
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=rbac-diagnosis-index
PINECONE_ENV=us-east-1
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
UPLOAD_DIR=./uploaded_reports
API_URL=http://127.0.0.1:8000
```

### 5️⃣ Run the Application

Start the FastAPI backend:

```bash
uvicorn server.main:app --reload
```

Start the Streamlit frontend (in a separate terminal):

```bash
streamlit run client/app.py
```

The API will be available at **[http://127.0.0.1:8000](http://127.0.0.1:8000)** and the UI at the localhost port provided by Streamlit.

-----

## ▶️ API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/auth/signup` | Register a new user (patient or doctor) |
| **POST** | `/auth/login` | Authenticate user and receive token |
| **POST** | `/reports/upload` | Upload a medical report (Patient only) |
| **POST** | `/diagnosis/from_report` | Request AI diagnosis based on uploaded report |
| **GET** | `/diagnosis/by_patient_name` | Retrieve diagnosis history (Doctor only) |

-----

## 🔮 Future Enhancements

  * ✅ **JWT Authentication** for improved security.
  * ✅ **Advanced Analytics Dashboard** for doctors.
  * ✅ **Multi-format Support** (Images, DICOM).
  * ✅ **Offline Mode** for PDF processing.

-----

## 📜 License

This project is licensed under the **MIT License**.

-----

## 📬 Contact

  * **Author**: Tharusha Rasath
  * **Email**: tharusharasatml@gmail.com

