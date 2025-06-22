import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from .config import TELEGRAM_BOT_TOKEN
from .image_generator import QuoteCardGenerator
from .color_utils import get_available_colors

# Configure logging - reduce telegram library verbosity
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Reduce telegram library logging
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

class QuoteBot:
    def __init__(self):
        self.generator = QuoteCardGenerator()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up bot command and message handlers."""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("colors", self.colors_command))
        self.application.add_handler(MessageHandler(
            filters.TEXT & (~filters.COMMAND), 
            self.handle_message
        ))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_text = (
            "👋 Welcome to Quote Bot!\n\n"
            "To create a quote card:\n"
            "1. Reply to any message\n"
            "2. Mention me (@your_bot_username) in your reply\n"
            "3. Optionally specify a color (e.g., 'red' or '#FF5733')\n\n"
            "Example: '@your_bot_username blue' or '@your_bot_username #FF5733'\n\n"
            "Use /colors to see available color names\n"
            "Use /help for more information"
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "🎨 Quote Bot Help\n\n"
            "**How to use:**\n"
            "1. Reply to any message in a group chat\n"
            "2. Mention the bot in your reply\n"
            "3. Optionally add a color name or hex code\n\n"
            "**Color formats:**\n"
            "• Named colors: red, blue, green, etc.\n"
            "• Hex colors: #FF5733, #00FF00, etc.\n\n"
            "**Commands:**\n"
            "/start - Show welcome message\n"
            "/help - Show this help\n"
            "/colors - List available color names\n\n"
            "**Examples:**\n"
            "• @bot_name\n"
            "• @bot_name red\n"
            "• @bot_name #FF5733"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def colors_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /colors command."""
        colors = get_available_colors()
        colors_text = "🎨 Available colors:\n\n" + ", ".join(colors)
        colors_text += "\n\nYou can also use hex colors like #FF5733"
        await update.message.reply_text(colors_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages that mention the bot."""
        message = update.message
        bot_username = context.bot.username
        
        # Check if message is a reply and mentions the bot
        if not message.reply_to_message:
            return
        
        if not message.text or f"@{bot_username}" not in message.text:
            return
        
        try:
            # Extract color from message (remove bot mention)
            text_parts = message.text.replace(f"@{bot_username}", "").strip().split()
            color = text_parts[0] if text_parts else "blue"
            
            # Get original message details
            original_message = message.reply_to_message
            author_name = self._get_user_display_name(original_message.from_user)
            message_text = original_message.text or "[Media or unsupported content]"
            
            # Log quote request
            chat_info = f"@{message.chat.username}" if message.chat.username else f"Chat ID: {message.chat.id}"
            requester = self._get_user_display_name(message.from_user)
            logger.info(f"📝 Quote request: {requester} in {chat_info} -> quoting '{author_name}' with color '{color}'")
            
            # Get avatar URL
            avatar_url = None
            if original_message.from_user.username:
                try:
                    # Get user profile photos
                    photos = await context.bot.get_user_profile_photos(
                        original_message.from_user.id, 
                        limit=1
                    )
                    if photos.photos:
                        # Get the largest photo
                        photo = photos.photos[0][-1]
                        file = await context.bot.get_file(photo.file_id)
                        avatar_url = file.file_path
                except Exception as e:
                    logger.warning(f"Failed to get profile photo: {e}")
            
            # Generate quote card
            quote_image = self.generator.generate_quote_card(
                message_text=message_text,
                author_name=author_name,
                avatar_url=avatar_url,
                background_color=color
            )
            
            # Send the image
            await message.reply_photo(
                photo=quote_image,
                caption=f"Quote by {author_name}"
            )
            
            logger.info(f"✅ Quote card generated successfully for {author_name}")
            
        except Exception as e:
            logger.error(f"Error generating quote card: {e}")
            await message.reply_text(
                "❌ Sorry, I couldn't generate the quote card. Please try again."
            )
    
    def _get_user_display_name(self, user) -> str:
        """Get user's display name."""
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif user.first_name:
            return user.first_name
        elif user.username:
            return f"@{user.username}"
        else:
            return "Unknown User"
    
    def run(self):
        """Start the bot."""
        logger.info("🤖 Starting Quote Bot...")
        self.application.run_polling(
            drop_pending_updates=True  # Ignore pending updates on startup
        )