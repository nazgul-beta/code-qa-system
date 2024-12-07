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
  - text-embedding-3-large (for embeddings)
  - gpt-4o-mini (for Q&A)
- GitHub token (optional, but recommended for higher rate limits)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install required packages:
```bash
pip install streamlit langchain-community langchain-openai faiss-cpu openai
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
   - Ensure your OpenAI API key has access to required models
   - New API keys may take 5-10 minutes to fully activate

2. **Rate Limits**:
   - If you encounter GitHub API rate limits, add a GitHub token
   - For heavy usage, consider upgrading your OpenAI API tier

3. **Model Access**:
   - If you see "model not found" errors, wait a few minutes for API access to propagate
   - Verify your OpenAI account has access to required models

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
