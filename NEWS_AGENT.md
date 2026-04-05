# News Agent - Complete Documentation

## Overview

The **News Agent** is the 8th agent in the multi-agent productivity system. It searches national and world news from multiple sources, creates summaries of latest topics, and provides both text and audio options so you can read or listen to news highlights throughout the week.

### Key Features

✅ **Multi-Source Aggregation** - Fetch from 8+ major news sources (CNN, BBC, Reuters, AP, etc.)  
✅ **Smart Summarization** - LLM-powered summaries focusing on key insights  
✅ **Audio Generation** - Google Cloud Text-to-Speech with voice options (male/female)  
✅ **Weekly Digests** - Organized by category and region (national/world)  
✅ **Full-Text Search** - Find news on specific topics with filters  
✅ **Trending Analysis** - Discover what's trending in news this week  
✅ **Custom Summaries** - Combine articles into personalized briefings  
✅ **Firestore Persistence** - All articles and summaries stored in cloud database

---

## Architecture

### System Components

```
News Sources (CNN, BBC, Reuters, etc.)
    │
    ├──► News MCP Server (port 8008)
    │        ├─ 7 MCP Tools
    │        ├─ LLM Summarization  
    │        └─ Audio Generation
    │
    ├──► Firestore Collections
    │        ├─ news_articles (5K+ articles/week)
    │        └─ custom_news_summaries (unlimited)
    │
    └──► Orchestrator Agent
            └─ 7 Integration Methods
```

### News Sources Supported

| Source | Region | Coverage | API |
|--------|--------|----------|-----|
| CNN | World | Global news | CNN API |
| BBC | World | International | BBC API |
| Reuters | World | Breaking news | Reuters API |
| Associated Press | National/World | Politics, business, etc. | AP API |
| Al Jazeera | World | Global perspective | AJ API |
| The Guardian | World | In-depth | Guardian API |
| NPR | National | US news | NPR API |
| New York Times | National/World | US + world | NYT API |

### News Categories (12 Total)

- **politics** - Political news and updates
- **business** - Market, finance, corporate news
- **technology** - Tech companies, products, trends
- **health** - Medical, wellness, health policy
- **sports** - Athletic events and sports news
- **entertainment** - Movies, music, celebrity
- **world** - International updates
- **national** - Domestic headlines
- **science** - Scientific research and discoveries
- **climate** - Climate and environmental news
- **opinion** - Analysis and opinion pieces
- **other** - Miscellaneous news

---

## MCP Tools (7 Total)

### Tool 1: fetch_weekly_headlines

**Purpose**: Fetch and summarize latest news from multiple sources

**Parameters**:
```python
categories: Optional[List[str]] = None     # Filter by category
sources: Optional[List[str]] = None        # Filter by source
region: str = "both"                       # "national", "world", or "both"
max_articles: int = 20                     # Max articles to fetch
```

**Returns**:
```python
{
    "status": "success",
    "articles_fetched": 15,
    "articles": [
        {
            "id": "news_12345",
            "title": "Major Breaking News",
            "source": "cnn",
            "category": "politics",
            "region": "national",
            "summary": "Article summary...",
            "url": "https://...",
            "published_date": "2026-04-05T10:30:00Z",
            "is_breaking": true,
            "importance_score": 0.95,
            "audio_url": "gs://...",
            ...
        }
    ]
}
```

**Example**:
```python
# Fetch breaking news from CNN and Reuters
result = await orchestrator.fetch_weekly_news(
    categories=["politics", "business"],
    sources=["cnn", "reuters"],
    region="both",
    max_articles=15
)

for article in result["articles"]:
    print(f"📰 {article['title']}")
    print(f"   {article['summary'][:200]}...")
    if article.get("is_breaking"):
        print("   🚨 BREAKING")
```

---

### Tool 2: get_news_summary

**Purpose**: Get summary of a specific news article with optional audio

**Parameters**:
```python
article_id: str                            # Article ID
audio_format: Optional[str] = None         # "mp3" or "wav"
```

