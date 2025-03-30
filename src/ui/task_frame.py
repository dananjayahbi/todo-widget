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
        
        # Status checkbox - left side
        self.toggle_var = tk.BooleanVar(value=self.task["status"] == "Completed")
        toggle_button = ttk.Checkbutton(
            header_frame,
            variable=self.toggle_var,
            command=self._on_status_toggled,
            style="Switch.TCheckbutton"
        )
        toggle_button.pack(side=LEFT, padx=(0, 5))
        
        # Title with appropriate styling - using white text
        title_style = "TLabel"
        if self.task["status"] == "Completed":
            title_style = "success.TLabel"
        elif self.task["priority"] == "High":
            title_style = "danger.TLabel"
            
        title_label = ttk.Label(
            header_frame,
            text=self.task["title"],
            font=("Helvetica", 12, "bold"),
            style=title_style,
            foreground="#FFFFFF",  # Ensuring white text
            wraplength=250  # Add wrapping for long titles
        )
        title_label.pack(side=LEFT, padx=5, fill=X, expand=True)
        
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
            foreground="#FFFFFF"  # Ensuring white text for priority label
        )
        priority_badge.pack(side=LEFT, padx=5)
        
        # Button frame - right side
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=RIGHT)
        
        edit_button = ttk.Button(
            button_frame,
            text="✍",
            command=self._on_edit,
            style="Link.TButton", 
            width=5
        )
        edit_button.pack(side=LEFT, padx=2)
        
        delete_button = ttk.Button(
            button_frame,
            text="🗑️",
            command=self._on_delete,
            style="Link.TButton",
            width=5
        )
        delete_button.pack(side=LEFT, padx=2)
        
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
        
        # Created date
        created_date_text = self._format_date(self.task["created_at"])
        created_label = ttk.Label(
            details_frame,
            text=f"Created: {created_date_text}",
            font=("Helvetica", 9)
        )
        created_label.grid(row=0, column=2, sticky=W)
        
        # Description (if exists)
        if self.task["description"]:
            # Limit description length for display
            desc_text = self.task["description"]
            if len(desc_text) > 100:
                desc_text = desc_text[:97] + "..."
                
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
