"""
Dialog for adding a new draft task.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from ..utils.helpers import center_window

class AddDraftDialog:
    """
    Dialog for creating a new draft task.
    """
    
    def __init__(self, parent, task_manager):
        """
        Initialize the add draft dialog.
        
        Args:
            parent: Parent window
            task_manager: TaskManager instance
        """
        self.parent = parent
        self.task_manager = task_manager
        
        # Create the dialog
        self.top = tk.Toplevel(parent)
        self.top.title("Add Draft Task")
        self.top.geometry("650x450")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Initialize variables
        self.title_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        
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
        
        # Title
        ttk.Label(frame, text="Draft Title:", font=("Helvetica", 12)).grid(row=0, column=0, sticky=W, pady=(0, 10))
        ttk.Entry(
            frame, 
            textvariable=self.title_var, 
            width=40,
            font=("Helvetica", 12)
        ).grid(row=0, column=1, columnspan=2, sticky=(W, E), pady=(0, 10))
        
        # Tags
        ttk.Label(frame, text="Tags:", font=("Helvetica", 12)).grid(row=1, column=0, sticky=W, pady=(0, 5))
        ttk.Entry(
            frame, 
            textvariable=self.tags_var, 
            width=40,
        ).grid(row=1, column=1, columnspan=2, sticky=(W, E), pady=(0, 5))
        ttk.Label(
            frame, 
            text="Separate tags with commas (e.g., work, meeting, important)",
            font=("Helvetica", 9),
            foreground="gray"
        ).grid(row=2, column=1, columnspan=2, sticky=W)
        
        # Description
        ttk.Label(frame, text="Description:", font=("Helvetica", 12)).grid(row=3, column=0, sticky=NW, pady=(10, 5))
        
        # Scrollable description text area
        desc_frame = ttk.Frame(frame)
        self.description_text = tk.Text(
            desc_frame, 
            width=40, 
            height=10,
            wrap=tk.WORD,
            font=("Helvetica", 11)
        )
        scrollbar = ttk.Scrollbar(desc_frame, orient=VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=scrollbar.set)
        
        self.description_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        desc_frame.grid(row=3, column=1, columnspan=2, sticky=(N, S, E, W), pady=(10, 10))
        
        # Action buttons
        button_frame = ttk.Frame(frame)
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.top.destroy,
            width=15,
            style="secondary.TButton"
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Save Draft",
            command=self._save_draft,
            width=15,
            style="success.TButton"
        ).pack(side=RIGHT)
        
        button_frame.grid(row=4, column=0, columnspan=3, sticky=E, pady=(10, 0))
    
    def _save_draft(self):
        """
        Validate and save the draft task.
        """
        title = self.title_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        
        # Parse tags - split by commas and strip whitespace
        tags_text = self.tags_var.get().strip()
        tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
        
        # Remove empty tags
        tags = [tag for tag in tags if tag]
        
        # Validate
        if not title:
            messagebox.showerror("Error", "Draft title is required", parent=self.top)
            return
        
        # Add the draft task
        self.task_manager.add_draft(
            title=title,
            description=description,
            tags=tags
        )
        
        self.top.destroy()
