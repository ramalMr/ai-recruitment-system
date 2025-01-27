import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# .env faylını yüklə
load_dotenv()

logger = logging.getLogger(__name__)

class EmailHandler:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Email konfiqurasiyasını yoxla
        self.sender_email = os.getenv("EMAIL_ADDRESS") or st.session_state.get('email_address')
        self.sender_password = os.getenv("EMAIL_PASSWORD") or st.session_state.get('email_password')
        
        if not self.sender_email or not self.sender_password:
            error_msg = "Email konfiqurasiyası tapılmadı! Zəhmət olmasa .env faylını və ya tənzimləmələri yoxlayın."
            logger.error(error_msg)
            raise ValueError(error_msg)

    async def send_email(self, to_email, subject, body):
        """Email göndərmə"""
        if not to_email or not subject or not body:
            raise ValueError("Email məlumatları tam deyil")

        try:
            # Email mesajını hazırla
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # HTML mətnini əlavə et
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)

            # SMTP server-ə qoşul
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                
                # Login və göndərmə
                try:
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                    logger.info(f"Email successfully sent to {to_email}")
                    return True
                except smtplib.SMTPAuthenticationError:
                    error_msg = "Email autentifikasiya xətası. Gmail App Password düzgün deyil."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                except Exception as e:
                    logger.error(f"SMTP error: {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Email göndərilməsi xətası: {str(e)}")
            raise

    async def send_selection_email(self, to_email, role):
        """Seçim emaili göndərmə"""
        if not to_email or not role:
            raise ValueError("Email və ya rol məlumatı çatışmır")

        subject = f"Təbriklər! {role} vəzifəsi üçün seçildiniz"
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Hörmətli namizəd,</h2>
            <p>Təbrik edirik! Siz <b>{role}</b> vəzifəsi üçün ilkin mərhələni uğurla keçdiniz.</p>
            <p>Texniki müsahibə üçün təyin olunmuş vaxt haqqında məlumat tezliklə göndəriləcək.</p>
            <br>
            <p>Hörmətlə,</p>
            <p>HR Komandası</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body)

    async def send_rejection_email(self, to_email, role, feedback, suggestions):
        """Rədd emaili göndərmə"""
        if not all([to_email, role, feedback]):
            raise ValueError("Email məlumatları tam deyil")

        subject = f"{role} vəzifəsi üçün müraciətiniz"
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Hörmətli namizəd,</h2>
            <p>Təəssüf ki, <b>{role}</b> vəzifəsi üçün müraciətiniz hal-hazırda tələblərimizə tam uyğun deyil.</p>
            <h3>Təhlil:</h3>
            <p>{feedback}</p>
            <h3>İnkişaf üçün məsləhətlər:</h3>
            <ul>
            {''.join([f"<li>{s}</li>" for s in (suggestions or [])])}
            </ul>
            <br>
            <p>Hörmətlə,</p>
            <p>HR Komandası</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body)

    async def send_interview_confirmation(self, to_email, role, meeting_details):
        """Müsahibə təsdiqi emaili"""
        if not all([to_email, role, meeting_details]):
            raise ValueError("Müsahibə məlumatları tam deyil")

        subject = f"Müsahibə Təsdiqi - {role} vəzifəsi"
        body = f"""
        <html>
        <head></head>
        <body>
            <h2>Hörmətli namizəd,</h2>
            <p><b>{role}</b> vəzifəsi üçün müsahibəniz planlaşdırılıb.</p>
            <p><strong>Tarix:</strong> {meeting_details['date']}</p>
            <p><strong>Saat:</strong> {meeting_details['time']}</p>
            <p><strong>Zoom Link:</strong> <a href="{meeting_details['join_url']}">{meeting_details['join_url']}</a></p>
            <p style="color: #ff0000;">⚠️ Xahiş edirik müsahibəyə 5 dəqiqə əvvəl qoşulasınız.</p>
            <br>
            <p>Hörmətlə,</p>
            <p>HR Komandası</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body)