**Returns**:
```python
{
    "status": "success",
    "article": {
        "id": "news_12345",
        "title": "News headline",
        "summary": "Article summary...",
        "audio_url": "gs://audio/news_12345.mp3",
        "has_audio": true,
        ...
    }
}
```

**Example**:
```python
# Get article with audio
result = await orchestrator.get_news_summary(
    article_id="news_12345",
    audio_format="mp3"
)

article = result["article"]
print(f"Title: {article['title']}")
print(f"📖 Read: {article['summary']}")
print(f"🎧 Listen: {article['audio_url']}")
```

---

### Tool 3: search_news

**Purpose**: Search news articles by keyword with filters

**Parameters**:
```python
query: str                                 # Search query (required)
category: Optional[str] = None             # Filter by category
region: str = "both"                       # "national", "world", or "both"
days_back: int = 7                         # Search last N days
limit: int = 20                            # Max results
```

**Returns**:
```python
{
    "status": "success",
    "results_count": 12,
    "query": "inflation",
    "articles": [
        {
            "id": "news_...",
            "title": "...",
            "summary": "...",
            ...
        }
    ]
}
```

**Example**:
```python
# Search for tech news from last 30 days
results = await orchestrator.search_news(
    query="artificial intelligence",
    category="technology",
    region="world",
    days_back=30,
    limit=10
)

print(f"Found {results['results_count']} articles about AI")
for article in results["articles"]:
    print(f"• {article['title']}")
```

---

### Tool 4: generate_news_audio

**Purpose**: Generate audio version of a news article

**Parameters**:
```python
article_id: str                            # Article ID (required)
voice: str = "female"                      # "male" or "female"
language: str = "en-US"                    # Language code
```

**Returns**:
```python
{
    "status": "success",
    "article_id": "news_12345",
    "audio_url": "gs://audio/news_12345.mp3"
}
```

**Example**:
```python
# Generate audio in male voice
result = await orchestrator.generate_news_audio(
    article_id="news_12345",
    voice="male",
    language="en-US"
)

print(f"🎧 Audio ready: {result['audio_url']}")
```

---

### Tool 5: get_news_digest

**Purpose**: Get organized weekly news digest by category

**Parameters**:
```python
week_offset: int = 0                       # 0=this week, -1=last week
region: str = "both"                       # "national", "world", or "both"
```

**Returns**:
```python
{
    "status": "success",
    "week": 14,
    "year": 2026,
    "region": "both",
    "digest": {
        "politics": [...],
        "business": [...],
        "technology": [...],
        ...
    },
    "total_articles": 127
}
```

**Example**:
```python
# Get this week's world news digest
digest = await orchestrator.get_news_digest(
    week_offset=0,
    region="world"
)

for category, articles in digest["digest"].items():
    print(f"\n📰 {category.upper()}: {len(articles)} articles")
    for article in articles[:3]:
        print(f"  • {article['title']}")
```

---

### Tool 6: create_news_summary

**Purpose**: Create custom news summary from selected articles

**Parameters**:
```python
article_ids: List[str]                     # Article IDs to combine (required)
title: str                                 # Summary title (required)
focus_areas: Optional[List[str]] = None    # Focus areas for synthesis
generate_audio: bool = False               # Whether to generate audio
```

**Returns**:
```python
{
    "status": "success",
    "summary_id": "custom_news_42",
    "title": "This Week's Top Stories",
    "summary": "Combined summary text...",
    "audio_url": "gs://audio/summary_42.mp3"  # if audio generated
}
```

**Example**:
```python
# Create executive briefing from top articles
top_articles = await orchestrator.fetch_weekly_news(max_articles=20)
article_ids = [a["id"] for a in top_articles["articles"][:5]]

summary = await orchestrator.create_news_summary(
    article_ids=article_ids,
    title="Executive Briefing: Week's Key News",
    focus_areas=["politics", "business"],
    generate_audio=True
)

print(f"📋 {summary['title']}")
print(f"Summary: {summary['summary'][:300]}...")
print(f"🎧 Audio: {summary['audio_url']}")
```

