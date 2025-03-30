"""
Main window for the ToDo application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta

from ..data.task_manager import TaskManager
from .task_frame import TaskFrame
from .add_task_dialog import AddTaskDialog
from .edit_task_dialog import EditTaskDialog
from .statistics_frame import StatisticsFrame
from .draft_frame import DraftsFrame
from ..utils.helpers import center_window

class TodoApp:
    """
    Main application window.
    """
    
    def __init__(self):
        """
        Initialize the application window.
        """
        self.root = tb.Window(
            title="ToDo Widget",
            themename="superhero",  # Always use dark theme
            size=(1000, 700),
            position=(100, 100),
            minsize=(800, 600),
            iconphoto=""
        )
        
        self.task_manager = TaskManager()
        self.current_filter = "Due Today"  # Changed default filter
        self.current_sort = "Due Date"
        
        # Center the window on screen
        center_window(self.root)
        
        self._setup_variables()
        self._create_widgets()
        self._setup_layout()
        self._load_tasks()
        
    def _setup_variables(self):
        """
        Setup tkinter variables.
        """
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        self.filter_var = tk.StringVar(value="Due Today")  # Changed default filter
        self.filter_var.trace_add("write", self._on_filter_changed)
        
        self.sort_var = tk.StringVar(value="Due Date")
    
    def _create_widgets(self):
        """
        Create the application widgets.
        """
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Header
        self.header_frame = ttk.Frame(self.main_frame)
        title_label = ttk.Label(
            self.header_frame, 
            text="ToDo Widget", 
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(side=LEFT, padx=10, pady=10)
        
        # Theme switcher removed - using only dark theme
        
        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Tasks Tab
        self.tasks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Tasks")
        
        # Drafts Tab
        self.drafts_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.drafts_tab, text="Drafts")
        
        # Search bar (in Tasks Tab)
        self.search_frame = ttk.Frame(self.tasks_tab)
        ttk.Label(self.search_frame, text="Search:").pack(side=LEFT, padx=(10, 5))
        search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        
        # Filters
        filter_frame = ttk.Frame(self.search_frame)
        ttk.Label(filter_frame, text="Filter:").pack(side=LEFT, padx=(10, 5))
        filter_options = ["All", "To Do", "In Progress", "Completed", "Overdue", "Due Today", "High Priority"]
        filter_dropdown = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var,
            values=filter_options,
            width=15,
            state="readonly"
        )
        filter_dropdown.pack(side=LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Sort by:").pack(side=LEFT, padx=(10, 5))
        sort_options = ["Due Date", "Priority", "Created Date", "Title"]
        sort_dropdown = ttk.Combobox(
            filter_frame, 
            textvariable=self.sort_var,
            values=sort_options,
            width=15,
            state="readonly"
        )
        sort_dropdown.pack(side=LEFT, padx=5)
        sort_dropdown.bind("<<ComboboxSelected>>", self._on_sort_changed)
        
        filter_frame.pack(side=LEFT, padx=10, fill=X, expand=True)
        
        # Task list frame with scrollbar
        self.task_container_frame = ttk.Frame(self.tasks_tab)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.task_container_frame)
        scrollbar = ttk.Scrollbar(self.task_container_frame, orient="vertical", command=self.canvas.yview)
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
        
        # Bottom action bar (for Tasks tab)
        self.action_frame = ttk.Frame(self.tasks_tab)
        add_button = ttk.Button(
            self.action_frame, 
            text="Add Task", 
            command=self._open_add_dialog,
            style="success.TButton",
            width=15
        )
        add_button.pack(side=LEFT, padx=10, pady=10)
        
        # Statistics frame (for Tasks tab)
        self.stats_frame = StatisticsFrame(self.tasks_tab, self.task_manager)
        
        # Drafts Frame (for Drafts tab)
        self.drafts_frame = DraftsFrame(self.drafts_tab, self.task_manager)
        
        # Set up tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_layout(self):
        """
        Layout the widgets.
        """
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.header_frame.pack(fill=X, pady=(0, 10))
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Layout for Tasks tab
        self.search_frame.pack(fill=X, pady=(10, 10))
        self.task_container_frame.pack(fill=BOTH, expand=True, pady=10)
        self.action_frame.pack(fill=X, pady=(10, 0))
        self.stats_frame.pack(fill=X, pady=10)
        
        # Layout for Drafts tab
        self.drafts_frame.pack(fill=BOTH, expand=True)
    
    def _on_tab_changed(self, event):
        """
        Handle tab change events.
        """
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Tasks":
            self._load_tasks()
        elif tab_name == "Drafts":
            self.drafts_frame.load_drafts()
    
    def _load_tasks(self):
        """
        Load tasks from the task manager.
        """
        # Clear existing tasks
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get tasks based on filters
        tasks = self._get_filtered_tasks()
        
        # Sort tasks
        tasks = self._sort_tasks(tasks)
        
        # Add tasks to the UI
        if not tasks:
            empty_label = ttk.Label(
                self.scrollable_frame, 
                text="No tasks found. Click 'Add Task' to create a new one.",
                font=("Helvetica", 12),
                foreground="gray"
            )
            empty_label.pack(pady=50)
        else:
            for task in tasks:
                task_frame = TaskFrame(
                    self.scrollable_frame, 
                    task, 
                    self._on_status_change,
                    self._on_edit_task,
                    self._on_delete_task
                )
                task_frame.pack(fill="x", pady=5)
        
        # Update statistics
        self.stats_frame.update_stats()
    
    def _get_filtered_tasks(self):
        """
        Get tasks based on current filter and search term.
        
        Returns:
            list: Filtered tasks
        """
        search_term = self.search_var.get().lower()
        filter_value = self.filter_var.get()
        
        all_tasks = self.task_manager.get_all_tasks()
        
        # Apply search filter
        if search_term:
            all_tasks = [
                task for task in all_tasks 
                if search_term in task["title"].lower() or 
                   search_term in task["description"].lower() or
                   any(search_term in tag.lower() for tag in task["tags"])
            ]
        
        # Apply status/priority filter
        if filter_value == "All":
            return all_tasks
        elif filter_value in ["To Do", "In Progress", "Completed"]:
            return [task for task in all_tasks if task["status"] == filter_value]
        elif filter_value == "High Priority":
            return [task for task in all_tasks if task["priority"] == "High"]
        elif filter_value == "Overdue":
            return self.task_manager.get_tasks_overdue()
        elif filter_value == "Due Today":
            return self.task_manager.get_tasks_due_today()
        
        return all_tasks
    
    def _sort_tasks(self, tasks):
        """
        Sort tasks based on the selected sort option.
        
        Args:
            tasks (list): Tasks to sort
            
        Returns:
            list: Sorted tasks
        """
        sort_by = self.sort_var.get()
        
        if sort_by == "Due Date":
            # Sort by due date, with tasks without due dates at the end
            return sorted(
                tasks,
                key=lambda x: datetime.fromisoformat(x["due_date"]) if x["due_date"] else datetime.max
            )
        elif sort_by == "Priority":
            # Sort by priority: High, Medium, Low
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            return sorted(tasks, key=lambda x: priority_order.get(x["priority"], 3))
        elif sort_by == "Created Date":
            return sorted(tasks, key=lambda x: x["created_at"])
        elif sort_by == "Title":
            return sorted(tasks, key=lambda x: x["title"].lower())
            
        return tasks
    
    def _open_add_dialog(self):
        """
        Open the add task dialog.
        """
        dialog = AddTaskDialog(self.root, self.task_manager)
        self.root.wait_window(dialog.top)
        self._load_tasks()
    
    def _on_edit_task(self, task_id):
        """
        Handle edit task action.
        
        Args:
            task_id (str): ID of the task to edit
        """
        task = self.task_manager.get_task_by_id(task_id)
        if task:
            dialog = EditTaskDialog(self.root, self.task_manager, task)
            self.root.wait_window(dialog.top)
            self._load_tasks()
    
    def _on_delete_task(self, task_id):
        """
        Handle delete task action.
        
        Args:
            task_id (str): ID of the task to delete
        """
        task = self.task_manager.get_task_by_id(task_id)
        if task:
            confirm = messagebox.askyesno(
                "Confirm Delete", 
                f"Are you sure you want to delete the task: {task['title']}?"
            )
            if confirm:
                self.task_manager.delete_task(task_id)
                self._load_tasks()
    
    def _on_status_change(self, task_id, new_status):
        """
        Handle task status change.
        
        Args:
            task_id (str): ID of the task to update
            new_status (str): New status
        """
        self.task_manager.update_task(task_id, status=new_status)
        self._load_tasks()
    
    def _on_search_changed(self, *args):
        """
        Handle search input changes.
        """
        self._load_tasks()
    
    def _on_filter_changed(self, *args):
        """
        Handle filter changes.
        """
        self._load_tasks()
    
    def _on_sort_changed(self, event):
        """
        Handle sort option changes.
        """
        self._load_tasks()
    
    def _toggle_theme(self):
        """
        Toggle between light and dark theme.
        This method is kept for backward compatibility but is no longer used.
        """
        pass
            
    def run(self):
        """
        Run the application.
        """
        self.root.mainloop()
