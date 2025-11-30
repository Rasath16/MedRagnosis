import streamlit as st
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL")

# Set page configuration
st.set_page_config(
    page_title="MedRagnosis - AI Medical Diagnosis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1e88e5;
        --secondary-color: #43a047;
        --background-color: #f5f7fa;
        --card-background: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .custom-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        color: white;
        margin-bottom: 2rem;
    }
    
    .info-card {
        background: navy blue;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 1rem;
        border-left: 4px solid #1e88e5;
    }
    
    .success-card {
        background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    
    .diagnosis-result {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #43a047;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Form styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
    }
    
    /* Header styling */
    h1 {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    h2 {
        color: #1e88e5;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #43a047;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Record card */
    .record-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border-top: 4px solid #764ba2;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    
    .badge-patient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .badge-doctor {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initial state management
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""
if "auth" not in st.session_state:
    st.session_state.auth = None

# API Functions
def signup_user(username, password, role):
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={"username": username, "password": password, "role": role}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def authenticate_user(username, password):
    try:
        response = requests.get(
            f"{API_URL}/auth/login",
            auth=HTTPBasicAuth(username, password)
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def upload_report(auth, files):
    try:
        headers = {'accept': 'application/json'}
        files_data = [('files', (file.name, file.getvalue(), file.type)) for file in files]
        response = requests.post(
            f"{API_URL}/reports/upload",
            auth=auth,
            files=files_data,
            headers=headers
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def get_diagnosis(auth, doc_id, question):
    try:
        data = {
            'doc_id': doc_id,
            'question': question
        }
        response = requests.post(
            f"{API_URL}/diagnosis/from_report",
            auth=auth,
            data=data
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

def get_doctor_diagnosis(auth, patient_name):
    try:
        response = requests.get(
            f"{API_URL}/diagnosis/by_patient_name",
            auth=auth,
            params={'patient_name': patient_name}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable. Please try again later."}

# Sidebar and Authentication Flow
st.sidebar.markdown("### 🏥 MedRagnosis")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    role_badge_class = "badge-patient" if st.session_state.role == "patient" else "badge-doctor"
    role_icon = "👤" if st.session_state.role == "patient" else "👨‍⚕️"
    
    st.sidebar.markdown(f"""
        <div class="info-card">
            <h4>{role_icon} Welcome Back!</h4>
            <p style="margin: 0.5rem 0;"><strong>{st.session_state.username}</strong></p>
            <span class="status-badge {role_badge_class}">{st.session_state.role.upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.auth = None
        st.rerun()
else:
    tab1, tab2 = st.sidebar.tabs(["🔐 Login", "📝 Signup"])
    
    with tab1:
        st.markdown("##### Login to your account")
        login_username = st.text_input("👤 Username", key="login_username", placeholder="Enter your username")
        login_password = st.text_input("🔑 Password", type="password", key="login_password", placeholder="Enter your password")
        
        if st.button("🚀 Login", key="login_btn", use_container_width=True):
            if login_username and login_password:
                with st.spinner("🔄 Authenticating..."):
                    status_code, data = authenticate_user(login_username, login_password)
                    if status_code == 200:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.session_state.role = data["role"]
                        st.session_state.auth = HTTPBasicAuth(login_username, login_password)
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {data.get('detail', 'Login failed')}")
            else:
                st.warning("⚠️ Please enter username and password")

    with tab2:
        st.markdown("##### Create a new account")
        signup_username = st.text_input("👤 Username", key="signup_username", placeholder="Choose a username")
        signup_password = st.text_input("🔑 Password", type="password", key="signup_password", placeholder="Create a password")
        signup_role = st.selectbox("👥 Role", ["patient", "doctor"], key="signup_role")
        
        if st.button("📝 Create Account", key="signup_btn", use_container_width=True):
            if signup_username and signup_password:
                with st.spinner("🔄 Creating account..."):
                    status_code, data = signup_user(signup_username, signup_password, signup_role)
                    if status_code == 200:
                        st.success("✅ Account created! Please login.")
                    elif status_code == 400:
                        st.error(f"❌ {data.get('detail', 'User already exists')}")
                    else:
                        st.error(f"❌ {data.get('detail', 'Signup failed')}")
            else:
                st.warning("⚠️ Please fill in all fields")

# Main Page Application
st.markdown('<div class="custom-card"><h1 style="color: white; margin: 0;">🏥 MedRagnosis</h1><p style="margin: 0.5rem 0 0 0; opacity: 0.95;">AI-Powered Medical Diagnosis & Patient Care</p></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="info-card">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Advanced GenAI technology analyzes your medical reports with precision and speed.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="info-card">
                <h3>📊 Instant Diagnosis</h3>
                <p>Get immediate insights and diagnosis based on your uploaded medical reports.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="info-card">
                <h3>🔒 Secure & Private</h3>
                <p>Your medical data is encrypted and accessible only to you and your doctors.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Please login or sign up from the sidebar to access the application")
    
else:
    if st.session_state.role == "patient":
        st.markdown("## 👤 Patient Dashboard")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📤 Upload Medical Report")
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            
            with st.form("upload_form"):
                st.markdown("Upload your medical reports (PDF or TXT files)")
                uploaded_files = st.file_uploader(
                    "Choose files",
                    type=["pdf", "txt"],
                    accept_multiple_files=True,
                    label_visibility="collapsed"
                )
                upload_submitted = st.form_submit_button("📤 Upload Reports", use_container_width=True)
                
                if upload_submitted and uploaded_files:
                    with st.spinner("⏳ Processing your reports..."):
                        status_code, data = upload_report(st.session_state.auth, uploaded_files)
                        if status_code == 200:
                            st.markdown(f"""
                                <div class="success-card">
                                    <h4>✅ Upload Successful!</h4>
                                    <p><strong>Document ID:</strong> <code>{data['doc_id']}</code></p>
                                    <p style="margin: 0;">Save this ID to get your diagnosis</p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.session_state.doc_id = data['doc_id']
                        else:
                            st.error(f"❌ {data.get('detail', 'Upload failed')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🩺 Get Diagnosis")
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            
            if 'doc_id' in st.session_state:
                with st.form("diagnosis_form"):
                    st.markdown("Ask our AI for a diagnosis")
                    diagnosis_doc_id = st.text_input(
                        "📄 Document ID",
                        value=st.session_state.doc_id,
                        placeholder="Enter your document ID"
                    )
                    diagnosis_question = st.text_area(
                        "❓ Your Question",
                        value="Please provide a diagnosis based on my report.",
                        height=100,
                        placeholder="What would you like to know about your report?"
                    )
                    diagnosis_submitted = st.form_submit_button("🔍 Get Diagnosis", use_container_width=True)
                    
                    if diagnosis_submitted:
                        with st.spinner("🤖 AI is analyzing your report..."):
                            status_code, data = get_diagnosis(
                                st.session_state.auth,
                                diagnosis_doc_id,
                                diagnosis_question
                            )
                            if status_code == 200:
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                                st.markdown("---")
                                st.markdown("### 📋 Diagnosis Results")
                                
                                st.markdown(f"""
                                    <div class="diagnosis-result">
                                        <h4 style="color: #43a047; margin-top: 0;">📊 Analysis</h4>
                                        <p>{data.get("diagnosis", "No diagnosis provided.")}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                if data.get("sources"):
                                    with st.expander("📚 View Sources", expanded=False):
                                        st.json(data.get("sources", []))
                            else:
                                st.error(f"❌ {data.get('detail', 'Diagnosis failed')}")
            else:
                st.info("📤 Please upload a report first to get a Document ID")
            
            if 'doc_id' not in st.session_state or not diagnosis_submitted:
                st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.role == "doctor":
        st.markdown("## 👨‍⚕️ Doctor Dashboard")
        
        st.markdown("### 🔍 Patient Diagnosis Records")
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        
        with st.form("doctor_form"):
            st.markdown("Search for patient diagnosis history")
            patient_name_input = st.text_input(
                "👤 Patient Username",
                placeholder="Enter patient's username"
            )
            view_submitted = st.form_submit_button("🔍 Search Records", use_container_width=True)
            
            if view_submitted and patient_name_input:
                with st.spinner(f"⏳ Fetching records for {patient_name_input}..."):
                    status_code, data = get_doctor_diagnosis(st.session_state.auth, patient_name_input)
                    if status_code == 200:
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.success(f"✅ Found {len(data)} diagnosis record(s) for **{patient_name_input}**")
                        
                        for idx, record in enumerate(data, 1):
                            st.markdown(f"""
                                <div class="record-card">
                                    <h4 style="color: #764ba2; margin-top: 0;">📋 Record #{idx}</h4>
                                    <p><strong>🆔 Record ID:</strong> <code>{record['_id']}</code></p>
                                    <p><strong>📅 Date:</strong> {datetime.datetime.fromtimestamp(record['timestamp']).strftime('%B %d, %Y at %H:%M:%S')}</p>
                                    <p><strong>📄 Document ID:</strong> <code>{record['doc_id']}</code></p>
                                    <p><strong>❓ Question:</strong> {record['question']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"📊 View Diagnosis #{idx}", expanded=False):
                                st.markdown("#### 🩺 Diagnosis Answer")
                                st.markdown(f'<div class="diagnosis-result">{record["answer"]}</div>', unsafe_allow_html=True)
                                
                                st.markdown("#### 📚 Sources")
                                if record['sources']:
                                    for source in record['sources']:
                                        st.markdown(f"- {source}")
                                else:
                                    st.info("No sources available")
                    else:
                        st.error(f"❌ {data.get('detail', 'Failed to fetch records')}")
        
        if not view_submitted:
            st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Your role is not recognized. Please contact support.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p><strong>MedRagnosis</strong> - Powered by GenAI & LangChain 🤖</p>
        <p style="font-size: 0.85rem;">Secure • Reliable • Intelligent Healthcare</p>
    </div>
""", unsafe_allow_html=True)