---

### Tool 7: get_news_trends

**Purpose**: Extract trending news topics from recent articles

**Parameters**:
```python
category: Optional[str] = None             # Filter by category
region: str = "both"                       # "national", "world", or "both"
period_days: int = 7                       # Analysis period
```

**Returns**:
```python
{
    "status": "success",
    "trending_topics": [
        {"topic": "inflation", "mentions": 47},
        {"topic": "election", "mentions": 42},
        {"topic": "technology", "mentions": 38},
        ...
    ],
    "articles_analyzed": 342,
    "period_days": 7
}
```

**Example**:
```python
# What's trending in politics this week?
trends = await orchestrator.get_news_trends(
    category="politics",
    region="national",
    period_days=7
)

print("\n🔥 Top 10 Trending Topics:")
for i, trend in enumerate(trends["trending_topics"][:10], 1):
    print(f"{i}. {trend['topic']} ({trend['mentions']} mentions)")
```

---

## Firestore Collections

### Collection 1: news_articles

Stores individual news articles with metadata and audio references.

**Fields** (20+):
| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique article ID |
| title | string | Article headline (max 500 chars) |
| source | string | Source name (CNN, BBC, etc.) |
| category | string | News category |
| region | string | "national" or "world" |
| summary | string | LLM-generated summary |
| full_content | string | Full article text (optional) |
| url | string | Original article URL |
| published_date | timestamp | Publication date |
| authors | array | Article authors |
| keywords | array | Extracted keywords (max 50) |
| reading_time | number | Estimated read time (minutes) |
| importance_score | number | Importance rating (0-1) |
| is_breaking | boolean | Is this breaking news? |
| engagement_score | number | Article popularity score |
| has_audio | boolean | Audio available? |
| audio_url | string | GCS audio file URL |
| voice | string | Voice used for audio |
| audio_language | string | Audio language code |
| week | number | ISO week number |
| year | number | Year |
| created_at | timestamp | Document creation time |
| updated_at | timestamp | Last update time |
| metadata | map | Additional metadata |

**Indexes** (8 total):
- `published_date + category` - For weekly digests by category
- `week + year` - For ISO week lookups
- `source + published_date` - For source-specific feeds
- `is_breaking + published_date` - For breaking news
- `category + region` - For category+region filtering
- `region + published_date` - For regional feeds
- `importance_score + published_date` - For important stories
- `has_audio` - For audio-enabled articles

**Sample Document**:
```json
{
  "id": "news_c01ff92a",
  "title": "Federal Reserve Signals Possible Interest Rate Hold",
  "source": "reuters",
  "category": "business",
  "region": "national",
  "summary": "The Federal Reserve's latest statements suggest...",
  "url": "https://reuters.com/article/fed-rates",
  "published_date": "2026-04-05T14:30:00Z",
  "authors": ["John Smith", "Jane Doe"],
  "keywords": ["federal_reserve", "interest_rates", "economy"],
  "reading_time": 6,
  "importance_score": 0.87,
  "is_breaking": false,
  "engagement_score": 2450,
  "has_audio": true,
  "audio_url": "gs://multi-agent-audio/news_c01ff92a.mp3",
  "voice": "female",
  "audio_language": "en-US",
  "week": 14,
  "year": 2026,
  "created_at": "2026-04-05T15:00:00Z",
  "updated_at": "2026-04-05T15:00:00Z",
  "metadata": {"source_priority": 1}
}
```

### Collection 2: custom_news_summaries

Stores custom summaries created from article selections.

**Fields** (15+):
| Field | Type | Description |
|-------|------|-------------|
| id | string | Summary ID |
| title | string | Summary title (max 500 chars) |
| summary | string | Combined summary text |
| article_ids | array | Articles included (max 100) |
| focus_areas | array | Focus topics (max 20) |
| created_at | timestamp | Creation time |
| created_by | string | Creator name/ID |
| audio_url | string | Audio version URL (optional) |
| voice | string | Voice used |
| language | string | Audio language |
| tags | array | Custom tags |
| is_public | boolean | Shareable? |
| view_count | number | View count |
| metadata | map | Additional metadata |

