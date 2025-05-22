# backend/app/services/document_processing.py
import os
from typing import List, Dict
import json

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from app.core import config
from app.services.text_extraction import extract_text_from_pdf
from app.core.database import update_document_status, update_document_embedding, get_document
#from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings

from langchain_google_genai import GoogleGenerativeAIEmbeddings
import onnxruntime
def chunk_pages(
    pages: List[Dict],
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP
) -> List[Document]:
    """
    Splits each page's text into overlapping character chunks.

    Returns LangChain Documents with metadata:
      page_content = chunk text
      metadata = { "doc_id", "page", "paragraph" }
    """
    docs: List[Document] = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    for page in pages:
        # Break into paragraphs on blank lines
        paras = [p.strip() for p in page["text"].split("\n\n") if p.strip()]
        for para_idx, para in enumerate(paras, start=1):
            # Each para may be long, so split into smaller chunks
            for chunk in splitter.split_text(para):
                docs.append(Document(
                    page_content=chunk,
                    metadata={
                        "doc_id": page["doc_id"],
                        "page": page["page"],
                        "paragraph": para_idx
                    }
                ))
    return docs
'''
class SentenceTransformerEmbedding(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        # Returns list of embedding vectors for documents
        return [self.model.encode(t, normalize_embeddings=True).tolist() for t in texts]

    def embed_query(self, text):
        # Embeds a single query string
        return self.model.encode(text, normalize_embeddings=True).tolist()
'''
def create_vector_store(
    docs: List[Document],
    persist_dir: str
) -> Chroma:
    """
    Embeds the list of Documents and writes to a ChromaDB directory.
    """

    #model_name = config.EMBEDDING_MODEL
    #if not model_name.startswith("sentence-transformers/"):
    #    model_name = f"sentence-transformers/{model_name}"
    #embedding_model = SentenceTransformerEmbedding(model_name)
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=config.GOOGLE_API_KEY)

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        # If the directory exists and is not empty, load the existing DB
        print(f"Loading existing ChromaDB from: {persist_dir}")
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding_model
        )
        # Add new documents to the existing DB
        print(f"Adding {len(docs)} new documents to the existing ChromaDB.")
        vectordb.add_documents(docs)
    else:
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
    
    vectordb.persist()
    return vectordb

def process_document(doc_id: int) -> bool:
    """
    Process a document by:
    1. Extracting text
    2. Chunking pages
    3. Creating vector embeddings
    
    Returns True if successful, False otherwise
    """
    try:
        # Get document from database
        document = get_document(doc_id)
        if not document:
            raise ValueError(f"Document with ID {doc_id} not found")
        
        # Create embedding directory for this document
        embedding_dir = os.path.join(config.EMBEDDING_DIR, f"doc_{doc_id}")
        os.makedirs(embedding_dir, exist_ok=True)
        
        # Extract text from PDF
        pages = extract_text_from_pdf(document['file_path'])
        
        # Chunk the pages
        chunked_docs = chunk_pages(pages)
        
        # Create vector store
        create_vector_store(chunked_docs, embedding_dir)
        
        # Save page data for future reference
        page_data_file = os.path.join(embedding_dir, "page_data.json")
        with open(page_data_file, 'w') as f:
            json.dump(pages, f)
        
        # Update document status in database
        update_document_embedding(doc_id, embedding_dir)
        update_document_status(
            doc_id, 
            is_processed=True, 
            page_count=len(pages)
        )
        
        return True
    
    except Exception as e:
        # Update document with error
        update_document_status(doc_id, is_processed=False, error=str(e))
        print(f"Error processing document {doc_id}: {str(e)}")
        return False