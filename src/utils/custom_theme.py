"""
Custom dark theme for the ToDo application.
"""
import ttkbootstrap as tb
from ttkbootstrap.themes import standard

def create_custom_dark_theme():
    """
    Create and register a custom dark theme using the specified color palette.
    
    Color Palette:
    - #1C1C1C (Very Dark Gray - Background)
    - #3D3D3D (Dark Gray - Widget Background)
    - #5E5E5E (Medium Gray - Borders, Separators)
    - #7F7F7F (Gray - Secondary Text)
    - #FFFFFF (White - Primary Text)
    
    Returns:
        str: The name of the registered theme
    """
    # Theme colors
    DARK_BG = "#1C1C1C"       # Very dark gray (background)
    WIDGET_BG = "#3D3D3D"      # Dark gray (widget background)
    BORDER = "#5E5E5E"         # Medium gray (borders)
    SECONDARY_TEXT = "#7F7F7F" # Gray (secondary text)
    PRIMARY_TEXT = "#FFFFFF"   # White for primary text (changed from #A0A0A0)
    
    # Accent colors for priorities and statuses
    HIGH_PRIORITY = "#FF5252"  # Red for high priority
    MEDIUM_PRIORITY = "#FFD740" # Amber for medium priority
    LOW_PRIORITY = "#4FC3F7"   # Light blue for low priority
    SUCCESS = "#66BB6A"        # Green for completed/success
    
    # Custom theme definition with required color attributes
    todowidget = {
        "type": "dark",
        "colors": {
            # Required positional arguments for the Colors class
            "light": "#FBFBFB",
            "dark": DARK_BG,
            "active": WIDGET_BG,
            
            # Other theme colors
            "primary": WIDGET_BG,
            "secondary": BORDER,
            "success": SUCCESS,
            "info": LOW_PRIORITY,
            "warning": MEDIUM_PRIORITY,
            "danger": HIGH_PRIORITY,
            "bg": DARK_BG,
            "fg": PRIMARY_TEXT,
            "selectbg": BORDER,
            "selectfg": PRIMARY_TEXT,
            "border": BORDER,
            "inputfg": PRIMARY_TEXT,
            "inputbg": DARK_BG,
        },
        "font": "Helvetica 10",
    }
    
    # Register the theme
    theme_name = "todowidget"
    standard.STANDARD_THEMES[theme_name] = todowidget
    
    return theme_name
