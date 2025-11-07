# Backend API Updates - New Features

## New Authentication

### Auth Middleware (`auth.py`)

**Usage:**
```python
from auth import require_auth, optional_auth

@app.route('/protected')
@require_auth
def protected_route():
    user_id = request.user_id
    return jsonify({"user": request.user})

@app.route('/optional')
@optional_auth
def optional_route():
    user_id = getattr(request, 'user_id', 'anonymous')
    return jsonify({"user_id": user_id})
```

**Configuration:**
Set `CLERK_DOMAIN` in `.env`:
```
CLERK_DOMAIN=your-app.clerk.accounts.dev
```

---

## New Services

### 1. Web Scraper (`services/web_scraper.py`)

**Features:**
- Robots.txt validation before scraping
- HTML content extraction with BeautifulSoup
- Headings, paragraphs, metadata extraction
- Multiple URL support
- Conservative fail-safe approach

**Usage:**
```python
from services.web_scraper import WebScraper

scraper = WebScraper(user_agent="MyBot/1.0")

# Scrape single URL
result = scraper.scrape_single_url("https://example.com")
if result['success']:
    print(result['title'])
    print(result['text'])
    print(result['headings'])

# Scrape multiple URLs
results = scraper.scrape_urls([
    "https://example.com/page1",
    "https://example.com/page2"
])

# Get combined text
combined = scraper.get_combined_text(results)
```

**Response Format:**
```python
{
    "success": True,
    "url": "https://example.com",
    "title": "Page Title",
    "text": "Full text content...",
    "headings": [
        {"level": "h1", "text": "Main Heading"},
        {"level": "h2", "text": "Subheading"}
    ],
    "metadata": {
        "description": "Meta description",
        "keywords": "meta, keywords",
        "og_title": "Open Graph title"
    }
}
```

### 2. Wikipedia Service (`services/wikipedia_service.py`)

**Features:**
- Keyword extraction from queries
- Wikipedia article search
- Content extraction with sections
- Multiple article combination
- Smart content truncation

**Usage:**
```python
from services.wikipedia_service import WikipediaService

wiki = WikipediaService(lang='en')

# Search and get content
result = wiki.get_content_for_query(
    "Artificial Intelligence",
    max_articles=3
)

if result['success']:
    print(f"Found {result['num_articles']} articles")
    print(result['combined_text'])
    
    for article in result['articles']:
        print(f"- {article['title']}: {article['url']}")
```

**Response Format:**
```python
{
    "success": True,
    "source": "wikipedia",
    "query": "Artificial Intelligence",
    "num_articles": 3,
    "articles": [
        {
            "title": "Artificial Intelligence",
            "url": "https://en.wikipedia.org/wiki/...",
            "summary": "AI is...",
            "content": "Full article content...",
            "sections": [
                {"title": "Introduction", "content": "..."},
                {"title": "History", "content": "..."}
            ]
        }
    ],
    "combined_text": "Combined content from all articles..."
}
```

---

## Updated Generate Endpoint

### New Request Format

```json
{
  "topic": "Machine Learning Applications",
  "urls": [
    "https://example.com/ml-article",
    "https://another-site.com/ml-guide"
  ],
  "num_slides": 7,
  "theme": "modern",
  "brand_colors": ["#1A73E8"],
  "source_text": "Additional context...",
  "ai_provider": "groq"
}
```

### New Response Format

```json
{
  "ppt_id": "uuid-here",
  "slides": [...],
  "download_url": "/api/v1/download/uuid",
  "content_sources": [
    {
      "type": "web_scraping",
      "details": [
        "https://example.com/ml-article",
        "https://another-site.com/ml-guide"
      ]
    },
    {
      "type": "user_provided",
      "details": []
    }
  ]
}
```

### Content Source Priority

1. **Web Scraping** (if URLs provided and allowed by robots.txt)
2. **User-provided text** (source_text field)
3. **Uploaded documents** (via /upload-source endpoint)
4. **Wikipedia** (automatic fallback if no other sources)

### Flow Logic

