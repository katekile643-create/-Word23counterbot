import os
import re
import logging
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters
)

# ==================== LOGGING SETUP ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PORT = int(os.environ.get('PORT', 8443))
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')

if not BOT_TOKEN:
    logger.error("❌ BOT_TOKEN environment variable not set!")
    sys.exit(1)

logger.info(f"🚀 Starting bot in {ENVIRONMENT} mode")

# ==================== TEXT ANALYSIS ENGINE ====================

class TextAnalyzer:
    """Advanced text analysis engine"""
    
    @staticmethod
    def analyze(text):
        """Perform comprehensive text analysis"""
        # Clean and prepare text
        text = text.strip()
        if not text:
            return None
        
        # Word count (using regex for better accuracy)
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Character counts
        char_with_spaces = len(text)
        char_without_spaces = len(re.sub(r'\s', '', text))
        
        # Sentence count (handle multiple punctuation)
        sentences = re.split(r'[.!?…]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        # Paragraph count
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs) if paragraphs else 1
        
        # Unique words
        unique_words = set(w.lower() for w in words)
        unique_word_count = len(unique_words)
        
        # Average word length
        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        
        # Word frequency for keyword density
        word_freq = {}
        for w in words:
            w_lower = w.lower()
            word_freq[w_lower] = word_freq.get(w_lower, 0) + 1
        
        # Top 10 most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate readability (simple metric)
        long_words = sum(1 for w in words if len(w) >= 7)
        readability_score = 100 - ((long_words / max(word_count, 1)) * 100)
        
        return {
            'word_count': word_count,
            'char_with_spaces': char_with_spaces,
            'char_without_spaces': char_without_spaces,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'unique_word_count': unique_word_count,
            'avg_word_length': round(avg_word_length, 1),
            'common_words': common_words,
            'readability_score': round(readability_score, 1),
            'has_text': True
        }
    
    @staticmethod
    def format_result(result, title="📊 Text Analysis"):
        """Format analysis results for display"""
        if not result:
            return "⚠️ No text to analyze. Please send me some text!"
        
        # Format common words
        common_words_str = ""
        if result['common_words']:
            for i, (word, count) in enumerate(result['common_words'][:5], 1):
                percentage = (count / result['word_count']) * 100
                common_words_str += f"  {i}. *{word}*: {count} times ({percentage:.1f}%)\n"
        else:
            common_words_str = "  None"
        
        # Build response
        response = f"""
*{title}*

📝 *Text Statistics:*
┌─────────────────────────┐
│ 📊 Words:              {result['word_count']}
│ ✏️ Characters (w/spaces): {result['char_with_spaces']}
│ ✏️ Characters (no spaces): {result['char_without_spaces']}
│ 📝 Sentences:          {result['sentence_count']}
│ 📄 Paragraphs:         {result['paragraph_count']}
│ 🔄 Unique Words:       {result['unique_word_count']}
│ 📐 Avg Word Length:    {result['avg_word_length']} chars
│ 📈 Readability Score:  {result['readability_score']}%
└─────────────────────────┘

🔍 *Top 5 Most Used Words:*
{common_words_str}

💡 *Need more?* Try /help for all commands!
"""
        return response

# ==================== BOT HANDLERS ====================

