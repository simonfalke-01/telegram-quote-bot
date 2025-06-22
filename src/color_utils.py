import re
from typing import Tuple

SOFT_COLOR_PALETTE = {
    'red': '#FF6B6B',
    'pink': '#FF8CC8',
    'purple': '#9B59B6',
    'blue': '#74B9FF',
    'cyan': '#00CEC9',
    'green': '#55A3FF',
    'yellow': '#FDCB6E',
    'orange': '#E17055',
    'brown': '#8D6E63',
    'gray': '#B2BEC3',
    'grey': '#B2BEC3',
    'black': '#2D3436',
    'white': '#FFFFFF'
}

def parse_color(color_input: str) -> Tuple[int, int, int]:
    """
    Parse color input and return RGB tuple.
    Accepts color names from soft palette or hex values.
    """
    color_input = color_input.lower().strip()
    
    # Check if it's a hex color
    if color_input.startswith('#'):
        hex_color = color_input[1:]
        if len(hex_color) == 6 and re.match(r'^[0-9a-f]{6}$', hex_color):
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        else:
            raise ValueError(f"Invalid hex color format: {color_input}")
    
    # Check if it's a named color
    if color_input in SOFT_COLOR_PALETTE:
        hex_color = SOFT_COLOR_PALETTE[color_input][1:]
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Default to blue if color not recognized
    return parse_color('blue')

def get_available_colors() -> list:
    """Return list of available color names."""
    return list(SOFT_COLOR_PALETTE.keys())