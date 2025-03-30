"""
Grid layout manager for responsive layouts.
"""
import tkinter as tk
from tkinter import ttk
import math

class SimpleGridLayout:
    """
    A simplified and more efficient grid layout manager.
    """
    
    def __init__(self, parent_frame, min_column_width=300, padding=5):
        """
        Initialize the grid layout manager.
        
        Args:
            parent_frame: The frame where items will be placed
            min_column_width: Minimum width for each column
            padding: Padding between grid items
        """
        self.parent_frame = parent_frame
        self.min_column_width = min_column_width
        self.padding = padding
        self.items = []
        self.current_columns = 1
        
        # Configure the parent frame for grid layout
        parent_frame.columnconfigure(0, weight=1)
    
    def calculate_columns(self):
        """
        Calculate the number of columns based on parent width.
        
        Returns:
            int: Number of columns to display
        """
        # Get parent width - try different approaches depending on widget hierarchy
        parent_width = self.parent_frame.winfo_width()
        
        if parent_width < 50:  # Not yet properly laid out
            # Try to get width from master
            if hasattr(self.parent_frame, 'master') and self.parent_frame.master:
                parent_width = self.parent_frame.master.winfo_width()
            
            # If still not available, try the parent's parent
            if parent_width < 50 and hasattr(self.parent_frame.master, 'master'):
                parent_width = self.parent_frame.master.master.winfo_width()
                
            # If all else fails, use a default width
            if parent_width < 50:
                parent_width = 800  # Reasonable default
        
        # Calculate columns with padding consideration
        available_width = parent_width - (2 * self.padding)  # Account for outer padding
        item_width_with_padding = self.min_column_width + (2 * self.padding)
        columns = max(1, int(available_width / item_width_with_padding))
        
        return columns
    
    def clear(self):
        """
        Clear all items from the grid.
        """
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        self.items = []
    
    def add_item(self, item_widget):
        """
        Add an item to the grid.
        
        Args:
            item_widget: Widget to add to the grid
        """
        self.items.append(item_widget)
        self.update_layout()
    
    def update_layout(self):
        """
        Update the layout of all items in the grid.
        """
        # Remove all items from the grid
        for item in self.items:
            if hasattr(item, 'grid_forget'):
                item.grid_forget()
        
        # Calculate columns based on current width
        columns = self.calculate_columns()
        
        # Update column configuration
        for i in range(columns):
            self.parent_frame.columnconfigure(i, weight=1)
        
        # Place items in grid
        for i, item in enumerate(self.items):
            row = i // columns
            col = i % columns
            
            # Grid the item with proper padding
            item.grid(row=row, column=col, sticky="nsew", padx=self.padding, pady=self.padding)
        
        # Store current column count
        self.current_columns = columns
    
    def refresh_on_resize(self, event=None):
        """
        Refresh the layout if the number of columns would change.
        
        Args:
            event: The resize event (optional)
        """
        new_columns = self.calculate_columns()
        if new_columns != self.current_columns:
            self.update_layout()

class VirtualizedGridLayout:
    """
    A virtualized grid layout that only renders visible items for better performance.
    Useful for very large collections of items.
    """
    
    def __init__(self, parent_frame, canvas, min_column_width=300, padding=5):
        """
        Initialize the virtualized grid layout manager.
        
        Args:
            parent_frame: The frame inside the canvas where items will be placed
            canvas: The canvas for scrolling and visibility detection
            min_column_width: Minimum width for each column
            padding: Padding between grid items
        """
        self.parent_frame = parent_frame
        self.canvas = canvas
        self.min_column_width = min_column_width
        self.padding = padding
        self.all_items = []  # All item data
        self.visible_items = {}  # Currently visible widgets
        self.current_columns = 1
        
        # Configure scroll region updates
        self.parent_frame.bind("<Configure>", self._update_scroll_region)
        
        # Configure visibility checks on scroll
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<Motion>", lambda e: self.check_visibility())
        
        # Also check visibility when scrolled
        # This handles both mouse wheel and scrollbar interactions
        self.canvas.bind("<MouseWheel>", lambda e: self.parent_frame.after(10, self.check_visibility))
        self.canvas.bind("<Button-4>", lambda e: self.parent_frame.after(10, self.check_visibility))
        self.canvas.bind("<Button-5>", lambda e: self.parent_frame.after(10, self.check_visibility))
    
    def _update_scroll_region(self, event=None):
        """Update the canvas scroll region to include all items."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize events."""
        new_columns = self.calculate_columns()
        if new_columns != self.current_columns:
            self.current_columns = new_columns
            self.update_layout()
            self.check_visibility()
    
    def calculate_columns(self):
        """Calculate the number of columns based on canvas width."""
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 50:  # Not yet properly sized
            return 1
            
        width_with_padding = self.min_column_width + (2 * self.padding)
        columns = max(1, int(canvas_width / width_with_padding))
        return columns
    
    def clear(self):
        """Clear all items from the grid."""
        for widget in self.visible_items.values():
            widget.destroy()
        self.all_items = []
        self.visible_items = {}
    
    def add_item(self, item_factory, item_data):
        """
        Add an item to the grid using a factory function.
        
        Args:
            item_factory: Function that creates a widget given data and parent
            item_data: Data for the item
        """
        self.all_items.append((item_factory, item_data))
        self.update_layout()
        self.check_visibility()
    
    def update_layout(self):
        """Update the layout based on the current column count."""
        # Remove all visible items
        for widget in self.visible_items.values():
            widget.destroy()
        self.visible_items = {}
        
        # Calculate the total rows needed and configure the parent frame height
        total_items = len(self.all_items)
        total_rows = math.ceil(total_items / self.current_columns)
        total_height = total_rows * (self.min_column_width + (2 * self.padding))
        
        # Update parent frame size to accommodate all items
        self.parent_frame.configure(height=total_height, width=self.canvas.winfo_width())
        
        # Check which items are visible and create them
        self.check_visibility()
    
    def check_visibility(self):
        """
        Check which items are visible in the viewport and create/destroy widgets accordingly.
        """
        if not self.all_items:
            return
            
        # Get the visible region of the canvas
        canvas_top = self.canvas.canvasy(0)
        canvas_bottom = canvas_top + self.canvas.winfo_height()
        canvas_width = self.canvas.winfo_width()
        
        # Calculate item positions
        for i, (item_factory, item_data) in enumerate(self.all_items):
            row = i // self.current_columns
            col = i % columns
            
            # Calculate the position of this item
            item_top = row * (self.min_column_width + (2 * self.padding))
            item_bottom = item_top + self.min_column_width + (2 * self.padding)
            
            # Check if this item is visible
            is_visible = (item_bottom >= canvas_top and item_top <= canvas_bottom)
            
            if is_visible and i not in self.visible_items:
                # Create the widget if it's visible but not created yet
                widget = item_factory(self.parent_frame, item_data)
                widget.grid(
                    row=row, column=col, 
                    sticky="nsew", 
                    padx=self.padding, 
                    pady=self.padding
                )
                self.visible_items[i] = widget
                
            elif not is_visible and i in self.visible_items:
                # Destroy the widget if it's not visible but created
                self.visible_items[i].destroy()
                del self.visible_items[i]
