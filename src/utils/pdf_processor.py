import streamlit as st
from typing import Optional
import tempfile
import os
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

class PDFProcessor:
    def __init__(self):
       
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def extract_text(self, pdf_file) -> Optional[str]:
        try:
            images = convert_from_bytes(pdf_file.read())
            
            text = ""
            for image in images:
             
                text += pytesseract.image_to_string(image, lang='eng') + "\n"
            
            return text.strip()
            
        except Exception as e:
            st.error(f"PDF emalı zamanı xəta: {str(e)}")
            return None

    def validate_pdf(self, file) -> bool:
        if file is None:
            return False
        try:
            convert_from_bytes(file.read())
            file.seek(0)  
            return True
        except:
            return False

    def save_temp_pdf(self, pdf_file) -> Optional[str]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                return tmp_file.name
        except Exception as e:
            st.error(f"Müvəqqəti fayl yaradılması xətası: {str(e)}")
            return None

    def get_pdf_preview(self, pdf_file):
        """PDF-in ilk səhifəsinin görüntüsünü qaytarır"""
        try:
            images = convert_from_bytes(
                pdf_file.getvalue(),
                first_page=1,
                last_page=1
            )
            
            if images:
             
                img = images[0]
                img.thumbnail((800, 800))
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                return img_byte_arr
                
        except Exception as e:
            st.error(f"PDF görüntüsü yaradılarkən xəta: {str(e)}")
            return None