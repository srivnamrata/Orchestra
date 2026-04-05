# 📚 Research Agent Quick Start Guide

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

### 2. Verify Research Agent is Running

```bash
curl http://localhost:8007/health
# Response: {"status": "healthy"}
```

---

## Common Use Cases

### Use Case 1: Get Weekly AI Research Highlights

**Goal**: Know what's trending in AI this week

```python
from backend.agents.orchestrator_agent_mcp import OrchestratorAgentMCP
from backend.services.llm_service import LLMService
from backend.services.pubsub_service import PubSubService

# Initialize
llm = LLMService()
pubsub = PubSubService()
orchestrator = OrchestratorAgentMCP(llm, pubsub)
await orchestrator.initialize()

# Get this week's highlights
result = await orchestrator.fetch_weekly_highlights(
    categories=["artificial_intelligence", "machine_learning"],
    max_articles=10
)

# Display results
for article in result["articles"]:
    print(f"\n📄 {article['title']}")
    print(f"   From: {article['source']}")
    print(f"   Summary: {article['summary'][:200]}...")
    print(f"   Read: {article['url']}")
```

**Output:**
```
📄 Transformer Architecture Breakthrough
   From: towards_data_science
   Summary: New efficient transformer design reduces...
   Read: https://example.com/article1

📄 Advanced Robotics with AI
   From: arxiv
   Summary: Novel approach to robotic learning...
   Read: https://example.com/article2
```

---

### Use Case 2: Find Articles on Specific Topic

**Goal**: Search for specific research topic

```python
# Search for transformer-related articles from the last 30 days
result = await orchestrator.search_articles(
    query="transformer attention mechanism",
    category="deep_learning",
    days_back=30,
    limit=5
)

print(f"Found {result['results_count']} articles:")
for article in result["articles"]:
    print(f"• {article['title']}")
    print(f"  {article['summary'][:150]}...")
```

---

### Use Case 3: Listen to Article Summary

**Goal**: Get audio version of research article

```python
# Get article with audio
result = await orchestrator.get_article_summary(
    article_id="article_12345",
    audio_format="mp3"
)

article = result["article"]
print(f"Title: {article['title']}")
print(f"Summary: {article['summary']}")
print(f"🎧 Audio: {article['audio_url']}")

# User can download and listen to the audio file
# Or stream directly if playing in browser
```

---

### Use Case 4: Get Weekly Digest Email

**Goal**: Create weekly research summary for email

```python
# Get complete weekly digest
digest = await orchestrator.get_weekly_digest(week_offset=0)

# Build email content
email_html = """
<h1>This Week in AI Research</h1>
"""

for category, articles in digest["digest"]["categories"].items():
    email_html += f"<h2>{category.replace('_', ' ').title()}</h2>"
    email_html += f"<p>Found {len(articles)} articles:</p><ul>"
    
    for article in articles[:5]:  # Top 5 per category
        email_html += f"""
        <li>
            <h3>{article['title']}</h3>
            <p>{article['summary']}</p>
            <a href="{article['url']}">Read More</a>
        </li>
        """
    
    email_html += "</ul>"

# Send email with digest
print("Ready to email:")
print(email_html)
```

---

### Use Case 5: Create Custom AI Briefing

**Goal**: Combine selected articles into one custom briefing

```python
# Fetch some articles
highlights = await orchestrator.fetch_weekly_highlights(
    categories=["deep_learning", "nlp"],
    max_articles=20
)

# Select top articles
top_article_ids = [
    a["id"] for a in highlights["articles"][:5]
]

# Create custom summary
briefing = await orchestrator.create_custom_summary(
    article_ids=top_article_ids,
    title="Weekly Deep Learning & NLP Briefing",
    focus_areas=["transformers", "language models", "applications"]
)

print(f"📻 Your Briefing: {briefing['title']}")
print(f"Summary:\n{briefing['summary']}")
print(f"📎 Audio: {briefing['audio_url']}")

# Share the audio link or email the summary
```

---

### Use Case 6: Track Trending Topics

**Goal**: Discover what researchers are focusing on

```python
# Get trending topics in deep learning from last 2 weeks
trends = await orchestrator.get_trending_topics(
    category="deep_learning",
    period_days=14
)

print("\n🔥 Top 10 Trending Topics in Deep Learning:")
for i, trend in enumerate(trends["trending_topics"][:10], 1):
    print(f"{i}. {trend['topic']} - {trend['mentions']} mentions")

# Use these insights for:
# - Understanding research directions
# - Finding relevant articles
# - Identifying skill gaps to learn
```

---

## API Examples

### Example 1: Minimal - Just Get Text

```python
# Quick summary retrieval
result = await orchestrator.fetch_weekly_highlights(max_articles=5)
articles = result["articles"]

for article in articles:
    print(f"{article['title']}\n{article['summary']}\n")
```

### Example 2: Full - Text + Audio

```python
# Get articles with audio versions
highlights = await orchestrator.fetch_weekly_highlights(
    categories=["machine_learning"],
    max_articles=3
)

for article in highlights["articles"]:
    # Get article with audio
    summary = await orchestrator.get_article_summary(
        article_id=article["id"],
        audio_format="mp3"
    )
    
    print(f"📄 {summary['article']['title']}")
    print(f"📖 Read: {summary['article']['summary'][:200]}...")
    print(f"🎧 Listen: {summary['article']['audio_url']}")
```

### Example 3: Search & Filter

