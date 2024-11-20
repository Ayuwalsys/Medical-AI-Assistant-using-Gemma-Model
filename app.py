import streamlit as st
import logging
import time
from models.chain_models import MedicalChain
from utils.vertex_ai_utils import initialize_vertex_ai
from components.ui_components import (
    render_sidebar_stats,
    render_feedback_form,
    render_disclaimer,
    render_medical_form,
    render_retrieved_info,
    render_metrics_dashboard
)

def display_statistics():
    """Display statistics in the sidebar"""
    if 'medical_chain' in st.session_state:
        stats = st.session_state.medical_chain.get_statistics()
        st.write("### 📊 Statistics")
        st.write(f"Total Consultations: {stats['total_requests']}")
        st.write(f"Unique Concerns: {stats['unique_concerns']}")
        
        st.write("Severity Distribution:")
        cols = st.columns(3)
        with cols[0]:
            st.write(f"High: {stats['severity_distribution']['HIGH']}")
        with cols[1]:
            st.write(f"Medium: {stats['severity_distribution']['MEDIUM']}")
        with cols[2]:
            st.write(f"Low: {stats['severity_distribution']['LOW']}")
def process_medical_query(patient_concern):
    """Process the medical query and display results"""
    if not patient_concern:
        st.warning("Please enter your symptoms first.")
        return

    with st.spinner('Analyzing your symptoms...'):
        try:
            example = {
                "Patient": patient_concern,
                "Description": patient_concern
            }
            
            status_container = st.empty()

            with status_container.container():
                st.info("🔄 Processing your request...")
                result = st.session_state.medical_chain.process(example)
            
            status_container.empty()
            
            # Create a unique response ID
            response_id = str(int(time.time()))
            
            # Display the response
            response_container = st.container()
            with response_container:
                st.markdown(result["FormattedOutput"])
                
                # Add feedback section below the response
                st.markdown("---")
                feedback = render_feedback_form(response_id)
                if feedback:
                    st.session_state.medical_chain.add_feedback(feedback)
                    st.success("Thank you for your feedback! 🙏")
                    
                    # Update statistics and metrics
                    st.session_state.stats = st.session_state.medical_chain.get_statistics()
                    st.session_state.user_metrics = st.session_state.medical_chain.get_user_metrics()
                    
                    # Force refresh to update sidebar metrics
                    st.experimental_rerun()
            
        except Exception as e:
            st.error(f"An error occurred while processing your request: {str(e)}")
            logging.error(f"Processing error: {str(e)}")
        

def render_disclaimer():
    """Render the medical disclaimer"""
    st.markdown("---")
    st.markdown("""
    ### ⚠️ Medical Disclaimer
    This AI assistant is for informational purposes only and should not replace professional medical advice. 
    Always consult with a qualified healthcare provider for medical diagnosis and treatment.
    """)

def main():
    st.set_page_config(
        page_title="Medical AI Assistant",
        page_icon="🏥",
        layout="wide"
    )
    
    # Sidebar for system status and controls
    with st.sidebar:
        st.write("### System Status")
        
        # Connection status and initialization
        try:
            if 'medical_chain' not in st.session_state:
                with st.spinner('Connecting to Gemma 7B...'):
                    endpoint = initialize_vertex_ai()
                    st.session_state.medical_chain = MedicalChain(endpoint)
                st.success("✅ Connected to Gemma 7B")
            else:
                st.success("✅ Connected to Gemma 7B")
            
            # Move test connection button to sidebar
            if st.button("Test Connection"):
                success, response = st.session_state.medical_chain.test_connection()
                if success:
                    st.success("Connection test successful!")
                else:
                    st.error(f"Connection test failed: {response}")
                    
        except Exception as e:
            st.error(f"Connection error: {str(e)}")
            return
            
        # Display statistics
        display_statistics()
        
        # Add model information footer
        st.markdown("---")
        st.markdown("### Model Information")
        st.info("""
        - Model: Gemma 7B
        - Project ID: angelic-goods-438016-f6
        - Region: us-central1
        """)
        
    # Main content area
    st.title("🏥 Medical AI Assistant")
    st.write("Please describe your medical concern below.")
    
    # Input fields
    patient_concern = st.text_area("What are your symptoms?")
    
    if st.button("Get Medical Advice"):
        process_medical_query(patient_concern)
    
    # Render disclaimer at the bottom
    render_disclaimer()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()