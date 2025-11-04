"""
Configuration for AI news sources to monitor.
"""

# Sources with RSS feeds (easier to scrape)
RSS_SOURCES = {
    "openai": {
        "name": "OpenAI",
        "urls": [
            "https://openai.com/news/rss.xml",
        ],
        "type": "rss"
    },
    "google": {
        "name": "Google AI",
        "urls": [
            "https://blog.google/rss/",
        ],
        "type": "rss",
        "filter_keyword": "ai"  # Filter for AI-related posts
    },
    "cohere": {
        "name": "Cohere",
        "urls": [
            "https://txt.cohere.com/rss/",
        ],
        "type": "rss"
    },
    "qwen": {
        "name": "Alibaba (Qwen)",
        "urls": [
            "https://qwenlm.github.io/feed.xml",
        ],
        "type": "rss"
    },
}

# Sources requiring web scraping (no RSS feed)
WEB_SOURCES = {
    "anthropic": {
        "name": "Anthropic",
        "urls": [
            "https://www.anthropic.com/news",
        ],
        "type": "web",
        "selectors": {
            "article": "article, .post, [class*='news'], [class*='blog']",
            "title": "h1, h2, h3, .title",
            "link": "a",
            "description": "p, .description, .excerpt",
            "date": "time, .date, [datetime]"
        }
    },
    "meta": {
        "name": "Meta AI",
        "urls": [
            "https://ai.meta.com/blog/",
        ],
        "type": "web",
        "selectors": {
            "article": "article, .post-item, [class*='blog']",
            "title": "h2, h3, .title",
            "link": "a",
            "description": "p, .excerpt",
            "date": "time, .date, [datetime]"
        }
    },
    "mistral": {
        "name": "Mistral",
        "urls": [
            "https://mistral.ai/news/",
        ],
        "type": "web",
        "selectors": {
            "article": "article, .news-item, [class*='post']",
            "title": "h1, h2, h3, .title",
            "link": "a",
            "description": "p, .description",
            "date": "time, .date, [datetime]"
        }
    },
    "xai": {
        "name": "xAI (Grok)",
        "urls": [
            "https://x.ai/blog/",
        ],
        "type": "web",
        "selectors": {
            "article": "article, .blog-post",
            "title": "h1, h2, h3, .title",
            "link": "a",
            "description": "p, .excerpt",
            "date": "time, .date, [datetime]"
        }
    },
}

# Additional changelog sources (try RSS first, fallback to web scraping)
CHANGELOG_SOURCES = {
    "openai_changelog": {
        "name": "OpenAI Platform Changelog",
        "urls": [
            "https://platform.openai.com/docs/changelog",
        ],
        "type": "web",
        "selectors": {
            "article": "[class*='changelog'], .update-item",
            "title": "h2, h3, .title",
            "link": "a",
            "description": "p, .description",
            "date": "time, .date, [datetime]"
        }
    },
    "anthropic_changelog": {
        "name": "Anthropic Release Notes",
        "urls": [
            "https://docs.anthropic.com/en/release-notes",
        ],
        "type": "web",
        "selectors": {
            "article": "[class*='release'], .changelog-item",
            "title": "h2, h3, .title",
            "link": "a",
            "description": "p, .description",
            "date": "time, .date, [datetime]"
        }
    },
    "gemini_changelog": {
        "name": "Google Gemini Changelog",
        "urls": [
            "https://ai.google.dev/gemini-api/docs/changelog",
        ],
        "type": "web",
        "selectors": {
            "article": "[class*='changelog'], .update",
            "title": "h2, h3, .title",
            "link": "a",
            "description": "p, .description",
            "date": "time, .date, [datetime]"
        }
    },
}

# Combine all sources
ALL_SOURCES = {**RSS_SOURCES, **WEB_SOURCES, **CHANGELOG_SOURCES}

# User-Agent for web requests (important for scraping)
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Request timeout (seconds)
REQUEST_TIMEOUT = 30

# Delay between requests (seconds) - be respectful
REQUEST_DELAY = 2
