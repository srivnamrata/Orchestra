# 📰 News Agent Quick Start Guide

## Getting Started

### 1. Start the System

**Local Development:**
```bash
cd d:\MultiAgent-Productivity
docker-compose up
```

**Cloud Run:**
```bash
./deploy-to-cloud.sh YOUR_PROJECT_ID us-central1
```

### 2. Verify News Agent is Running

```bash
curl http://localhost:8008/health
# Response: {"status": "healthy"}
```

---

## Common Use Cases

### Use Case 1: Get Weekly News Headlines

**Goal**: Know what happened this week in national and world news

```python
from backend.agents.orchestrator_agent_mcp import OrchestratorAgentMCP
from backend.services.llm_service import LLMService
from backend.services.pubsub_service import PubSubService

# Initialize
llm = LLMService()
pubsub = PubSubService()
orchestrator = OrchestratorAgentMCP(llm, pubsub)
await orchestrator.initialize()

# Get this week's headlines
result = await orchestrator.fetch_weekly_news(
    region="both",
    max_articles=15
)

# Display results
for article in result["articles"]:
    print(f"\n📰 {article['title']}")
    print(f"   From: {article['source'].upper()}")
    print(f"   Category: {article['category']}")
    print(f"   Summary: {article['summary'][:200]}...")
    if article.get("is_breaking"):
        print(f"   🚨 BREAKING NEWS")
    print(f"   Read: {article['url']}")
```

**Output**:
```
📰 Federal Reserve Signals Possible Interest Rate Hold
   From: REUTERS
   Category: business
   Summary: The Federal Reserve's latest statements...
   Read: https://example.com/article1

📰 New Climate Report Released
   From: BBC
   Category: climate
   Summary: Scientists release findings on climate...
   Read: https://example.com/article2
```

---

### Use Case 2: Find News on Specific Topic

**Goal**: Search for articles about a specific topic

```python
# Search for vaccine news from last 30 days
result = await orchestrator.search_news(
    query="vaccine",
    category="health",
    days_back=30,
    limit=10
)

print(f"Found {result['results_count']} articles about vaccines:")
for article in result["articles"]:
    print(f"• {article['title']}")
    print(f"  {article['summary'][:150]}...")
```

---

### Use Case 3: Listen to News Article

**Goal**: Get audio version of news article to listen while commuting

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

# User can download and listen to the mp3 file
```

---

### Use Case 4: Create Daily News Briefing

**Goal**: Summarize today's top news into single briefing

```python
# Get top articles
headlines = await orchestrator.fetch_weekly_news(
    region="both",
    max_articles=20
)

# Get audio for top 5
top_5_ids = [a["id"] for a in headlines["articles"][:5]]

# Create combined summary
briefing = await orchestrator.create_news_summary(
    article_ids=top_5_ids,
    title="Today's Top 5 News",
    focus_areas=["politics", "business", "technology"],
    generate_audio=True
)

print(f"📋 {briefing['title']}")
print(f"\n{briefing['summary']}")
print(f"\n🎧 Audio Version: {briefing['audio_url']}")
```

---

### Use Case 5: Track What's Trending

**Goal**: Discover what topics are dominating news this week

```python
# Get trending topics
trends = await orchestrator.get_news_trends(
    region="world",
    period_days=7
)

print("\n🔥 Top 10 Trending Topics This Week:")
for i, trend in enumerate(trends["trending_topics"][:10], 1):
    print(f"{i}. {trend['topic']} - {trend['mentions']} mentions")

# Now search for more about top trending topic
top_topic = trends["trending_topics"][0]["topic"]
search = await orchestrator.search_news(
    query=top_topic,
    limit=5
)

print(f"\n📰 Top articles about {top_topic}:")
for article in search["articles"]:
    print(f"• {article['title']}")
```

---

### Use Case 6: Get Organized Weekly Digest

**Goal**: See all news organized by category for the week

```python
# Get complete weekly digest
digest = await orchestrator.get_news_digest(
    week_offset=0,  # 0=this week, -1=last week
    region="both"
)

print(f"\n📰 News Digest - Week {digest['week']}")
print("=" * 50)

# Show count per category
for category in ["politics", "business", "technology", "health"]:
    articles = digest["digest"].get(category, [])
    print(f"\n{category.upper()}: {len(articles)} articles")
    
    # Show top 3 in category
    for article in articles[:3]:
        print(f"  • {article['title']}")
        if article.get("is_breaking"):
            print(f"    🚨 BREAKING")
