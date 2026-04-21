import os
import glob
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

def check_pinecone_env():
    if not os.getenv("PINECONE_API_KEY"):
        raise ValueError("PINECONE_API_KEY must be set in .env")

def get_rag_context(ticker: str, form_type: str = "10-K", query: str = "financial performance, risks, strategic initiatives", top_k: int = 15) -> str:
    """
    Retrieves the most relevant chunks from the Pinecone vector database using Pinecone Inference API.
    """
    check_pinecone_env()
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("sec")
    
    try:
        # Embed the query
        embed_resp = pc.inference.embed(
            model="llama-text-embed-v2",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        query_vector = embed_resp[0].values
        
        # Search the index. The text is automatically mapped into metadata['text'] 
        # by Pinecone's integrated inference feature.
        results = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        
        context_chunks = []
        for match in results.matches:
            # Metadata should hold the original text
            text = match.metadata.get("text", "")
            if text:
                context_chunks.append(text)
                
        return "\n\n---\n\n".join(context_chunks)
    except Exception as e:
        return f"Warning: RAG Retrieval failed: {e}"
