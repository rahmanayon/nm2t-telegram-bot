#!/usr/bin/env python3
"""
NM2T Telegram Bot - Newsletter distribution bot for NM2T
"""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
import feedparser

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

# Beehiiv feed URL - configurable via environment variable
BEEHIIV_FEED_URL = os.getenv('BEEHIIV_FEED_URL', 'https://newsletter.nm2t.com/feed')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Start command handler - sends welcome message
    """
    welcome_text = (
        "Welcome to the NM2T Newsletter Bot! 🚀\n\n"
        "I help you stay updated with the latest NM2T newsletter content.\n\n"
        "Available commands:\n"
        "/latest - Get the latest newsletter issue\n"
        "/subscribe - Subscribe to newsletter updates\n"
        "/about - Learn about NM2T\n"
        "/help - Show this help message\n"
    )
    await update.message.reply_text(welcome_text)

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Latest command handler - fetches and displays latest newsletter
    """
    try:
        await update.message.reply_text("Fetching latest newsletter...")
        
        feed = feedparser.parse(BEEHIIV_FEED_URL.strip())
        
        if not feed.entries:
            await update.message.reply_text(
                "No newsletter entries found. The feed may not be configured yet. "
                "Please check back later or visit https://newsletter.nm2t.com"
            )
            return
        
        # Get the latest entry
        latest_entry = feed.entries[0]
        title = latest_entry.get('title', 'Untitled')
        link = latest_entry.get('link', 'https://newsletter.nm2t.com')
        summary = latest_entry.get('summary', 'No summary available')
        
        # Truncate summary to 500 chars
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        # Format the message
        message = (
            f"*Latest Issue: {title}*\n\n"
            f"{summary}\n\n"
            f"[Read Full Article]({link})"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
    except Exception as e:
        logger.error(f"Error fetching latest newsletter: {e}")
        await update.message.reply_text(
            f"Sorry, I encountered an error fetching the latest newsletter.\n"
            f"Error: {str(e)[:100]}\n\n"
            f"Visit https://newsletter.nm2t.com to read directly."
        )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Subscribe command handler
    """
    subscribe_text = (
        "Thanks for your interest in subscribing! 📬\n\n"
        "You can subscribe to the NM2T newsletter directly at:\n"
        "https://newsletter.nm2t.com\n\n"
        "Once subscribed, you'll receive:\n"
        "• Latest stories and insights\n"
        "• Weekly curated content\n"
        "• Exclusive updates\n\n"
        "Use /latest to get the most recent issue anytime!"
    )
    await update.message.reply_text(subscribe_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    About command handler
    """
    about_text = (
        "About NM2T Newsletter 📰\n\n"
        "NM2T is a newsletter dedicated to providing insightful content, "
        "industry news, and valuable resources.\n\n"
        "We cover:\n"
        "• Technology trends\n"
        "• Industry insights\n"
        "• Best practices\n"
        "• Community highlights\n\n"
        "Visit: https://newsletter.nm2t.com"
    )
    await update.message.reply_text(about_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Help command handler
    """
    help_text = (
        "NM2T Newsletter Bot Help 🤖\n\n"
        "Available Commands:\n"
        "/start - Start the bot and see welcome message\n"
        "/latest - Get the latest newsletter issue\n"
        "/subscribe - Learn how to subscribe\n"
        "/about - About NM2T Newsletter\n"
        "/help - Show this help message\n\n"
        "Use these commands to navigate and get the content you need!"
    )
    await update.message.reply_text(help_text)

def main() -> None:
    """
    Start the bot
    """
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("latest", latest))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot
    logger.info("Starting NM2T Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
