import io
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
from .color_utils import parse_color

class QuoteCardGenerator:
    def __init__(self):
        # Base dimensions - will be dynamically adjusted
        self.base_width = 1200
        self.min_height = 400
        self.max_height = 1000
        self.padding = 60
        self.avatar_size = 200  # Increased for horizontal layout
        self.card_margin = 60  # Increased to show more background
        
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with fallback to default."""
        # List of font paths to try (macOS, Ubuntu/Debian, Windows)
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Ubuntu/Debian
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Ubuntu/Debian Bold
            "/usr/share/fonts/TTF/DejaVuSans.ttf",  # Some Linux distributions
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",  # Some Linux distributions Bold
            "arial.ttf",  # Windows fallback
            "Arial.ttf"   # Windows fallback
        ]
        
        # Select appropriate paths based on bold requirement
        if bold:
            priority_paths = [
                "/System/Library/Fonts/Arial Bold.ttf",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Ubuntu/Debian
                "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",  # Some Linux
            ]
            font_paths = priority_paths + font_paths
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # Ultimate fallback - load default font at specified size
        try:
            return ImageFont.load_default(size=size)
        except:
            return ImageFont.load_default()
    
    def _download_avatar(self, avatar_url: str) -> Optional[Image.Image]:
        """Download and process user avatar."""
        try:
            response = requests.get(avatar_url, timeout=10)
            response.raise_for_status()
            avatar = Image.open(io.BytesIO(response.content))
            avatar = avatar.convert('RGBA')
            avatar = avatar.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (self.avatar_size, self.avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, self.avatar_size, self.avatar_size], fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (self.avatar_size, self.avatar_size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0))
            output.putalpha(mask)
            
            return output
        except Exception as e:
            print(f"Failed to download avatar: {e}")
            return None
    
    def _create_default_avatar(self, name: str, bg_color: Tuple[int, int, int]) -> Image.Image:
        """Create a default avatar with initials and border."""
        # Create avatar with dark theme colors
        avatar_bg = (60, 60, 60, 255)  # Dark gray for dark theme
        avatar = Image.new('RGBA', (self.avatar_size, self.avatar_size), avatar_bg)
        draw = ImageDraw.Draw(avatar)
        
        # Get initials
        initials = ''.join([word[0].upper() for word in name.split()[:2]])
        if not initials:
            initials = 'U'
        
        font = self._get_font(100, bold=True)  # Increased font size
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.avatar_size - text_width) // 2
        y = (self.avatar_size - text_height) // 2
        
        draw.text((x, y), initials, fill=(200, 200, 200, 255), font=font)  # Light text for dark theme
        
        # Make circular
        mask = Image.new('L', (self.avatar_size, self.avatar_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, self.avatar_size, self.avatar_size], fill=255)
        
        output = Image.new('RGBA', (self.avatar_size, self.avatar_size), (0, 0, 0, 0))
        output.paste(avatar, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _calculate_dynamic_dimensions(self, message_text: str, author_name: str) -> Tuple[int, int]:
        """Calculate optimal card dimensions based on content length."""
        # Estimate text dimensions
        text_font = self._get_font(48)  # Use actual text font size
        name_font = self._get_font(52, bold=True)
        
        # Calculate text area width (accounting for horizontal layout)
        text_area_width = self.base_width - (2 * self.card_margin) - (2 * self.padding) - self.avatar_size - 40
        
        # Wrap text to get line count
        lines = self._wrap_text(message_text, text_font, text_area_width)
        
        # Calculate required height
        line_height = 60
        name_height = 65
        text_height = len(lines) * line_height
        avatar_height = self.avatar_size
        
        # Total content height (max of avatar height and text + name height)
        content_height = max(avatar_height, name_height + text_height + 20)  # 20px spacing
        
        # Calculate card height with padding
        card_height = content_height + (2 * self.card_margin) + (2 * self.padding)
        
        # Constrain to min/max bounds
        card_height = max(self.min_height, min(card_height, self.max_height))
        
        return self.base_width, card_height
    
    def generate_quote_card(self, 
                          message_text: str, 
                          author_name: str, 
                          avatar_url: Optional[str] = None,
                          background_color: str = 'blue') -> io.BytesIO:
        """Generate a quote card image."""
        
        # Calculate dynamic dimensions
        card_width, card_height = self._calculate_dynamic_dimensions(message_text, author_name)
        
        # Parse background color (dark theme by default)
        bg_color = parse_color(background_color) if background_color != 'blue' else (45, 45, 55)  # Dark blue-gray
        
        # Create image
        image = Image.new('RGB', (card_width, card_height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Create card background (dark theme)
        card_bg = (35, 35, 40)  # Dark card background
        card_coords = [
            self.card_margin, 
            self.card_margin, 
            card_width - self.card_margin, 
            card_height - self.card_margin
        ]
        
        # Draw card with rounded corners
        corner_radius = 25
        draw.rounded_rectangle(card_coords, corner_radius, fill=card_bg)
        
        # Get avatar
        if avatar_url:
            avatar = self._download_avatar(avatar_url)
        else:
            avatar = None
            
        if not avatar:
            avatar = self._create_default_avatar(author_name, bg_color)
        
        # Add border to avatar (matching background color but lighter)
        border_color = tuple(min(255, c + 30) for c in bg_color)  # Lighter version of bg
        bordered_avatar = Image.new('RGBA', (self.avatar_size + 8, self.avatar_size + 8), (*border_color, 255))
        
        # Create circular border mask
        border_mask = Image.new('L', (self.avatar_size + 8, self.avatar_size + 8), 0)
        border_draw = ImageDraw.Draw(border_mask)
        border_draw.ellipse([0, 0, self.avatar_size + 8, self.avatar_size + 8], fill=255)
        bordered_avatar.putalpha(border_mask)
        
        # Position avatar (horizontal layout)
        avatar_x = self.card_margin + self.padding
        avatar_y = self.card_margin + self.padding
        
        # Paste bordered avatar first
        image.paste(bordered_avatar, (avatar_x - 4, avatar_y - 4), bordered_avatar)
        
        # Paste main avatar
        if avatar.mode == 'RGBA':
            image.paste(avatar, (avatar_x, avatar_y), avatar)
        else:
            image.paste(avatar, (avatar_x, avatar_y))
        
        # Text area positioning (horizontal layout)
        text_area_x = avatar_x + self.avatar_size + 40
        text_area_width = card_width - text_area_x - self.card_margin - self.padding
        
        # Author name (positioned in text area)
        name_font = self._get_font(52, bold=True)
        name_y = avatar_y + 10
        draw.text((text_area_x, name_y), author_name, fill=(220, 220, 220), font=name_font)  # Light text for dark theme
        
        # Message text
        text_font = self._get_font(48)
        text_start_y = name_y + 65  # Start below name
        text_max_width = text_area_width
        
        # Wrap text
        lines = self._wrap_text(message_text, text_font, text_max_width)
        
        # Limit lines to fit in card
        line_height = 60
        available_height = card_height - text_start_y - self.card_margin - self.padding
        max_lines = available_height // line_height
        if len(lines) > max_lines:
            lines = lines[:max_lines-1] + ['...']
        
        # Draw text lines
        for i, line in enumerate(lines):
            line_y = text_start_y + (i * line_height)
            draw.text((text_area_x, line_y), line, fill=(190, 190, 190), font=text_font)  # Light gray text for dark theme
        
        # Save to BytesIO with high quality
        output = io.BytesIO()
        image.save(output, format='PNG', optimize=True, quality=95, dpi=(300, 300))
        output.seek(0)
        
        return output