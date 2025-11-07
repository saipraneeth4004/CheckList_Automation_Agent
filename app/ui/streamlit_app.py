"""
Streamlit application for Monthly Close Checklist Automation
"""

import streamlit as st
import requests
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
import sys
import os

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

# Page config
st.set_page_config(
    page_title="Month-End Checklist Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .status-complete {
        color: #28a745;
        font-weight: bold;
    }
    .status-incomplete {
        color: #ffc107;
        font-weight: bold;
    }
    .status-missing {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def create_session() -> str:
    """Create a new session"""
    try:
        response = requests.post(f"{API_BASE_URL}/session/create")
        response.raise_for_status()
        return response.json()["session_id"]
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return None


def upload_files(session_id: str, files: List) -> bool:
    """Upload files to the server"""
    try:
        files_data = []
        for file in files:
            files_data.append(("files", (file.name, file.getvalue(), file.type)))
        
        response = requests.post(
            f"{API_BASE_URL}/upload/{session_id}",
            files=files_data
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error uploading files: {str(e)}")
        return False


def validate_files(session_id: str) -> Dict[str, Any]:
    """Validate uploaded files"""
    try:
        response = requests.post(f"{API_BASE_URL}/validate/{session_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error validating files: {str(e)}")
        return None


def send_chat_message(session_id: str, message: str, context: Dict = None) -> str:
    """Send a chat message"""
    try:
        payload = {
            "session_id": session_id,
            "message": message,
            "context": context
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=payload)
        response.raise_for_status()
        return response.json()["message"]
    except Exception as e:
        return f"Error: {str(e)}"


def get_item_guidance(session_id: str, item_id: str) -> Dict[str, Any]:
    """Get guidance for a checklist item"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/checklist/guidance/{session_id}/{item_id}"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error getting guidance: {str(e)}")
        return None


def generate_document(session_id: str, item_id: str, user_data: Dict) -> Dict[str, Any]:
    """Generate a document"""
    try:
        payload = {
            "session_id": session_id,
            "checklist_item_id": item_id,
            "user_data": user_data
        }
        response = requests.post(f"{API_BASE_URL}/generate-document", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error generating document: {str(e)}")
        return None


def display_header():
    """Display app header"""
    st.markdown('<div class="main-header">📊 Monthly Close Checklist Automation</div>', unsafe_allow_html=True)
    st.markdown("AI-powered month-end close validation and assistance")
    st.markdown("---")


def display_sidebar():
    """Display sidebar"""
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/checklist.png", width=80)
        st.title("Navigation")
        
        page = st.radio(
            "Select Page",
            ["📁 Upload & Validate", "📋 Checklist Status", "💬 AI Assistant", "📄 Generate Documents"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Session info
        if st.session_state.session_id:
            st.success(f"✅ Session Active")
            if st.button("🔄 New Session"):
                st.session_state.session_id = None
                st.session_state.validation_results = None
                st.session_state.chat_history = []
                st.rerun()
        else:
            st.warning("⚠️ No Session")
        
        st.markdown("---")
        
        # Quick stats
        if st.session_state.validation_results:
            summary = st.session_state.validation_results.get("summary", {})
            st.metric("Completion Rate", f"{summary.get('completion_rate', 0):.0f}%")
            st.metric("Complete", summary.get('complete', 0))
            st.metric("Incomplete", summary.get('incomplete', 0))
            st.metric("Missing", summary.get('missing', 0))
        
        return page


def page_upload_validate():
    """Upload and validate page"""
    st.header("📁 Upload Month-End Files")
    
    # Create session if needed
    if not st.session_state.session_id:
        if st.button("Start New Session", type="primary"):
            session_id = create_session()
            if session_id:
                st.session_state.session_id = session_id
                st.success(f"✅ Session created: {session_id[:8]}...")
                st.rerun()
    
    if st.session_state.session_id:
        st.info(f"Session ID: {st.session_state.session_id[:8]}...")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload your month-end accounting files",
            accept_multiple_files=True,
            type=['xlsx', 'xls', 'csv', 'pdf', 'txt'],
            help="Upload Excel, CSV, PDF, or text files containing your month-end data"
        )
        
        if uploaded_files:
            st.write(f"📎 {len(uploaded_files)} file(s) selected")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("⬆️ Upload Files", type="primary"):
                    with st.spinner("Uploading files..."):
                        if upload_files(st.session_state.session_id, uploaded_files):
                            st.success("✅ Files uploaded successfully!")
            
            with col2:
                if st.button("🔍 Validate Checklist", type="primary"):
                    with st.spinner("Validating checklist..."):
                        results = validate_files(st.session_state.session_id)
                        if results:
                            st.session_state.validation_results = results
                            st.success("✅ Validation complete!")
                            st.rerun()
        
        # Display validation results
        if st.session_state.validation_results:
            st.markdown("---")
            st.subheader("📊 Validation Results")
            
            summary = st.session_state.validation_results["summary"]
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Items", summary["total_items"])
            with col2:
                st.metric("✅ Complete", summary["complete"])
            with col3:
                st.metric("⚠️ Incomplete", summary["incomplete"])
            with col4:
                st.metric("❌ Missing", summary["missing"])
            
            # Progress bar
            progress = summary["completion_rate"] / 100
            st.progress(progress)
            st.write(f"**Completion Rate:** {summary['completion_rate']:.1f}%")


def page_checklist_status():
    """Checklist status page"""
    st.header("📋 Checklist Status")
    
    if not st.session_state.validation_results:
        st.warning("⚠️ No validation results available. Please upload and validate files first.")
        return
    
    # Display guidance if available
    if hasattr(st.session_state, 'current_guidance') and st.session_state.current_guidance:
        st.success("📖 **AI Guidance**")
        guidance = st.session_state.current_guidance
        st.markdown(guidance.get("guidance", "No guidance available"))
        
        if guidance.get("next_steps"):
            st.info("**Next Steps:**")
            for step in guidance["next_steps"]:
                st.write(f"- {step}")
        
        if st.button("Close Guidance"):
            st.session_state.current_guidance = None
            st.rerun()
        
        st.markdown("---")
    
    results = st.session_state.validation_results
    checklist_results = results["checklist_results"]
    
    # Filter options
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["complete", "incomplete", "missing"],
            default=["incomplete", "missing"]
        )
    with col2:
        show_all = st.checkbox("Show All Items", value=False)
    
    # Display items
    filtered_items = checklist_results if show_all else [
        item for item in checklist_results if item["status"] in status_filter
    ]
    
    for item in filtered_items:
        status = item["status"]
        status_emoji = {
            "complete": "✅",
            "incomplete": "⚠️",
            "missing": "❌"
        }.get(status, "❓")
        
        with st.expander(f"{status_emoji} {item['name']} - {status.upper()}"):
            st.write(f"**Description:** {item['description']}")
            st.write(f"**Confidence:** {item['confidence']:.0%}")
            
            if item["matched_files"]:
                st.write(f"**Matched Files:** {', '.join(item['matched_files'])}")
            
            if item["issues"]:
                st.warning("**Issues:**")
                for issue in item["issues"]:
                    st.write(f"- {issue}")
            
            if item["recommendations"]:
                st.info("**Recommendations:**")
                for rec in item["recommendations"]:
                    st.write(f"- {rec}")
            
            if status != "complete":
                if st.button(f"Get Help with {item['name']}", key=f"help_{item['id']}"):
                    guidance = get_item_guidance(st.session_state.session_id, item['id'])
                    if guidance:
                        st.session_state.current_guidance = guidance
                        st.rerun()


def page_ai_assistant():
    """AI assistant page"""
    st.header("💬 AI Assistant")
    
    if not st.session_state.session_id:
        st.warning("⚠️ Please start a session first.")
        return
    
    st.write("Ask me anything about your month-end close process!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Get AI response
        with st.spinner("Thinking..."):
            response = send_chat_message(st.session_state.session_id, prompt)
        
        # Add assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Quick action buttons
    if st.session_state.validation_results:
        st.markdown("---")
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Analyze My Results"):
                prompt = "Please analyze my current checklist results and provide recommendations."
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                response = send_chat_message(st.session_state.session_id, prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("❓ What's Missing?"):
                prompt = "What checklist items are missing or incomplete?"
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                response = send_chat_message(st.session_state.session_id, prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()


def page_generate_documents():
    """Document generation page"""
    st.header("📄 Generate Documents")
    
    if not st.session_state.session_id:
        st.warning("⚠️ Please start a session first.")
        return
    
    if not st.session_state.validation_results:
        st.info("💡 Upload and validate your files first to see which documents are missing.")
        return
    
    st.write("Generate missing documents based on your data:")
    
    # Get incomplete/missing items
    checklist_results = st.session_state.validation_results["checklist_results"]
    incomplete_items = [
        item for item in checklist_results 
        if item["status"] in ["incomplete", "missing"]
    ]
    
    if not incomplete_items:
        st.success("🎉 All checklist items are complete! No documents need to be generated.")
        return
    
    # Select document to generate
    item_options = {item["name"]: item["id"] for item in incomplete_items}
    selected_item_name = st.selectbox("Select document to generate", list(item_options.keys()))
    selected_item_id = item_options[selected_item_name]
    
    st.markdown("---")
    st.subheader(f"Generate: {selected_item_name}")
    
    # Simple data input
    st.write("Provide the necessary data:")
    
    user_data = {}
    
    if selected_item_id == "bank_reconciliation":
        user_data["period"] = st.text_input("Period", "December 2024")
        user_data["bank_account"] = st.text_input("Bank Account", "")
        user_data["bank_balance"] = st.number_input("Bank Statement Balance", value=0.0)
    
    elif selected_item_id in ["ar_aging", "ap_aging"]:
        st.write("You can generate a template and fill it with your data later.")
        user_data["customers" if "ar" in selected_item_id else "vendors"] = []
    
    elif selected_item_id == "accruals":
        st.write("Generate a template for journal entries.")
        user_data["entries"] = []
    
    if st.button("Generate Document", type="primary"):
        with st.spinner("Generating document..."):
            result = generate_document(st.session_state.session_id, selected_item_id, user_data)
            if result and result.get("success"):
                st.success(f"✅ Document generated: {result['filename']}")
                st.download_button(
                    label="📥 Download Document",
                    data=requests.get(f"http://localhost:8000{result['download_url']}").content,
                    file_name=result['filename'],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )


def main():
    """Main application"""
    display_header()
    page = display_sidebar()
    
    # Route to pages
    if page == "📁 Upload & Validate":
        page_upload_validate()
    elif page == "📋 Checklist Status":
        page_checklist_status()
    elif page == "💬 AI Assistant":
        page_ai_assistant()
    elif page == "📄 Generate Documents":
        page_generate_documents()


if __name__ == "__main__":
    main()
