import streamlit as st
import asyncio
import logging
from datetime import datetime, timedelta
import pytz
from src.config.constants import UI_TEXTS, ROLE_REQUIREMENTS
from src.utils.session import SessionManager
from src.core.groq_agent import GroqAgent
from src.core.email_handler import EmailHandler
from src.utils.pdf_processor import PDFProcessor
from src.ui.components import UIComponents
from src.core.zoom_handler import CustomZoomTool
from dotenv import load_dotenv
import os
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ApplicationManager:
    def __init__(self):
        self.session_manager = SessionManager()
        self.ui_components = UIComponents()
        self.pdf_processor = PDFProcessor()
        
    def initialize_agents(self):
        """API açarlarının yoxlanması və agent obyektlərinin yaradılması"""
        if not st.session_state['groq_api_key']:
            st.sidebar.error("Zəhmət olmasa Groq API açarını daxil edin!")
            return None, None

        try:
            groq_agent = GroqAgent(st.session_state['groq_api_key'])
            email_handler = EmailHandler()
            return groq_agent, email_handler
        except Exception as e:
            logger.error(f"Agent initialization error: {str(e)}")
            st.error("Agent obyektlərinin yaradılması zamanı xəta!")
            return None, None

    def process_resume(self, resume_file, groq_agent):
        """CV faylının emalı və təhlili"""
        if not resume_file:
            return False

        st.subheader("Yüklənmiş CV")
        
        try:
            
            preview = self.pdf_processor.get_pdf_preview(resume_file)
            if preview:
                st.image(preview, caption="CV Görüntüsü", use_column_width=True)
           
            resume_file.seek(0)

            if not st.session_state['resume_text']:
                with st.spinner("CV-niz emal olunur..."):
                    resume_text = self.pdf_processor.extract_text(resume_file)
                    if resume_text:
                        st.session_state['resume_text'] = resume_text
                        st.success("CV uğurla emal edildi!")

                        # email unvani cixar
                        email_from_resume = asyncio.run(groq_agent.extract_email(resume_text))
                        if email_from_resume:
                            st.session_state['candidate_email'] = email_from_resume
                            st.success(f"Email ünvanı tapıldı: {email_from_resume}")
                        else:
                            st.warning("CV-dən email ünvanı tapılmadı.")
                        return True
                    else:
                        st.error("PDF emal edilə bilmədi.")
                        return False

            return True

        except Exception as e:
            logger.error(f"Resume processing error: {str(e)}")
            st.error("CV emalı zamanı xəta baş verdi!")
            return False

    async def schedule_interview(self, role, email_handler):
        """Müsahibənin planlaşdırılması"""
        try:
            zoom_configs = {
                'account_id': st.session_state['zoom_account_id'],
                'client_id': st.session_state['zoom_client_id'],
                'client_secret': st.session_state['zoom_client_secret']
            }

            if not all(zoom_configs.values()):
                st.error("Zoom tənzimləmələrini tamamlayın!")
                return False

            baku_tz = pytz.timezone('Asia/Baku')
            current_time = datetime.now(baku_tz)
            next_workday = current_time + timedelta(days=1)
            
            if next_workday.weekday() >= 5:
                next_workday += timedelta(days=8 - next_workday.weekday())

            interview_time = next_workday.replace(hour=11, minute=0, second=0, microsecond=0)

            zoom_tool = CustomZoomTool(**zoom_configs)
            
            meeting_details = {
                "topic": f"{role} Texniki Müsahibə",
                "start_time": interview_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration": 60,
                "timezone": "Asia/Baku"
            }

            meeting_response = await zoom_tool.create_meeting(meeting_details)
            
            if st.session_state.get('candidate_email'):
                await email_handler.send_interview_confirmation(
                    to_email=st.session_state['candidate_email'],
                    role=role,
                    meeting_details={
                        "date": interview_time.strftime("%Y-%m-%d"),
                        "time": interview_time.strftime("%H:%M"),
                        "join_url": meeting_response.get("join_url")
                    }
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Interview scheduling error: {str(e)}")
            st.error("Müsahibə planlaşdırılması zamanı xəta!")
            return False



def render_sidebar():
    """Render sidebar with configuration inputs"""
    with st.sidebar:
        st.header("Tənzimləmələr")
        
        st.subheader("Groq API Tənzimləmələri")
        api_key = st.text_input(
            "Groq API Key",
            value=st.session_state.get('groq_api_key', os.getenv("GROQ_API_KEY", "")),
            type="password"
        )
        st.session_state['groq_api_key'] = api_key
        
        st.subheader("Email Tənzimləmələri")
        email_address = st.text_input(
            "Email Address",
            value=st.session_state.get('email_address', os.getenv("EMAIL_ADDRESS", "")),
            type="password"
        )
        st.session_state['email_address'] = email_address
        
        email_password = st.text_input(
            "Email Password",
            value=st.session_state.get('email_password', os.getenv("EMAIL_PASSWORD", "")),
            type="password"
        )
        st.session_state['email_password'] = email_password
        
        st.subheader("Zoom Tənzimləmələri")
        account_id = st.text_input(
            "Zoom Account ID",
            value=st.session_state.get('zoom_account_id', os.getenv("ZOOM_ACCOUNT_ID", "")),
            type="password"
        )
        st.session_state['zoom_account_id'] = account_id
        
        client_id = st.text_input(
            "Zoom Client ID",
            value=st.session_state.get('zoom_client_id', os.getenv("ZOOM_CLIENT_ID", "")),
            type="password"
        )
        st.session_state['zoom_client_id'] = client_id
        
        client_secret = st.text_input(
            "Zoom Client Secret",
            value=st.session_state.get('zoom_client_secret', os.getenv("ZOOM_CLIENT_SECRET", "")),
            type="password"
        )
        st.session_state['zoom_client_secret'] = client_secret

def display_analysis_results(analysis_result):
    """Təhlil nəticələrini göstərmək üçün helper funksiya"""
    if not analysis_result:
        return
        
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Uyğunluq", f"{analysis_result['uyğunluq_faizi']}%")
    with col2:
        st.metric("Qərar", analysis_result['qərar'].upper())

    with st.expander("Ətraflı Təhlil", expanded=True):
        st.write(analysis_result['təhlil'])
        
        st.write("**Güclü tərəflər:**")
        for strength in analysis_result['güclü_tərəflər']:
            st.write(f"- {strength}")
        
        st.write("**İnkişaf tələb edən sahələr:**")
        for weakness in analysis_result['zəif_tərəflər']:
            st.write(f"- {weakness}")
        
        st.write("**Məsləhətlər:**")
        for suggestion in analysis_result['məsləhətlər']:
            st.write(f"- {suggestion}")

def main():
    try:
      
        SessionManager.init_session_state()
        
        st.title(UI_TEXTS["title"])
        
        render_sidebar()
        
        app = ApplicationManager()
        
        groq_agent, email_handler = app.initialize_agents()
        if not groq_agent or not email_handler:
            return

        role = st.selectbox(
            "Müraciət etdiyiniz vəzifəni seçin:",
            list(ROLE_REQUIREMENTS.keys())
        )

        with st.expander("Vəzifə tələbləri", expanded=True):
            st.markdown(ROLE_REQUIREMENTS[role])

        if st.button("📝 Yeni Müraciət"):
            SessionManager.reset_application()
            st.experimental_rerun()

        resume_file = st.file_uploader(
            "CV-nizi yükləyin (PDF)",
            type=["pdf"],
            key="resume_uploader"
        )

        if resume_file:
            app.process_resume(resume_file, groq_agent)

        email = st.text_input(
            "Namizədin email ünvanı",
            value=st.session_state['candidate_email'],
            key="email_input"
        )
        st.session_state['candidate_email'] = email

        
        if st.session_state.get('analysis_result'):
            display_analysis_results(st.session_state['analysis_result'])

        # CV təhlili
        if st.session_state['resume_text'] and email and not st.session_state['analysis_complete']:
            if st.button("CV-ni Təhlil Et"):
                with st.spinner("CV-niz təhlil olunur..."):
                    try:
                        analysis_result = asyncio.run(groq_agent.analyze_resume(
                            st.session_state['resume_text'],
                            role
                        ))
                     
                       
                        st.session_state['analysis_result'] = analysis_result
                        
                        with st.expander("CV Mətni", expanded=False):
                            st.text_area(
                                "Çıxarılmış CV Mətni",
                                st.session_state['resume_text'],
                                height=300,
                                disabled=True
                            )

                        display_analysis_results(analysis_result)

                        is_selected = analysis_result.get("qərar") == "qəbul"
                        
                        if is_selected:
                            st.success("Təbriklər! Sizin bacarıqlarınız tələblərə uyğundur.")
                            st.session_state['analysis_complete'] = True
                            st.session_state['is_selected'] = True
                            st.experimental_rerun()
                        else:
                            st.warning("Təəssüf ki, sizin bacarıqlarınız hal-hazırda tələblərə tam uyğun deyil.")
                            
                            with st.spinner("Rəy emaili göndərilir..."):
                                try:
                                    asyncio.run(email_handler.send_rejection_email(
                                        to_email=email,
                                        role=role,
                                        feedback=analysis_result['təhlil'],
                                        suggestions=analysis_result.get("məsləhətlər", [])
                                    ))
                                    st.info("Sizə ətraflı rəy emaili göndərildi.")
                                except Exception as e:
                                    logger.error(f"Rejection email error: {str(e)}")
                                    st.error("Email göndərilə bilmədi.")

                    except Exception as e:
                        logger.error(f"CV analysis error: {str(e)}")
                        st.error("CV təhlili zamanı xəta baş verdi!")

        if st.session_state['analysis_complete'] and st.session_state['is_selected']:
            st.success("Təbriklər! Sizin bacarıqlarınız tələblərə uyğundur.")
            st.info("Müsahibə prosesinə keçmək üçün 'Davam Et' düyməsini sıxın.")

            if st.button("Davam Et", key="proceed_button"):
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.spinner("📧 Təsdiq emaili göndərilir..."):
                        try:
                            asyncio.run(email_handler.send_selection_email(
                                to_email=st.session_state['candidate_email'],
                                role=role
                            ))
                            st.success("✅ Təsdiq emaili göndərildi!")
                        except Exception as e:
                            st.error("❌ Email göndərilməsi xətası!")
                            logger.error(f"Selection email error: {str(e)}")
                
                with col2:
                    with st.spinner("📅 Müsahibə planlaşdırılır..."):
                        try:
                            if asyncio.run(app.schedule_interview(role, email_handler)):
                                st.success("✅ Müsahibə planlaşdırıldı!")
                            else:
                                st.error("❌ Müsahibə planlaşdırılması xətası!")
                        except Exception as e:
                            st.error("❌ Müsahibə planlaşdırılması xətası!")
                            logger.error(f"Interview scheduling error: {str(e)}")

                st.success("""
                    🎉 Müraciətiniz Uğurla Tamamlandı!
                    
                    Görülən işlər:
                    1. Seçim təsdiqi ✅
                    2. Müsahibə planlaşdırıldı ✅
                    3. Zoom link göndərildi ✅
                    
                    Növbəti addımlar:
                    1. Email-inizi yoxlayın
                    2. Müsahibəyə 5 dəqiqə əvvəl qoşulun
                    3. Texniki müsahibəyə hazırlaşın
                """)

        if st.sidebar.button("Müraciəti Sıfırla"):
            SessionManager.reset_application()
            st.experimental_rerun()

    except Exception as e:
        logger.error(f"Main application error: {str(e)}")
        st.error("Sistemdə xəta baş verdi. Səhifəni yeniləyin və ya dəstəklə əlaqə saxlayın.")

if __name__ == "__main__":
    main()