```python
# Advanced search
results = await orchestrator.search_articles(
    query="neural network efficiency",
    category="deep_learning",
    days_back=60,
    limit=20
)

# Process results
important_articles = [
    a for a in results["articles"]
    if "breakthrough" in a.get("title", "").lower()
]

for article in important_articles:
    print(f"⭐ {article['title']}")
```

---

## Integration with Other Agents

### Example: Research + Note Taking

```python
# Get interesting article
research = await orchestrator.fetch_weekly_highlights(max_articles=1)
article = research["articles"][0]

# Create a note about it
note = await orchestrator.create_note(
    title=f"Research: {article['title']}",
    content=f"""Source: {article['source']}
URL: {article['url']}

Summary:
{article['summary']}

Key Points:
- Point 1
- Point 2
- Point 3

Action Items:
- [ ] Read full article
- [ ] Implement key concepts
- [ ] Share with team
"""
)

print(f"✅ Created note: {note['id']}")
```

### Example: Research + Calendar

```python
# Get trending topics
trends = await orchestrator.get_trending_topics(period_days=7)
top_topics = [t["topic"] for t in trends["trending_topics"][:3]]

# Create learning event
event = await orchestrator.create_event(
    title=f"Learn: {', '.join(top_topics)}",
    start_time="2024-04-08T10:00:00Z",
    end_time="2024-04-08T11:00:00Z",
    description=f"Research session on trending topics: {', '.join(top_topics)}"
)

print(f"📅 Created learning session: {event['id']}")
```

---

## Configuration Options

### Environment Variables

```bash
# For Cloud Run deployment
MCP_RESEARCH_HOST=multi-agent-research
MCP_RESEARCH_PORT=8007

# For local development
MCP_RESEARCH_HOST=localhost
MCP_RESEARCH_PORT=8007
```

### Request Parameters

```python
# All optional - sensible defaults
await orchestrator.fetch_weekly_highlights(
    categories=["machine_learning", "robotics"],  # None = all categories
    sources=["towards_data_science", "arxiv"],     # None = all sources
    max_articles=15                                # Default: 10
)

await orchestrator.search_articles(
    query="neural networks",                      # Required
    category="deep_learning",                     # Optional
    days_back=30,                                 # Default: 7
    limit=20                                      # Default: 10
)

await orchestrator.generate_audio(
    article_id="article_123",                     # Required
    voice="female",                               # Default: "female"
    language="en-US"                              # Default: "en-US"
)
```

---

## Response Format

All methods return structured JSON:

```python
{
    "status": "success",  # or "error"
    "message": "Optional error message",
    "data": {
        # Method-specific data
    },
    "timestamp": "2024-04-05T10:30:00Z",
    "request_id": "req_12345"
}
```

---

## Error Handling

```python
try:
    result = await orchestrator.search_articles(
        query="quantum computing",
        days_back=7
    )
    
    if result["status"] == "success":
        articles = result.get("articles", [])
        print(f"Found {len(articles)} articles")
    else:
        print(f"Error: {result.get('message')}")
        
except Exception as e:
    print(f"Failed: {e}")
    # Handle connection errors, timeouts, etc.
```

---

## Performance Tips

1. **Batch Operations**
   ```python
   # Good - single call
   highlights = await orchestrator.fetch_weekly_highlights(max_articles=20)
   
   # Less efficient - 20 separate calls
   for i in range(20):
       article = await orchestrator.search_articles(...)
   ```

2. **Cache Results**
   ```python
   # Store results in memory/cache
   weekly_digest = await orchestrator.get_weekly_digest()
   # Reuse this throughout the week
   ```

3. **Optimize Article Selection**
   ```python
   # Get articles once with filtering
   results = await orchestrator.fetch_weekly_highlights(
       categories=["machine_learning"],
       max_articles=50
   )
   # Process locally instead of querying again
   ```

---

## Troubleshooting

### Issue: Connection Refused

```
Error: Connection refused - MCP Server at port 8007
```

**Solution**: Verify research agent is running

```bash
docker-compose ps  # Check if research_mcp is up
curl http://localhost:8007/health  # Test connectivity
docker-compose logs research_mcp  # View logs
```

### Issue: No Articles Found

```
Results: articles_fetched: 0
```

**Solution**: Check date range and category

```python
# Expand search parameters
result = await orchestrator.fetch_weekly_highlights(
    max_articles=50,      # Increase limit
    days_back=14          # Search further back
)
```

### Issue: Audio Generation Failed

```
Error: Audio URL is None
```

**Solution**: Verify Google Cloud Text-to-Speech is configured

```bash
# Check environment
echo $GOOGLE_APPLICATION_CREDENTIALS
# Ensure GCP project has TTS API enabled
gcloud services enable texttospeech.googleapis.com
```

---

## Next: Explore Other Agents

Now that you're familiar with Research Agent, try integrating it with:

- **📋 Task Agent** (`create_task`) - Create tasks based on articles
- **📅 Calendar Agent** (`create_event`) - Schedule learning/research sessions
- **📝 Notes Agent** (`create_note`) - Save insights and summaries
- **🎓 Critic Agent** (`review_code`) - Review research code implementations
- **📊 Auditor Agent** (`audit_activity`) - Track research activities

---

## Support

For issues or questions:

1. Check [RESEARCH_AGENT.md](RESEARCH_AGENT.md) for detailed documentation
2. Review logs: `docker-compose logs research_mcp`
3. Test connectivity: `curl http://localhost:8007/health`
4. Check Firestore: Verify collections exist in Firebase Console

---

**Happy researching! 🎓**

---

**Last Updated**: April 5, 2026  
**Version**: 1.0  
**Status**: Production Ready
