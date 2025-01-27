import os
from groq import Groq
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqAgent:
    def __init__(self, api_key: str = None):
        """Initialize Groq agent with API key"""
        load_dotenv()
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY tapılmadı!")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Groq-un təklif etdiyi model

    async def analyze_resume(self, resume_text: str, role: str) -> Dict:
        """CV-ni təhlil edir və nəticəni qaytarır"""
        try:
            prompt = f"""
            Aşağıdakı CV-ni təhlil et və {role} vəzifəsi üçün uyğunluğunu qiymətləndir.
            
            CV Mətni:
            {resume_text}
            
            Aşağıdakı JSON formatında cavab ver:
            {{
                "təhlil": "CV-nin ətraflı təhlili",
                "güclü_tərəflər": ["güclü tərəflərin siyahısı"],
                "zəif_tərəflər": ["inkişaf tələb edən sahələr"],
                "uyğunluq_faizi": "0-100 arası rəqəm",
                "qərar": "qəbul" ya "rədd",
                "məsləhətlər": ["inkişaf üçün məsləhətlər"]
            }}
            """
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sən HR və texniki mütəxəssislərdən ibarət komandanın üzvüsən."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.5,
                max_tokens=2000
            )
            
            response = chat_completion.choices[0].message.content
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"CV təhlili zamanı xəta: {str(e)}")
            return {
                "təhlil": "Xəta baş verdi",
                "güclü_tərəflər": [],
                "zəif_tərəflər": [],
                "uyğunluq_faizi": "0",
                "qərar": "rədd",
                "məsləhətlər": ["Sistemdə texniki problem yarandı. Zəhmət olmasa daha sonra yenidən cəhd edin."]
            }

    async def extract_email(self, text: str) -> Optional[str]:
        """Mətndən email ünvanını çıxarır"""
        try:
            prompt = f"""
            Aşağıdakı mətndən email ünvanını tap və qaytar.
            Yalnız email ünvanını qaytar, əlavə mətn lazım deyil.
            Əgər email tapılmasa, boş string qaytar.

            Mətn:
            {text}
            """
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=100
            )
            
            email = chat_completion.choices[0].message.content.strip()
            return email if '@' in email else None
            
        except Exception as e:
            logger.error(f"Email çıxarılması zamanı xəta: {str(e)}")
            return None