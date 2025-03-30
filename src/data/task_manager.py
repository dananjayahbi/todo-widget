"""
Task management for the ToDo application.
"""
import uuid
from datetime import datetime
from dateutil import parser
from .json_handler import JsonHandler

class TaskManager:
    """
    Manages all task operations.
    """
    PRIORITY_LEVELS = ["Low", "Medium", "High"]
    STATUS_OPTIONS = ["To Do", "In Progress", "Completed"]
    
    def __init__(self, file_path="data/todos.json", drafts_path="data/drafts.json"):
        """
        Initialize the task manager.
        
        Args:
            file_path (str): Path to the tasks JSON file
            drafts_path (str): Path to the drafts JSON file
        """
        self.json_handler = JsonHandler(file_path)
        self.drafts_handler = JsonHandler(drafts_path)
        
        # Load tasks and drafts
        self.tasks = self.json_handler.load_data()
        self.drafts = self.drafts_handler.load_data()
        
        # Print loaded data for debugging
        print(f"Loaded {len(self.tasks)} tasks from {file_path}")
        print(f"Loaded {len(self.drafts)} drafts from {drafts_path}")
        
        # Verify task structure of first task if available
        if self.tasks and len(self.tasks) > 0:
            print(f"First task: {self.tasks[0]['title']} - Status: {self.tasks[0]['status']}")
    
    def add_task(self, title, description="", due_date=None, 
                priority="Medium", tags=None, status="To Do"):
        """
        Add a new task.
        
        Args:
            title (str): Task title
            description (str): Task description
            due_date (str): Due date in ISO format
            priority (str): Priority level (Low, Medium, High)
            tags (list): List of tags
            status (str): Task status
            
        Returns:
            dict: The newly created task
        """
        if tags is None:
            tags = []
            
        new_task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "due_date": due_date,
            "priority": priority,
            "status": status,
            "tags": tags,
            "completed_at": None
        }
        
        self.tasks.append(new_task)
        self.json_handler.save_data(self.tasks)
        return new_task
    
    def add_draft(self, title, description="", tags=None):
        """
        Add a new draft task.
        
        Args:
            title (str): Draft title
            description (str): Draft description
            tags (list): List of tags
            
        Returns:
            dict: The newly created draft
        """
        if tags is None:
            tags = []
            
        new_draft = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "tags": tags
        }
        
        self.drafts.append(new_draft)
        self.drafts_handler.save_data(self.drafts)
        return new_draft
    
    def update_task(self, task_id, **kwargs):
        """
        Update an existing task.
        
        Args:
            task_id (str): ID of the task to update
            **kwargs: Task attributes to update
            
        Returns:
            dict: The updated task or None if not found
        """
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                # Update task with provided values
                for key, value in kwargs.items():
                    if key in task:
                        task[key] = value
                
                # If status changed to Completed, update completed_at
                if "status" in kwargs and kwargs["status"] == "Completed" and not task.get("completed_at"):
                    task["completed_at"] = datetime.now().isoformat()
                # If status changed from Completed, clear completed_at
                elif "status" in kwargs and kwargs["status"] != "Completed":
                    task["completed_at"] = None
                    
                self.tasks[i] = task
                self.json_handler.save_data(self.tasks)
                return task
        return None
    
    def update_draft(self, draft_id, **kwargs):
        """
        Update an existing draft.
        
        Args:
            draft_id (str): ID of the draft to update
            **kwargs: Draft attributes to update
            
        Returns:
            dict: The updated draft or None if not found
        """
        for i, draft in enumerate(self.drafts):
            if draft["id"] == draft_id:
                # Update draft with provided values
                for key, value in kwargs.items():
                    if key in draft:
                        draft[key] = value
                    
                self.drafts[i] = draft
                self.drafts_handler.save_data(self.drafts)
                return draft
        return None
    
    def delete_task(self, task_id):
        """
        Delete a task.
        
        Args:
            task_id (str): ID of the task to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.json_handler.save_data(self.tasks)
                return True
        return False
    
    def delete_draft(self, draft_id):
        """
        Delete a draft.
        
        Args:
            draft_id (str): ID of the draft to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        for i, draft in enumerate(self.drafts):
            if draft["id"] == draft_id:
                del self.drafts[i]
                self.drafts_handler.save_data(self.drafts)
                return True
        return False
    
    def get_all_tasks(self):
        """
        Get all tasks.
        
        Returns:
            list: All tasks
        """
        return self.tasks
    
    def get_all_drafts(self):
        """
        Get all draft tasks.
        
        Returns:
            list: All draft tasks
        """
        return self.drafts
    
    def get_task_by_id(self, task_id):
        """
        Get a task by ID.
        
        Args:
            task_id (str): Task ID
            
        Returns:
            dict: Task or None if not found
        """
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def get_draft_by_id(self, draft_id):
        """
        Get a draft by ID.
        
        Args:
            draft_id (str): Draft ID
            
        Returns:
            dict: Draft or None if not found
        """
        for draft in self.drafts:
            if draft["id"] == draft_id:
                return draft
        return None
    
    def get_tasks_by_status(self, status):
        """
        Get tasks by status.
        
        Args:
            status (str): Task status
            
        Returns:
            list: Tasks with the specified status
        """
        return [task for task in self.tasks if task["status"] == status]
    
    def get_tasks_by_priority(self, priority):
        """
        Get tasks by priority.
        
        Args:
            priority (str): Task priority
            
        Returns:
            list: Tasks with the specified priority
        """
        return [task for task in self.tasks if task["priority"] == priority]
    
    def get_tasks_by_tag(self, tag):
        """
        Get tasks by tag.
        
        Args:
            tag (str): Task tag
            
        Returns:
            list: Tasks with the specified tag
        """
        return [task for task in self.tasks if tag in task["tags"]]
    
    def get_tasks_due_today(self):
        """
        Get tasks due today.
        
        Returns:
            list: Tasks due today
        """
        today = datetime.now().date()
        due_today = [
            task for task in self.tasks 
            if task["due_date"] and 
            parser.parse(task["due_date"]).date() == today
        ]
        print(f"Due today: {len(due_today)} tasks, today is {today}")
        return due_today
    
    def get_tasks_overdue(self):
        """
        Get overdue tasks.
        
        Returns:
            list: Overdue tasks
        """
        today = datetime.now().date()
        overdue = [
            task for task in self.tasks 
            if (task["status"] != "Completed" and
               task["due_date"] and 
               parser.parse(task["due_date"]).date() < today)
        ]
        print(f"Overdue: {len(overdue)} tasks, today is {today}")
        return overdue
    
    def get_stats(self):
        """
        Get task statistics.
        
        Returns:
            dict: Task statistics
        """
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t["status"] == "Completed"])
        in_progress = len([t for t in self.tasks if t["status"] == "In Progress"])
        todo = len([t for t in self.tasks if t["status"] == "To Do"])
        
        priority_stats = {
            "Low": len([t for t in self.tasks if t["priority"] == "Low"]),
            "Medium": len([t for t in self.tasks if t["priority"] == "Medium"]),
            "High": len([t for t in self.tasks if t["priority"] == "High"])
        }
        
        overdue = len(self.get_tasks_overdue())
        due_today = len(self.get_tasks_due_today())
        draft_count = len(self.drafts)
        
        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "todo": todo,
            "priority": priority_stats,
            "overdue": overdue,
            "due_today": due_today,
            "draft_count": draft_count
        }
