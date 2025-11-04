# AI News Scraper Bot

An automated GitHub Actions-based agent that monitors AI news from major companies and sends daily updates to Slack.

## Features

- **Daily automated scraping** of AI news from 8+ major sources
- **Smart duplicate detection** to avoid sending the same news twice
- **Slack integration** with rich formatted messages
- **Mixed scraping strategies**: RSS feeds (fast) and web scraping (comprehensive)
- **State persistence** via Git to track seen entries
- **Zero infrastructure** - runs entirely on GitHub Actions (free for public repos)

## Sources Monitored

### RSS Feed Sources (Fast & Reliable)
1. **OpenAI** - Blog and news
2. **Google AI** - AI-related blog posts
3. **Cohere** - Blog posts
4. **Alibaba (Qwen)** - Blog updates

### Web Scraping Sources
5. **Anthropic** - News and announcements
6. **Meta AI** - AI blog
7. **Mistral** - News
8. **xAI (Grok)** - Blog

### Changelog Sources
- OpenAI Platform Changelog
- Anthropic Release Notes
- Google Gemini API Changelog

## Setup Instructions

### 1. Fork or Clone This Repository

```bash
git clone <your-repo-url>
cd 80.claude-github-agent-research
```

### 2. Create a Slack Webhook

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name your app (e.g., "AI News Bot") and select your workspace
4. In the app settings, go to **"Incoming Webhooks"**
5. Toggle **"Activate Incoming Webhooks"** to ON
6. Click **"Add New Webhook to Workspace"**
7. Select the channel where you want to receive updates
8. Copy the webhook URL (looks like `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

### 3. Add Slack Webhook to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Name: `SLACK_WEBHOOK_URL`
5. Value: Paste your Slack webhook URL
6. Click **"Add secret"**

### 4. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will now run daily at 9 AM UTC

### 5. Test the Workflow Manually

1. Go to **Actions** tab
2. Click on **"AI News Scraper"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait a few minutes and check your Slack channel for updates

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── scrape.yml           # GitHub Actions workflow
├── src/
│   ├── scrapers/
│   │   ├── rss_scraper.py      # RSS feed scraper
│   │   └── web_scraper.py      # Web page scraper
│   ├── slack_notifier.py        # Slack integration
│   └── state_manager.py         # State file management
├── config.py                    # Source configurations
├── main.py                      # Main orchestration script
├── state.json                   # State tracking (auto-updated)
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## How It Works

1. **GitHub Actions** triggers the workflow daily at 9 AM UTC (or manually)
2. **RSS Scraper** fetches updates from RSS feed sources
3. **Web Scraper** extracts articles from websites without RSS feeds
4. **State Manager** filters out previously seen entries
5. **Slack Notifier** formats and sends new updates to your Slack channel
6. **Git Auto-Commit** saves the updated state file back to the repository

## Configuration

### Changing the Schedule

Edit `.github/workflows/scrape.yml` and modify the cron expression:

```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

Cron format: `minute hour day month weekday`
- `0 9 * * *` = 9 AM UTC daily
- `0 */6 * * *` = Every 6 hours
- `0 0 * * 1` = Every Monday at midnight

### Adding New Sources

Edit `config.py` and add your source to the appropriate section:

**For RSS feeds:**
```python
RSS_SOURCES = {
    "newsource": {
        "name": "New Source Name",
        "urls": ["https://example.com/feed.xml"],
        "type": "rss"
    }
}
```

**For web scraping:**
```python
WEB_SOURCES = {
    "newsource": {
        "name": "New Source Name",
        "urls": ["https://example.com/blog"],
        "type": "web",
        "selectors": {
            "article": "article, .post",
            "title": "h2, h3",
            "link": "a",
            "description": "p",
            "date": "time"
        }
    }
}
```

### Customizing Slack Message Format

Edit `src/slack_notifier.py` to modify the message appearance. The bot uses Slack's Block Kit for rich formatting.

## Local Testing

You can test the scraper locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Slack webhook URL
export SLACK_WEBHOOK_URL="your-webhook-url-here"

# Run the scraper
python main.py
```

## Troubleshooting

### Workflow Not Running

- Check that GitHub Actions is enabled in your repository
- Public repos have unlimited Actions minutes; private repos have 2000 mins/month
- Scheduled workflows may be delayed a few minutes on free tier
- Repos with no activity for 60 days will have workflows paused

### No Updates Being Sent

- Check the Actions logs for errors
- Verify the Slack webhook URL is correct
- Ensure sources are returning data (test locally)
- Check if `state.json` needs to be reset (delete all seen_entries)

### Web Scraping Errors

- Websites may change their HTML structure - update selectors in `config.py`
- Some sites may block scrapers - check robots.txt
- Add delays in `config.py` if getting rate limited

### State File Conflicts

If you get merge conflicts in `state.json`:
1. Keep your version (the one with more entries)
2. Or reset it by replacing content with:
   ```json
   {"last_checked": null, "seen_entries": {}, "etags": {}, "last_modified": {}}
   ```

## Rate Limiting & Best Practices

- The scraper adds 2-second delays between requests (configurable in `config.py`)
- RSS feeds use conditional GET (ETag/Last-Modified) to minimize bandwidth
- Web scraping is limited to the first 20 articles per source
- State file is automatically cleaned up to keep only 200 entries per source

## Privacy & Legal

- All scraped sources are public blogs and news sites
- The bot respects rate limits and adds delays between requests
- No personal data is collected or stored
- State file only contains article URLs and IDs

## License

MIT License - Feel free to modify and use for your own purposes.

## Contributing

Contributions welcome! Please:
1. Test your changes locally first
2. Update documentation if adding features
3. Keep the code simple and maintainable

## Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Test locally with `python main.py`
3. Open an issue on GitHub with error details
