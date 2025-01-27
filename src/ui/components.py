import streamlit as st
from ..config.constants import UI_TEXTS, ROLE_REQUIREMENTS
from ..utils.session import SessionManager
from streamlit_pdf_viewer import pdf_viewer
import os

class UIComponents:
    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.header(UI_TEXTS["settings"])
            
            
            st.subheader("Groq Tənzimləmələri")
            api_key = st.text_input(
                UI_TEXTS["api_key"],
                type="password",
                value=st.session_state.groq_api_key
            )
            if api_key:
                SessionManager.update_session('groq_api_key', api_key)

            
            st.subheader("Zoom Tənzimləmələri")
            zoom_fields = {
                'zoom_account_id': "Zoom Hesab ID",
                'zoom_client_id': "Zoom Client ID",
                'zoom_client_secret': "Zoom Client Secret"
            }
            
            for key, label in zoom_fields.items():
                value = st.text_input(
                    label,
                    type="password",
                    value=st.session_state.get(key, "")
                )
                if value:
                    SessionManager.update_session(key, value)

            
            st.subheader("Email Tənzimləmələri")
            email_fields = {
                'email_sender': "Göndərən Email",
                'email_passkey': "Email Şifrəsi",
                'company_name': "Şirkət Adı"
            }
            
            for key, label in email_fields.items():
                value = st.text_input(
                    label,
                    type="password" if 'passkey' in key else "default",
                    value=st.session_state.get(key, "")
                )
                if value:
                    SessionManager.update_session(key, value)

    @staticmethod
    def render_pdf_viewer(pdf_file, tmp_file_path: str):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            try:
                pdf_viewer(tmp_file_path)
            finally:
                os.unlink(tmp_file_path)
        
        with col2:
            st.download_button(
                label="📥 Yüklə",
                data=pdf_file,
                file_name=pdf_file.name,
                mime="application/pdf"
            )

    @staticmethod
    def render_analysis_results(analysis_result: dict):
        st.subheader("Təhlil Nəticələri")
        
        
        score = analysis_result.get("uyğunluq_faizi", 0)
        st.metric(
            label="Uyğunluq Faizi",
            value=f"{score}%",
            help="Vəzifə tələblərinə uyğunluq faizi"
        )

        
        col1, col2 = st.columns(2)
        with col1:
            st.write("💪 Güclü tərəflər:")
            for skill in analysis_result.get("güclü_tərəflər", []):
                st.write(f"✓ {skill}")
        
        with col2:
            st.write("🎯 İnkişaf edilməli sahələr:")
            for skill in analysis_result.get("çatışmayan_bacarıqlar", []):
                st.write(f"• {skill}")

        
        st.write("📝 Ətraflı təhlil:")
        st.write(analysis_result.get("təhlil", ""))
        
        st.write("💡 Məsləhətlər:")
        st.write(analysis_result.get("məsləhətlər", ""))
        