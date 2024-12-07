# Code Q&A System

A powerful code Q&A system that processes GitHub repositories to answer technical questions about codebases. The system uses RAG (Retrieval Augmented Generation) to provide contextually relevant answers based on repository content.

## Features

- Process any public GitHub repository
- Answer technical questions about the codebase
- Context-aware code explanations
- Syntax-highlighted code snippets in responses
- Supports multiple programming languages

## Prerequisites

- Python 3.11 or higher
- OpenAI API key with access to:
  - text-embedding-3-large model (for embeddings generation)
  - gpt-4o-mini model (for Q&A processing)
  
Note: Make sure your OpenAI API key has access to these models. New API keys may take 5-10 minutes to fully activate.
- GitHub token (optional, but recommended for higher rate limits)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install prerequisites:

a. Install Rust (required for some Python packages):
```bash
# Windows: Download and run rustup-init.exe from https://rustup.rs/
# After installation, restart your terminal
rustup update
```

b. Install Python development tools:
```bash
# First, ensure you have the latest pip and development tools
python -m pip install --upgrade pip setuptools wheel

# For Windows users: Install additional required development tools
python -m pip install python-dev-tools
python -m pip install distutils-precedence
```

c. Install required packages:
```bash
# Install required packages (use --user flag if you're not using a virtual environment)
# Install them in groups to handle dependencies better
python -m pip install --user numpy==1.24.3 requests==2.31.0
python -m pip install --user torch==2.1.1
python -m pip install --user streamlit==1.29.0 openai>=1.6.1
python -m pip install --user langchain==0.1.0 langchain-community==0.0.10 langchain-openai==0.0.2
python -m pip install --user faiss-cpu==1.7.4 sentence-transformers==2.2.2 transformers==4.35.2

# Verify streamlit installation
python -m streamlit --version
```

If you get "command not found" error when running streamlit, you can either:
- Run using python -m: `python -m streamlit run main.py`
- Add pip's binary directory to PATH (restart terminal after):
  ```bash
  # For Unix/Mac (add to ~/.bashrc or ~/.zshrc):
  export PATH="$HOME/.local/bin:$PATH"
  
  # For Windows (add to User Environment Variables):
  # Add %APPDATA%\Python\Python3x\Scripts to PATH
  ```

3. Set up environment variables:

Create a `.env` file in the project root directory:
```env
OPENAI_API_KEY=your-openai-api-key
GITHUB_TOKEN=your-github-token  # Optional but recommended
```

4. Create the Streamlit configuration:

Create a `.streamlit/config.toml` file with the following content:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
enableCORS = false
enableXsrfProtection = false
```

## Running the Application

1. Start the Streamlit server:
```bash
streamlit run main.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Enter a GitHub repository URL in the input field
2. Wait for the repository to be processed
3. Ask questions about the codebase in the query input
4. View answers and relevant code snippets

Example questions:
- "What are the main features of this codebase?"
- "How does the error handling work?"
- "Explain the authentication process"

## Troubleshooting

1. **API Key Issues**:
   - Ensure your OpenAI API key is correctly set in the `.env` file
   - New API keys may take 5-10 minutes to fully activate
   - If you see "model not found" errors, verify your API key has access to gpt-4o-mini and text-embedding-3-large models

2. **Installation Issues**:
   - Make sure you're using Python 3.11 or higher: `python --version`
   - If you encounter GPU-related errors, you can safely ignore them as we use CPU-only versions
   - For package conflicts, try creating a fresh virtual environment:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install --upgrade pip
     pip install -r requirements.txt
     ```

3. **GitHub API Limits**:
   - Without a token, you're limited to 60 requests per hour
   - Add a GitHub token to increase this to 5000 requests per hour
   - Create a token at: https://github.com/settings/tokens

4. **Runtime Issues**:
   - If the application seems slow, it's usually due to API rate limits or large repositories
   - For better performance, ensure good internet connectivity
   - The first run might be slower as it needs to download models and process the repository

## Architecture

The system uses:
- Langchain for RAG implementation and chain orchestration
- OpenAI's text-embedding-3-large for text embeddings
- Streamlit for web interface
- GitHub API for repository processing
- FAISS for vector storage and similarity search

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Your chosen license]
