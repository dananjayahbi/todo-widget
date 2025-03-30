"""
Helper utilities for the ToDo application.
"""
import tkinter as tk
from datetime import datetime
from dateutil import parser
from ttkbootstrap.dialogs import Querybox

def format_date(date_str, format_str="%b %d, %Y"):
    """
    Format date string for consistent display across the application.
    
    Args:
        date_str: ISO format date string
        format_str: Output date format string
            
    Returns:
        str: Formatted date string or "Not set" if None
    """
    if not date_str:
        return "Not set"
    
    try:
        date_obj = parser.parse(date_str)
        return date_obj.strftime(format_str)
    except Exception:
        return date_str

def center_window(window, parent=None):
    """
    Center a window on the screen or parent window.
    
    Args:
        window: Window to center
        parent: Parent window (if None, center on screen)
    """
    window.update_idletasks()
    
    if parent:
        # Center on parent
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        width = window.winfo_width()
        height = window.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
    else:
        # Center on screen
        width = window.winfo_width()
        height = window.winfo_height()
        
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
    
    window.geometry(f"+{x}+{y}")

def get_centered_date(parent, title="Select Date"):
    """
    Open a centered date picker dialog.
    
    Args:
        parent: Parent window
        title: Dialog title
            
    Returns:
        date object or None if canceled
    """
    # Get the date using ttkbootstrap's Querybox
    date_result = Querybox.get_date(parent=parent, title=title)
    
    # Find the date picker dialog (it's usually the last toplevel created)
    for widget in parent.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.winfo_viewable():
            # Center the found dialog
            center_window(widget, parent)
            break
    
    return date_result
