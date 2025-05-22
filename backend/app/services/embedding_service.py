# backend/app/services/embedding_service.py
import os
from typing import List, Dict, Optional
import json

#from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

from langchain.embeddings.base import Embeddings
#from sentence_transformers import SentenceTransformer

from langchain_google_genai import GoogleGenerativeAIEmbeddings

import onnxruntime
from app.core import config
from app.core.database import get_document, get_documents_by_ids, get_all_documents
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

c


def get_embedding_model():
    """Get the embedding model to use for queries"""
    model_name = config.EMBEDDING_MODEL
    
    # Add prefix if missing
    if not model_name.startswith("sentence-transformers/"):
        model_name = f"sentence-transformers/{model_name}"
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
'''
def get_embedding_model():
    embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=config.GOOGLE_API_KEY)
    return embedding_model


    
def get_vector_store_for_document(doc_id: int) -> Optional[Chroma]:
    """Get the vector store for a specific document"""
    document = get_document(doc_id)
    
    if not document or not document['embedding_path'] or not document['is_processed']:
        return None
    
    embedding_model = get_embedding_model()
    vector_store = Chroma(
        persist_directory=document['embedding_path'],
        embedding_function=embedding_model
    )
    
    return vector_store

def get_document_page_data(doc_id: int) -> List[Dict]:
    """Get the page data for a document"""
    document = get_document(doc_id)
    
    if not document or not document['embedding_path']:
        return []
    
    page_data_file = os.path.join(document['embedding_path'], "page_data.json")
    
    if not os.path.exists(page_data_file):
        return []
    
    with open(page_data_file, 'r') as f:
        return json.load(f)

def retrieve_relevant_chunks(
    question: str,
    doc_ids: List[int] = None,
    k: int = config.TOP_K_RESULTS
) -> Dict[int, List[Document]]:
    """
    Retrieve relevant chunks from documents based on a question
    
    Args:
        question: The question to search for
        doc_ids: List of document IDs to search (if None, search all processed documents)
        k: Number of chunks to retrieve per document
        
    Returns:
        Dict mapping document IDs to lists of retrieved chunks
    """
    embedding_model = get_embedding_model()
    question_embedding = embedding_model.embed_query(question)
    
    # Get documents to search
    if doc_ids:
        documents = get_documents_by_ids(doc_ids)
    else:
        documents = get_all_documents()
    
    # Filter to only processed documents with embeddings
    documents = [
        doc for doc in documents 
        if doc['is_processed'] and doc['embedding_path']
    ]
    
    results = {}
    
    for document in documents:
        doc_id = document['id']
        vector_store = get_vector_store_for_document(doc_id)
        
        if not vector_store:
            continue
            
        # Search for similar chunks
        chunks = vector_store.similarity_search_by_vector(
            question_embedding, 
            k=k
        )
        
        if chunks:
            results[doc_id] = chunks
    
    return results