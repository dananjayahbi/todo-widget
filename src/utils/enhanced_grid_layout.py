"""
Enhanced grid layout system with support for variable-sized items.
"""
import tkinter as tk
from tkinter import ttk
import math

class EnhancedGridLayout:
    """
    An enhanced grid layout manager that supports items of varying sizes and spans.
    """
    
    def __init__(self, parent_frame, min_column_width=300, padding=5, animation_speed=10):
        """
        Initialize the enhanced grid layout manager.
        
        Args:
            parent_frame: The frame where items will be placed
            min_column_width: Minimum width for each column
            padding: Padding between grid items
            animation_speed: Speed of animations (ms per step, lower is faster)
        """
        self.parent_frame = parent_frame
        self.min_column_width = min_column_width
        self.padding = padding
        self.animation_speed = animation_speed
        self.items = []  # List of (widget, rowspan, colspan) tuples
        self.current_columns = 1
        self.grid_map = {}  # Maps (row, col) to item index
        
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
        for widget, _, _ in self.items:
            widget.destroy()
        self.items = []
        self.grid_map = {}
    
    def add_item(self, item_widget, rowspan=1, colspan=1):
        """
        Add an item to the grid with optional spanning.
        
        Args:
            item_widget: Widget to add to the grid
            rowspan: Number of rows this item spans (default: 1)
            colspan: Number of columns this item spans (default: 1)
        """
        self.items.append((item_widget, rowspan, colspan))
        self.update_layout()
    
    def _find_available_position(self, colspan):
        """
        Find the next available position in the grid for an item with the specified colspan.
        
        Args:
            colspan: Number of columns the item spans
            
        Returns:
            tuple: (row, column) for the item
        """
        columns = self.calculate_columns()
        
        # If colspan is greater than available columns, reduce it
        colspan = min(colspan, columns)
        
        for row in range(100):  # Limit search to 100 rows to prevent infinite loop
            for col in range(columns - colspan + 1):
                # Check if all cells in the span are available
                available = True
                for c in range(col, col + colspan):
                    if (row, c) in self.grid_map:
                        available = False
                        break
                
                if available:
                    return row, col
        
        # If we get here, something went wrong - use a default position
        return 0, 0
    
    def update_layout(self):
        """
        Update the layout of all items in the grid.
        """
        # Calculate columns based on current width
        columns = self.calculate_columns()
        
        # If columns changed, perform a full layout update
        if columns != self.current_columns:
            self._perform_full_layout_update(columns)
        else:
            # Just update the most recently added item
            if self.items:
                item_widget, rowspan, colspan = self.items[-1]
                row, col = self._find_available_position(colspan)
                
                # Update the grid map
                for r in range(row, row + rowspan):
                    for c in range(col, col + colspan):
                        self.grid_map[(r, c)] = len(self.items) - 1
                
                # Place the widget
                item_widget.grid(
                    row=row, column=col, 
                    rowspan=rowspan, columnspan=colspan,
                    sticky="nsew", 
                    padx=self.padding, 
                    pady=self.padding
                )
        
        # Update column configuration
        for i in range(columns):
            self.parent_frame.columnconfigure(i, weight=1)
        
        # Store current column count
        self.current_columns = columns
    
    def _perform_full_layout_update(self, columns):
        """
        Perform a full layout update, repositioning all items.
        
        Args:
            columns: Number of columns to use
        """
        # Remove all items from the grid
        for item_widget, _, _ in self.items:
            if hasattr(item_widget, 'grid_forget'):
                item_widget.grid_forget()
        
        # Clear the grid map
        self.grid_map = {}
        
        # Place items in grid
        for i, (item_widget, rowspan, colspan) in enumerate(self.items):
            # If colspan is greater than available columns, reduce it
            actual_colspan = min(colspan, columns)
            
            # Find an available position
            row, col = self._find_available_position(actual_colspan)
            
            # Update the grid map
            for r in range(row, row + rowspan):
                for c in range(col, col + actual_colspan):
                    self.grid_map[(r, c)] = i
            
            # Grid the item with proper padding
            item_widget.grid(
                row=row, column=col, 
                rowspan=rowspan, columnspan=actual_colspan,
                sticky="nsew", 
                padx=self.padding, 
                pady=self.padding
            )
    
    def animate_layout_change(self, new_columns):
        """
        Animate the transition when layout changes.
        
        Args:
            new_columns: New number of columns
        """
        if not hasattr(self, '_animating') or not self._animating:
            self._animating = True
            self._animate_step(new_columns, 0)
    
    def _animate_step(self, new_columns, step):
        """
        Perform one step of the animation.
        
        Args:
            new_columns: Target number of columns
            step: Current animation step
        """
        if step < 10:  # 10 steps for the animation
            # Calculate intermediate column value
            intermediate_columns = self.current_columns + (new_columns - self.current_columns) * step / 10
            
            # Update layout with this intermediate value (simplified)
            self._perform_full_layout_update(int(intermediate_columns))
            
            # Schedule the next step
            self.parent_frame.after(self.animation_speed, 
                                  lambda: self._animate_step(new_columns, step + 1))
        else:
            # Final step - set to the exact target layout
            self._perform_full_layout_update(new_columns)
            self.current_columns = new_columns
            self._animating = False
    
    def refresh_on_resize(self, event=None):
        """
        Refresh the layout if the number of columns would change.
        
        Args:
            event: The resize event (optional)
        """
        new_columns = self.calculate_columns()
        if new_columns != self.current_columns:
            # Option 1: Immediate update
            # self.update_layout()
            
            # Option 2: Animated update
            self.animate_layout_change(new_columns)