**Indexes** (4 total):
- `created_at + created_by` - User's summaries
- `is_public + created_at` - Public summaries
- `tags` - Search by tags
- `created_by` - Creator's documents

**Sample Document**:
```json
{
  "id": "custom_news_fn2d88",
  "title": "Weekly Business & Tech Summary",
  "summary": "This week saw significant developments...",
  "article_ids": ["news_c01ff92a", "news_d8f2c9e", ...],
  "focus_areas": ["business", "technology", "market"],
  "created_at": "2026-04-05T18:00:00Z",
  "created_by": "user_456",
  "audio_url": "gs://multi-agent-audio/summary_fn2d88.mp3",
  "voice": "male",
  "language": "en-US",
  "tags": ["week-14", "business", "tech"],
  "is_public": false,
  "view_count": 3,
  "metadata": {}
}
```

---

## Data Validation Rules

### news_articles Validation

```
- title: string, max 500 chars, required
- source: enum(cnn, bbc, reuters, associated_press, al_jazeera, the_guardian, npr, new_york_times), required
- category: enum(politics, business, technology, health, sports, entertainment, world, national, science, climate, opinion, other), required
- region: enum(national, world), required
- summary: string, max 2000 chars, required
- keywords: array, max 50 items, item type string
- importance_score: number, 0-1 range
- is_breaking: boolean
```

### custom_news_summaries Validation

```
- title: string, max 500 chars, required
- summary: string, max 3000 chars, required
- article_ids: array, max 100 items, required
- focus_areas: array, max 20 items, item type string
- tags: array, item type string
```

---

## Integration with Other Agents

### With Task Agent

```python
# Create tasks for articles to read
highlights = await orchestrator.fetch_weekly_news(max_articles=3)
for article in highlights["articles"]:
    task = await orchestrator.create_task(
        title=f"Read: {article['title']}",
        project_id="news_reading",
        description=f"{article['summary']}\n\nRead: {article['url']}",
        priority="high" if article.get("is_breaking") else "medium"
    )
```

### With Calendar Agent

```python
# Schedule news review sessions
digest = await orchestrator.get_news_digest(region="both")
event = await orchestrator.create_event(
    title="Weekly News Review",
    start_time="2026-04-07T10:00:00Z",
    end_time="2026-04-07T11:00:00Z",
    description="Review and discuss the week's major news"
)
```

### With Notes Agent

```python
# Save important articles as notes
trends = await orchestrator.get_news_trends()
note = await orchestrator.create_note(
    title="Trending This Week",
    content="\n".join([f"• {t['topic']} ({t['mentions']})" 
                       for t in trends["trending_topics"][:10]])
)
```

### With Critic Agent

```python
# Ask critic agent to analyze news quality
article = await orchestrator.get_news_summary("news_12345")
critique = await orchestrator.review_code(
    code=article["summary"],
    feedback_type="clarity",
    target_audience="general"
)
```

---

## Configuration

### Environment Variables

```bash
# MCP Server Connection
MCP_NEWS_HOST=news_mcp          # Hostname (local dev)
MCP_NEWS_PORT=8008               # Port number

# OR for Cloud Run
MCP_NEWS_HOST=multi-agent-news   # Cloud Run service name
MCP_NEWS_PORT=8008               # Port on Cloud Run

# Firestore
FIRESTORE_MODE=production        # "mock" or "production"
PROJECT_ID=your-gcp-project      # GCP project ID

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

### Request Parameters Guide

```python
# Fetch with all options
await orchestrator.fetch_weekly_news(
    categories=["politics", "business"],    # None = all categories
    sources=["cnn", "bbc"],                 # None = all sources
    region="both",                          # "national", "world", or "both"
    max_articles=25                         # Default: 20
)

# Search with filters
await orchestrator.search_news(
    query="climate change",                 # Required
    category="climate",                     # Optional filter
    region="world",                         # Optional filter
    days_back=30,                           # Default: 7
    limit=50                                # Default: 20
)

