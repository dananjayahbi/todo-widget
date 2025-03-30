"""
Grid layout manager for responsive layouts.
"""
import tkinter as tk
from tkinter import ttk

class ResponsiveGridLayout:
    """
    Manages a responsive grid layout that adjusts columns based on container width.
    """
    
    def __init__(self, parent_frame, canvas, min_column_width=300):
        """
        Initialize the responsive grid layout manager.
        
        Args:
            parent_frame: The frame where items will be placed
            canvas: The canvas containing the frame (for width calculations)
            min_column_width: Minimum width for each column
        """
        self.parent_frame = parent_frame
        self.canvas = canvas
        self.min_column_width = min_column_width
        self.rows = []
        self.current_row = None
        self.current_row_items = 0
        self.columns = 1  # Default to 1 column
        self.all_items = []  # Track all added items for easier reorganization
        
        # Bind to configure events to detect resize
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Initial update after a short delay
        self.parent_frame.after(100, self.on_canvas_resize)
    
    def calculate_columns(self):
        """
        Calculate the number of columns based on available width.
        
        Returns:
            int: Number of columns to display
        """
        available_width = self.canvas.winfo_width()
        
        # Fallback to parent's width if canvas width is too small
        if available_width < 50:
            available_width = self.canvas.master.winfo_width()
            if available_width < 50:  # Still not properly initialized
                return 1
            
        # Make sure we don't have too narrow columns
        columns = max(1, int(available_width // self.min_column_width))
        return columns
    
    def on_canvas_resize(self, event=None):
        """
        Handle canvas resize events.
        
        Args:
            event: The resize event
        """
        new_columns = self.calculate_columns()
        if new_columns != self.columns:
            print(f"Column count changed from {self.columns} to {new_columns}")
            self.columns = new_columns
            self.reorganize_items()
        
        # Update the canvas scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update the scrollable frame width - make sure it's at least as wide as the canvas
        canvas_width = self.canvas.winfo_width()
        min_width = max(canvas_width, self.columns * self.min_column_width)
        self.parent_frame.configure(width=min_width)
        
        # Update the canvas window width to match the canvas width
        self.canvas.itemconfig(self.canvas.find_withtag("self.scrollable_frame"), width=canvas_width)
    
    def clear(self):
        """
        Clear all items from the grid.
        """
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        self.rows = []
        self.current_row = None
        self.current_row_items = 0
        self.all_items = []
    
    def add_item(self, item_widget):
        """
        Add an item to the grid.
        
        Args:
            item_widget: Widget to add to the grid
        """
        # Ensure the item has fixed dimensions
        if hasattr(item_widget, 'configure'):
            item_widget.configure(width=self.min_column_width)
        
        # Keep track of all items for easier reorganization
        self.all_items.append(item_widget)
        
        # Ensure columns is up to date
        self.columns = self.calculate_columns()
        print(f"Adding item to grid with {self.columns} columns")
        
        # Create a new row if needed
        if self.current_row is None or self.current_row_items >= self.columns:
            self.current_row = ttk.Frame(self.parent_frame)
            self.current_row.pack(fill="x", expand=True, pady=5)
            self.rows.append(self.current_row)
            self.current_row_items = 0
            
            # Configure weights for columns in the new row
            for i in range(self.columns):
                self.current_row.columnconfigure(i, weight=1, uniform="column")
        
        # Add the item to the current row
        item_frame = ttk.Frame(self.current_row)
        item_frame.grid(row=0, column=self.current_row_items, sticky="nsew", padx=5)
        
        # Make the item frame expand to fill its cell
        item_frame.rowconfigure(0, weight=1)
        item_frame.columnconfigure(0, weight=1)
        
        # Remove any existing geometry management from the item
        if hasattr(item_widget, 'pack_forget'):
            item_widget.pack_forget()
        if hasattr(item_widget, 'grid_forget'):
            item_widget.grid_forget()
        
        # Add the widget to the frame with proper fill
        item_widget.pack(in_=item_frame, fill="both", expand=True)
        
        self.current_row_items += 1
        print(f"Added item, current row now has {self.current_row_items} items")
        
        # Force update the layout
        self.parent_frame.update_idletasks()
        
        # Ensure parent frame is wide enough
        canvas_width = self.canvas.winfo_width()
        min_width = max(canvas_width, self.columns * self.min_column_width)
        self.parent_frame.configure(width=min_width)
    
    def reorganize_items(self):
        """
        Reorganize all items in the grid when the column count changes.
        """
        if not self.all_items:
            return
        
        print(f"Reorganizing {len(self.all_items)} items into {self.columns} columns")
            
        # Store a copy of the items
        items_to_reorganize = list(self.all_items)
        
        # Clear the grid
        for row in self.rows:
            row.destroy()
        
        self.rows = []
        self.current_row = None
        self.current_row_items = 0
        self.all_items = []
        
        # Ensure parent frame is wide enough for all columns
        canvas_width = self.canvas.winfo_width()
        min_width = max(canvas_width, self.columns * self.min_column_width)
        self.parent_frame.configure(width=min_width)
        
        # Re-add all items with the new column count
        for item in items_to_reorganize:
            self.add_item(item)
        
        # Force update the layout
        self.parent_frame.update_idletasks()
