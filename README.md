# Telegram Quote Bot

A Telegram bot that creates beautiful quote cards from replied messages. When users reply to a message and mention the bot, it generates a visually appealing image with the original message, author's name, and profile picture.

## Features

- 🎨 **Beautiful Quote Cards**: Generate quote cards with customizable background colors
- 🌈 **Color Support**: Use named colors (red, blue, green, etc.) or hex codes (#FF5733)
- 👤 **Profile Pictures**: Automatically includes the original author's profile picture
- 🎯 **Group Chat Ready**: Works seamlessly in group conversations
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- 🔧 **Extensible**: Modular architecture for easy feature additions

## Quick Start

### Prerequisites

- Python 3.11+
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))
- Docker (optional, for containerized deployment)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-quote-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **View logs**
   ```bash
   docker-compose logs -f quote-bot
   ```

## Usage

### Basic Usage

1. Add the bot to your group chat
2. Reply to any message you want to quote
3. Mention the bot in your reply: `@your_bot_name`
4. The bot will generate and send a quote card

### With Custom Colors

- **Named colors**: `@your_bot_name red`
- **Hex colors**: `@your_bot_name #FF5733`

### Available Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help information
- `/colors` - List all available color names

### Supported Colors

**Named Colors:**
- red, pink, purple, blue, cyan, green
- yellow, orange, brown, gray, grey
- black, white

**Custom Colors:**
- Any valid hex color (e.g., #FF5733, #00FF00)

## Project Structure

```
telegram-quote-bot/
├── src/
│   ├── __init__.py
│   ├── bot.py              # Main bot logic
│   ├── image_generator.py  # Quote card generation
│   ├── color_utils.py      # Color parsing utilities
│   └── config.py           # Configuration management
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container definition
├── docker-compose.yaml    # Docker Compose configuration
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather | Yes |

### Customization

The bot is designed to be easily extensible. Key areas for customization:

- **Colors**: Add new colors in `src/color_utils.py`
- **Card Design**: Modify dimensions and styling in `src/image_generator.py`
- **Bot Behavior**: Extend functionality in `src/bot.py`

## Development

### Setting up Development Environment

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run in development mode**
   ```bash
   python main.py
   ```

### Adding New Features

The modular architecture makes it easy to add new features:

1. **New Commands**: Add handlers in `src/bot.py`
2. **Image Effects**: Extend `src/image_generator.py`
3. **Color Schemes**: Update `src/color_utils.py`
4. **Configuration**: Add options in `src/config.py`

## Troubleshooting

### Common Issues

**Bot doesn't respond:**
- Check if bot token is correctly set in `.env`
- Ensure bot is added to the group chat
- Verify bot has permission to read messages

**Image generation fails:**
- Check if PIL dependencies are installed
- Verify font files are available (fallback fonts are used automatically)

**Profile pictures not loading:**
- This is normal for users with private profiles
- Bot will generate initials-based avatars as fallback

### Docker Issues

**Container won't start:**
```bash
docker-compose logs quote-bot
```

**Permission issues:**
```bash
# Ensure proper file permissions
chmod +x main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Look through existing GitHub issues
3. Create a new issue with detailed information

## Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Image processing powered by [Pillow](https://python-pillow.org/)
- Containerized with Docker