"""
Dialog for viewing draft details in read-only mode.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..utils.helpers import center_window, format_date

class ViewDraftDialog:
    """
    Dialog for viewing draft details in read-only mode.
    """
    
    def __init__(self, parent, draft):
        """
        Initialize the view draft dialog.
        
        Args:
            parent: Parent window
            draft: Draft to view
        """
        self.parent = parent
        self.draft = draft
        
        # Create the dialog
        self.top = tk.Toplevel(parent)
        self.top.title(f"View Draft: {draft['title']}")
        self.top.geometry("650x450")
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
            text=self.draft["title"],
            font=("Helvetica", 16, "bold"),
            foreground="#FFFFFF"
        ).pack(anchor=W)
        
        # Draft indicator badge
        draft_badge = ttk.Label(
            title_frame,
            text="Draft",
            style="info.Inverse.TLabel",
            font=("Helvetica", 10),
            padding=(5, 2),
            foreground="#FFFFFF"
        )
        draft_badge.pack(anchor=W, pady=(5, 0))
        
        # Separator
        ttk.Separator(frame, orient='horizontal').pack(fill=X, pady=10)
        
        # Created date
        created_date = format_date(self.draft["created_at"])
        ttk.Label(
            frame,
            text=f"Created on: {created_date}",
            font=("Helvetica", 11)
        ).pack(anchor=W, pady=(0, 15))
        
        # Tags section
        if self.draft.get("tags") and len(self.draft["tags"]) > 0:
            ttk.Label(
                frame,
                text="Tags:",
                font=("Helvetica", 12, "bold")
            ).pack(anchor=W, pady=(0, 5))
            
            tags_frame = ttk.Frame(frame)
            tags_frame.pack(fill=X, pady=(0, 15), anchor=W)
            
            for tag in self.draft["tags"]:
                tag_label = ttk.Label(
                    tags_frame,
                    text=tag,
                    style="info.Inverse.TLabel",
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
        if self.draft.get("description"):
            desc_text.insert("1.0", self.draft["description"])
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