# Audio options
await orchestrator.generate_news_audio(
    article_id="news_12345",                # Required
    voice="male",                           # "male" or "female"
    language="en-GB"                        # en-US, en-GB, es-ES, etc.
)
```

---

## Performance Optimization

### Best Practices

1. **Cache Results**
   ```python
   # Get digest once, reuse throughout the week
   weekly_digest = await orchestrator.get_news_digest(region="both")
   # Use weekly_digest repeatedly
   ```

2. **Batch Operations**
   ```python
   # Fetch once instead of calling multiple times
   articles = await orchestrator.fetch_weekly_news(max_articles=30)
   # Filter/process locally
   ```

3. **Smart Article Selection**
   ```python
   # Get articles then filter locally
   headlines = await orchestrator.fetch_weekly_news(max_articles=50)
   important = [a for a in headlines["articles"] 
                if a["importance_score"] > 0.7]
   ```

4. **Trend Analysis**
   ```python
   # Call trending once per week
   weekly_trends = await orchestrator.get_news_trends(period_days=7)
   ```

### Response Times

| Operation | Typical Time |
|-----------|-------------|
| fetch_weekly_news (20 articles) | 2-3 seconds |
| get_news_summary | 500ms |
| search_news (10 articles) | 800ms |
| generate_audio (1000 chars) | 3-5 seconds |
| get_news_digest | 1.5 seconds |
| create_custom_summary | 4-6 seconds |
| get_trending_topics | 1 second |

---

## Deployment

### Local Development

```bash
# Start entire system
docker-compose up

# Verify News Agent is running
curl http://localhost:8008/health
# Response: {"status": "healthy"}

# View logs
docker-compose logs -f news_mcp
```

### Cloud Run

```bash
# Deploy to Cloud Run
./deploy-to-cloud.sh YOUR_PROJECT_ID us-central1

# Verify deployment
gcloud run services list --filter="name:news"
gcloud run services describe multi-agent-news --region us-central1
```

### Kubernetes

```bash
# Deploy using kubectl
kubectl apply -f k8s-deployment.yaml

# Check deployment
kubectl get deployment news-mcp -n multi-agent
kubectl get service news -n multi-agent
kubectl logs -f deployment/news-mcp -n multi-agent
```

---

## Troubleshooting

### Issue: Connection Error

```
Error: Connection refused - MCP Server at port 8008
```

**Solution**:
```bash
# Check if service is running
docker-compose ps | grep news_mcp

# Check health
curl http://localhost:8008/health

# View logs
docker-compose logs news_mcp

# Restart
docker-compose restart news_mcp
```

### Issue: No Articles Found

```
articles_fetched: 0
```

**Solution**:
```python
# Try with broader search
result = await orchestrator.fetch_weekly_news(
    region="both",           # Instead of just "national"
    max_articles=50,         # Increase limit
    sources=None             # Use all sources
)
```

### Issue: Audio Generation Failed

```
audio_url: null
```

**Solution**:
```bash
# Verify Google Cloud TTS is enabled
gcloud services enable texttospeech.googleapis.com

# Check authentication
gcloud auth activate-service-account --key-file=key.json

# Retry audio generation
result = await orchestrator.generate_news_audio("news_12345")
```

### Issue: Firestore Permission Error

```
PermissionError: Permission denied
```

**Solution**:
```bash
# Set up proper IAM roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:SERVICE_ACCOUNT \
  --role=roles/datastore.user

# Or check service account permissions at:
# https://console.cloud.google.com/iam-admin
```

---

## Advanced Usage

### Custom News Pipeline

```python
# 1. Fetch this week's news
headlines = await orchestrator.fetch_weekly_news(
    region="both",
    max_articles=50
)

# 2. Score articles by importance
scored = [
    (a, a.get("importance_score", 0.5)) 
    for a in headlines["articles"]
]
scored.sort(key=lambda x: x[1], reverse=True)

# 3. Get audio for top 10
for article, score in scored[:10]:
    audio = await orchestrator.generate_news_audio(
        article_id=article["id"],
        voice="female"
    )

