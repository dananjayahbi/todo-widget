"""
Task Frame for displaying individual tasks.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
from dateutil import parser

from ..utils.helpers import format_date
from .view_task_dialog import ViewTaskDialog  # Import the new dialog

class TaskFrame(ttk.Frame):
    """
    Frame for displaying an individual task.
    """
    
    def __init__(self, parent, task, on_status_change, on_edit, on_delete):
        """
        Initialize the task frame.
        
        Args:
            parent: Parent widget
            task (dict): Task data
            on_status_change (callable): Callback for status change
            on_edit (callable): Callback for edit action
            on_delete (callable): Callback for delete action
        """
        super().__init__(parent, padding=5)
        
        self.task = task
        self.on_status_change = on_status_change
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Configure the frame to properly expand in the grid
        self.configure(width=300, height=200)
        self.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents
        
        # Apply appropriate styling based on task status
        self._apply_styling()
        self._create_widgets()
    
    def _apply_styling(self):
        """
        Apply styling based on task status and priority.
        """
        # Create a style name based on the task's status and priority
        if self.task["status"] == "Completed":
            self.configure(style="success.TFrame")
        elif self.task["priority"] == "High":
            self.configure(style="danger.TFrame")
        elif self.task["priority"] == "Medium":
            self.configure(style="warning.TFrame")
        else:
            self.configure(style="info.TFrame")
        
        # Custom colors for the task container
        # For completed tasks, use a slightly lighter background
        if self.task["status"] == "Completed":
            self.container_bg = "#3D3D3D"
            self.text_color = "#FFFFFF"
        # For high priority tasks, use a slightly reddish background
        elif self.task["priority"] == "High":
            self.container_bg = "#3D3D3D"
            self.text_color = "#FFFFFF"
        else:
            self.container_bg = "#3D3D3D"
            self.text_color = "#FFFFFF"
    
    def _format_date(self, date_str):
        """
        Format date string for display.
        
        Args:
            date_str: ISO format date string
            
        Returns:
            str: Formatted date string or empty string if None
        """
        return format_date(date_str)
    
    def _create_widgets(self):
        """
        Create the widgets for the task frame.
        """
        # Container with border and padding
        container = ttk.Frame(self, padding=8, relief="raised", borderwidth=1)
        container.pack(fill=BOTH, expand=True)
        
        # Header row (title, status, buttons)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X)
        
        # Configure header_frame columns for better control
        header_frame.columnconfigure(0, weight=0)  # Checkbox column - fixed width
        header_frame.columnconfigure(1, weight=1)  # Title column - expandable
        header_frame.columnconfigure(2, weight=0)  # Priority badge - fixed width
        header_frame.columnconfigure(3, weight=0)  # Buttons - fixed width
        
        # Status checkbox - left side
        self.toggle_var = tk.BooleanVar(value=self.task["status"] == "Completed")
        toggle_button = ttk.Checkbutton(
            header_frame,
            variable=self.toggle_var,
            command=self._on_status_toggled,
            style="Switch.TCheckbutton"
        )
        toggle_button.grid(row=0, column=0, sticky=W, padx=(0, 5))
        
        # Get title text and truncate if too long for tooltip
        title_text = self.task["title"]
        tooltip_text = title_text
        
        # Title with appropriate styling - using white text
        title_style = "TLabel"
        if self.task["status"] == "Completed":
            title_style = "success.TLabel"
        elif self.task["priority"] == "High":
            title_style = "danger.TLabel"
            
        title_label = ttk.Label(
            header_frame,
            text=title_text,
            font=("Helvetica", 12, "bold"),
            style=title_style,
            foreground="#FFFFFF",  # Ensuring white text
            wraplength=180,  # Control wrapping for long titles
            justify=LEFT,
            anchor=W
        )
        title_label.grid(row=0, column=1, sticky=W+E, padx=5)
        
        # Bind tooltip for full title on hover if title is long
        if len(title_text) > 25:
            self._create_tooltip(title_label, tooltip_text)
        
        # Priority badge with white text
        priority_colors = {
            "High": "danger", 
            "Medium": "warning", 
            "Low": "info"
        }
        priority_style = priority_colors.get(self.task["priority"], "secondary")
        priority_badge = ttk.Label(
            header_frame,
            text=self.task["priority"],
            style=f"{priority_style}.Inverse.TLabel",
            font=("Helvetica", 9),
            padding=(5, 2),
            foreground="#FFFFFF"
        )
        priority_badge.grid(row=0, column=2, sticky=E, padx=2)
        
        # Button frame - right side
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=3, sticky=E)
        
        # Add View button
        view_button = ttk.Button(
            button_frame,
            text="👁️",
            command=self._on_view,
            style="primary.Link.TButton", 
            width=3,
            takefocus=False  # Prevent focus outline
        )
        view_button.pack(side=LEFT, padx=1)
        
        edit_button = ttk.Button(
            button_frame,
            text="✍",
            command=self._on_edit,
            style="info.Link.TButton", 
            width=3,
            takefocus=False  # Prevent focus outline
        )
        edit_button.pack(side=LEFT, padx=1)
        
        delete_button = ttk.Button(
            button_frame,
            text="🗑️",
            command=self._on_delete,
            style="danger.Link.TButton",
            width=3,
            takefocus=False  # Prevent focus outline
        )
        delete_button.pack(side=LEFT, padx=1)
        
        # Details section - use grid for better alignment
        details_frame = ttk.Frame(container, padding=(10, 5, 0, 0))
        details_frame.pack(fill=X, expand=True)
        
        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(2, weight=1)
        
        # Status indicator
        status_label = ttk.Label(
            details_frame,
            text=f"Status: {self.task['status']}",
            font=("Helvetica", 9)
        )
        status_label.grid(row=0, column=0, sticky=W)
        
        # Due date with formatting
        due_date_text = self._format_date(self.task["due_date"])
        due_date_label = ttk.Label(
            details_frame,
            text=f"Due: {due_date_text}",
            font=("Helvetica", 9)
        )
        due_date_label.grid(row=0, column=1, sticky=W)
        
        # Description (if exists)
        if self.task["description"]:
            # Limit description length for display
            desc_text = self.task["description"]
            if len(desc_text) > 200:
                desc_text = desc_text[:200] + "..."
                
            desc_label = ttk.Label(
                container,
                text=desc_text,
                wraplength=300,  # Adjusted wraplength for better display
                justify=LEFT,
                font=("Helvetica", 9),
                foreground="gray"
            )
            desc_label.pack(fill=X, padx=10, pady=(5, 0), anchor=W)
        
        # Tags (if exist) with white text
        if self.task["tags"]:
            tags_frame = ttk.Frame(container)
            tags_frame.pack(fill=X, padx=10, pady=(5, 0), anchor=W)
            
            for tag in self.task["tags"]:
                tag_label = ttk.Label(
                    tags_frame,
                    text=tag,
                    style="secondary.Inverse.TLabel",
                    font=("Helvetica", 8),
                    padding=(5, 0),
                    foreground="#FFFFFF"  # Ensuring white text for tags
                )
                tag_label.pack(side=LEFT, padx=(0, 5))

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a widget when cursor hovers over it."""
        def enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)  # Remove window decorations
            
            # Calculate position
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height()
            
            # Position tooltip a bit below the widget
            self.tooltip.wm_geometry(f"+{x}+{y+10}")
            
            # Create label with tooltip text
            label = ttk.Label(
                self.tooltip, 
                text=text, 
                justify=LEFT,
                background="#3D3D3D", 
                foreground="#FFFFFF",
                relief=SOLID,
                borderwidth=1,
                padding=(5, 3)
            )
            label.pack()
        
        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                del self.tooltip
        
        # Bind events
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _on_view(self):
        """
        Handle view button click.
        """
        ViewTaskDialog(self.winfo_toplevel(), self.task)

    def _on_status_toggled(self):
        """
        Handle status checkbox toggle.
        """
        new_status = "Completed" if self.toggle_var.get() else "To Do"
        self.on_status_change(self.task["id"], new_status)

    def _on_edit(self):
        """
        Handle edit button click.
        """
        self.on_edit(self.task["id"])

    def _on_delete(self):
        """
        Handle delete button click.
        """
        self.on_delete(self.task["id"])
