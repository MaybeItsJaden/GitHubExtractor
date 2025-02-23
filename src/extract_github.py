import json
import requests
import sys
import tempfile
import time
import zipfile
import shutil
from pathlib import Path

def extract_repo(repo_url):
    # Create storage directory if it doesn't exist
    storage_dir = Path("extracted_repos")
    storage_dir.mkdir(exist_ok=True)
    
    print("\n🔄 Starting repository extraction...")
    
    # Extract repo name from URL, removing .git if present
    repo_name = repo_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    
    # Create temporary directory for zip extraction
    temp_dir = Path(tempfile.mkdtemp())
    zip_path = temp_dir / f"{repo_name}.zip"
    extract_path = temp_dir / repo_name
    
    # Remove .git from the URL if present
    repo_url = repo_url.rstrip('/')
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    download_url = f"{repo_url}/archive/master.zip"
    if not download_url.startswith(('http://', 'https://')):
        download_url = f"https://github.com/{download_url}"
    
    try:
        # Try master branch first, if it fails try main branch
        print(f"📥 Attempting to download from: {download_url}")
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 404:
            # Try main branch instead
            download_url = f"{repo_url}/archive/main.zip"
            print(f"📥 Repository not found on master branch, trying main: {download_url}")
            response = requests.get(download_url, stream=True)
        
        # Check response status and provide detailed error messages
        if response.status_code == 404:
            print(f"❌ Repository not found. Please check if the URL is correct and the repository exists.")
            return
        elif response.status_code == 403:
            print(f"❌ Access forbidden. This might be a private repository or you've hit GitHub's rate limit.")
            return
        elif response.status_code != 200:
            print(f"❌ Failed to download repository. Status code: {response.status_code}")
            print(f"Error message: {response.text}")
            return
        
        # Continue with download if status is 200
        print(f"✅ Connected successfully to repository")
        
        # Download the zip file with progress indicator
        dot_count = 0
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        progress = 0
        
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress += len(chunk)
                    if total_size > 0:
                        percentage = (progress * 100) / total_size
                        sys.stdout.write(f"\rDownloading: {percentage:.1f}%")
                        sys.stdout.flush()
                    else:
                        if dot_count % 3 == 0:
                            sys.stdout.write(".")
                            sys.stdout.flush()
                        dot_count += 1
        
        print("\n📦 Download complete!")
        
        # Extract the downloaded zip file
        print("📂 Extracting files...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Process each file and write contents to a JSONL file
        print("📝 Writing contents to file...")
        output_file = storage_dir / f"{repo_name}_contents.jsonl"

        with open(output_file, "w", encoding="utf-8") as out_file:
            # Find the actual extracted directory (it might have a different name)
            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                print("❌ No files found in the extracted directory")
                return
        
            extract_path = extracted_dirs[0]  # Use the first directory found
            print(f"📂 Processing files from: {extract_path}")
            
            for file_path in extract_path.rglob("*"):
                if file_path.is_file():
                    try:
                        relative_path = str(file_path.relative_to(extract_path))
                        
                        # Skip certain file types and directories
                        if any(relative_path.startswith(x) for x in ['.git/', 'node_modules/', '.env']):
                            continue
                    
                        try:
                            content = file_path.read_text(encoding="utf-8")
                            # Format the content with proper line breaks
                            formatted_content = content.replace('\n', '\\n')
                            # Create a JSON object with formatted display
                            file_data = {
                                "type": "file",
                                "metadata": {
                                    "name": file_path.name,
                                    "path": relative_path,
                                    "language": get_file_language(relative_path),  # New helper function
                                },
                                "content": content,
                            }
                            json.dump(file_data, out_file, ensure_ascii=False, indent=None)
                            out_file.write('\n')
                            sys.stdout.write(".")
                            sys.stdout.flush()
                        except UnicodeDecodeError:
                            # Handle binary files
                            file_data = {
                                "type": "binary",
                                "name": file_path.name,
                                "path": relative_path,
                                "display": f"// Binary File: {relative_path}",
                                "content": None,
                                "error": "Binary file"
                            }
                            json.dump(file_data, out_file, ensure_ascii=False)
                            out_file.write('\n')
                    
                    except Exception as e:
                        error_data = {
                            "type": "error",
                            "path": str(relative_path),
                            "display": f"// Error in file: {relative_path}",
                            "error": f"Error reading file: {str(e)}"
                        }
                        json.dump(error_data, out_file, ensure_ascii=False)
                        out_file.write('\n')

        print(f"\n✅ Extraction complete! Saved to {output_file}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred while downloading: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    finally:
        # Clean up temporary files if they exist
        if 'temp_dir' in locals():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up temporary files: {str(e)}")

def get_file_language(file_path):
    extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.md': 'markdown',
        '.json': 'json',
        '.yml': 'yaml',
        '.yaml': 'yaml',
        '.sh': 'bash',
        '.bash': 'bash',
        '.sql': 'sql',
        '.txt': 'text',
    }
    ext = Path(file_path).suffix.lower()
    return extensions.get(ext, 'text')