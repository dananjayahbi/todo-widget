"""
Frame for displaying and managing draft tasks.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
from dateutil import parser

from .assign_draft_dialog import AssignDraftDialog
from .add_draft_dialog import AddDraftDialog
from ..utils.helpers import format_date

class DraftTaskFrame(ttk.Frame):
    """
    Frame for displaying an individual draft task.
    """
    
    def __init__(self, parent, draft, on_assign, on_delete):
        """
        Initialize the draft task frame.
        
        Args:
            parent: Parent widget
            draft (dict): Draft task data
            on_assign (callable): Callback for assign action
            on_delete (callable): Callback for delete action
        """
        super().__init__(parent, padding=5)
        
        self.draft = draft
        self.on_assign = on_assign
        self.on_delete = on_delete
        
        self.configure(style="info.TFrame")
        self._create_widgets()
    
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
        Create the widgets for the draft task frame.
        """
        # Container with border and padding
        container = ttk.Frame(self, padding=8, relief="raised", borderwidth=1)
        container.pack(fill=X, expand=True)
        
        # Header row (title, buttons)
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X)
        
        # Draft icon - left side
        draft_icon = ttk.Label(
            header_frame,
            text="📝",
            font=("Helvetica", 12)
        )
        draft_icon.pack(side=LEFT, padx=(0, 5))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text=self.draft["title"],
            font=("Helvetica", 12, "bold"),
            style="info.TLabel"
        )
        title_label.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        # Button frame - right side
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=RIGHT)
        
        assign_button = ttk.Button(
            button_frame,
            text="Assign",
            command=self._on_assign,
            style="success.Outline.TButton", 
            width=8
        )
        assign_button.pack(side=LEFT, padx=2)
        
        delete_button = ttk.Button(
            button_frame,
            text="🗑️",
            command=self._on_delete,
            style="Link.TButton",
            width=5
        )
        delete_button.pack(side=LEFT, padx=2)
        
        # Details section
        details_frame = ttk.Frame(container, padding=(10, 5, 0, 0))
        details_frame.pack(fill=X, expand=True)
        
        # Created date
        created_date_text = self._format_date(self.draft["created_at"])
        created_label = ttk.Label(
            details_frame,
            text=f"Created: {created_date_text}",
            font=("Helvetica", 9)
        )
        created_label.pack(side=LEFT)
        
        # Description (if exists)
        if self.draft["description"]:
            # Limit description length for display
            desc_text = self.draft["description"]
            if len(desc_text) > 100:
                desc_text = desc_text[:97] + "..."
                
            desc_label = ttk.Label(
                container,
                text=desc_text,
                wraplength=550,
                justify=LEFT,
                font=("Helvetica", 9),
                foreground="gray"
            )
            desc_label.pack(fill=X, padx=10, pady=(5, 0), anchor=W)
        
        # Tags (if exist)
        if self.draft["tags"]:
            tags_frame = ttk.Frame(container)
            tags_frame.pack(fill=X, padx=10, pady=(5, 0), anchor=W)
            
            for tag in self.draft["tags"]:
                tag_label = ttk.Label(
                    tags_frame,
                    text=tag,
                    style="secondary.Inverse.TLabel",
                    font=("Helvetica", 8),
                    padding=(5, 0)
                )
                tag_label.pack(side=LEFT, padx=(0, 5))

    def _on_assign(self):
        """
        Handle assign button click.
        """
        self.on_assign(self.draft["id"])

    def _on_delete(self):
        """
        Handle delete button click.
        """
        self.on_delete(self.draft["id"])


class DraftsFrame(ttk.Frame):
    """
    Frame for displaying and managing draft tasks.
    """
    
    def __init__(self, parent, task_manager):
        """
        Initialize the drafts frame.
        
        Args:
            parent: Parent widget
            task_manager: TaskManager instance
        """
        super().__init__(parent, padding=10)
        
        self.task_manager = task_manager
        self.parent = parent
        
        self._create_widgets()
        self.load_drafts()
    
    def _create_widgets(self):
        """
        Create the widgets for the drafts frame.
        """
        # Header section
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame, 
            text="Draft Tasks", 
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=LEFT)
        
        add_button = ttk.Button(
            header_frame,
            text="Add Draft",
            command=self._open_add_draft_dialog,
            style="success.TButton",
            width=12
        )
        add_button.pack(side=RIGHT)
        
        # Drafts list with scrollbar
        container_frame = ttk.Frame(self)
        container_frame.pack(fill=BOTH, expand=True)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(container_frame)
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling to the canvas
        self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        # For Linux/Unix systems
        self.canvas.bind("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_drafts(self):
        """
        Load and display draft tasks.
        """
        # Clear existing drafts
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get all drafts
        drafts = self.task_manager.get_all_drafts()
        
        # Display drafts
        if not drafts:
            empty_label = ttk.Label(
                self.scrollable_frame, 
                text="No draft tasks. Click 'Add Draft' to create one.",
                font=("Helvetica", 12),
                foreground="gray"
            )
            empty_label.pack(pady=50)
        else:
            for draft in drafts:
                draft_frame = DraftTaskFrame(
                    self.scrollable_frame, 
                    draft, 
                    self._on_assign_draft,
                    self._on_delete_draft
                )
                draft_frame.pack(fill="x", pady=5)
    
    def _open_add_draft_dialog(self):
        """
        Open the add draft dialog.
        """
        dialog = AddDraftDialog(self.parent, self.task_manager)
        self.parent.wait_window(dialog.top)
        self.load_drafts()
    
    def _on_assign_draft(self, draft_id):
        """
        Handle assigning a draft task.
        
        Args:
            draft_id (str): ID of the draft to assign
        """
        draft = self.task_manager.get_draft_by_id(draft_id)
        if draft:
            dialog = AssignDraftDialog(self.parent, self.task_manager, draft)
            self.parent.wait_window(dialog.top)
            self.load_drafts()
    
    def _on_delete_draft(self, draft_id):
        """
        Handle deleting a draft task.
        
        Args:
            draft_id (str): ID of the draft to delete
        """
        draft = self.task_manager.get_draft_by_id(draft_id)
        if draft:
            confirm = messagebox.askyesno(
                "Confirm Delete", 
                f"Are you sure you want to delete the draft: {draft['title']}?"
            )
            if confirm:
                self.task_manager.delete_draft(draft_id)
                self.load_drafts()
