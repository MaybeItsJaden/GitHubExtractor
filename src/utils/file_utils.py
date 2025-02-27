"""
Utility functions for file handling.
"""

import os
import shutil
import logging

def ensure_directory(directory_path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def get_file_size(file_path):
    """
    Get the size of a file in bytes.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Size of the file in bytes, or 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError):
        return 0

def get_directory_size(directory_path):
    """
    Calculate the total size of a directory in bytes.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        int: Total size in bytes
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += get_file_size(file_path)
    return total_size

def clean_directory(directory_path):
    """
    Remove all contents from a directory without deleting the directory itself.
    
    Args:
        directory_path (str): Path to the directory to clean
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not os.path.exists(directory_path):
            return True
            
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        return True
    except Exception as e:
        logging.error(f"Error cleaning directory {directory_path}: {str(e)}")
        return False 