"""
Dialog for viewing task details in read-only mode.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..utils.helpers import center_window, format_date

class ViewTaskDialog:
    """
    Dialog for viewing task details in read-only mode.
    """
    
    def __init__(self, parent, task):
        """
        Initialize the view task dialog.
        
        Args:
            parent: Parent window
            task: Task to view
        """
        self.parent = parent
        self.task = task
        
        # Create the dialog
        self.top = tk.Toplevel(parent)
        self.top.title(f"View Task: {task['title']}")
        self.top.geometry("650x500")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Create widgets
        self._create_widgets()
        
        # Center the dialog on the parent window
        center_window(self.top, parent)
    
    def _create_widgets(self):
        """
        Create the dialog widgets.
        """
        frame = ttk.Frame(self.top, padding=20)
        frame.pack(fill=BOTH, expand=True)
        
        # Title section with heading style
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=X, pady=(0, 15))
        
        ttk.Label(
            title_frame, 
            text=self.task["title"],
            font=("Helvetica", 16, "bold"),
            foreground="#FFFFFF"
        ).pack(anchor=W)
        
        # Status badge
        status_style = {
            "To Do": "info",
            "In Progress": "warning",
            "Completed": "success"
        }.get(self.task["status"], "secondary")
        
        status_badge = ttk.Label(
            title_frame,
            text=self.task["status"],
            style=f"{status_style}.Inverse.TLabel",
            font=("Helvetica", 10),
            padding=(5, 2),
            foreground="#FFFFFF"
        )
        status_badge.pack(anchor=W, pady=(5, 0))
        
        # Priority badge
        priority_style = {
            "High": "danger",
            "Medium": "warning",
            "Low": "info"
        }.get(self.task["priority"], "secondary")
        
        priority_badge = ttk.Label(
            title_frame,
            text=f"Priority: {self.task['priority']}",
            style=f"{priority_style}.Inverse.TLabel",
            font=("Helvetica", 10),
            padding=(5, 2),
            foreground="#FFFFFF"
        )
        priority_badge.pack(anchor=W, pady=(5, 0))
        
        # Separator
        ttk.Separator(frame, orient='horizontal').pack(fill=X, pady=10)
        
        # Dates section
        dates_frame = ttk.Frame(frame)
        dates_frame.pack(fill=X, pady=(0, 15))
        
        # Created date
        created_date = format_date(self.task["created_at"])
        ttk.Label(
            dates_frame,
            text=f"Created on: {created_date}",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        # Due date
        due_date = format_date(self.task["due_date"]) if self.task.get("due_date") else "Not set"
        ttk.Label(
            dates_frame,
            text=f"Due date: {due_date}",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 5))
        
        # Completed date (if applicable)
        if self.task.get("completed_at"):
            completed_date = format_date(self.task["completed_at"])
            ttk.Label(
                dates_frame,
                text=f"Completed on: {completed_date}",
                font=("Helvetica", 11),
                foreground="#66BB6A"  # Green for completion
            ).pack(anchor=W, pady=(0, 5))
            
        # Tags section
        if self.task.get("tags") and len(self.task["tags"]) > 0:
            ttk.Label(
                frame,
                text="Tags:",
                font=("Helvetica", 12, "bold")
            ).pack(anchor=W, pady=(0, 5))
            
            tags_frame = ttk.Frame(frame)
            tags_frame.pack(fill=X, pady=(0, 15), anchor=W)
            
            for tag in self.task["tags"]:
                tag_label = ttk.Label(
                    tags_frame,
                    text=tag,
                    style="secondary.Inverse.TLabel",
                    font=("Helvetica", 9),
                    padding=(5, 2),
                    foreground="#FFFFFF"
                )
                tag_label.pack(side=LEFT, padx=(0, 5), pady=2)
        
        # Description section
        ttk.Label(
            frame,
            text="Description:",
            font=("Helvetica", 12, "bold")
        ).pack(anchor=W, pady=(0, 5))
        
        # Description text in a scrollable frame
        desc_frame = ttk.Frame(frame)
        desc_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Read-only text widget for description
        desc_text = tk.Text(
            desc_frame,
            wrap=tk.WORD,
            width=40,
            height=10,
            font=("Helvetica", 11),
            background="#3D3D3D",  # Slightly lighter than background
            foreground="#FFFFFF"
        )
        scrollbar = ttk.Scrollbar(desc_frame, orient=VERTICAL, command=desc_text.yview)
        desc_text.configure(yscrollcommand=scrollbar.set)
        
        desc_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Insert the description text and make it read-only
        if self.task.get("description"):
            desc_text.insert("1.0", self.task["description"])
        else:
            desc_text.insert("1.0", "No description provided.")
        
        desc_text.configure(state="disabled")  # Make it read-only
        
        # Close button at the bottom
        ttk.Button(
            frame,
            text="Close",
            command=self.top.destroy,
            style="secondary.TButton",
            width=15
        ).pack(side=RIGHT, pady=(10, 0))
