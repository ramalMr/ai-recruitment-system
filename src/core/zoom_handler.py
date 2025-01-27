import logging
import json
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import base64
import streamlit as st

# .env faylını yüklə
load_dotenv()

logger = logging.getLogger(__name__)

class CustomZoomTool:
    def __init__(self, account_id, client_id, client_secret):
        # Konfiqurasiya məlumatlarını yoxla
        self.account_id = account_id or os.getenv("ZOOM_ACCOUNT_ID")
        self.client_id = client_id or os.getenv("ZOOM_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("ZOOM_CLIENT_SECRET")
        
        if not all([self.account_id, self.client_id, self.client_secret]):
            logger.error("Zoom konfiqurasiyası tapılmadı!")
            st.sidebar.error("Zoom konfiqurasiyasını tamamlayın!")
            raise ValueError("Zoom məlumatları .env faylında tapılmadı")
            
        self.base_url = "https://api.zoom.us/v2"
        self.token = None

    def get_access_token(self):
        """Zoom API access token əldə edir"""
        try:
            url = "https://zoom.us/oauth/token"
            
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'account_credentials',
                'account_id': self.account_id
            }

            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data['access_token']
                return self.token
            else:
                error_msg = f"Token response: {response.status_code} - {response.text}"
                logger.error(error_msg)
                st.error("Zoom API xətası: Token alına bilmədi")
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Zoom token xətası: {str(e)}")
            raise

    async def create_meeting(self, meeting_details):
        """Zoom görüşü yaradır"""
        try:
            if not self.token:
                self.token = self.get_access_token()

            url = f"{self.base_url}/users/me/meetings"

            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

            meeting_data = {
                "topic": meeting_details["topic"],
                "type": 2,
                "start_time": meeting_details["start_time"],
                "duration": meeting_details["duration"],
                "timezone": meeting_details["timezone"],
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "join_before_host": True,
                    "waiting_room": True,
                    "auto_recording": "none"
                }
            }

            response = requests.post(url, headers=headers, json=meeting_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "join_url": data['join_url'],
                    "meeting_id": data['id'],
                    "start_url": data.get('start_url')
                }
            else:
                error_msg = f"Meeting creation failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                st.error("Zoom görüşü yaradıla bilmədi")
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"Zoom görüş yaratma xətası: {str(e)}")
            raise