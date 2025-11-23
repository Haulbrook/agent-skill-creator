# API Setup Guide

This guide helps you configure API keys for full functionality.

## Required vs Optional APIs

### Essential (Recommended)
- **Anthropic Claude API**: For AI-powered cover letters and analysis
  - Free tier: $5/month typical usage
  - Get key: https://console.anthropic.com/

### Optional (For Enhanced Features)
- **LinkedIn API**: For LinkedIn job search
- **Indeed API**: For Indeed job search
- **Glassdoor API**: For company reviews
- **OpenAI API**: Alternative to Claude for text generation

## Setup Instructions

1. Create a `.env` file in the agent directory:

```bash
cp .env.example .env
```

2. Add your API keys:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LINKEDIN_API_KEY=your_key
INDEED_PUBLISHER_ID=your_id
GLASSDOOR_API_KEY=your_key
```

3. The agent will automatically use these keys when available.

## Free Tier Limits

- **Anthropic Claude**: ~$5-10/month for typical usage
- **Indeed API**: 1000 queries/month free
- **JSearch API**: 100 searches/month free

## Fallback Behavior

The agent works even without API keys:
- Uses sample data for demonstrations
- Job search uses web scraping (limited)
- Cover letters use templates (no AI customization)

For best results, configure at least the Anthropic API key.
