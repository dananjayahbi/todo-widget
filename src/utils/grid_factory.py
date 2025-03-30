"""
Factory for creating appropriate grid layouts based on requirements.
"""
from .grid_layout import SimpleGridLayout, VirtualizedGridLayout
from .enhanced_grid_layout import EnhancedGridLayout

def create_grid_layout(parent_frame, layout_type="simple", **kwargs):
    """
    Factory function to create the appropriate grid layout.
    
    Args:
        parent_frame: The frame where items will be placed
        layout_type: Type of layout to create ("simple", "virtualized", "enhanced")
        **kwargs: Additional arguments to pass to the layout constructor
    
    Returns:
        A grid layout instance of the requested type
    """
    canvas = kwargs.pop("canvas", None)
    min_column_width = kwargs.pop("min_column_width", 300)
    padding = kwargs.pop("padding", 5)
    
    if layout_type == "simple":
        return SimpleGridLayout(
            parent_frame=parent_frame,
            min_column_width=min_column_width,
            padding=padding
        )
    elif layout_type == "virtualized":
        if canvas is None:
            raise ValueError("canvas parameter is required for virtualized layout")
        return VirtualizedGridLayout(
            parent_frame=parent_frame,
            canvas=canvas,
            min_column_width=min_column_width,
            padding=padding
        )
    elif layout_type == "enhanced":
        animation_speed = kwargs.pop("animation_speed", 10)
        return EnhancedGridLayout(
            parent_frame=parent_frame,
            min_column_width=min_column_width,
            padding=padding,
            animation_speed=animation_speed
        )
    else:
        raise ValueError(f"Unknown layout type: {layout_type}")
