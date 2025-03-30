"""
Main window for the ToDo application.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import traceback
from dateutil import parser  # Add the missing import

from ..data.task_manager import TaskManager
from .task_frame import TaskFrame
from .add_task_dialog import AddTaskDialog
from .edit_task_dialog import EditTaskDialog
from .statistics_frame import StatisticsFrame
from .draft_frame import DraftsFrame
from ..utils.helpers import center_window
from ..utils.custom_theme import create_custom_dark_theme
from ..utils.grid_layout import SimpleGridLayout
from ..utils.card_styles import apply_card_styles

class TodoApp:
    """
    Main application window.
    """
    
    def __init__(self):
        """
        Initialize the application window.
        """
        # Create and register our custom theme
        custom_theme = create_custom_dark_theme()
        
        self.root = tb.Window(
            title="ToDo Widget",
            themename=custom_theme,  # Use our custom theme
            size=(1000, 700),
            position=(100, 100),
            minsize=(800, 600),
            iconphoto=""
        )
        
        # Set the window to maximized state
        self.root.state('zoomed')  # For Windows
        # For Linux/Mac, use: self.root.attributes('-zoomed', True)
        
        self.task_manager = TaskManager()
        self.current_filter = "All"  # Changed default filter to All
        self.current_sort = "Due Date"
        
        # Add state tracking for loaded data
        self.tasks_loaded = False
        self.drafts_loaded = False
        self.tasks_need_refresh = True
        self.drafts_need_refresh = True
        
        # Center the window on screen
        center_window(self.root)
        
        # Configure custom styles
        self._configure_custom_styles()
        
        self._setup_variables()
        self._create_widgets()
        self._setup_layout()
        
        # Schedule the initial refresh after the UI is fully loaded
        self.root.after(100, self._initial_refresh)
        
    def _initial_refresh(self):
        """
        Perform initial data refresh after UI is fully loaded.
        """
        print("Performing initial refresh on startup...")
        # Force a data refresh from files
        self.task_manager.refresh_data()
        # Load tasks with fresh data
        self._load_tasks()
        self.tasks_loaded = True
        self.tasks_need_refresh = False
    
    def _configure_custom_styles(self):
        """
        Configure custom styles for widgets.
        """
        style = ttk.Style()
        
        # Configure frame styles with custom colors
        style.configure("TFrame", background="#1C1C1C")
        style.configure("TNotebook", background="#1C1C1C")
        
        # Update tab text to white for better visibility
        style.configure("TNotebook.Tab", background="#3D3D3D", foreground="#FFFFFF")
        style.map("TNotebook.Tab", 
                  background=[("selected", "#5E5E5E")],
                  foreground=[("selected", "#FFFFFF")])
        
        # Configure label styles with white text
        style.configure("TLabel", background="#1C1C1C", foreground="#FFFFFF")
        style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), foreground="#FFFFFF")
        
        # Configure button styles with white text
        style.configure("TButton", background="#3D3D3D", foreground="#FFFFFF")
        
        # Update combobox styles for filter and sort menus
        style.configure("TCombobox", foreground="#FFFFFF", fieldbackground="#3D3D3D")
        style.map("TCombobox", fieldbackground=[("readonly", "#3D3D3D")])
        style.map("TCombobox", selectbackground=[("readonly", "#5E5E5E")])
        style.map("TCombobox", selectforeground=[("readonly", "#FFFFFF")])
        
        # Entry styles
        style.configure("TEntry", fieldbackground="#3D3D3D", foreground="#FFFFFF")
        
    def _setup_variables(self):
        """
        Setup tkinter variables.
        """
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)
        
        self.filter_var = tk.StringVar(value="Due Today")  # Changed default filter to Due Today
        self.filter_var.trace_add("write", self._on_filter_changed)
        
        self.sort_var = tk.StringVar(value="Priority")  # Changed default sort to Priority
        
        # Add a variable to track completed tasks visibility
        self.show_completed_var = tk.BooleanVar(value=True)
        self.show_completed_var.trace_add("write", self._on_show_completed_changed)
    
    def _create_widgets(self):
        """
        Create the application widgets.
        """
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Header frame (keeping empty for potential future use)
        self.header_frame = ttk.Frame(self.main_frame)
        
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

        # Add a refresh button
        refresh_button = ttk.Button(
            filter_frame,
            text="🔄 Refresh",
            command=self._refresh_tasks,
            style="info.TButton",
            width=12
        )
        refresh_button.pack(side=LEFT, padx=(15, 5))
        
        # Replace checkbox with toggle button for completed tasks
        completed_toggle_frame = ttk.Frame(filter_frame)
        completed_toggle_frame.pack(side=LEFT, padx=(15, 5))
        
        ttk.Label(
            completed_toggle_frame, 
            text="Show Completed:", 
            font=("Helvetica", 10)
        ).pack(side=LEFT, padx=(0, 5))
        
        # Create toggle button with different text based on state
        self.completed_toggle_button = ttk.Button(
            completed_toggle_frame,
            text="On",
            command=self._toggle_completed_visibility,
            style="success.TButton" if self.show_completed_var.get() else "secondary.Outline.TButton",
            width=6
        )
        self.completed_toggle_button.pack(side=LEFT)
        
        filter_frame.pack(side=LEFT, padx=10, fill=X, expand=True)
        
        # Task list frame with scrollbar
        self.task_container_frame = ttk.Frame(self.tasks_tab)
        self.task_container_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.task_container_frame, highlightthickness=0, bg="#1C1C1C")
        scrollbar = ttk.Scrollbar(self.task_container_frame, orient="vertical", command=self.canvas.yview)
        
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
        
        # Setup the grid layout for tasks with simple implementation
        self.tasks_grid_layout = SimpleGridLayout(
            parent_frame=self.scrollable_frame,
            min_column_width=320,
            padding=5
        )
        
        # Update the scrollable frame width when canvas changes
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add mouse wheel scrolling to the canvas
        self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        # For Linux/Unix systems
        self.canvas.bind("<Button-4>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda event: self.canvas.yview_scroll(1, "units"))
        
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
    
    def _on_canvas_configure(self, event):
        """
        Update scrollable frame width when canvas is resized.
        """
        # Update the width of the frame to fill the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
        # Force update the scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # When canvas resizes, check if layout needs to be updated
        self.tasks_grid_layout.refresh_on_resize(event)
    
    def _setup_layout(self):
        """
        Layout the widgets.
        """
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        # Remove the vertical padding that was used for the title
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
        print(f"Tab changed to: {tab_name}")
        
        if tab_name == "Tasks":
            if not self.tasks_loaded or self.tasks_need_refresh:
                print("Loading tasks data")
                self._load_tasks()
                self.tasks_loaded = True
                self.tasks_need_refresh = False
            else:
                print("Using cached tasks data")
        elif tab_name == "Drafts":
            if not self.drafts_loaded or self.drafts_need_refresh:
                print("Loading drafts data")
                self.drafts_frame.load_drafts()
                self.drafts_loaded = True
                self.drafts_need_refresh = False
            else:
                print("Using cached drafts data")
    
    def _load_tasks(self):
        """
        Load tasks from the task manager.
        """
        try:
            # Clear existing tasks
            self.tasks_grid_layout.clear()

            # Get all tasks for debugging
            all_tasks = self.task_manager.get_all_tasks()
            print(f"All tasks count: {len(all_tasks)}")

            # Get tasks based on filters
            tasks = self._get_filtered_tasks()
            print(f"Filtered tasks count: {len(tasks)}")

            # Sort tasks
            tasks = self._sort_tasks(tasks)

            # Create a new debug frame every time rather than trying to reuse it
            # This avoids errors with invalid window path names
            if hasattr(self, 'debug_frame'):
                try:
                    self.debug_frame.destroy()
                except Exception:
                    pass  # Ignore errors if it's already been destroyed
            
            # Create a fresh debug frame
            self.debug_frame = ttk.Frame(self.scrollable_frame)
            self.debug_frame.grid(row=0, column=0, columnspan=10, sticky="ew", padx=10, pady=5)

            ttk.Label(
                self.debug_frame,
                text=f"Total tasks: {len(all_tasks)} | Filtered: {len(tasks)} | Filter: {self.filter_var.get()} | Show Completed: {self.show_completed_var.get()}",
                foreground="#FFFFFF",
                font=("Helvetica", 10)
            ).pack(anchor=tk.W)

            # Add tasks to the UI
            if not tasks:
                empty_label = ttk.Label(
                    self.scrollable_frame,
                    text="No tasks found. Click 'Add Task' to create a new one.",
                    font=("Helvetica", 12),
                    foreground="gray"
                )
                empty_label.grid(row=1, column=0, columnspan=10, pady=50)
            else:
                # Add tasks to the grid layout
                for task in tasks:
                    task_frame = TaskFrame(
                        self.scrollable_frame,
                        task,
                        self._on_status_change,
                        self._on_edit_task,
                        self._on_delete_task
                    )
                    # Apply consistent card styling
                    apply_card_styles(task_frame)
                    # Add to grid layout
                    self.tasks_grid_layout.add_item(task_frame)
                    print(f"Added task to UI: {task['title']}")

            # Update statistics
            self.stats_frame.update_stats()

        except Exception as e:
            error_msg = f"Error loading tasks: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # Print to console

            # Display error in UI
            error_frame = ttk.Frame(self.scrollable_frame)
            error_frame.pack(fill=X, pady=10, padx=10)

            ttk.Label(
                error_frame,
                text="Error loading tasks:",
                foreground="#FF5252",
                font=("Helvetica", 12, "bold")
            ).pack(anchor=W)

            error_text = tk.Text(error_frame, height=10, width=80, bg="#3D3D3D", fg="#FFFFFF")
            error_text.insert("1.0", error_msg)
            error_text.configure(state="disabled")
            error_text.pack(fill=X, pady=5)
    
    def _get_filtered_tasks(self):
        """
        Get tasks based on current filter and search term.
        
        Returns:
            list: Filtered tasks
        """
        search_term = self.search_var.get().lower()
        filter_value = self.filter_var.get()
        show_completed = self.show_completed_var.get()
        
        all_tasks = self.task_manager.get_all_tasks()
        print(f"Filter: {filter_value}, Search: '{search_term}', Show Completed: {show_completed}, Total tasks before filtering: {len(all_tasks)}")
        
        # Debugging: print the first task if available
        if all_tasks:
            print(f"Sample task: {all_tasks[0]['title']} - Status: {all_tasks[0]['status']}")
        
        # First apply regular filters
        filtered_tasks = all_tasks.copy()
        
        # Apply search filter
        if search_term:
            filtered_tasks = [
                task for task in filtered_tasks 
                if search_term in task["title"].lower() or 
                   search_term in (task["description"] or "").lower() or
                   any(search_term in tag.lower() for tag in task["tags"])
            ]
            print(f"After search filter: {len(filtered_tasks)} tasks")
        
        # Apply status/priority filter
        if filter_value == "All":
            # Keep all tasks, no further filtering needed
            pass
        elif filter_value in ["To Do", "In Progress", "Completed"]:
            filtered_tasks = [task for task in filtered_tasks if task["status"] == filter_value]
            print(f"After status filter: {len(filtered_tasks)} tasks")
        elif filter_value == "High Priority":
            filtered_tasks = [task for task in filtered_tasks if task["priority"] == "High"]
            print(f"After priority filter: {len(filtered_tasks)} tasks")
        elif filter_value == "Overdue":
            today = datetime.now().date()
            filtered_tasks = [
                task for task in filtered_tasks 
                if task["due_date"] and 
                   parser.parse(task["due_date"]).date() < today
            ]
            print(f"Overdue tasks: {len(filtered_tasks)}")
        elif filter_value == "Due Today":
            today = datetime.now().date()
            filtered_tasks = [
                task for task in filtered_tasks 
                if task["due_date"] and 
                   parser.parse(task["due_date"]).date() == today
            ]
            print(f"Due today tasks: {len(filtered_tasks)}")
        
        # Finally apply the completed filter - but only if not specifically showing completed tasks
        if not show_completed and filter_value != "Completed":
            filtered_tasks = [task for task in filtered_tasks if task["status"] != "Completed"]
            print(f"After hiding completed: {len(filtered_tasks)} tasks")
        
        return filtered_tasks
    
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
            # Add error handling for invalid date formats
            def get_sort_date(task):
                if not task.get("due_date"):
                    return datetime.max
                try:
                    return datetime.fromisoformat(task["due_date"])
                except (ValueError, TypeError):
                    print(f"Invalid date format for task {task['title']}: {task['due_date']}")
                    return datetime.max
            
            return sorted(tasks, key=get_sort_date)
        elif sort_by == "Priority":
            # Sort by priority: High, Medium, Low
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            return sorted(tasks, key=lambda x: priority_order.get(x["priority"], 3))
        elif sort_by == "Created Date":
            # Add error handling for invalid date formats
            def get_created_date(task):
                if not task.get("created_at"):
                    return datetime.min
                try:
                    return datetime.fromisoformat(task["created_at"])
                except (ValueError, TypeError):
                    return datetime.min
            
            return sorted(tasks, key=get_created_date)
        elif sort_by == "Title":
            return sorted(tasks, key=lambda x: x["title"].lower())
            
        return tasks
    
    def mark_tasks_for_refresh(self):
        """Mark tasks data as needing refresh."""
        self.tasks_need_refresh = True
    
    def mark_drafts_for_refresh(self):
        """Mark drafts data as needing refresh."""
        self.drafts_need_refresh = True
    
    def _open_add_dialog(self):
        """
        Open the add task dialog.
        """
        dialog = AddTaskDialog(self.root, self.task_manager)
        self.root.wait_window(dialog.top)
        self.mark_tasks_for_refresh()
        if self.notebook.tab(self.notebook.select(), "text") == "Tasks":
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
            self.mark_tasks_for_refresh()
            if self.notebook.tab(self.notebook.select(), "text") == "Tasks":
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
                self.mark_tasks_for_refresh()
                if self.notebook.tab(self.notebook.select(), "text") == "Tasks":
                    self._load_tasks()
    
    def _on_status_change(self, task_id, new_status):
        """
        Handle task status change.
        
        Args:
            task_id (str): ID of the task to update
            new_status (str): New status
        """
        self.task_manager.update_task(task_id, status=new_status)
        self.mark_tasks_for_refresh()
        if self.notebook.tab(self.notebook.select(), "text") == "Tasks":
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
    
    def _on_show_completed_changed(self, *args):
        """
        Handle show/hide completed tasks toggle changes.
        """
        print(f"Show completed changed to: {self.show_completed_var.get()}")
        self._load_tasks()
    
    def _toggle_completed_visibility(self):
        """
        Toggle the visibility of completed tasks.
        """
        # Toggle the variable value
        current_state = self.show_completed_var.get()
        self.show_completed_var.set(not current_state)
        
        # Update the button text and style
        new_state = self.show_completed_var.get()
        if new_state:
            self.completed_toggle_button.configure(
                text="On", 
                style="success.TButton"
            )
        else:
            self.completed_toggle_button.configure(
                text="Off", 
                style="secondary.Outline.TButton"
            )
    
    def _refresh_tasks(self):
        """
        Explicitly refresh the tasks data and UI.
        """
        print("Manually refreshing tasks...")
        self.mark_tasks_for_refresh()
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