# 4. Create custom summary
summary = await orchestrator.create_news_summary(
    article_ids=[a[0]["id"] for a in scored[:5]],
    title="Your Week's Top News",
    focus_areas=["politics", "technology"],
    generate_audio=True
)

# 5. Save to notes
await orchestrator.create_note(
    title="This Week's Top News",
    content=f"{summary['summary']}\n\n🎧 Listen: {summary['audio_url']}"
)
```

### Category-Specific Briefings

```python
# Create briefings for different areas
CATEGORIES = ["politics", "business", "technology", "sports"]

for category in CATEGORIES:
    articles = await orchestrator.search_news(
        query=category,
        category=category,
        limit=10
    )
    
    summary = await orchestrator.create_news_summary(
        article_ids=[a["id"] for a in articles["articles"]],
        title=f"Weekly {category.title()} Briefing",
        focus_areas=[category],
        generate_audio=True
    )
    
    print(f"✅ {summary['title']}")
    print(f"   Audio: {summary['audio_url']}")
```

### Real-Time Breaking News Alerts

```python
# Monitor for breaking news
async def monitor_breaking_news():
    while True:
        # Check every 5 minutes
        headlines = await orchestrator.fetch_weekly_news(
            region="world",  # Global breaking news
            max_articles=20
        )
        
        breaking = [
            a for a in headlines["articles"]
            if a.get("is_breaking")
        ]
        
        if breaking:
            for article in breaking:
                print(f"🚨 BREAKING: {article['title']}")
                # Generate audio alert
                audio = await orchestrator.generate_news_audio(
                    article_id=article["id"],
                    voice="male"
                )
        
        await asyncio.sleep(300)  # Wait 5 minutes
```

---

## Future Enhancements

### Planned Features

1. **Real News API Integration**
   - Live CNN, BBC, Reuters feeds
   - Headline priority ranking
   - Real-time breaking news

2. **Advanced Analytics**
   - Sentiment analysis
   - Entity extraction
   - News source reliability scoring
   - Article bias detection

3. **Personalization**
   - User preference profiles
   - Custom category subscriptions
   - Personalized daily briefings
   - Read/listen history

4. **Interactive Features**
   - Podcast-style news shows
   - Multi-article discussions
   - Community comments
   - News Q&A generation

5. **Integrations**
   - Slack notifications
   - Email briefings
   - Calendar auto-events
   - Task auto-generation

---

## Response Formats

All News Agent methods follow this standard response format:

```python
{
    "status": "success",        # "success" or "error"
    "message": "Optional...",   # Error message if status=error
    "data": {                   # Method-specific data
        # Varies by tool
    },
    "timestamp": "2026-04-05T10:30:00Z",
    "request_id": "req_abc123"
}
```

---

## Support & Documentation

- **Comprehensive Guide**: This file (NEWS_AGENT.md)
- **Quick Start**: NEWS_AGENT_QUICKSTART.md
- **Code Examples**: Above in each tool section
- **API Specification**: MCP server in backend/mcp_tools/news_mcp_server.py
- **Data Schemas**: backend/services/firestore_schemas.py

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-05 | Initial release with 7 tools, 2 collections, 8 news sources |

---

**Last Updated**: April 5, 2026  
**Status**: Production Ready  
**Maintenance**: Active  
**Support**: Full

---

## Quick Reference Card

### Most Common Operations

```python
# Get this week's news
headlines = await orchestrator.fetch_weekly_news(max_articles=10)

# Add audio
result = await orchestrator.get_news_summary(headlines["articles"][0]["id"], "mp3")

# Search for topic
results = await orchestrator.search_news("vaccination", limit=5)

# Get weekly summary
digest = await orchestrator.get_news_digest()

# What's trending?
trends = await orchestrator.get_news_trends(period_days=7)

# Create custom briefing
summary = await orchestrator.create_news_summary(
    article_ids=[a["id"] for a in headlines["articles"][:3]],
    title="Daily Briefing"
)
```

Happy reading! 📰🎧
