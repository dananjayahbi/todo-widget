#!/usr/bin/env python3
"""
Main entry point for the ToDo Widget application.
"""
import os
import sys
import json
from src.ui.main_window import TodoApp
from src.data.task_manager import TaskManager

def main():
    """
    Initialize and run the application.
    """
    # Ensure required directories exist
    os.makedirs('data', exist_ok=True)
    
    # Ensure both JSON files exist
    ensure_json_file('data/todos.json')
    ensure_json_file('data/drafts.json')
    
    # Test draft functionality
    drafts_path = 'data/drafts.json'
    with open(drafts_path, 'r') as file:
        drafts = json.load(file)
    
    # If no drafts exist, try creating a test draft
    if not drafts:
        try:
            task_manager = TaskManager()
            task_manager.add_draft(
                title="Test Draft", 
                description="This is a test draft created on startup",
                tags=["test"]
            )
            print("Added test draft successfully")
        except Exception as e:
            print(f"Error creating test draft: {str(e)}")
    
    # Start the application
    app = TodoApp()
    app.run()

def ensure_json_file(file_path):
    """
    Ensure that a JSON file exists, creating it if it doesn't.
    
    Args:
        file_path (str): Path to the JSON file
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([], file)

if __name__ == "__main__":
    main()
