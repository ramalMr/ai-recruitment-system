import streamlit as st
from typing import Dict, Any

class SessionManager:
    @staticmethod
    def init_session_state():
        """Initialize all session state variables"""
       
        if 'groq_api_key' not in st.session_state:
            st.session_state['groq_api_key'] = ''
        if 'zoom_account_id' not in st.session_state:
            st.session_state['zoom_account_id'] = ''
        if 'zoom_client_id' not in st.session_state:
            st.session_state['zoom_client_id'] = ''
        if 'zoom_client_secret' not in st.session_state:
            st.session_state['zoom_client_secret'] = ''
            
        if 'resume_text' not in st.session_state:
            st.session_state['resume_text'] = ''
        if 'candidate_email' not in st.session_state:
            st.session_state['candidate_email'] = ''
        if 'analysis_complete' not in st.session_state:
            st.session_state['analysis_complete'] = False
        if 'is_selected' not in st.session_state:
            st.session_state['is_selected'] = False

    @staticmethod
    def reset_application():
        """Reset all application related session state variables"""
        st.session_state['resume_text'] = ''
        st.session_state['candidate_email'] = ''
        st.session_state['analysis_complete'] = False
        st.session_state['is_selected'] = False