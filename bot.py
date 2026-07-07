import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    logger.error("TELEGRAM_TOKEN environment variable not set!")
    exit(1)

# Store user stats (in production, use a database)
user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = f"""
👋 Hello {user.first_name}!

Welcome to **Word23 Counter Bot**! 📝

I can help you count words, characters, and more.

🔹 Send me any text and I'll count the words
🔹 Use /help to see all commands
🔹 Use /stats to see your usage statistics

Let's get started! Send me a message. ✨
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 Try Now", callback_data="try_now")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = """
📖 **Available Commands:**

/start - Welcome message
/help - Show this help message
/stats - View your word count statistics
/about - About this bot
/contact - Contact the developer

**How to use:**
Simply send me any text message, and I'll count:
• Total words
• Total characters (with and without spaces)
• Number of sentences
• Number of paragraphs

**Examples:**
`Hello world!` → 2 words
`This is a longer sentence.` → 5 words
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user_id = update.effective_user.id
    stats = user_stats.get(user_id, {"total_words": 0, "total_messages": 0, "last_used": None})
    
    if stats["total_messages"] == 0:
        await update.message.reply_text("📊 You haven't used this bot yet! Send me some text to get started.")
        return
    
    stats_text = f"""
📊 **Your Statistics**

📝 Total words counted: {stats['total_words']}
💬 Total messages processed: {stats['total_messages']}
⏰ Last used: {stats['last_used'] or 'Never'}
    """
    await update.message.reply_text(stats_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send about information."""
    about_text = """
🤖 **About Word23 Counter Bot**

This bot was created to help you count words, characters, and more in your messages.

**Version:** 1.0.0
**Created by:** Your Name
**Hosted on:** Railway
**Source Code:** GitHub

**Why Word23?**
Fast, accurate, and always free to use!

📧 For support: /contact
    """
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send contact information."""
    contact_text = """
📧 **Contact**

For support, feedback, or feature requests:

• Send a message to @YourTelegramUsername
• Email: your.email@example.com

I'll get back to you as soon as possible! 🙌
    """
    await update.message.reply_text(contact_text, parse_mode="Markdown")

async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Count words, characters, sentences, and paragraphs."""
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text:
        await update.message.reply_text("Please send me some text to count.")
        return
    
    # Word counting logic
    words = text.split()
    word_count = len(words)
    
    # Character counts
    char_count_with_spaces = len(text)
    char_count_without_spaces = len(text.replace(" ", ""))
    
    # Sentence count (roughly counting periods, exclamation, question marks)
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    sentence_count = sentence_count if sentence_count > 0 else 1
    
    # Paragraph count (split by newlines and filter empty)
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs) if paragraphs else 1
    
    # Update user statistics
    if user_id not in user_stats:
        user_stats[user_id] = {"total_words": 0, "total_messages": 0, "last_used": None}
    
    user_stats[user_id]["total_words"] += word_count
    user_stats[user_id]["total_messages"] += 1
    user_stats[user_id]["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create response
    response = f"""
📊 **Text Analysis Results**

📝 **Words:** {word_count}
🔤 **Characters (with spaces):** {char_count_with_spaces}
🔡 **Characters (without spaces):** {char_count_without_spaces}
📖 **Sentences:** {sentence_count}
📄 **Paragraphs:** {paragraph_count}

---
ℹ️ Send more text to keep counting!
    """
    
    # Add fun fact for longer texts
    if word_count > 100:
        response += "\n🌟 Wow! That's a long text! Keep writing! ✍️"
    elif word_count > 50:
        response += "\n💪 Nice! You're on a roll!"
    elif word_count > 20:
        response += "\n👍 Good job! Keep going!"
    
    await update.message.reply_text(response, parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "try_now":
        await query.edit_message_text(
            "📝 **Ready to count!**\n\nSend me any text and I'll count everything for you. Try it now! 🚀",
            parse_mode="Markdown"
        )
    elif query.data == "about":
        about_text = """
🤖 **Word23 Counter Bot**

**Version:** 1.0.0
**Features:**
• Word counting
• Character counting
• Sentence counting
• Paragraph counting
• User statistics

**Free • Fast • Reliable**

Made with ❤️ for the Telegram community.
        """
        await query.edit_message_text(about_text, parse_mode="Markdown")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    logger.info("Starting Word23 Counter Bot...")
    
    # Create the Application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("contact", contact_command))
    
    # Add message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_words))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot is ready! Starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
