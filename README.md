# 🤖 Word23 Counter Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

A powerful Telegram bot for advanced text analysis and word counting.

## ✨ Features

- 📊 **Word Count**: Count words, characters, sentences, paragraphs
- 🔍 **Keyword Analysis**: Find most used words and density
- 📈 **Readability Score**: Check text readability
- 🌍 **Multi-language**: Works with any language
- 🎯 **Interactive Buttons**: Easy navigation
- ⚡ **Auto-Analysis**: Just send text and get results

## 🚀 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with menu |
| `/help` | Show all commands |
| `/about` | Bot information |
| `/count [text]` | Quick word count |
| `/stats` | Detailed statistics |
| `/readability [text]` | Check readability |

## 🛠️ Tech Stack

- Python 3.11
- python-telegram-bot 20.7
- Railway (Deployment)
- GitHub (Version Control)

## 📦 Installation

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/word23counter-bot.git
cd word23counter-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your BOT_TOKEN

# Run bot
python bot.py