```python
content_sources = []

# 1. Try scraping URLs
if urls:
    scrape_results = scraper.scrape_urls(urls)
    successful = [r for r in scrape_results.values() if r['success']]
    if successful:
        content_sources.append({
            "type": "web_scraping",
            "text": scraper.get_combined_text(scrape_results)
        })

# 2. Use provided text
if source_text:
    content_sources.append({
        "type": "user_provided",
        "text": source_text
    })

# 3. Fallback to Wikipedia
if not content_sources:
    wiki_result = wiki_service.get_content_for_query(topic)
    if wiki_result['success']:
        content_sources.append({
            "type": "wikipedia",
            "text": wiki_result['combined_text']
        })

# Combine all sources
combined_content = "\n\n".join([s['text'] for s in content_sources])

# Pass to AI with context
context_topic = f"{topic}\n\nContext:\n{combined_content}"
presentation_data = ai_client.generate_presentation_structure(context_topic, num_slides)
```

---

## Testing

### Test Web Scraping

```python
# test_scraper.py
from services.web_scraper import WebScraper

scraper = WebScraper()
result = scraper.scrape_single_url("https://en.wikipedia.org/wiki/Python_(programming_language)")

print(f"Success: {result['success']}")
print(f"Title: {result.get('title')}")
print(f"Text length: {len(result.get('text', ''))}")
print(f"Headings: {len(result.get('headings', []))}")
```

### Test Wikipedia Service

```python
# test_wikipedia.py
from services.wikipedia_service import WikipediaService

wiki = WikipediaService()
result = wiki.get_content_for_query("Machine Learning", max_articles=2)

print(f"Success: {result['success']}")
print(f"Articles found: {result.get('num_articles')}")
print(f"Combined text length: {len(result.get('combined_text', ''))}")

for article in result.get('articles', []):
    print(f"- {article['title']}")
```

### Test Full Generation Flow

```bash
curl -X POST http://localhost:5000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Climate Change",
    "urls": ["https://climate.nasa.gov/"],
    "num_slides": 5,
    "theme": "professional"
  }'
```

---

## Error Handling

### Robots.txt Blocked

```python
{
    "url": "https://example.com",
    "success": False,
    "error": "Scraping not allowed: robots.txt blocks access",
    "robots_txt_blocked": True
}
```

### Wikipedia Not Found

```python
{
    "success": False,
    "error": "No Wikipedia articles found for query"
}
```

### No Content Sources

If all scraping fails and Wikipedia has no results, system uses topic only for generation.

---

## Performance Notes

- **Web Scraping:** 1-3 seconds per URL
- **Wikipedia:** 1-2 seconds for 3 articles
- **Combined:** ~5-10 seconds for full content gathering
- **AI Generation:** 5-15 seconds (depends on provider)

**Total time:** ~10-25 seconds for complete PPT generation

---

## Security Considerations

### Robots.txt Compliance
- Always checks before scraping
- Respects crawl delays
- Identifies bot with User-Agent
- Fails safely (denies if unclear)

### Rate Limiting
- BeautifulSoup: No built-in rate limiting
- Wikipedia API: Respectful of Wikipedia policies
- Recommended: Add request throttling for production

### Content Validation
- Validates URLs before scraping
- Sanitizes extracted content
- Limits content length to avoid token overflow
- Removes script/style tags

---

## Configuration Options

### Web Scraper

```python
scraper = WebScraper(
    user_agent="AI-PPT-Generator-Bot/1.0"  # Customize user agent
)
```

### Wikipedia Service

```python
wiki = WikipediaService(
    lang='en'  # Change language ('es', 'fr', 'de', etc.)
)

result = wiki.get_content_for_query(
    query="Your topic",
    max_articles=3  # Number of articles to fetch
)
```

---

## Maintenance Tasks

### Update Dependencies

```bash
pip install --upgrade beautifulsoup4 lxml wikipedia pyjwt cryptography
```

### Clear Temp Images

```python
import os
import shutil

if os.path.exists('temp_images'):
    shutil.rmtree('temp_images')
os.makedirs('temp_images')
```

### Monitor Logs

```bash
tail -f logs/app.log | grep -E "(scraping|wikipedia)"
```

---

## Future Enhancements

- [ ] Add caching for Wikipedia results
- [ ] Implement request throttling
- [ ] Add support for more content sources (arXiv, Medium, etc.)
- [ ] PDF export of scraped content
- [ ] Content quality scoring
- [ ] Multi-language support
- [ ] Advanced content filtering
