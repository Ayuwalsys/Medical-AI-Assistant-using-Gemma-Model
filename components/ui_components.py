import streamlit as st
from datetime import datetime
from typing import Dict, Any,  Optional, List

def render_sidebar_stats(stats):
    st.sidebar.title("📊 Statistics")
    st.sidebar.write("Total Consultations:", stats["total_responses"])
    st.sidebar.write("Unique Concerns:", stats["unique_concerns"])
    
    st.sidebar.write("Severity Distribution:")
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.metric("High", stats["severity_distribution"]["HIGH"])
    with col2:
        st.metric("Medium", stats["severity_distribution"]["MEDIUM"])
    with col3:
        st.metric("Low", stats["severity_distribution"]["LOW"])

def render_feedback_form(response_id: str) -> Optional[Dict[str, Any]]:
    """Render feedback form after each consultation"""
    st.markdown("### 📝 Was this response helpful?")
    
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        feedback = st.radio(
            "Rate this response:",
            ["👍 Helpful", "😐 Somewhat Helpful", "👎 Not Helpful"],
            key=f"feedback_{response_id}",
            horizontal=True
        )
        
        additional_feedback = st.text_area(
            "Additional comments (optional):",
            key=f"comments_{response_id}"
        )
        
        if st.button("Submit Feedback", key=f"submit_{response_id}"):
            return {
                "rating": feedback,
                "comments": additional_feedback,
                "response_id": response_id,
                "timestamp": datetime.now()
            }
    return None

def render_disclaimer():
    st.markdown("""
    ---
    ⚠️ **Disclaimer**:
    - This is an AI-powered medical assistant for informational purposes only
    - Not a substitute for professional medical advice
    - In case of emergency, contact your local emergency services immediately
    """)

def render_medical_form():
    with st.form("medical_form"):
        patient_concern = st.text_area("What are your symptoms?", height=100)
        description = st.text_area("Additional context (optional)", height=100)
        submitted = st.form_submit_button("Get Medical Advice")
        
        return submitted, patient_concern, description

def render_retrieved_info(retrieved_info: List[str]):
    with st.expander("📚 Retrieved Medical Information", expanded=False):
        for info in retrieved_info:
            st.markdown(info)

def render_metrics_dashboard(stats: Dict[str, Any], user_metrics: Dict[str, Any]):
    """Render comprehensive metrics dashboard"""
    st.sidebar.markdown("### 📊 Performance Metrics")
    
    # Usage Statistics
    st.sidebar.markdown("#### Usage Stats")
    st.sidebar.write(f"Total Consultations: {stats['total_responses']}")
    st.sidebar.write(f"Unique Concerns: {stats['unique_concerns']}")
    
    # User Feedback Metrics
    if 'user_metrics' in st.session_state:
        st.sidebar.markdown("#### User Feedback")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric(
                "Satisfaction Rate",
                f"{user_metrics['average_rating']}%",
                delta=user_metrics['feedback_trend']
            )
        with col2:
            st.metric(
                "Total Feedback",
                user_metrics['total_feedback']
            )
        
        # Feedback Distribution
        st.sidebar.markdown("#### Feedback Distribution")
        ratings = user_metrics['response_ratings']
        total_ratings = sum(ratings.values())
        if total_ratings > 0:
            st.sidebar.progress(ratings['helpful'] / total_ratings)
            st.sidebar.caption(f"👍 Helpful: {ratings['helpful']}")
            st.sidebar.progress(ratings['somewhat_helpful'] / total_ratings)
            st.sidebar.caption(f"😐 Somewhat: {ratings['somewhat_helpful']}")
            st.sidebar.progress(ratings['not_helpful'] / total_ratings)
            st.sidebar.caption(f"👎 Not Helpful: {ratings['not_helpful']}")