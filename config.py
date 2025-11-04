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
    "meta_research": {
        "name": "Meta AI Research",
        "urls": [
            "https://research.facebook.com/feed/",
        ],
        "type": "rss"
    },
    # To add more RSS feeds:
    # - For sites without RSS, use RSS.app (https://rss.app) or FetchRSS (https://fetchrss.com)
    # - Create feeds for: Anthropic news, Mistral news, xAI blog
    # - Then add them here with the generated feed URLs
    # Example:
    # "anthropic": {
    #     "name": "Anthropic",
    #     "urls": ["https://feed.rss.app/YOUR_FEED_ID"],  # Replace with your RSS.app feed URL
    #     "type": "rss"
    # },
}

# Sources requiring web scraping (no RSS feed)
# NOTE: Many sites block scrapers or have unreliable HTML structures.
# Recommended: Use RSS.app or FetchRSS to create RSS feeds instead (see RSS_SOURCES above)
WEB_SOURCES = {
    # Commented out - these sources are currently failing or unreliable:
    # - Anthropic: Only finds 1 article (CSS selectors may need updating)
    # - Meta AI Blog: Returns 400 Bad Request (use Meta Research RSS instead)
    # - Mistral: CSS selectors don't match current site structure
    # - xAI: Returns 403 Forbidden (blocks scrapers)
    #
    # To re-enable, update CSS selectors or create RSS feeds via third-party services

    # "anthropic": {
    #     "name": "Anthropic",
    #     "urls": ["https://www.anthropic.com/news"],
    #     "type": "web",
    #     "selectors": {
    #         "article": "article, .post, [class*='news'], [class*='blog']",
    #         "title": "h1, h2, h3, .title",
    #         "link": "a",
    #         "description": "p, .description, .excerpt",
    #         "date": "time, .date, [datetime]"
    #     }
    # },
}

# Additional changelog sources
# NOTE: These are currently failing due to 403 errors or incorrect selectors
# Consider using third-party RSS generation services for these
CHANGELOG_SOURCES = {
    # Commented out - currently failing:
    # - OpenAI Changelog: 403 Forbidden
    # - Anthropic Release Notes: No articles found
    # - Gemini Changelog: No articles found

    # "openai_changelog": {
    #     "name": "OpenAI Platform Changelog",
    #     "urls": ["https://platform.openai.com/docs/changelog"],
    #     "type": "web",
    #     "selectors": {
    #         "article": "[class*='changelog'], .update-item",
    #         "title": "h2, h3, .title",
    #         "link": "a",
    #         "description": "p, .description",
    #         "date": "time, .date, [datetime]"
    #     }
    # },
}

# Combine all sources
ALL_SOURCES = {**RSS_SOURCES, **WEB_SOURCES, **CHANGELOG_SOURCES}

# User-Agent for web requests (important for scraping)
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Request timeout (seconds)
REQUEST_TIMEOUT = 30

# Delay between requests (seconds) - be respectful
REQUEST_DELAY = 2