```

---

### Use Case 7: National vs World News

**Goal**: Compare national and international news

```python
# Get national news
national = await orchestrator.fetch_weekly_news(
    region="national",
    max_articles=10
)

# Get world news
world = await orchestrator.fetch_weekly_news(
    region="world",
    max_articles=10
)

print("🇺🇸 NATIONAL NEWS:")
for article in national["articles"][:5]:
    print(f"• {article['title']}")

print("\n🌍 WORLD NEWS:")
for article in world["articles"][:5]:
    print(f"• {article['title']}")
```

---

## Integration with Other Agents

### Example: News + Tasks

```python
# Get urgent news
headlines = await orchestrator.fetch_weekly_news(
    region="both",
    max_articles=10
)

# Create tasks for important articles
for article in headlines["articles"]:
    if article.get("is_breaking") or article.get("importance_score", 0) > 0.8:
        task = await orchestrator.create_task(
            title=f"Read: {article['title'][:50]}",
            project_id="news_tracking",
            description=f"{article['summary']}\n\nSource: {article['url']}",
            priority="high"
        )

print("✅ Created tasks for important news")
```

### Example: News + Calendar

```python
# Get trending topics
trends = await orchestrator.get_news_trends()

# Create event to discuss trending topics
event = await orchestrator.create_event(
    title="Weekly News Discussion",
    start_time="2026-04-07T14:00:00Z",
    end_time="2026-04-07T15:00:00Z",
    description=f"Discuss trending topics:\n" + 
                "\n".join([t["topic"] for t in trends["trending_topics"][:5]])
)

print("✅ Created news discussion event")
```

### Example: News + Notes

```python
# Create weekly news summary note
digest = await orchestrator.get_news_digest()
trends = await orchestrator.get_news_trends()

note_content = "# Week's Top News\n\n"
note_content += "## Trending Topics:\n"
for trend in trends["trending_topics"][:10]:
    note_content += f"- {trend['topic']} ({trend['mentions']})\n"

note_content += "\n## By Category:\n"
for category, articles in digest["digest"].items():
    note_content += f"- **{category}**: {len(articles)} articles\n"

note = await orchestrator.create_note(
    title="This Week's News Summary",
    content=note_content
)

print("✅ Created news summary note")
```

---

## API Examples

### Example 1: Minimal - Just Get Text

```python
# Quick summary retrieval
result = await orchestrator.fetch_weekly_news(max_articles=5)

for article in result["articles"]:
    print(f"{article['title']}\n{article['summary']}\n")
```

### Example 2: Full - Text + Audio

```python
# Get articles with audio versions
headlines = await orchestrator.fetch_weekly_news(
    category="technology",
    max_articles=3
)

for article in headlines["articles"]:
    # Generate audio
    audio = await orchestrator.generate_news_audio(
        article_id=article["id"],
        voice="female"
    )
    
    print(f"📄 {audio['article']['title']}")
    print(f"📖 Read: {audio['article']['summary'][:200]}...")
    print(f"🎧 Listen: {audio['audio_url']}")
```

### Example 3: Filter & Organize

```python
# Get all news
all_news = await orchestrator.fetch_weekly_news(max_articles=50)

# Filter by importance
important = [
    a for a in all_news["articles"]
    if a.get("importance_score", 0) > 0.7
]

# Sort by time
important.sort(key=lambda x: x.get("published_date", ""), reverse=True)

print(f"Found {len(important)} important articles")
for article in important[:10]:
    print(f"⭐ {article['title']}")
```

---

## Configuration Options

### Environment Variables

```bash
# For Cloud Run deployment
MCP_NEWS_HOST=multi-agent-news
MCP_NEWS_PORT=8008

# For local development
MCP_NEWS_HOST=localhost
MCP_NEWS_PORT=8008
```

### Method Parameters Guide

```python
# Fetch with specific options
await orchestrator.fetch_weekly_news(
    categories=["politics", "business"],  # None = all
    sources=["cnn", "reuters"],           # None = all
    region="both",                        # "national", "world", "both"
    max_articles=20                       # Default: 20
)

# Search with all options
await orchestrator.search_news(
    query="climate",                      # Required
    category="science",                   # Optional
    region="both",                        # Optional
    days_back=14,                         # Default: 7
    limit=30                              # Default: 20
)

