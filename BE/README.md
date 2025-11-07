# SlideX - Backend

A production-ready Flask REST API backend for generating AI-powered PowerPoint presentations.

## Features

- 🧠 **AI Content Generation**: Uses Claude or Groq API to generate presentation outlines and content
- 🖼️ **Image Integration**: Fetches royalty-free images from Pixabay API
- 🎨 **Multiple Themes**: Support for 7 different presentation themes
- 📊 **Data Visualization**: Auto-generate charts from CSV/structured data
- ✏️ **Live Editing**: Update slides and replace images dynamically
- 🔒 **Robots.txt Compliance**: Checks robots.txt before any web scraping
- 📄 **Document Upload**: Extract content from PDF and DOCX files
- 💾 **In-Memory Storage**: Fast temporary storage (easily swappable with DB)
- 📝 **Comprehensive Logging**: File and console logging for debugging

## Tech Stack

- **Flask 3.0** - Web framework
- **python-pptx** - PowerPoint generation
- **Anthropic Claude API** - Primary AI content generation
- **Groq API** - Alternative AI content generation
- **Pixabay API** - Royalty-free image search
- **PyPDF2 & python-docx** - Document parsing

## Prerequisites

- Python 3.11+
- pip or poetry for dependency management
- API Keys:
  - Claude API key (from Anthropic) OR Groq API key
  - Pixabay API key (optional, for images)

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` file:

```bash
cp .env.example .env
```

4. Add your API keys to `.env`:

```env
CLAUDE_API_KEY=your_claude_api_key_here
# OR
GROQ_API_KEY=your_groq_api_key_here

PIXABAY_API_KEY=your_pixabay_api_key_here
```

## Running the Server

Development mode:

```bash
python app.py
```

Production mode (with gunicorn):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The server will run on `http://localhost:5000`

## API Endpoints

### 1. Generate Presentation

**POST** `/api/v1/generate`

Generate a new PowerPoint presentation from a topic or uploaded document.

**Request Body:**

```json
{
  "topic": "The Future of Artificial Intelligence",
  "theme": "modern",
  "slide_count": 7,
  "brand_colors": ["#1A73E8", "#FF6B6B"],
  "source_text": "Optional long text content...",
  "data": {
    "categories": ["Q1", "Q2", "Q3"],
    "values": [100, 150, 200]
  }
}
```

**Parameters:**

- `topic` (string): Presentation topic (required if no source_text)
- `source_text` (string): Raw text content (required if no topic)
- `theme` (string): Theme name - `modern`, `dark`, `professional`, `business`, `academic`, `minimal`, `creative` (default: `modern`)
- `slide_count` (integer): Number of slides (default: 5)
- `brand_colors` (array): Hex color codes for branding (optional)
- `data` (object): Chart data with categories and values (optional)

**Response:**

```json
{
  "ppt_id": "550e8400-e29b-41d4-a716-446655440000",
  "slides": [
    {
      "index": 0,
      "title": "Introduction to AI",
      "bullets": ["Point 1", "Point 2", "Point 3"],
      "speaker_notes": "Detailed notes for presenter...",
      "layout": "content",
      "suggested_images": [
        {
          "id": "12345",
          "preview_url": "https://...",
          "keywords": "artificial intelligence"
        }
      ]
    }
  ],
  "download_url": "/api/v1/download/550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Climate Change Solutions",
    "theme": "professional",
    "slide_count": 5
  }'
```

---

### 2. Get Presentation Metadata

**GET** `/api/v1/ppt/<ppt_id>`

Retrieve metadata for a generated presentation (without binary data).

**Response:**

```json
{
  "ppt_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Climate Change Solutions",
  "theme": "professional",
  "slides": [...],
  "generated_at": "2025-11-07T10:30:00",
  "download_url": "/api/v1/download/550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL Example:**

```bash
curl http://localhost:5000/api/v1/ppt/550e8400-e29b-41d4-a716-446655440000
```

---

### 3. Download Presentation

**GET** `/api/v1/download/<ppt_id>`

Download the PowerPoint file as a `.pptx` file.

**Response:** Binary PPTX file with `Content-Disposition: attachment`

**cURL Example:**

```bash
curl -O -J http://localhost:5000/api/v1/download/550e8400-e29b-41d4-a716-446655440000
```

---

### 4. Update Slide Content

**PATCH** `/api/v1/ppt/<ppt_id>/slide/<slide_index>`

Update the content of a specific slide.

**Request Body:**

```json
{
  "title": "Updated Slide Title",
  "bullets": ["New point 1", "New point 2"],
  "speaker_notes": "Updated notes"
}
```

**Response:** Updated PPT metadata (same format as GET /ppt/<id>)

**cURL Example:**

```bash
curl -X PATCH http://localhost:5000/api/v1/ppt/550e8400.../slide/0 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Introduction",
    "bullets": ["New intro point"]
  }'
```

---

### 5. Replace Slide Image

**POST** `/api/v1/replace-image`

Replace the image on a slide with a different Pixabay image.

**Request Body:**

```json
{
  "ppt_id": "550e8400-e29b-41d4-a716-446655440000",
  "slide_index": 0,
  "pixabay_image_id": "67890"
}
```

**Response:** Updated PPT metadata

**cURL Example:**

```bash
curl -X POST http://localhost:5000/api/v1/replace-image \
  -H "Content-Type: application/json" \
  -d '{
    "ppt_id": "550e8400...",
    "slide_index": 2,
    "pixabay_image_id": "123456"
  }'
