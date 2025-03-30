"""
Dialog for assigning a draft task.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Querybox
from datetime import datetime

from ..utils.helpers import center_window, format_date, get_centered_date

class AssignDraftDialog:
    """
    Dialog for assigning a draft task.
    """
    
    def __init__(self, parent, task_manager, draft):
        """
        Initialize the assign draft dialog.
        
        Args:
            parent: Parent window
            task_manager: TaskManager instance
            draft: Draft task to assign
        """
        self.parent = parent
        self.task_manager = task_manager
        self.draft = draft
        
        # Create the dialog
        self.top = tk.Toplevel(parent)
        self.top.title("Assign Draft Task")
        self.top.geometry("650x500")
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        
        # Initialize variables
        self.title_var = tk.StringVar(value=draft["title"])
        self.priority_var = tk.StringVar(value="Medium")
        self.status_var = tk.StringVar(value="To Do")
        
        # Set default due date to today
        today = datetime.now().isoformat()
        self.due_date_var = tk.StringVar(value=today)
        
        # Format the tags
        tags_text = ", ".join(draft["tags"]) if draft["tags"] else ""
        self.tags_var = tk.StringVar(value=tags_text)
        
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
        ttk.Label(frame, text="Task Title:", font=("Helvetica", 12)).grid(row=0, column=0, sticky=W, pady=(0, 5))
        ttk.Entry(
            frame, 
            textvariable=self.title_var, 
            width=40,
            font=("Helvetica", 12)
        ).grid(row=0, column=1, columnspan=2, sticky=(W, E), pady=(0, 5))
        
        # Priority
        ttk.Label(frame, text="Priority:", font=("Helvetica", 12)).grid(row=1, column=0, sticky=W, pady=(0, 5))
        priorities = self.task_manager.PRIORITY_LEVELS
        ttk.Combobox(
            frame, 
            textvariable=self.priority_var,
            values=priorities,
            state="readonly",
            width=15
        ).grid(row=1, column=1, sticky=W, pady=(0, 5))
        
        # Status
        ttk.Label(frame, text="Status:", font=("Helvetica", 12)).grid(row=1, column=2, sticky=W, pady=(0, 5), padx=(10, 0))
        statuses = self.task_manager.STATUS_OPTIONS
        ttk.Combobox(
            frame, 
            textvariable=self.status_var,
            values=statuses,
            state="readonly",
            width=15
        ).grid(row=1, column=3, sticky=W, pady=(0, 5))
        
        # Due Date
        ttk.Label(frame, text="Due Date:", font=("Helvetica", 12)).grid(row=2, column=0, sticky=W, pady=(0, 5))
        date_frame = ttk.Frame(frame)
        date_entry = ttk.Entry(
            date_frame, 
            textvariable=self.due_date_var, 
            width=20
        )
        date_entry.pack(side=LEFT, padx=(0, 5))
        ttk.Button(
            date_frame,
            text="Select Date",
            command=self._select_date,
            width=15
        ).pack(side=LEFT)
        date_frame.grid(row=2, column=1, columnspan=3, sticky=W, pady=(0, 5))
        
        # Tags
        ttk.Label(frame, text="Tags:", font=("Helvetica", 12)).grid(row=3, column=0, sticky=W, pady=(0, 5))
        ttk.Entry(
            frame, 
            textvariable=self.tags_var, 
            width=40,
        ).grid(row=3, column=1, columnspan=3, sticky=(W, E), pady=(0, 5))
        ttk.Label(
            frame, 
            text="Separate tags with commas (e.g., work, meeting, important)",
            font=("Helvetica", 9),
            foreground="gray"
        ).grid(row=4, column=1, columnspan=3, sticky=W)
        
        # Description
        ttk.Label(frame, text="Description:", font=("Helvetica", 12)).grid(row=5, column=0, sticky=NW, pady=(10, 5))
        
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
        
        # Set the description text
        if self.draft["description"]:
            self.description_text.insert("1.0", self.draft["description"])
        
        desc_frame.grid(row=5, column=1, columnspan=3, sticky=(N, S, E, W), pady=(10, 10))
        
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
            text="Assign Task",
            command=self._assign_task,
            width=15,
            style="success.TButton"
        ).pack(side=RIGHT)
        
        button_frame.grid(row=6, column=0, columnspan=4, sticky=E, pady=(10, 0))
    
    def _select_date(self):
        """
        Open date picker to select a due date.
        """
        date_string = get_centered_date(parent=self.top, title="Select Due Date")
        if date_string:
            # Format the date as ISO format - date_string is already a datetime.date object
            try:
                selected_date = datetime.combine(date_string, datetime.min.time())
                self.due_date_var.set(selected_date.isoformat())
                
                # Display the formatted date to the user
                formatted_date = format_date(selected_date.isoformat())
                messagebox.showinfo("Date Selected", f"Selected date: {formatted_date}", parent=self.top)
            except ValueError:
                pass
    
    def _assign_task(self):
        """
        Validate and assign the draft task.
        """
        title = self.title_var.get().strip()
        priority = self.priority_var.get()
        status = self.status_var.get()
        due_date = self.due_date_var.get()
        description = self.description_text.get("1.0", tk.END).strip()
        
        # Parse tags - split by commas and strip whitespace
        tags_text = self.tags_var.get().strip()
        tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []
        
        # Remove empty tags
        tags = [tag for tag in tags if tag]
        
        # Validate
        if not title:
            messagebox.showerror("Error", "Task title is required", parent=self.top)
            return
        
        # Create a real task from the draft
        self.task_manager.add_task(
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            tags=tags,
            status=status
        )
        
        # Delete the draft
        self.task_manager.delete_draft(self.draft["id"])
        
        self.top.destroy()
