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

# Custom CSS
st.markdown("""
<style>
    :root {
        --primary-color: #1e88e5;
        --secondary-color: #43a047;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
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
    
    .record-card {
        background: navy blue;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border-top: 4px solid #764ba2;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.5rem 0;
    }
    
    .badge-patient { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color:navy blue; }
    .badge-doctor { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color:= navy blue; }
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

# --- API Functions ---

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
        # Expects JWT response
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password, "role": "patient"} # role ignored by login
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
        
        # Decide endpoint based on mode
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
    """Fetches the logged-in patient's diagnosis history."""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{API_URL}/diagnosis/my_history", headers=headers)
        return response.status_code, response.json()
    except requests.exceptions.ConnectionError:
        return 503, {"detail": "Server is unavailable."}


# --- Sidebar & Auth Flow ---
st.sidebar.markdown("### 🏥 MedRagnosis")
st.sidebar.markdown("---")

if st.session_state.logged_in:
    role_badge = "badge-patient" if st.session_state.role == "patient" else "badge-doctor"
    role_icon = "👤" if st.session_state.role == "patient" else "👨‍⚕️"
    
    st.sidebar.markdown(f"""
        <div class="info-card">
            <h4>{role_icon} Welcome!</h4>
            <p><strong>{st.session_state.username}</strong></p>
            <span class="status-badge {role_badge}">{st.session_state.role.upper()}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.token = ""
        st.session_state.role = ""
        st.rerun()
else:
    tab1, tab2 = st.sidebar.tabs(["🔐 Login", "📝 Signup"])
    
    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if login_user and login_pass:
                with st.spinner("Authenticating..."):
                    code, data = authenticate_user(login_user, login_pass)
                    if code == 200:
                        st.session_state.logged_in = True
                        st.session_state.username = data["username"]
                        st.session_state.role = data["role"]
                        st.session_state.token = data["access_token"]
                        st.success("Success!")
                        st.rerun()
                    else:
                        st.error(data.get("detail", "Login failed"))
    
    with tab2:
        reg_user = st.text_input("Choose Username", key="reg_user")
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Role", ["patient", "doctor"], key="reg_role")
        if st.button("Create Account", use_container_width=True):
            if reg_user and reg_pass:
                code, data = signup_user(reg_user, reg_pass, reg_role)
                if code == 200:
                    st.success("Account created! Please login.")
                else:
                    st.error(data.get("detail", "Failed"))

# --- Main Page Layout ---
# --- Main Page Layout ---
st.markdown('<div class="custom-card"><h1 style="color: white; margin: 0;">🏥 MedRagnosis</h1><p style="margin: 0.5rem 0 0 0; opacity: 0.9;">AI-Powered Medical Intelligence</p></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.info("👈 Please login from the sidebar to access the platform.")
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h2 style="color: #667eea; margin-bottom: 1rem;">Transform Healthcare with AI-Driven Insights</h2>
        <p style="font-size: 1.1rem; color: #666; max-width: 800px; margin: 0 auto; line-height: 1.6;">
            MedRagnosis combines cutting-edge artificial intelligence with medical expertise to provide 
            accurate diagnosis analysis, treatment recommendations, and comprehensive health insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Features
    st.markdown("<h3 style='text-align: center; color: #764ba2; margin: 2rem 0 1.5rem 0;'>🌟 Platform Features</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-card" style="text-align: center; height: 280px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">🔍</div>
            <h3 style="color: #667eea; margin-bottom: 0.8rem;">AI Report Analysis</h3>
            <p style="color: #666; line-height: 1.5;">
                Upload medical reports and get instant AI-powered analysis with intelligent diagnosis suggestions.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card" style="text-align: center; height: 280px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">💬</div>
            <h3 style="color: #667eea; margin-bottom: 0.8rem;">Interactive Consultation</h3>
            <p style="color: #666; line-height: 1.5;">
                Chat with our AI assistant for personalized health insights and medical information.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card" style="text-align: center; height: 280px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">👨‍⚕️</div>
            <h3 style="color: #667eea; margin-bottom: 0.8rem;">Doctor Verification</h3>
            <p style="color: #666; line-height: 1.5;">
                All AI diagnoses are reviewed and verified by licensed medical professionals.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # How It Works Section
    st.markdown("<h3 style='text-align: center; color: #764ba2; margin: 3rem 0 1.5rem 0;'>🚀 How It Works</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #667eea;">👤 For Patients</h4>
            <ol style="color: #666; line-height: 2;">
                <li><strong>Sign Up & Login</strong> - Create your secure account</li>
                <li><strong>Upload Reports</strong> - Submit your medical documents (PDF/TXT)</li>
                <li><strong>AI Analysis</strong> - Get instant intelligent diagnosis insights</li>
                <li><strong>Ask Questions</strong> - Interactive consultation with AI assistant</li>
                <li><strong>Track Status</strong> - Monitor doctor verification in real-time</li>
                <li><strong>View History</strong> - Access all your past consultations</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="color: #f5576c;">👨‍⚕️ For Doctors</h4>
            <ol style="color: #666; line-height: 2;">
                <li><strong>Professional Login</strong> - Access your doctor dashboard</li>
                <li><strong>Review Diagnoses</strong> - See pending AI-generated diagnoses</li>
                <li><strong>Patient History</strong> - Search and view patient records</li>
                <li><strong>Verify/Reject</strong> - Approve or reject AI diagnoses</li>
                <li><strong>Add Notes</strong> - Provide professional medical commentary</li>
                <li><strong>Ensure Quality</strong> - Maintain diagnostic accuracy standards</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    # Technology Stack
    st.markdown("<h3 style='text-align: center; color: #764ba2; margin: 3rem 0 1.5rem 0;'>⚡ Powered By Advanced AI</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖</div>
            <p style="color: #666; font-weight: 600;">LangChain RAG</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <p style="color: #666; font-weight: 600;">Vector Database</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔐</div>
            <p style="color: #666; font-weight: 600;">Secure Auth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">☁️</div>
            <p style="color: #666; font-weight: 600;">Cloud API</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Important Disclaimer
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    st.warning("""
    **⚠️ Important Medical Disclaimer**
    
    MedRagnosis is an AI-powered diagnostic assistance tool designed to support healthcare decision-making. 
    It is **NOT a substitute** for professional medical advice, diagnosis, or treatment. All AI-generated 
    diagnoses are subject to doctor verification. Always consult qualified healthcare providers for medical 
    concerns. Never disregard professional medical advice or delay seeking it because of information from this platform.
    """)
    
    # Call to Action
    st.markdown("""
    <div style="text-align: center; padding: 2.5rem; margin-top: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
        <h2 style="color: white; margin-bottom: 1rem;">Ready to Experience Smart Healthcare?</h2>
        <p style="color: white; opacity: 0.95; margin-bottom: 1.5rem; font-size: 1.1rem;">
            Join thousands of patients and doctors using AI-powered medical intelligence.
        </p>
        <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px; display: inline-block;">
            <p style="color: white; font-size: 1.2rem; margin: 0;">
                👈 <strong>Use the sidebar to login or create your account</strong>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # ------------------ PATIENT VIEW ------------------
    if st.session_state.role == "patient":
        
        # Tabs for different patient functions
        tab_consult, tab_history = st.tabs(["💬 Consultation", "📜 My History & Status"])
        
        # --- TAB 1: Chat & Upload ---
        with tab_consult:
            col1, col2 = st.columns([1, 1.5])
            
            # LEFT: Upload
            with col1:
                st.markdown("### 📤 Upload Report")
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                with st.form("upload_form"):
                    uploaded_files = st.file_uploader("PDF/TXT Files", type=["pdf", "txt"], accept_multiple_files=True)
                    submitted = st.form_submit_button("Upload & Analyze", use_container_width=True)
                    
                    if submitted and uploaded_files:
                        with st.spinner("Processing (OCR + Vectorizing)..."):
                            code, data = upload_report(st.session_state.token, uploaded_files)
                            if code == 200:
                                st.session_state.doc_id = data['doc_id']
                                # AUTO-CLEAR: Reset chat on new upload
                                st.session_state.messages = [] 
                                st.success(f"Uploaded! ID: {data['doc_id']}")
                            else:
                                st.error(data.get("detail", "Error"))
                st.markdown('</div>', unsafe_allow_html=True)

            # RIGHT: Chat 
            with col2:
                # Header + Clear Button
                h_col, b_col = st.columns([3, 1])
                with h_col:
                    st.markdown("### 💬 AI Consultant")
                with b_col:
                    if st.button("🗑️ Clear Chat", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()
                
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                
                if 'doc_id' in st.session_state:
                    # Analysis Mode Toggle
                    mode = st.radio("Analysis Scope:", ["Current Report", "All Reports (Trends)"], horizontal=True)
                    api_mode = "trends" if mode == "All Reports (Trends)" else "current"

                    if "messages" not in st.session_state:
                        st.session_state.messages = []

                    # Display Chat History
                    chat_container = st.container(height=400)
                    with chat_container:
                        if not st.session_state.messages:
                            st.info(f"Ready to analyze {mode.lower()}. Ask me anything!")
                        for msg in st.session_state.messages:
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])

                    # Chat Input
                    if prompt := st.chat_input("Type your medical question..."):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with chat_container:
                            with st.chat_message("user"):
                                st.markdown(prompt)
                        
                        with chat_container:
                            with st.chat_message("assistant"):
                                with st.spinner("Thinking..."):
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
                                            with st.expander("Sources"):
                                                st.json(data["sources"])
                                        st.session_state.messages.append({"role": "assistant", "content": ans})
                                        
                                        # Optional: Hint that status is pending
                                        st.caption("ℹ️ diagnosis saved to history (Pending Doctor Review)")
                                    else:
                                        st.error(f"Error: {data.get('detail')}")
                else:
                    st.info("Please upload a report to start.")
                st.markdown('</div>', unsafe_allow_html=True)

        # --- TAB 2: History & Status ---
        with tab_history:
            st.markdown("### 🩺 Diagnosis History & Doctor Reviews")
            if st.button("🔄 Refresh Status", key="refresh_hist"):
                st.rerun()
                
            with st.spinner("Fetching history..."):
                code, history = get_patient_history(st.session_state.token)
            
            if code == 200:
                if not history:
                    st.info("No diagnosis history found.")
                else:
                    for rec in history:
                        # Determine Styling based on Status
                        status = rec.get('verification_status', 'pending').lower()
                        
                        if status == 'verified':
                            color = "#27ae60" # Green
                            icon = "✅"
                            status_text = "VERIFIED BY DOCTOR"
                        elif status == 'rejected':
                            color = "#e74c3c" # Red
                            icon = "❌"
                            status_text = "REJECTED"
                        else:
                            color = "#f39c12" # Orange
                            icon = "⏳"
                            status_text = "PENDING REVIEW"

                        # Render Card
                        with st.expander(f"{icon} {datetime.datetime.fromtimestamp(rec['timestamp']).strftime('%Y-%m-%d %H:%M')} - {rec.get('question')[:50]}..."):
                            st.markdown(f"**Q:** {rec.get('question')}")
                            st.markdown(f"**AI Answer:** {rec.get('answer')}")
                            st.markdown("---")
                            st.markdown(f"<h5 style='color:{color}'>{icon} Status: {status_text}</h5>", unsafe_allow_html=True)
                            
                            if rec.get('doctor_note'):
                                st.info(f"👨‍⚕️ **Doctor's Note:** {rec['doctor_note']}")
                            
                            if rec.get('verified_by'):
                                st.caption(f"Reviewed by: Dr. {rec['verified_by']}")
            else:
                st.error("Could not fetch history. Server might be down.")

    # ------------------ DOCTOR VIEW ------------------
    elif st.session_state.role == "doctor":
        st.markdown("## 👨‍⚕️ Doctor Dashboard")
        
        tab_history, tab_review = st.tabs(["🔍 Patient History", "🩺 Pending Reviews"])
        
        # TAB 1: Search 
        with tab_history:
            patient_name = st.text_input("Enter Patient Username")
            if st.button("Search Records"):
                with st.spinner("Fetching..."):
                    code, data = get_doctor_diagnosis(st.session_state.token, patient_name)
                    if code == 200:
                        st.success(f"Found {len(data)} records")
                        for rec in data:
                            # Show verification status in doctor search as well
                            status = rec.get("verification_status", "pending")
                            icon = "✅" if status == "verified" else "⏳"
                            
                            with st.expander(f"{icon} {rec.get('question', 'No Q')[:40]}..."):
                                st.write(f"**Question:** {rec.get('question')}")
                                st.write(f"**AI Answer:** {rec.get('answer')}")
                                st.caption(f"Status: {status} | Date: {datetime.datetime.fromtimestamp(rec.get('timestamp', 0))}")
                    else:
                        st.error(data.get("detail", "Error"))
        
        #  TAB 2: Validation 
        with tab_review:
            if st.button("🔄 Refresh Pending"):
                st.rerun()
            
            # Fetch pending records
            code, pending = get_pending_reviews(st.session_state.token)
            
            if code == 200: 
                if pending:
                    for rec in pending:
                        with st.expander(f"Patient: {rec.get('requester')} | {rec.get('question')[:40]}..."):
                            st.write(f"**Question:** {rec.get('question')}")
                            st.info(f"**AI Diagnosis:** {rec.get('answer')}")
                            
                            note = st.text_input("Doctor Note", key=f"note_{rec['_id']}")
                            
                            c1, c2 = st.columns(2)
                            if c1.button("✅ Approve", key=f"app_{rec['_id']}"):
                                res_code, res_msg = verify_record(st.session_state.token, rec['_id'], "verified", note or "Approved")
                                if res_code == 200: 
                                    st.success("Verified!")
                                    st.rerun()
                                
                            if c2.button("❌ Reject", key=f"rej_{rec['_id']}"):
                                res_code, res_msg = verify_record(st.session_state.token, rec['_id'], "rejected", note or "Rejected")
                                if res_code == 200: 
                                    st.warning("Rejected!")
                                    st.rerun()
                else:
                    st.info("No pending reviews found. All caught up! 🎉")
            else:
                st.error("Failed to load pending reviews.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p><strong>MedRagnosis</strong> - Powered by GenAI & LangChain 🤖</p>
        <p style="font-size: 0.85rem;">Secure • Reliable • Intelligent Healthcare</p>
    </div>
""", unsafe_allow_html=True)