```

---

### 6. Search Pixabay Images

**GET** `/api/v1/pixabay/search?q=<query>&page=<page>&per_page=<count>`

Proxy endpoint to search Pixabay for images.

**Query Parameters:**

- `q` (string): Search query (required)
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Results per page (default: 20, max: 200)

**Response:**

```json
{
  "images": [
    {
      "id": "12345",
      "previewURL": "https://...",
      "webformatURL": "https://...",
      "largeImageURL": "https://...",
      "tags": "nature, forest, trees",
      "user": "photographer_name",
      "pageURL": "https://pixabay.com/..."
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

**cURL Example:**

```bash
curl "http://localhost:5000/api/v1/pixabay/search?q=nature&page=1"
```

---

### 7. Upload Source Document

**POST** `/api/v1/upload-source`

Upload a PDF or DOCX file to extract text content for presentation generation.

**Form Data:**

- `file`: PDF or DOCX file (multipart/form-data)

**Response:**

```json
{
  "source_id": "uuid",
  "text": "Extracted text content from the document...",
  "filename": "document.pdf"
}
```

**cURL Example:**

```bash
curl -X POST http://localhost:5000/api/v1/upload-source \
  -F "file=@/path/to/document.pdf"
```

---

### 8. Check Robots.txt

**GET** `/api/v1/robots-check?url=<url>`

Check if a URL allows scraping based on its robots.txt file.

**Query Parameters:**

- `url` (string): URL to check (required)

**Response:**

```json
{
  "url": "https://example.com/page",
  "allowed": true,
  "message": "Scraping is allowed by robots.txt"
}
```

**cURL Example:**

```bash
curl "http://localhost:5000/api/v1/robots-check?url=https://example.com"
```

---

### 9. Delete Presentation

**DELETE** `/api/v1/ppt/<ppt_id>`

Delete a presentation from storage.

**Response:**

```json
{
  "success": true,
  "message": "Presentation deleted"
}
```

**cURL Example:**

```bash
curl -X DELETE http://localhost:5000/api/v1/ppt/550e8400-e29b-41d4-a716-446655440000
```

---

### 10. Health Check

**GET** `/api/v1/health`

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "service": "SlideX API",
  "version": "1.0.0"
}
```

## Project Structure

```
BE/
├── app.py                  # Main Flask application
├── storage.py              # In-memory storage module
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── generate.py        # POST /generate
│   ├── ppt_management.py  # GET, DELETE /ppt/<id>
│   ├── replace_image.py   # POST /replace-image
│   ├── pixabay_proxy.py   # GET /pixabay/search
│   └── upload_and_robots.py # POST /upload-source, GET /robots-check
├── services/              # Business logic
│   ├── __init__.py
│   ├── claude_client.py   # Claude API wrapper
│   ├── groq.py           # Groq API wrapper
│   ├── pixabay.py        # Pixabay API wrapper
│   ├── ppt_service.py    # PowerPoint generation
│   └── robots.py         # Robots.txt checker
├── prompts/               # AI prompt templates
│   ├── outline_generation.txt
│   ├── slide_content.txt
│   └── text_summarization.txt
├── tests/                 # Unit tests
│   ├── test_robots.py
│   └── test_ppt_generation.py
└── logs/                  # Application logs
    └── app.log
```

## Configuration

Environment variables (`.env` file):

```env
# Required: AI API Key (choose one)
CLAUDE_API_KEY=your_claude_api_key
GROQ_API_KEY=your_groq_api_key

# Required: Image API
PIXABAY_API_KEY=your_pixabay_key

# Optional: Server Configuration
PORT=5000
FLASK_ENV=development
CORS_ORIGINS=*

# Optional: AI Model Configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022
GROQ_MODEL=llama-3.3-70b-versatile
```

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=. tests/
```

Run specific test file:

```bash
pytest tests/test_robots.py -v
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error title",
  "message": "Detailed error message",
  "code": 400
}
```

HTTP Status Codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Logging

Logs are written to:

- Console (stdout) - INFO level
- `logs/app.log` - INFO level with rotation (max 10MB, 10 backups)

Log format: `[timestamp] LEVEL in module: message`

## Swapping to Database

To replace in-memory storage with a database:

1. Create a new storage implementation (e.g., `postgres_storage.py`)
2. Implement the same interface as `PPTStorage` class
3. Update imports in API modules
4. No changes needed to API endpoints

Example with SQLAlchemy:

```python
# postgres_storage.py
from sqlalchemy import create_engine
from models import PPT

class PostgresStorage:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def create(self, data):
        # SQLAlchemy insert
        pass

    def get(self, ppt_id):
        # SQLAlchemy query
        pass
    # ... implement other methods
```

## Rate Limiting

Consider adding rate limiting for production:

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/v1/generate')
@limiter.limit("10 per minute")
def generate():
    ...
```

## Security Considerations

- Always validate user inputs
- Never log API keys
- Use HTTPS in production
- Implement authentication for production use
- Set proper CORS origins (not `*`)
- Validate file uploads (size, type, content)
- Sanitize filenames

## Deployment

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t ai-ppt-backend .
docker run -p 5000:5000 --env-file .env ai-ppt-backend
```

### Using systemd

Create `/etc/systemd/system/ai-ppt-backend.service`:

```ini
[Unit]
Description=SlideX Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ai-ppt-backend
Environment="PATH=/var/www/ai-ppt-backend/venv/bin"
ExecStart=/var/www/ai-ppt-backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

## License

See main project LICENSE

## Support

For issues or questions, please open an issue in the repository.
