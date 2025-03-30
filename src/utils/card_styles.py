"""
Utility for consistent card styling across the application.
"""

def apply_card_styles(frame, min_width=300, min_height=180):
    """
    Apply consistent styling to card frames.
    
    Args:
        frame: Frame to style
        min_width: Minimum width for the frame
        min_height: Minimum height for the frame
    """
    # Set fixed width and height for each card
    frame.configure(width=min_width, height=min_height)
    frame.pack_propagate(False)  # Prevent the frame from shrinking
    
    # Ensure the frame doesn't expand beyond its fixed width
    if hasattr(frame, 'grid_propagate'):
        frame.grid_propagate(False)
        
    return frame
