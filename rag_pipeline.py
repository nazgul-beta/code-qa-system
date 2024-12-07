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

    # Create retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # Custom prompt template for code questions and documentation
    prompt_template = """You are an expert coding assistant specializing in code explanation and documentation. Analyze the provided code snippets and context carefully.

    When explaining code:
    1. Break down complex logic into simple terms
    2. Highlight key programming patterns and best practices
    3. Explain the purpose and functionality of important code segments
    4. Generate inline documentation for functions and classes when requested
    5. Provide context about how different parts of the code interact

    If asked to generate documentation:
    1. Follow standard documentation formats (e.g., Google style for Python)
    2. Include parameter descriptions, return values, and examples
    3. Document any important side effects or exceptions
    4. Maintain consistent documentation style

    Context: {context}

    Question: {question}

    Answer in a clear and structured format, highlighting important code aspects and patterns: """

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
