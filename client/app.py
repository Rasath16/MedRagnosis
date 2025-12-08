import streamlit as st
import requests
import json
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Set page configuration
st.set_page_config(
    page_title="MedRagnosis - AI Medical Diagnosis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --danger-gradient: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        --info-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stSidebar"] .stSelectbox select {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Hero Header */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    .hero-header h1 {
        color: white;
        margin: 0;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .hero-header p {
        color: rgba(255, 255, 255, 0.95);
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        font-weight: 300;
    }
    
    /* Modern Cards */
    .modern-card {
        background: #1E2A56;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .info-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        backdrop-filter: blur(10px);
    }
    
    .info-card h4 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .info-card p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.3rem 0;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-patient { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .badge-doctor { 
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    
    /* Welcome Card in Sidebar */
    .welcome-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem 0;
    }
    
    .welcome-card h4 {
        color: white !important;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .welcome-card p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.3rem 0;
        font-size: 1rem;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    /* Chat Container */
    [data-testid="stChatMessageContainer"] {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px dashed rgba(102, 126, 234, 0.3);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        background: #1E2A56;
        border: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        font-weight: 600;
    }
    
    /* Record Card Styles */
    .record-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 4px solid #764ba2;
    }
    
    /* Status Colors */
    .status-verified {
        color: #27ae60;
        font-weight: 600;
    }
    
    .status-pending {
        color: #f39c12;
        font-weight: 600;
    }
    
    .status-rejected {
        color: #e74c3c;
        font-weight: 600;
    }
    
    /* Logo/Brand */
    .brand-logo {
        font-size: 2rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        margin: 1.5rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 0 2rem 0;
        color: #666;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }
    
    .footer p {
        margin: 0.5rem 0;
    }
    
    /* Feature Icons */
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Success Message Styling */
    .stSuccess {
        border-radius: 10px;
        border-left: 4px solid #27ae60;
    }
    
    /* Info Message Styling */
    .stInfo {
        border-radius: 10px;
        border-left: 4px solid #4facfe;
    }
    
    /* Error Message Styling */
    .stError {
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# Initial state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "token" not in st.session_state:
    st.session_state.token = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# API Functions

def signup_user(username, password, role):
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={"username": username, "password": password, "role": role}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def authenticate_user(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password, "role": "patient"}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def upload_report(token, files):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        files_data = [('files', (file.name, file.getvalue(), file.type)) for file in files]
        response = requests.post(
            f"{API_URL}/reports/upload",
            headers=headers,
            files=files_data
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def get_chat_response(token, doc_id, messages, mode="current"):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        if mode == "trends":
            endpoint = f"{API_URL}/diagnosis/longitudinal"
        else:
            endpoint = f"{API_URL}/diagnosis/chat"
            
        payload = {
            "doc_id": doc_id,
            "messages": messages
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def get_doctor_diagnosis(token, patient_name):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{API_URL}/diagnosis/by_patient_name",
            headers=headers,
            params={'patient_name': patient_name}
        )
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def get_pending_reviews(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/diagnosis/pending", headers=headers)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def verify_record(token, record_id, status, note):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        payload = {"record_id": record_id, "status": status, "note": note}
        response = requests.post(f"{API_URL}/diagnosis/verify", headers=headers, json=payload)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def get_patient_history(token):
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/diagnosis/my_history", headers=headers)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}

def download_report_file(token, doc_id):
    """
    Downloads the report file from the backend.
    """
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/reports/view/{doc_id}", headers=headers)
        if response.status_code == 200:
            return response.content
        return None
    except requests.exceptions.ConnectionError:
        return None


# Sidebar & Auth Flow 
st.sidebar.markdown('<div class="brand-logo">🏥</div>', unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: white; margin-bottom: 1rem;'>MedRagnosis</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 2rem;'>AI-Powered Healthcare Intelligence</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

if st.session_state.logged_in:
    role_badge = "badge-patient" if st.session_state.role == "patient" else "badge-doctor"
    role_icon = "👤" if st.session_state.role == "patient" else "👨‍⚕️"
    role_name = "Patient" if st.session_state.role == "patient" else "Doctor"
    
    st.sidebar.markdown(f"""
        <div class="welcome-card">
            <h4>{role_icon} Welcome Back!</h4>
            <p style='font-size: 1.1rem; font-weight: 600;'>{st.session_state.username}</p>
            <span class="status-badge {role_badge}">{role_name}</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.session_state.role = ""
        st.rerun()
else:
    tab1, tab2 = st.sidebar.tabs(["🔐 Login", "📝 Signup"])
    
    with tab1:
        st.markdown("##### Sign in to your account")
        login_user = st.text_input("Username", key="login_user", placeholder="Enter your username")
        login_pass = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
        
        if st.button("🔓 Login", use_container_width=True):
            if login_user and login_pass:
                with st.spinner("Authenticating..."):
                    code, data = authenticate_user(login_user, login_pass)
                    if code == 200:
                        st.session_state.logged_in = True
                        st.session_state.username = data["username"]
                        st.session_state.role = data["role"]
                        st.session_state.token = data["access_token"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {data.get('detail', 'Login failed')}")
            else:
                st.warning("Please fill in all fields")
    
    with tab2:
        st.markdown("##### Create a new account")
        reg_user = st.text_input("Choose Username", key="reg_user", placeholder="Pick a username")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Create a secure password")
        reg_role = st.selectbox("Account Type", ["patient", "doctor"], key="reg_role")
        
        if st.button("✨ Create Account", use_container_width=True):
            if reg_user and reg_pass:
                code, data = signup_user(reg_user, reg_pass, reg_role)
                if code == 200:
                    st.success("✅ Account created! Please login.")
                else:
                    st.error(f"❌ {data.get('detail', 'Registration failed')}")
            else:
                st.warning("Please fill in all fields")

# Enhanced Main Page Layout
st.markdown("""
    <div class="hero-header">
        <h1>🏥 MedRagnosis</h1>
        <p>Transforming Healthcare with AI-Powered Medical Intelligence</p>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    # Landing Page for Non-Logged In Users
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="modern-card">
                <div class="feature-icon">🤖</div>
                <h3>AI-Powered Analysis</h3>
                <p>Advanced machine learning algorithms analyze your medical reports with precision and speed.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="modern-card">
                <div class="feature-icon">🔒</div>
                <h3>Secure & Private</h3>
                <p>Your health data is encrypted and protected with enterprise-grade security measures.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="modern-card">
                <div class="feature-icon">⚡</div>
                <h3>Instant Insights</h3>
                <p>Get immediate analysis and actionable insights from your medical documents.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 **Get Started:** Login or create an account from the sidebar to access the platform")
    
else:
# PATIENT VIEW 
    if st.session_state.role == "patient":
        
        tab_consult, tab_history = st.tabs(["💬 AI Consultation", "📜 My Medical History"])
        
        with tab_consult:
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                st.markdown("### 📤 Upload Medical Report")
                
                with st.form("upload_form"):
                    st.markdown("Upload your medical documents for AI analysis")
                    uploaded_files = st.file_uploader(
                        "Select PDF or TXT files", 
                        type=["pdf", "txt"], 
                        accept_multiple_files=True,
                        help="You can upload multiple files at once"
                    )
                    submitted = st.form_submit_button("🚀 Upload & Analyze", use_container_width=True)
                    
                    if submitted and uploaded_files:
                        with st.spinner("🔄 Processing your reports (OCR + AI Vectorization)..."):
                            code, data = upload_report(st.session_state.token, uploaded_files)
                            if code == 200:
                                st.session_state.doc_id = data['doc_id']
                                st.session_state.messages = [] 
                                st.success(f"✅ Successfully uploaded! Document ID: {data['doc_id']}")
                            else:
                                st.error(f"❌ {data.get('detail', 'Upload failed')}")
                    elif submitted and not uploaded_files:
                        st.warning("⚠️ Please select files to upload")
                
            with col2:
                h_col, b_col = st.columns([3, 1])
                with h_col:
                    st.markdown("### 💬 AI Medical Consultant")
                with b_col:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()
                
                if 'doc_id' in st.session_state:
                    mode = st.radio(
                        "Analysis Scope:", 
                        ["Current Report", "All Reports (Trends)"], 
                        horizontal=True,
                        help="Choose whether to analyze just the current report or track trends across all your reports"
                    )
                    api_mode = "trends" if mode == "All Reports (Trends)" else "current"

                    if "messages" not in st.session_state:
                        st.session_state.messages = []

                    chat_container = st.container(height=400)
                    with chat_container:
                        if not st.session_state.messages:
                            st.info(f"🤖 AI ready to analyze your {mode.lower()}. Ask me anything about your health!")
                        for msg in st.session_state.messages:
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])

                    if prompt := st.chat_input("💭 Type your medical question here..."):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with chat_container:
                            with st.chat_message("user"):
                                st.markdown(prompt)
                        
                        with chat_container:
                            with st.chat_message("assistant"):
                                with st.spinner("🧠 Analyzing..."):
                                    code, data = get_chat_response(
                                        st.session_state.token,
                                        st.session_state.doc_id,
                                        st.session_state.messages,
                                        mode=api_mode
                                    )
                                    
                                    if code == 200:
                                        ans = data.get("diagnosis", "No response")
                                        st.markdown(ans)
                                        if data.get("sources"):
                                            with st.expander("📚 View Sources"):
                                                st.json(data["sources"])
                                        st.session_state.messages.append({"role": "assistant", "content": ans})
                                        st.caption("ℹ️ Diagnosis saved to history (⏳ Pending Doctor Review)")
                                    else:
                                        st.error(f"❌ Error: {data.get('detail')}")
                else:
                    st.info("📋 Please upload a medical report to start the consultation")

        with tab_history:
            col_title, col_refresh = st.columns([4, 1])
            with col_title:
                st.markdown("### 🩺 Diagnosis History & Doctor Reviews")
            with col_refresh:
                if st.button("🔄 Refresh", key="refresh_hist"):
                    st.rerun()
                
            with st.spinner("📥 Fetching your medical history..."):
                code, history = get_patient_history(st.session_state.token)
            
            if code == 200:
                if not history:
                    st.info("📭 No diagnosis history found. Start by uploading a report and asking questions!")
                else:
                    for rec in history:
                        status = rec.get('verification_status', 'pending').lower()
                        
                        if status == 'verified':
                            color = "#27ae60"
                            icon = "✅"
                            status_text = "VERIFIED BY DOCTOR"
                        elif status == 'rejected':
                            color = "#e74c3c"
                            icon = "❌"
                            status_text = "REJECTED BY DOCTOR"
                        else:
                            color = "#f39c12"
                            icon = "⏳"
                            status_text = "PENDING REVIEW"

                        timestamp = datetime.datetime.fromtimestamp(rec['timestamp']).strftime('%B %d, %Y at %I:%M %p')
                        question_preview = rec.get('question', '')[:60] + "..." if len(rec.get('question', '')) > 60 else rec.get('question', '')
                        
                        with st.expander(f"{icon} {timestamp} - {question_preview}"):
                            st.markdown(f"**❓ Question:** {rec.get('question')}")
                            st.markdown(f"**🤖 AI Analysis:** {rec.get('answer')}")
                            st.markdown("---")
                            st.markdown(f"<h5 style='color:{color}'>{icon} Status: {status_text}</h5>", unsafe_allow_html=True)
                            
                            if rec.get('doctor_note'):
                                st.info(f"👨‍⚕️ **Doctor's Note:** {rec['doctor_note']}")
                            
                            if rec.get('verified_by'):
                                st.caption(f"✍️ Reviewed by: Dr. {rec['verified_by']}")
            else:
                st.error("❌ Could not fetch history. Server might be down.")
      

   # DOCTOR VIEW
    elif st.session_state.role == "doctor":
        st.markdown("## 👨‍⚕️ Doctor Dashboard")
        
        tab_history, tab_review = st.tabs(["🔍 Patient Search", "🩺 Pending Reviews"])
        
        with tab_history:
            # --- REMOVED <div class="modern-card"> ---
            st.markdown("### 🔍 Search Patient Records")
            
            col_search, col_btn = st.columns([3, 1])
            with col_search:
                patient_name = st.text_input("Enter Patient Username", placeholder="Search by username")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                search_btn = st.button("🔎 Search", use_container_width=True)
            
            if search_btn and patient_name:
                with st.spinner("🔍 Searching records..."):
                    code, data = get_doctor_diagnosis(st.session_state.token, patient_name)
                    if code == 200:
                        st.success(f"✅ Found {len(data)} record(s) for {patient_name}")
                        for rec in data:
                            status = rec.get("verification_status", "pending")
                            icon = "✅" if status == "verified" else "❌" if status == "rejected" else "⏳"
                            timestamp = datetime.datetime.fromtimestamp(rec.get('timestamp', 0)).strftime('%B %d, %Y')
                            
                            with st.expander(f"{icon} {timestamp} - {rec.get('question', 'No Question')[:50]}..."):
                                st.markdown(f"**❓ Patient Question:** {rec.get('question')}")
                                st.markdown(f"**🤖 AI Diagnosis:** {rec.get('answer')}")
                                
                                # --- Report View Logic ---
                                doc_id = rec.get("doc_id")
                                filename = rec.get("filename", "Unknown File")
                                if doc_id and doc_id != "all-reports":
                                    st.markdown(f"**📄 Source File:** {filename}")
                                    if filename != "Unknown File":
                                        file_bytes = download_report_file(st.session_state.token, doc_id)
                                        if file_bytes:
                                            st.download_button(
                                                label=f"📥 Download {filename}",
                                                data=file_bytes,
                                                file_name=filename,
                                                mime='application/pdf',
                                                key=f"dl_search_{rec['_id']}"
                                            )
                                
                                st.markdown("---")
                                
                                status_color = "#27ae60" if status == "verified" else "#e74c3c" if status == "rejected" else "#f39c12"
                                st.markdown(f"<h5 style='color:{status_color}'>{icon} Status: {status.upper()}</h5>", unsafe_allow_html=True)
                                
                                if rec.get('doctor_note'):
                                    st.info(f"📝 **Doctor's Note:** {rec['doctor_note']}")
                                if rec.get('verified_by'):
                                    st.caption(f"👨‍⚕️ Reviewed by: Dr. {rec['verified_by']}")
                    else:
                        st.error(f"❌ {data.get('detail', 'Search failed')}")
            elif search_btn and not patient_name:
                st.warning("⚠️ Please enter a patient username")
          
        
        with tab_review:
            col_title, col_refresh = st.columns([4, 1])
            with col_title:
                st.markdown("### 🩺 Pending Diagnosis Reviews")
            with col_refresh:
                if st.button("🔄 Refresh", key="refresh_pending"):
                    st.rerun()
            
            with st.spinner("📥 Loading pending reviews..."):
                code, pending = get_pending_reviews(st.session_state.token)
            
            if code == 200:
                if pending:
                    st.info(f"📋 You have **{len(pending)}** diagnosis awaiting review")
                    
                    for idx, rec in enumerate(pending):
                        timestamp = datetime.datetime.fromtimestamp(rec.get('timestamp', 0)).strftime('%B %d, %Y at %I:%M %p')
                        
                        with st.expander(f"⏳ Patient: **{rec.get('requester')}** | {timestamp}", expanded=(idx==0)):
                            st.markdown("#### 📋 Patient Query")
                            st.info(rec.get('question'))
                            
                            st.markdown("#### 🤖 AI-Generated Diagnosis")
                            st.markdown(f"> {rec.get('answer')}")

                            # Report View Logic
                            st.markdown("---")
                            st.markdown("#### 📄 Clinical Source")
                            doc_id = rec.get("doc_id")
                            filename = rec.get("filename", "Unknown File")
                            
                            if doc_id == "all-reports":
                                st.warning("⚠️ This is a longitudinal analysis across multiple reports.")
                            elif doc_id:
                                col_info, col_dl = st.columns([3, 1])
                                with col_info:
                                    st.markdown(f"**Filename:** `{filename}`")
                                with col_dl:
                                    if filename != "Unknown File":
                                        file_bytes = download_report_file(st.session_state.token, doc_id)
                                        if file_bytes:
                                            st.download_button(
                                                label="📥 Download",
                                                data=file_bytes,
                                                file_name=filename,
                                                mime='application/pdf',
                                                key=f"dl_rev_{rec['_id']}",
                                                use_container_width=True
                                            )
                                        else:
                                            st.warning("File missing")
                                    else:
                                        st.caption("🚫 Source file not found")
                            
                            st.markdown("---")
                            st.markdown("#### ✍️ Your Professional Review")
                            
                            note = st.text_area(
                                "Doctor's Notes", 
                                key=f"note_{rec['_id']}",
                                placeholder="Add your professional assessment, recommendations, or corrections...",
                                height=100
                            )
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            c1, c2, c3 = st.columns([1, 1, 2])
                            
                            with c1:
                                if st.button("✅ Approve", key=f"app_{rec['_id']}", use_container_width=True):
                                    if note:
                                        res_code, res_msg = verify_record(
                                            st.session_state.token, 
                                            rec['_id'], 
                                            "verified", 
                                            note
                                        )
                                        if res_code == 200:
                                            st.success("✅ Diagnosis verified!")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {res_msg.get('detail', 'Verification failed')}")
                                    else:
                                        st.warning("⚠️ Please add a note before approving")
                            
                            with c2:
                                if st.button("❌ Reject", key=f"rej_{rec['_id']}", use_container_width=True):
                                    if note:
                                        res_code, res_msg = verify_record(
                                            st.session_state.token, 
                                            rec['_id'], 
                                            "rejected", 
                                            note
                                        )
                                        if res_code == 200:
                                            st.warning("❌ Diagnosis rejected!")
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {res_msg.get('detail', 'Rejection failed')}")
                                    else:
                                        st.warning("⚠️ Please add a note explaining the rejection")
                            
                            with c3:
                                st.caption("💡 **Tip:** Always provide detailed notes for your review")
                else:
                    st.success("🎉 All caught up! No pending reviews at the moment.")
                    st.markdown("""
                        <div style='text-align: center; padding: 2rem; color: #666;'>
                            <div style='font-size: 4rem; margin-bottom: 1rem;'>✨</div>
                            <h3>Great work, Doctor!</h3>
                            <p>You've reviewed all pending diagnoses. Check back later for new submissions.</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to load pending reviews. Please try again.")
           