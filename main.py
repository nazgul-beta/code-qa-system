import streamlit as st
from code_processor import process_github_repo
from rag_pipeline import setup_rag_pipeline, query_codebase
import tempfile
import os
import re
import requests
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add error handler for NumPy-related issues
def handle_numpy_error():
    error_message = """
    NumPy initialization error detected. This is likely due to Windows compatibility issues.
    
    Please try the following steps:
    1. Uninstall the current NumPy installation:
       ```
       python -m pip uninstall numpy
       ```
    2. Install the stable Windows version:
       ```
       python -m pip install numpy==1.26.2
       ```
    3. Restart the application
    
    If the issue persists, please check the troubleshooting section in the README.
    """
    st.error(error_message)
    logger.error("NumPy initialization failed")

# Configure Streamlit page
st.set_page_config(
    page_title="Code Q&A System",
    page_icon="💻",
    layout="wide"
)

def extract_repo_info(github_url):
    """Extract owner and repo name from GitHub URL."""
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, github_url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def main():
    try:
        # Try importing numpy here to catch any initialization errors
        try:
            import numpy as np
            logger.info("NumPy initialized successfully")
        except Exception as numpy_error:
            logger.error(f"NumPy initialization error: {str(numpy_error)}")
            handle_numpy_error()
            return

        st.title("💻 Code Q&A System")
        st.write("Enter a GitHub repository URL to analyze its code!")

        # Display initialization status
        st.info("Application initialized and ready to process repositories.")
        
        # Session state initialization
        if 'rag_pipeline' not in st.session_state:
            st.session_state.rag_pipeline = None
            logger.info("Initialized rag_pipeline session state")
        if 'repo_processed' not in st.session_state:
            st.session_state.repo_processed = False
            logger.info("Initialized repo_processed session state")
        if 'current_repo' not in st.session_state:
            st.session_state.current_repo = None
            logger.info("Initialized current_repo session state")
        if 'code_documents' not in st.session_state:
            st.session_state.code_documents = None
            logger.info("Initialized code_documents session state")
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")
        return

    # GitHub repository input
    github_url = st.text_input("Enter GitHub Repository URL", 
                              placeholder="https://github.com/owner/repo")

    # Add a button to clear the current repository
    if st.session_state.repo_processed:
        if st.button("🔄 Process New Repository"):
            st.session_state.repo_processed = False
            st.session_state.rag_pipeline = None
            st.session_state.current_repo = None
            st.session_state.code_documents = None
            st.experimental_rerun()

    if github_url:
        owner, repo_name = extract_repo_info(github_url)
        
        # Check if it's a new repository
        current_repo = f"{owner}/{repo_name}" if owner and repo_name else None
        if current_repo != st.session_state.get('current_repo'):
            st.session_state.repo_processed = False
            st.session_state.rag_pipeline = None
            st.session_state.current_repo = current_repo
        
        if owner and repo_name:
            # Check if we need to process this repository
            current_repo = f"{owner}/{repo_name}"
            if current_repo != st.session_state.get('current_repo'):
                with st.spinner("Fetching and processing repository..."):
                    try:
                        # Process repository and setup RAG pipeline
                        code_documents = process_github_repo(owner, repo_name)
                        st.session_state.code_documents = code_documents  # Store documents
                        st.session_state.rag_pipeline = setup_rag_pipeline(code_documents)
                        st.session_state.repo_processed = True
                        st.session_state.current_repo = current_repo
                        st.success(f"Successfully processed repository: {owner}/{repo_name}")
                except Exception as e:
                    error_message = str(e)
                    if "api_key" in error_message.lower():
                        st.error("OpenAI API key is missing or invalid. Please check your API key configuration.")
                    elif "model_not_found" in error_message or "does not have access to model" in error_message:
                        st.warning("OpenAI API model access is not active yet. This is normal if you just enabled access to new models.")
                        st.info("Please wait a few minutes for the changes to take effect. API access changes can take 5-10 minutes to propagate.")
                        if st.button("🔄 Retry Processing"):
                            st.experimental_rerun()
                    else:
                        st.error(f"Error processing repository: {error_message}")
                        logger.error(f"Repository processing error: {error_message}")
                    st.session_state.repo_processed = False
        else:
            st.error("Invalid GitHub repository URL format")

    # Q&A Interface
    if st.session_state.rag_pipeline:
        st.markdown("### Ask Questions About Your Code")
        query = st.text_input("Enter your question:")

        if query:
            with st.spinner("Searching through the codebase..."):
                try:
                    results = query_codebase(st.session_state.rag_pipeline, query)
                    
                    st.markdown("### Answer")
                    st.write(results['answer'])
                    
                    st.markdown("### Relevant Code Snippets")
                    for idx, context in enumerate(results['source_documents'], 1):
                        with st.expander(f"Snippet {idx} - {context.metadata.get('file_name', 'Unknown')}"):
                            st.code(context.page_content, language='python')
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    logger.error(f"Query processing error: {str(e)}")

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 11):
            st.error("This application requires Python 3.11 or higher. Please upgrade your Python installation.")
            sys.exit(1)
            
        main()
    except ModuleNotFoundError as e:
        error_msg = str(e)
        module_name = error_msg.split("'")[1] if "'" in error_msg else error_msg
        
        if "distutils" in error_msg:
            st.error("""
            The distutils module is missing. This is common with Python 3.13.0.
            Please install setuptools first:
            ```
            python -m pip install setuptools
            python -m pip install wheel
            python -m pip install numpy==1.26.2
            ```
            """)
        else:
            st.error(f"""
            Missing required module: {module_name}
            
            Please install the required package:
            ```
            python -m pip install {module_name}
            ```
            
            If you're experiencing installation issues, please check the troubleshooting section in the README.
            """)
        logger.error(f"Missing module: {error_msg}")
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Main application error: {str(e)}")
        if "numpy" in str(e).lower():
            handle_numpy_error()
