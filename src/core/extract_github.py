"""
Core functionality for extracting GitHub repositories.
"""

import os
import requests
import zipfile
import io
import logging
import re
from urllib.parse import urlparse

def extract_repository(repo_url, output_dir='./output'):
    """
    Extract a GitHub repository to the specified output directory.
    
    Args:
        repo_url (str): URL of the GitHub repository
        output_dir (str): Directory to save the extracted repository
    
    Returns:
        bool: True if extraction was successful, False otherwise
    """
    logging.info(f"Extracting repository: {repo_url}")
    
    try:
        # Clean and normalize the GitHub URL
        repo_url = normalize_github_url(repo_url)
        if not repo_url:
            logging.error("Invalid GitHub repository URL format")
            return False
            
        # Parse the GitHub URL to get owner and repo name
        owner, repo = parse_github_url(repo_url)
        
        if not owner or not repo:
            logging.error(f"Could not parse owner and repository from URL: {repo_url}")
            return False
            
        logging.info(f"Attempting to download repository: {owner}/{repo}")
        
        # Try main branch first
        download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
        logging.info(f"Trying main branch: {download_url}")
        response = requests.get(download_url)
        
        # If main branch fails, try master branch
        if response.status_code != 200:
            download_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
            logging.info(f"Trying master branch: {download_url}")
            response = requests.get(download_url)
            
        # If both fail, try default branch (which GitHub will redirect to)
        if response.status_code != 200:
            download_url = f"https://github.com/{owner}/{repo}/archive/HEAD.zip"
            logging.info(f"Trying default branch: {download_url}")
            response = requests.get(download_url)
        
        # Check if we got a successful response
        if response.status_code != 200:
            error_message = f"Failed to download repository: {response.status_code}"
            if response.status_code == 404:
                error_message += " (Repository not found or is private)"
            logging.error(error_message)
            return False
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract the zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(output_dir)
            
        logging.info(f"Repository extracted to: {output_dir}")
        return True
        
    except Exception as e:
        logging.error(f"Error extracting repository: {str(e)}")
        return False

def normalize_github_url(url):
    """
    Normalize a GitHub repository URL to a standard format.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        str: Normalized URL or None if invalid
    """
    # Remove trailing slashes and .git extension
    url = url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Handle different GitHub URL formats
    github_patterns = [
        r'https?://github\.com/([^/]+)/([^/]+)',  # https://github.com/user/repo
        r'git@github\.com:([^/]+)/([^/]+)',       # git@github.com:user/repo
        r'github\.com/([^/]+)/([^/]+)',           # github.com/user/repo
        r'([^/]+)/([^/]+)'                        # user/repo (simple format)
    ]
    
    for pattern in github_patterns:
        match = re.match(pattern, url)
        if match:
            owner, repo = match.groups()
            return f"https://github.com/{owner}/{repo}"
    
    return None

def parse_github_url(url):
    """
    Parse a GitHub URL to extract owner and repository name.
    
    Args:
        url (str): GitHub repository URL
        
    Returns:
        tuple: (owner, repository) or (None, None) if parsing fails
    """
    try:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]
    except:
        pass
    
    return None, None

def analyze_repository(repo_path):
    """
    Analyze a repository to extract useful information.
    
    Args:
        repo_path (str): Path to the extracted repository
        
    Returns:
        dict: Repository analysis results
    """
    # This is a placeholder for future implementation
    return {
        "files_count": 0,
        "languages": [],
        "size": 0
    } 