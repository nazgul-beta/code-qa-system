from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_rag_pipeline(documents, max_retries=3):
    """Setup the RAG pipeline with the processed documents and retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing OpenAI embeddings (attempt {attempt + 1}/{max_retries})...")
            
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            test_embedding = embeddings.embed_query("test")
            logger.info("Successfully initialized text-embedding-3-large model")
            break
        except Exception as e:
            error_msg = str(e)
            if "does not have access to model" in error_msg or "not allowed to generate embeddings" in error_msg:
                if attempt < max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1}: API access might not be fully propagated. Retrying in a few seconds...")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise Exception("OpenAI API access is still being activated. This typically takes 5-10 minutes after enabling access. Please try again in a few minutes.")
            raise Exception(f"Error initializing embeddings: {error_msg}")

    try:
        logger.info("Creating vector store...")
        vector_store = FAISS.from_documents(documents, embeddings)
        logger.info("Vector store created successfully")
    except Exception as e:
        logger.error(f"Error in embedding setup: {str(e)}")
        raise Exception(f"Error setting up embeddings: {str(e)}")

    # Create retriever with enhanced context window
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,  # Retrieve more context documents for better understanding
            "fetch_k": 8,  # Fetch more candidates before selecting top k
            "lambda_mult": 0.5,  # Adjust diversity of results
        }
    )

    # Enhanced prompt template for context-aware code explanations
    prompt_template = """You are an expert coding assistant specializing in code explanation and documentation, with deep understanding of software architecture and design patterns. Analyze the provided code snippets and context carefully.

    When explaining code:
    1. Break down complex logic into simple terms using clear examples
    2. Highlight key programming patterns, design principles, and best practices used
    3. Explain the purpose, functionality, and rationale behind code decisions
    4. Identify potential improvements or optimization opportunities
    5. Provide context about how different components interact
    6. Include relevant code examples when helpful

    For documentation requests:
    1. Follow standard documentation formats (e.g., Google style for Python)
    2. Include comprehensive parameter descriptions, return values, and examples
    3. Document side effects, exceptions, and edge cases
    4. Maintain consistent documentation style
    5. Add usage examples and common patterns
    6. Note any dependencies or requirements

    For debugging or issue analysis:
    1. Identify potential problem areas in the code
    2. Suggest improvements for error handling
    3. Point out common pitfalls or edge cases
    4. Recommend best practices for testing

    For architectural questions:
    1. Explain the overall design patterns used
    2. Describe component interactions and data flow
    3. Highlight scalability and maintainability aspects
    4. Discuss trade-offs in the current implementation

    Context: {context}

    Question: {question}

    Answer in a clear, structured format with the following sections as relevant:
    1. Overview: Brief summary of the main points
    2. Detailed Explanation: In-depth analysis with examples
    3. Key Points: Important takeaways or best practices
    4. Recommendations: Suggestions for improvements (if applicable)
    """

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Create QA chain with gpt-4o-mini model
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0, model="gpt-4o-mini"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain

def query_codebase(qa_chain, query, max_retries=3):
    """Query the codebase using the RAG pipeline with retry logic."""
    for attempt in range(max_retries):
        try:
            results = qa_chain.invoke({"query": query})
            return {
                "answer": results["result"],
                "source_documents": results["source_documents"]
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
            
            if "does not have access to model" in error_msg:
                if attempt < max_retries - 1:
                    logger.info("API access might not be fully propagated. Retrying...")
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return {
                    "answer": "The OpenAI API access is still being activated. This typically takes 5-10 minutes after enabling access. Please try again in a few minutes.",
                    "source_documents": []
                }
            
            return {
                "answer": f"Error processing query: {error_msg}",
                "source_documents": []
            }
