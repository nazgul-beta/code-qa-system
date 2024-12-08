from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import requests
import base64
import json
import tempfile
import os

def is_code_file(filename):
    """Check if a file is a code file based on extension."""
    code_extensions = {'.py', '.js', '.java', '.cpp', '.h', '.cs', '.rb', '.go', '.ts', '.tsx', '.jsx'}
    return any(filename.lower().endswith(ext) for ext in code_extensions)

def get_repo_contents(owner, repo, path=""):
    """Recursively get repository contents using GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {}
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        if 'rate limit exceeded' in response.text.lower():
            raise Exception("GitHub API rate limit exceeded. Please provide a GitHub token to increase the limit.")
        elif not github_token:
            raise Exception("GitHub API requires authentication. Please provide a GitHub token.")
        else:
            raise Exception(f"Access denied to GitHub repository. Please check if the repository is private and if your token has correct permissions.")
    elif response.status_code == 404:
        raise Exception(f"Repository or path not found: {owner}/{repo}/{path}")
    elif response.status_code != 200:
        raise Exception(f"Failed to fetch repo contents: HTTP {response.status_code} - {response.text}")
    
    return response.json()

def process_github_repo(owner, repo_name):
    """Process GitHub repository and return documents for RAG pipeline."""
    documents = []
    
    try:
        # Configure text splitter optimized for code analysis
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,  # Large enough to capture full functions/classes
            chunk_overlap=500,  # Significant overlap for maintaining context
            length_function=len,
            # Comprehensive separators for intelligent code splitting
            separators=[
                # Class and function definitions
                "\nclass ", "\ndef ", "\nfunction ", "\nasync def ",
                # Decorators and special methods
                "\n@", "\n    def ", "\n    async def ",
                # JavaScript/TypeScript specific
                "\nconst ", "\nlet ", "\nvar ", "\nexport ", "\nimport ",
                # Common code blocks
                "\nif __name__ == ", "\ntry:", "\nfor ", "\nwhile ",
                # General structure
                "\n\n", "\n", " ", ""
            ]
        )

        def process_contents(path=""):
            contents = get_repo_contents(owner, repo_name, path)
            
            # Handle single file response
            if not isinstance(contents, list):
                contents = [contents]
            
            for item in contents:
                if item['type'] == 'dir':
                    process_contents(item['path'])
                elif item['type'] == 'file' and is_code_file(item['name']):
                    try:
                        # Get file content
                        response = requests.get(item['download_url'])
                        if response.status_code != 200:
                            continue
                            
                        content = response.text
                        chunks = text_splitter.split_text(content)
                        
                        # Create documents with metadata
                        file_documents = [
                            Document(
                                page_content=chunk,
                                metadata={
                                    "file_name": item['name'],
                                    "file_path": item['path'],
                                    "file_type": os.path.splitext(item['name'])[1],
                                    "chunk_id": idx,
                                    "repo": f"{owner}/{repo_name}"
                                }
                            )
                            for idx, chunk in enumerate(chunks)
                        ]
                        documents.extend(file_documents)
                        
                    except Exception as e:
                        print(f"Error processing file {item['path']}: {str(e)}")
                        continue
        
        process_contents()

    except Exception as e:
        error_msg = str(e)
        if "rate limit exceeded" in error_msg.lower():
            raise Exception("GitHub API rate limit exceeded. Please wait or provide a GitHub token to increase the limit.")
        elif "requires authentication" in error_msg:
            raise Exception("This repository requires authentication. Please provide a GitHub token.")
        elif "not found" in error_msg:
            raise Exception(f"Repository not found or is private. Please check the URL and your access permissions.")
        else:
            raise Exception(f"Error accessing repository: {error_msg}")

    return documents
