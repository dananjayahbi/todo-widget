"""
Frame for displaying task statistics.
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StatisticsFrame(ttk.Frame):
    """
    Frame for displaying task statistics.
    """
    
    def __init__(self, parent, task_manager):
        """
        Initialize the statistics frame.
        
        Args:
            parent: Parent widget
            task_manager: TaskManager instance
        """
        super().__init__(parent, padding=10)
        
        self.task_manager = task_manager
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        self._create_widgets()
        self.update_stats()
    
    def _create_widgets(self):
        """
        Create the statistics widgets.
        """
        # Title
        title_label = ttk.Label(
            self, 
            text="Task Statistics", 
            font=("Helvetica", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky=W, pady=(0, 10))
        
        # Count statistics frame
        self.count_frame = ttk.LabelFrame(self, text="Task Counts")
        self.count_frame.grid(row=1, column=0, sticky=(N, W, E, S), padx=(0, 5), pady=(0, 10))
        
        # Status statistics frame
        self.status_frame = ttk.LabelFrame(self, text="By Status")
        self.status_frame.grid(row=1, column=1, sticky=(N, W, E, S), padx=(5, 0), pady=(0, 10))
        
        # Create all labels - they'll be populated in update_stats
        self.create_stat_labels()
    
    def create_stat_labels(self):
        """
        Create all the static labels for statistics.
        """
        # Count statistics
        ttk.Label(self.count_frame, text="Total Tasks:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.total_label = ttk.Label(self.count_frame, text="0")
        self.total_label.grid(row=0, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.count_frame, text="High Priority:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.high_priority_label = ttk.Label(self.count_frame, text="0")
        self.high_priority_label.grid(row=1, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.count_frame, text="Due Today:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.due_today_label = ttk.Label(self.count_frame, text="0")
        self.due_today_label.grid(row=2, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.count_frame, text="Overdue:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.overdue_label = ttk.Label(self.count_frame, text="0", foreground="red")
        self.overdue_label.grid(row=3, column=1, sticky=E, padx=5, pady=2)
        
        # Status statistics
        ttk.Label(self.status_frame, text="To Do:").grid(row=0, column=0, sticky=W, padx=5, pady=2)
        self.todo_label = ttk.Label(self.status_frame, text="0")
        self.todo_label.grid(row=0, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.status_frame, text="In Progress:").grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.in_progress_label = ttk.Label(self.status_frame, text="0")
        self.in_progress_label.grid(row=1, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.status_frame, text="Completed:").grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.completed_label = ttk.Label(self.status_frame, text="0")
        self.completed_label.grid(row=2, column=1, sticky=E, padx=5, pady=2)
        
        ttk.Label(self.status_frame, text="Completion Rate:").grid(row=3, column=0, sticky=W, padx=5, pady=2)
        self.completion_rate_label = ttk.Label(self.status_frame, text="0%")
        self.completion_rate_label.grid(row=3, column=1, sticky=E, padx=5, pady=2)
    
    def update_stats(self):
        """
        Update the statistics display.
        """
        stats = self.task_manager.get_stats()
        
        # Update count statistics
        self.total_label.config(text=str(stats["total"]))
        self.high_priority_label.config(text=str(stats["priority"]["High"]))
        self.due_today_label.config(text=str(stats["due_today"]))
        self.overdue_label.config(text=str(stats["overdue"]))
        
        # Update status statistics
        self.todo_label.config(text=str(stats["todo"]))
        self.in_progress_label.config(text=str(stats["in_progress"]))
        self.completed_label.config(text=str(stats["completed"]))
        
        # Calculate completion rate
        if stats["total"] > 0:
            completion_rate = (stats["completed"] / stats["total"]) * 100
            self.completion_rate_label.config(text=f"{completion_rate:.1f}%")
        else:
            self.completion_rate_label.config(text="0.0%")