# Audio for voice preference
await orchestrator.generate_news_audio(
    article_id="news_123",                # Required
    voice="male",                         # "male" or "female"
    language="en-GB"                      # Language code
)
```

---

## Response Formats

All News Agent methods return structured JSON:

```python
{
    "status": "success",              # or "error"
    "message": "Optional error msg",
    "data": {
        # Method-specific data
    },
    "timestamp": "2026-04-05T10:30:00Z",
    "request_id": "req_abc123"
}
```

### Success Response Example:
```json
{
    "status": "success",
    "articles_fetched": 15,
    "articles": [
        {
            "id": "news_12345",
            "title": "Breaking News",
            "source": "cnn",
            "category": "politics",
            "summary": "Article summary...",
            "is_breaking": true,
            "audio_url": "gs://...",
            "url": "https://..."
        }
    ],
    "timestamp": "2026-04-05T10:30:00Z"
}
```

---

## Error Handling

```python
try:
    result = await orchestrator.fetch_weekly_news(
        category="politics",
        max_articles=10
    )
    
    if result["status"] == "success":
        print(f"Found {result['articles_fetched']} articles")
    else:
        print(f"Error: {result.get('message')}")
        
except Exception as e:
    print(f"Failed to fetch news: {e}")
    # Handle connection errors, timeouts, etc.
```

---

## News Sources

### Major Sources

| Source | Region | Focus |
|--------|--------|-------|
| CNN | International | Breaking news |
| BBC | International | In-depth reporting |
| Reuters | Global | Wire service |
| AP (Associated Press) | National/Global | News agency |
| Al Jazeera | Global | International news |
| The Guardian | UK/Global | Analysis |
| NPR | National | Public radio |
| New York Times | National/Global | Major newspaper |

---

## News Categories

```
politics              - Political news
business              - Finances, markets, corporate
technology           - Tech companies, startups, products
health               - Medical, wellness, healthcare
sports               - Athletic events, sports news
entertainment        - Entertainment, celebrity, media
world                - International news
national             - Domestic news
science              - Scientific research
climate              - Environmental news
opinion              - Analysis and opinion
other                - Misc news
```

---

## Performance Tips

1. **Batch Operations**
   ```python
   # Good - single call
   articles = await orchestrator.fetch_weekly_news(max_articles=20)
   
   # Less efficient - 20 separate calls
   for i in range(20):
       article = await orchestrator.search_news(...)
   ```

2. **Cache Results**
   ```python
   # Store results in cache
   weekly_news = await orchestrator.get_news_digest()
   # Reuse throughout the week
   ```

3. **Optimize Filters**
   ```python
   # Get articles once with filters
   results = await orchestrator.fetch_weekly_news(
       region="national",
       max_articles=50
   )
   # Filter locally instead of querying again
   ```

---

## Troubleshooting

### Issue: Connection Refused

```
Error: Connection refused - MCP Server at port 8008
```

**Solution**:
```bash
docker-compose ps  # Check if news_mcp is running
curl http://localhost:8008/health
docker-compose logs news_mcp  # View error logs
```

### Issue: No Articles Found

```
articles_fetched: 0
```

**Solution**:
```python
# Expand search parameters
result = await orchestrator.fetch_weekly_news(
    region="both",        # Include both national and world
    max_articles=100,     # Increase limit
    sources=None          # Use all available sources
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

# Check GCP permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

---

## Next Steps

1. **Read Full Documentation**: See [NEWS_AGENT.md](NEWS_AGENT.md) for complete details
2. **Explore Other Agents**: Try integrating with Task, Calendar, or Notes agents
3. **Customize**: Add your own news sources and categories
4. **Deploy**: Use the deployment guides for production setup

---

## Quick Command Reference

```bash
# Health check
curl http://localhost:8008/health

# Start locally
docker-compose up

# Deploy to Cloud
./deploy-to-cloud.sh PROJECT_ID us-central1

# View logs
docker-compose logs -f news_mcp

# Unit tests  
pytest tests/test_news_agent.py

# Lint code
pylint backend/mcp_tools/news_mcp_server.py
```

---

## Common Operations Cheat Sheet

```python
# Weekly headlines
headlines = await orchestrator.fetch_weekly_news(max_articles=10)

# With audio
summary = await orchestrator.get_news_summary("news_123", "mp3")

# Search topics
results = await orchestrator.search_news("politics", limit=5)

# Weekly summary
digest = await orchestrator.get_news_digest()

# Trending topics
trends = await orchestrator.get_news_trends(period_days=7)

# Custom briefing
brief = await orchestrator.create_news_summary(
    article_ids=[...],
    title="My Briefing"
)
```

---

**Happy reading! 📰🎧**

---

**Version**: 1.0  
**Last Updated**: April 5, 2026  
**Status**: Production Ready
