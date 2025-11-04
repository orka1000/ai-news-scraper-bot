# Adding More AI News Sources

Your bot currently monitors **5 reliable RSS sources**. Here's how to add more sources using third-party RSS feed generation services.

## Current Working Sources

✅ **OpenAI Blog** - RSS feed
✅ **Google AI Blog** - RSS feed
✅ **Cohere Blog** - RSS feed
✅ **Alibaba (Qwen) Blog** - RSS feed
✅ **Meta AI Research** - RSS feed

## Missing Sources (No Native RSS)

These sources don't have official RSS feeds but you can create them:

❌ **Anthropic News** - https://www.anthropic.com/news
❌ **Mistral AI News** - https://mistral.ai/news
❌ **xAI (Grok) Blog** - https://x.ai/blog
❌ **OpenAI Changelog** - https://platform.openai.com/docs/changelog
❌ **Anthropic Release Notes** - https://docs.anthropic.com/en/release-notes
❌ **Google Gemini Changelog** - https://ai.google.dev/gemini-api/docs/changelog

---

## How to Create RSS Feeds

### Option 1: RSS.app (Easiest)

**Free tier:** 1 feed
**Paid:** $9/month for unlimited feeds

1. Go to https://rss.app
2. Click **"Generate RSS Feed"**
3. Paste the website URL (e.g., `https://www.anthropic.com/news`)
4. The tool will automatically detect articles
5. Copy the generated feed URL (e.g., `https://feed.rss.app/abc123`)
6. Add to `config.py`:

```python
"anthropic": {
    "name": "Anthropic",
    "urls": ["https://feed.rss.app/abc123"],  # Your feed URL here
    "type": "rss"
},
```

### Option 2: FetchRSS (Free Alternative)

**Free tier:** 5 feeds, updates every 6 hours
**Paid:** $7/month for 20 feeds

1. Go to https://fetchrss.com
2. Click **"Create Feed"**
3. Enter the website URL
4. Use the visual builder to select article elements
5. Copy the generated feed URL
6. Add to `config.py` (same format as above)

### Option 3: FiveFilters Feed Creator (Self-Hosted)

**Free & open source**

1. Go to https://createfeed.fivefilters.org
2. Enter the URL and specify CSS selectors
3. Click **"Preview"** to test
4. Use the generated feed URL
5. Add to `config.py`

---

## Step-by-Step Example: Adding Anthropic News

### 1. Create the RSS Feed

Using **RSS.app**:

1. Visit https://rss.app
2. Click "Generate RSS Feed"
3. Enter: `https://www.anthropic.com/news`
4. Click "Generate"
5. Copy the feed URL: `https://feed.rss.app/YOUR_ID`

### 2. Update config.py

Open `config.py` and add to `RSS_SOURCES`:

```python
RSS_SOURCES = {
    # ... existing sources ...

    "anthropic": {
        "name": "Anthropic",
        "urls": ["https://feed.rss.app/YOUR_ID"],
        "type": "rss"
    },
}
```

### 3. Test Locally (Optional)

```bash
export SLACK_WEBHOOK_URL="your-webhook"
python main.py
```

Check your Slack for Anthropic news!

### 4. Commit and Push

```bash
git add config.py
git commit -m "Add Anthropic RSS feed"
git push origin main
```

The bot will automatically start monitoring Anthropic news on the next run!

---

## Recommended Feeds to Add

Here are the suggested feed creations in priority order:

### Priority 1: Main Company Blogs
1. **Anthropic News** - https://www.anthropic.com/news
2. **Mistral AI News** - https://mistral.ai/news
3. **xAI Blog** - https://x.ai/blog

### Priority 2: Changelogs (Developer-Focused)
4. **Anthropic Release Notes** - https://docs.anthropic.com/en/release-notes
5. **OpenAI Platform Changelog** - https://platform.openai.com/docs/changelog
6. **Google Gemini Changelog** - https://ai.google.dev/gemini-api/docs/changelog

### Priority 3: Additional Sources
7. **DeepMind Blog** - https://deepmind.google/discover/blog/
8. **Hugging Face Blog** - https://huggingface.co/blog
9. **Stability AI News** - https://stability.ai/news
10. **AI21 Labs Blog** - https://www.ai21.com/blog

---

## Tips & Best Practices

### Feed Quality
- Test feeds in an RSS reader first (Feedly, Inoreader)
- Check update frequency (some services cache for hours)
- Verify articles have titles, links, and descriptions

### Avoiding Duplicates
- Don't add the same source twice with different URLs
- The state manager will handle duplicates within a source

### Rate Limits
- Free RSS generation services may have update delays
- Paid plans offer faster updates (5-15 min intervals)

### Troubleshooting
- If a feed stops working, regenerate it
- Check if the website structure changed
- Try a different RSS generation service

---

## Cost Comparison

| Service | Free Tier | Paid Plan | Update Frequency |
|---------|-----------|-----------|------------------|
| **RSS.app** | 1 feed | $9/mo unlimited | Every 15 min |
| **FetchRSS** | 5 feeds | $7/mo 20 feeds | Every 6 hours (free), 15 min (paid) |
| **FiveFilters** | Unlimited | $5/mo hosted | Manual/on-demand |
| **Feedly Pro** | N/A | $6/mo | Instant (uses their builder) |

**Recommendation:** Start with FetchRSS free tier (5 feeds) to add Anthropic, Mistral, xAI, and 2 changelogs.

---

## Alternative: Fix Web Scrapers

If you prefer not to use third-party services, you can fix the web scrapers:

1. Inspect each website's HTML structure
2. Update CSS selectors in `config.py`
3. Uncomment the sources in `WEB_SOURCES`
4. Test locally before pushing

**Note:** Web scraping is more fragile - sites may change structure or block scrapers.

---

## Questions?

- Check the [README.md](README.md) for basic setup
- See [config.py](config.py) for configuration examples
- Open an issue on GitHub if you need help