class BotHandlers:
    """All bot command and message handlers"""
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message with interactive buttons"""
        user = update.effective_user
        welcome_text = (
            f"👋 *Welcome, {user.first_name}!*\n\n"
            "I'm *Word23 Counter Bot* - your advanced text analysis assistant! 📊\n\n"
            "✨ *What I can do for you:*\n"
            "• Count words, characters, sentences & paragraphs\n"
            "• Find unique words and keyword density\n"
            "• Calculate readability scores\n"
            "• Analyze multiple languages\n\n"
            "🚀 *Quick Start:*\n"
            "• Send me any text - I'll analyze it instantly!\n"
            "• Use /count [text] for quick word counting\n"
            "• Use /stats for detailed analysis\n\n"
            "Let's get started! Send me something to analyze 👇"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Quick Count", callback_data="quick_count"),
                InlineKeyboardButton("📈 Full Stats", callback_data="full_stats")
            ],
            [
                InlineKeyboardButton("📝 Sample Text", callback_data="sample_text"),
                InlineKeyboardButton("❓ Help", callback_data="help_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"User {user.id} started the bot")

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display help information"""
        help_text = """
📖 *Help & Commands*

*Basic Commands:*
/start - Welcome message
/help - Show this help
/about - About this bot

*Analysis Commands:*
/count [text] - Count words instantly
/stats - Get detailed text statistics
/readability [text] - Check readability score

*Quick Tips:*
• Just send any text for automatic analysis
• Use inline buttons for quick actions
• Works with multiple languages
• Supports long texts up to 4096 characters

*Examples:*
/count Hello world! This is a test.
/stats (then send your text)
/readability Your text here

*Need help?* Just ask! 😊
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display about information"""
        about_text = """
🤖 *Word23 Counter Bot*

*Version:* 2.0.0
*Status:* 🟢 Online
*Creator:* @Word23

*Features:*
• Real-time text analysis
• Advanced word counting
• Character statistics
• Readability scoring
• Keyword density analysis
• Multi-language support

*Technical:*
• Python 3.11
• python-telegram-bot v20.7
• Deployed on Railway

*Source Code:* 
GitHub: word23counter-bot

Made with ❤️ for the Telegram community
"""
        await update.message.reply_text(about_text, parse_mode='Markdown')

    @staticmethod
    async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /count command"""
        if not context.args:
            await update.message.reply_text(
                "⚠️ *Usage:* `/count [your text here]`\n\n"
                "Example: `/count This is my text to count`",
                parse_mode='Markdown'
            )
            return
        
        text = ' '.join(context.args)
        analyzer = TextAnalyzer()
        result = analyzer.analyze(text)
        
        if result:
            response = analyzer.format_result(result, "📊 Quick Word Count")
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("⚠️ No valid text to analyze!")

    @staticmethod
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        keyboard = [
            [
                InlineKeyboardButton("📝 Enter Text", callback_data="enter_text"),
                InlineKeyboardButton("📊 Sample Text", callback_data="sample_stats")
            ],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📈 *Advanced Text Statistics*\n\n"
            "Choose an option below:\n"
            "• Enter your own text for analysis\n"
            "• Use a sample text to see the features\n\n"
            "I'll provide detailed statistics including:\n"
            "✅ Word, character, sentence counts\n"
            "✅ Unique words & keyword density\n"
            "✅ Readability score\n"
            "✅ And much more!",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    @staticmethod
    async def readability_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check readability of text"""
        if not context.args:
            await update.message.reply_text(
                "📖 *Readability Checker*\n\n"
                "Usage: `/readability [your text]`\n\n"
                "Example: `/readability This is a complex sentence with many long words.`",
                parse_mode='Markdown'
            )
            return
        
        text = ' '.join(context.args)
        analyzer = TextAnalyzer()
        result = analyzer.analyze(text)
        
        if result:
            score = result['readability_score']
            rating = "Excellent" if score > 80 else "Good" if score > 60 else "Fair" if score > 40 else "Needs Improvement"
            
            response = f"""
📖 *Readability Analysis*

*Score:* {score}%
*Rating:* {rating}

📊 *Details:*
• Total words: {result['word_count']}
• Long words (7+ chars): {sum(1 for w in text.split() if len(w) >= 7)}
• Average word length: {result['avg_word_length']} chars

💡 *Tips to improve readability:*
• Use shorter sentences
• Avoid complex words
• Break up long paragraphs
• Use active voice
"""
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("⚠️ No valid text to analyze!")

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message automatically"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Check if user is in stats mode
        if context.user_data.get('awaiting_stats'):
            context.user_data['awaiting_stats'] = False
            analyzer = TextAnalyzer()
            result = analyzer.analyze(text)
            if result:
                response = analyzer.format_result(result, "📈 Detailed Statistics")
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text("⚠️ No valid text to analyze!")
            return
        
        # Default: Auto-analyze
        analyzer = TextAnalyzer()
        result = analyzer.analyze(text)
        
        if result:
            # Show quick stats with option for more
            keyboard = [
                [
                    InlineKeyboardButton("📈 Full Stats", callback_data="analyze_this"),
                    InlineKeyboardButton("📖 Readability", callback_data="readability_this")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            response = analyzer.format_result(result, "📝 Auto Analysis")
            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("⚠️ No valid text to analyze!")

    @staticmethod
    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button presses"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Main menu options
        if query.data == "main_menu":
            await BotHandlers.start(update, context)
            return
        
        elif query.data == "help_menu":
            await BotHandlers.help_command(update, context)
            return
        
        # Stats options
        elif query.data == "enter_text":
            context.user_data['awaiting_stats'] = True
            await query.edit_message_text(
                "📝 *Enter Your Text*\n\n"
                "Please send me the text you want to analyze.\n"
                "I'll provide a complete statistical breakdown!",
                parse_mode='Markdown'
            )
            return
        
        elif query.data == "sample_stats":
            sample = """The quick brown fox jumps over the lazy dog. This is a sample text to demonstrate the statistical analysis features of this bot. It contains multiple sentences and different types of words to show how the analysis works in practice. The analysis will count words, characters, sentences, and provide readability scores."""
            
            analyzer = TextAnalyzer()
            result = analyzer.analyze(sample)
            response = analyzer.format_result(result, "📊 Sample Text Analysis")
            await query.edit_message_text(response, parse_mode='Markdown')
            return
        
        # Quick count
        elif query.data == "quick_count":
            await query.edit_message_text(
                "📊 *Quick Word Count*\n\n"
                "Send me any text or use:\n"
                "`/count [your text]`\n\n"
                "I'll count words instantly!",
                parse_mode='Markdown'
            )
            return
        
        # Full stats
        elif query.data == "full_stats":
            await BotHandlers.stats_command(update, context)
            return
        
        # Sample text
        elif query.data == "sample_text":
            sample = "This is a sample text to show you how Word23 Counter Bot works! It can analyze any text and provide detailed statistics. Try it with your own text."
            
            analyzer = TextAnalyzer()
            result = analyzer.analyze(sample)
            response = analyzer.format_result(result, "📊 Sample Analysis")
            await query.edit_message_text(response, parse_mode='Markdown')
            return
        
        # Analyze this specific text
        elif query.data == "analyze_this":
            # Get the last message content (stored in context)
            if context.user_data.get('last_text'):
                text = context.user_data['last_text']
                analyzer = TextAnalyzer()
                result = analyzer.analyze(text)
                if result:
                    response = analyzer.format_result(result, "📈 Full Analysis")
                    await query.edit_message_text(response, parse_mode='Markdown')
            return
        
        # Readability of this text
        elif query.data == "readability_this":
            if context.user_data.get('last_text'):
                text = context.user_data['last_text']
                # Reconstruct the readability command
                await BotHandlers.readability_command(
                    update, 
                    ContextTypes.DEFAULT_TYPE(
                        args=text.split(),
                        message=update.effective_message,
                        chat_data=context.chat_data,
                        user_data=context.user_data,
                        bot_data=context.bot_data
                    )
                )
            return

# ==================== MAIN APPLICATION ====================

def main():
    """Main function to run the bot"""
    logger.info("🤖 Starting Word23 Counter Bot...")
    
    # Create application
    application = ApplicationBuilder() \
        .token(BOT_TOKEN) \
        .build()
    
    # Store last text per user for analysis features
    async def store_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.text:
            context.user_data['last_text'] = update.message.text
        return None
    
    # Add command handlers
    application.add_handler(CommandHandler("start", BotHandlers.start))
    application.add_handler(CommandHandler("help", BotHandlers.help_command))
    application.add_handler(CommandHandler("about", BotHandlers.about_command))
    application.add_handler(CommandHandler("count", BotHandlers.count_command))
    application.add_handler(CommandHandler("stats", BotHandlers.stats_command))
    application.add_handler(CommandHandler("readability", BotHandlers.readability_command))
    
    # Add message handler for text messages
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda u, c: store_text(u, c) or BotHandlers.handle_text(u, c)
        )
    )
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(BotHandlers.button_callback))
    
    # Start the bot
    if ENVIRONMENT == 'production':
        logger.info("🚀 Starting bot in production mode with webhook...")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=None  # Railway handles this automatically
        )
    else:
        logger.info("🔄 Starting bot in polling mode...")
        application.run_polling()

if __name__ == '__main__':
    main()
