import os
import json
import glob
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
from pinecone import Pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Init Downloader
dl = Downloader("AgentSoup", "agent@soup.local")
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index = pc.Index("sec")

def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=' ', strip=True)
    import re
    return re.sub(r'\s+', ' ', text)

def process_and_upload(ticker: str, form_type="10-K"):
    print(f"Fetching {form_type} for {ticker}...")
    dl.get(form_type, ticker, limit=1)
    
    # Locate file
    download_dir = "sec-edgar-filings"
    search_pattern = os.path.join(download_dir, ticker, form_type, "*", "*.txt")
    files = glob.glob(search_pattern)
    if not files:
        files = glob.glob(os.path.join(download_dir, ticker, form_type, "*", "*.html"))
        
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    text = clean_html(content)
    print(f"Cleaned {ticker} {form_type}. Characters: len(text)")
    
    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.split_text(text)
    
    print(f"Uploading {len(docs)} chunks to Pinecone index 'sec'...")
    # Upload via Inference Upsert if available, or we just pass the text and let Serverless inference do it!
    # Wait, simple pinecone upsert for integrated models takes text!
    # Format for Pinecone Integrated Inference:
    records = []
    for i, chunk in enumerate(docs):
        records.append({
            "id": f"{ticker}-{form_type}-{i}",
            "text": chunk, # The llama-text-embed-v2 model embedded in Pinecone will auto-vectorize this!
        })
        
    # Batch upsert 100 at a time
    batch_size = 96 # pinecone batch max embed is commonly 96
    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i:i+batch_size]
        
        try:
            # Generate embeddings natively
            embed_resp = pc.inference.embed(
                model="llama-text-embed-v2",
                inputs=batch_docs,
                parameters={"input_type": "passage"}
            )
            
            # Format vectors for upsert
            vectors = []
            for j, data in enumerate(embed_resp):
                vectors.append({
                    "id": f"{ticker}-{form_type}-{i+j}",
                    "values": data.values,
                    "metadata": {"text": batch_docs[j]}
                })
                
            index.upsert(vectors=vectors)
            print(f"Upserted {i+len(batch_docs)}/{len(docs)} chunks for {ticker}")
        except Exception as e:
            print(f"Failure upserting chunk {i}: {e}")
            break

process_and_upload("AAPL")
process_and_upload("MSFT")
