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
from ..utils.card_styles import apply_card_styles
from ..utils.grid_layout import SimpleGridLayout

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
        
        # Configure the frame to properly expand in the grid
        self.configure(style="info.TFrame", width=300, height=180)
        self.pack_propagate(False)  # Prevent the frame from shrinking to fit its contents
        
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
        # Container with border and padding - enhanced style
        container = ttk.Frame(self, padding=8, relief="raised", borderwidth=1)
        container.pack(fill=BOTH, expand=True)
        
        # Header row (title, buttons) - improved layout
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=X, pady=(0, 5))
        
        # Draft icon with better styling
        draft_icon = ttk.Label(
            header_frame,
            text="📝",
            font=("Helvetica", 14)
        )
        draft_icon.pack(side=LEFT, padx=(0, 5))
        
        # Title with enhanced styling
        title_label = ttk.Label(
            header_frame,
            text=self.draft["title"],
            font=("Helvetica", 12, "bold"),
            style="info.TLabel",
            foreground="#FFFFFF"
        )
        title_label.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        # Button frame with improved button styling
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side=RIGHT)
        
        assign_button = ttk.Button(
            button_frame,
            text="✓ Assign",
            command=self._on_assign,
            style="success.Outline.TButton", 
            width=10
        )
        assign_button.pack(side=LEFT, padx=2)
        
        delete_button = ttk.Button(
            button_frame,
            text="🗑️",
            command=self._on_delete,
            style="danger.Link.TButton",
            width=3
        )
        delete_button.pack(side=LEFT, padx=2)
        
        # Add a separator for visual structure
        separator = ttk.Separator(container, orient='horizontal')
        separator.pack(fill=X, pady=5)
        
        # Details section - improved layout
        details_frame = ttk.Frame(container)
        details_frame.pack(fill=BOTH, expand=True, padx=5)
        
        # Created date with icon
        date_frame = ttk.Frame(details_frame)
        date_frame.pack(fill=X, anchor=W, pady=(0, 5))
        
        ttk.Label(
            date_frame,
            text="🕒",
            font=("Helvetica", 10)
        ).pack(side=LEFT, padx=(0, 5))
        
        created_date_text = self._format_date(self.draft["created_at"])
        created_label = ttk.Label(
            date_frame,
            text=f"Created: {created_date_text}",
            font=("Helvetica", 9)
        )
        created_label.pack(side=LEFT)
        
        # Description with better styling
        if self.draft["description"]:
            desc_frame = ttk.Frame(details_frame)
            desc_frame.pack(fill=BOTH, expand=True, pady=(0, 5))
            
            # Description icon
            ttk.Label(
                desc_frame,
                text="📋",
                font=("Helvetica", 10)
            ).pack(side=LEFT, anchor=N, padx=(0, 5), pady=(0, 5))
            
            # Description text with better wrapping and styling
            desc_text = self.draft["description"]
            if len(desc_text) > 100:
                desc_text = desc_text[:97] + "..."
                
            desc_label = ttk.Label(
                desc_frame,
                text=desc_text,
                wraplength=240,
                justify=LEFT,
                font=("Helvetica", 9),
                foreground="#E0E0E0"
            )
            desc_label.pack(side=LEFT, fill=BOTH, expand=True, anchor=W)
        
        # Tags with improved styling
        if self.draft["tags"]:
            tags_frame = ttk.Frame(container)
            tags_frame.pack(fill=X, pady=(5, 0), anchor=W)
            
            # Tags icon
            ttk.Label(
                tags_frame,
                text="🏷️",
                font=("Helvetica", 10)
            ).pack(side=LEFT, padx=(5, 5))
            
            # Tags with better styling
            tags_container = ttk.Frame(tags_frame)
            tags_container.pack(side=LEFT, fill=X)
            
            for tag in self.draft["tags"]:
                tag_label = ttk.Label(
                    tags_container,
                    text=tag,
                    style="info.Inverse.TLabel",
                    font=("Helvetica", 8),
                    padding=(5, 2),
                    foreground="#FFFFFF"
                )
                tag_label.pack(side=LEFT, padx=(0, 5), pady=2)

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
        self.canvas = tk.Canvas(container_frame, highlightthickness=0, bg="#1C1C1C")
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=self.canvas.yview)
        
        # Configure the canvas
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create the scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create the window in the canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.scrollable_frame, 
            anchor="nw",
            tags="self.scrollable_frame"
        )
        
        # Setup the grid layout for drafts with simple implementation
        self.drafts_grid_layout = SimpleGridLayout(
            parent_frame=self.scrollable_frame,
            min_column_width=320,
            padding=5
        )
        
        # Update scrollable frame width when canvas changes
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling to the canvas
        self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        # For Linux/Unix systems
        self.canvas.bind("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))
    
    def _on_canvas_configure(self, event):
        """
        Update scrollable frame width when canvas is resized.
        """
        # Update the width of the frame to fill the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        # Force update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # When canvas resizes, refresh the layout if needed
        self.drafts_grid_layout.refresh_on_resize(event)
    
    def load_drafts(self):
        """
        Load and display draft tasks.
        """
        # Clear existing drafts
        self.drafts_grid_layout.clear()
        
        # Get all drafts
        drafts = self.task_manager.get_all_drafts()
        print(f"Loading {len(drafts)} drafts")
        
        # Display drafts
        if not drafts:
            empty_label = ttk.Label(
                self.scrollable_frame,
                text="No draft tasks. Click 'Add Draft' to create one.",
                font=("Helvetica", 12),
                foreground="gray"
            )
            empty_label.grid(row=0, column=0, columnspan=10, pady=50)
        else:
            # Add drafts to the grid layout
            for draft in drafts:
                print(f"Adding draft: {draft['title']}")
                draft_frame = DraftTaskFrame(
                    self.scrollable_frame, 
                    draft,
                    self._on_assign_draft,
                    self._on_delete_draft
                )
                # Apply consistent styling
                apply_card_styles(draft_frame)
                # Add to grid layout
                self.drafts_grid_layout.add_item(draft_frame)
                
            # Force layout update
            self.scrollable_frame.update_idletasks()
    
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
