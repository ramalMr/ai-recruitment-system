# AI Recruitment System

## Project Structure

```
ai-recruitment-system/
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── main.py               # Main application entry point
├── README.md             # Project documentation
│
├── src/                  # Source code directory
│   ├── __init__.py
│   │
│   ├── config/          # Configuration files
│   │   ├── __init__.py
│   │   ├── constants.py   # UI texts and role requirements
│   │   └── settings.py    # App settings and configurations
│   │
│   ├── core/           # Core functionality
│   │   ├── __init__.py
│   │   ├── groq_agent.py      # Groq AI integration
│   │   ├── email_handler.py    # Email handling
│   │   └── zoom_handler.py     # Zoom meetings integration
│   │
│   ├── utils/          # Utility functions
│   │   ├── __init__.py
│   │   ├── pdf_processor.py    # PDF processing utilities
│   │   └── session.py          # Session management
│   │
│   └── ui/             # UI components
│       ├── __init__.py
│       └── components.py        # Streamlit UI components
│
├── tests/              # Test files
│   ├── __init__.py
│   ├── test_groq_agent.py
│   ├── test_email_handler.py
│   └── test_zoom_handler.py
│
├── docs/               # Documentation
│   ├── images/         # Documentation images
│   └── api/            # API documentation
│
└── logs/              # Log files
    └── app.log        # Application logs
```

## System Requirements

### Required Software
- Python 3.8 or higher
- Tesseract OCR
- PDF2Image dependencies (poppler)

### Installation on Different OS

#### Windows
```bash
# Install Tesseract OCR
winget install tesseract-ocr

# Install Poppler
winget install poppler

# Add to PATH
# Add these paths to your system environment variables:
# C:\Program Files\Tesseract-OCR
# C:\Program Files\poppler\bin
```

#### macOS
```bash
# Using Homebrew
brew install tesseract
brew install poppler
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

## Environment Variables

Create a `.env` file in the root directory:

```env
# Email Configuration
EMAIL_ADDRESS="your-email@gmail.com"
EMAIL_PASSWORD="your-app-password"

# Groq AI Configuration
GROQ_API_KEY="your-groq-api-key"

# Zoom Configuration
ZOOM_ACCOUNT_ID="your-zoom-account-id"
ZOOM_CLIENT_ID="your-zoom-client-id"
ZOOM_CLIENT_SECRET="your-zoom-client-secret"

# Company Information
COMPANY_NAME="your-company-name"

# System Configuration
TESSERACT_PATH="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Windows only
POPPLER_PATH="C:\\Program Files\\poppler\\bin"  # Windows only
```

## Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/ramalMr/ai-recruitment-system.git
cd ai-recruitment-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Verify installations:
```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
python -c "from pdf2image import pdfinfo_from_path; print('PDF2Image OK')"
```

## Dependencies List

```txt
# requirements.txt
streamlit==1.28.0
python-dotenv==1.0.0
groq==0.3.0
pdf2image==1.16.3
pytesseract==0.3.10
python-docx==0.8.11
Pillow==10.0.0
pytz==2023.3
httpx==0.24.1
python-jose==3.3.0
pytest==7.4.0
pytest-asyncio==0.21.1
```

## Configuration Files

### `src/config/constants.py`
```python
UI_TEXTS = {
    "title": "AI Recruitment System",
    # ... other UI texts
}

ROLE_REQUIREMENTS = {
    "Software Engineer": "...",
    "Data Scientist": "...",
    # ... other role requirements
}
```

### `src/config/settings.py`
```python
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"

# Create necessary directories
LOGS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# App settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = ['.pdf']
```

## Database Schema

While this version doesn't use a database, here's the proposed schema for future implementation:

```sql
-- Future Database Schema
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    resume_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    zoom_meeting_id VARCHAR(255),
    scheduled_at TIMESTAMP,
    status VARCHAR(50)
);
```

## Security Considerations

1. API Key Storage:
   - All sensitive data stored in `.env`
   - Not committed to version control
   - Different keys for development/production

2. File Security:
   - Temporary file cleanup
   - Size limitations
   - Extension validation

3. Email Security:
   - TLS encryption
   - App-specific passwords
   - Rate limiting

## Common Issues & Solutions

1. Tesseract Not Found:
```bash
# Windows
set TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"

# Linux/Mac
export TESSERACT_PATH=/usr/bin/tesseract
```

2. PDF Processing Errors:
```bash
# Windows
set POPPLER_PATH="C:\Program Files\poppler\bin"

# Linux/Mac
# Usually works out of the box
```

3. SMTP Authentication:
   - Enable 2FA in Gmail
   - Generate App Password
   - Use App Password instead of regular password

## Future Improvements

1. Database Integration
   - PostgreSQL for data persistence
   - Redis for caching

2. AI Enhancements
   - Multiple AI model support
   - Custom training capabilities

3. UI/UX Improvements
   - Dark mode
   - Mobile responsiveness
   - Real-time updates

