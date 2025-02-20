#!/usr/bin/env python3
from extract_github import extract_repo

def main():
    print("🔹 Welcome to GitHub Repository Extractor 🔹")
    repo_url = input("Enter the GitHub repository URL: ").strip()
    
    if not repo_url.startswith("https://github.com/"):
        print("❌ Invalid GitHub repository URL. Please enter a valid GitHub URL")
        return
    
    # Clean up the URL
    repo_url = repo_url.rstrip('/')
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    
    extract_repo(repo_url)

if __name__ == "__main__":
    main()