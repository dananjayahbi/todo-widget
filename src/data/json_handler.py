"""
JSON file operations for the ToDo application.
"""
import json
import os
from datetime import datetime
import logging

class JsonHandler:
    """
    Handles all JSON file operations.
    """
    def __init__(self, file_path="data/todos.json"):
        """
        Initialize the JSON handler with the specified file path.
        
        Args:
            file_path (str): Path to the JSON file
        """
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """
        Ensure the JSON file exists, create it if it doesn't.
        """
        if not os.path.exists(self.file_path):
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([], file)

    def load_data(self):
        """
        Load data from the JSON file.
        
        Returns:
            list: List of todo items
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            logging.error("Error decoding JSON file. Creating a new one.")
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump([], file)
            return []
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            return []

    def save_data(self, data):
        """
        Save data to the JSON file.
        
        Args:
            data (list): List of todo items to save
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, default=self._json_serial)
            return True
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")
            return False
    
    @staticmethod
    def _json_serial(obj):
        """
        JSON serializer for objects not serializable by default json code
        
        Args:
            obj: Object to serialize
            
        Returns:
            str: Serialized object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
