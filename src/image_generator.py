import io
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
from .color_utils import parse_color

class QuoteCardGenerator:
    def __init__(self):
        self.card_width = 800
        self.card_height = 400
        self.padding = 40
        self.avatar_size = 80
        
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with fallback to default."""
        try:
            font_path = "/System/Library/Fonts/Arial.ttf" if not bold else "/System/Library/Fonts/Arial Bold.ttf"
            return ImageFont.truetype(font_path, size)
        except:
            try:
                return ImageFont.truetype("arial.ttf", size)
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
    
    def _create_default_avatar(self, name: str) -> Image.Image:
        """Create a default avatar with initials."""
        avatar = Image.new('RGBA', (self.avatar_size, self.avatar_size), (200, 200, 200, 255))
        draw = ImageDraw.Draw(avatar)
        
        # Get initials
        initials = ''.join([word[0].upper() for word in name.split()[:2]])
        if not initials:
            initials = 'U'
        
        font = self._get_font(40, bold=True)
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.avatar_size - text_width) // 2
        y = (self.avatar_size - text_height) // 2
        
        draw.text((x, y), initials, fill=(100, 100, 100, 255), font=font)
        
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
    
    def generate_quote_card(self, 
                          message_text: str, 
                          author_name: str, 
                          avatar_url: Optional[str] = None,
                          background_color: str = 'blue') -> io.BytesIO:
        """Generate a quote card image."""
        
        # Parse background color
        bg_color = parse_color(background_color)
        
        # Create image
        image = Image.new('RGB', (self.card_width, self.card_height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Create card background
        card_margin = 20
        card_bg = (255, 255, 255, 240)
        card_coords = [
            card_margin, 
            card_margin, 
            self.card_width - card_margin, 
            self.card_height - card_margin
        ]
        
        # Draw card with rounded corners (approximation)
        corner_radius = 15
        draw.rounded_rectangle(card_coords, corner_radius, fill=card_bg[:3])
        
        # Get avatar
        if avatar_url:
            avatar = self._download_avatar(avatar_url)
        else:
            avatar = None
            
        if not avatar:
            avatar = self._create_default_avatar(author_name)
        
        # Position avatar
        avatar_x = card_margin + self.padding
        avatar_y = card_margin + self.padding
        
        # Paste avatar
        if avatar.mode == 'RGBA':
            image.paste(avatar, (avatar_x, avatar_y), avatar)
        else:
            image.paste(avatar, (avatar_x, avatar_y))
        
        # Author name
        name_font = self._get_font(32, bold=True)
        name_x = avatar_x + self.avatar_size + 20
        name_y = avatar_y + 10
        draw.text((name_x, name_y), author_name, fill=(50, 50, 50), font=name_font)
        
        # Message text
        text_font = self._get_font(28)
        text_start_y = avatar_y + self.avatar_size + 30
        text_max_width = self.card_width - (2 * card_margin) - (2 * self.padding)
        
        # Wrap text
        lines = self._wrap_text(message_text, text_font, text_max_width)
        
        # Limit lines to fit in card
        line_height = 35  # Increased line height for larger font
        max_lines = (self.card_height - text_start_y - card_margin - self.padding) // line_height
        if len(lines) > max_lines:
            lines = lines[:max_lines-1] + ['...']
        
        # Draw text lines
        for i, line in enumerate(lines):
            line_y = text_start_y + (i * line_height)
            draw.text((card_margin + self.padding, line_y), line, fill=(70, 70, 70), font=text_font)
        
        # Save to BytesIO
        output = io.BytesIO()
        image.save(output, format='PNG')
        output.seek(0)
        
        return output