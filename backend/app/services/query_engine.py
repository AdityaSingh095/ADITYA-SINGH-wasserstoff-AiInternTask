# backend/app/services/query_engine.py
import os
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.docstore.document import Document

from app.core import config
from app.core.database import get_document
from app.services.embedding_service import retrieve_relevant_chunks

def group_chunks_by_document(chunks_by_doc_id: Dict[int, List[Document]]) -> Dict[str, List[Dict]]:
    """
    Group chunks by document for generating responses.
    
    Returns a dictionary mapping doc_ids to lists of chunk information:
    {
        "doc_id.pdf": [
            {"text": "[Page 1, Para 2] chunk content...", "page": 1, "paragraph": 2},
            ...
        ]
    }
    """
    grouped = {}
    
    for doc_id, chunks in chunks_by_doc_id.items():
        document = get_document(doc_id)
        if not document:
            continue
            
        doc_filename = document['original_filename']
        grouped[doc_filename] = []
        
        for chunk in chunks:
            citation = f"[Page {chunk.metadata['page']}, Paragraph {chunk.metadata['paragraph']}]"
            chunk_info = {
                "text": f"{citation} {chunk.page_content}",
                "page": chunk.metadata["page"],
                "paragraph": chunk.metadata["paragraph"]
            }
            grouped[doc_filename].append(chunk_info)
    
    return grouped

def get_llm():
    """Get the LLM for generating answers"""
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL, 
        temperature=config.LLM_TEMPERATURE,
        google_api_key=config.GOOGLE_API_KEY
    )


def get_document_answer(
    doc_id: str,
    chunk_list: List[Dict],
    question: str,
    llm=None
) -> Dict:
    """
    Generate an answer for a specific document based on retrieved chunks
    
    Args:
        doc_id: Document ID (filename)
        chunk_list: List of chunks with text and citation info
        question: User question
        llm: Optional LLM instance
        
    Returns:
        Dictionary with response and citations
    """
    if llm is None:
        llm = get_llm()
    
    context = "\n\n".join(chunk["text"] for chunk in chunk_list)

    prompt = f"""
    You are an expert assistant. Given the context from documents and a user question, provide a precise answer with clear citations.
    If the answer is not provided in context just return "answer not available in pdf". Don't make up your own answers.
    
    Context:
    {context}

    Question: {question}

    Answer with proper citations (page, paragraph).
    """

    result = llm.invoke(prompt)
    response = result.content if hasattr(result, "content") else result
    
    return {
        "response": response,
        "citations": [{"page": c["page"], "paragraph": c["paragraph"]} for c in chunk_list]
    }

def synthesize_themes(doc_responses: Dict[str, Dict], llm=None) -> List[Dict]:
    """
    Takes the grouped answers from documents and generates a summary of common themes.
    Each theme is backed with citations at the document level.
    
    Returns a list of themes:
    [
        {"theme": "Theme name", "description": "Theme description", "documents": ["doc1.pdf", "doc2.pdf"]},
        ...
    ]
    """
    if llm is None:
        llm = get_llm()
    
    theme_input = ""
    for doc_id, data in doc_responses.items():
        theme_input += f"Document: {doc_id}\nResponse:\n{data['response']}\n\n"

    prompt = f"""Identify key themes from the document responses and present them as concise headlines in a few words and a brief description about the theme and add documents that have this theme.

    Document Responses:
    {theme_input}

    For each theme, provide:
    1. Theme name (short headline)
    2. Documents that have this theme
    3. Brief description of the theme

    Format your response exactly like this:
    THEME: [theme name]
    DOCUMENTS: [comma-separated list of document names]
    DESCRIPTION: [brief description]

    Repeat this format for each theme you identify.
    """
    
    response = llm.invoke(prompt)
    theme_text = response.content if hasattr(response, "content") else response
    
    # Parse themes from the response
    themes = []
    current_theme = {}
    
    for line in theme_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("THEME:"):
            if current_theme and "theme" in current_theme:  # Save previous theme
                themes.append(current_theme)
            current_theme = {"theme": line[6:].strip()}
        elif line.startswith("DOCUMENTS:"):
            current_theme["documents"] = [doc.strip() for doc in line[10:].split(",")]
        elif line.startswith("DESCRIPTION:"):
            current_theme["description"] = line[12:].strip()
    
    # Add the last theme
    if current_theme and "theme" in current_theme:
        themes.append(current_theme)
    
    return themes

def process_user_query(
    question: str,
    doc_ids: List[int] = None,
    k: int = config.TOP_K_RESULTS
) -> Dict:
    """
    Process a user query against selected documents
    
    Args:
        question: User question
        doc_ids: List of document IDs to search (if None, search all processed documents)
        k: Number of chunks to retrieve per document
        
    Returns:
        Dictionary with document responses and themes
    """
    # Get relevant chunks from documents
    chunks_by_doc_id = retrieve_relevant_chunks(question, doc_ids, k)
    
    # Group chunks by document
    grouped_chunks = group_chunks_by_document(chunks_by_doc_id)
    
    # No results found
    if not grouped_chunks:
        return {
            "document_responses": {},
            "themes": []
        }
    
    # Get LLM
    llm = get_llm()
    
    # Generate answers for each document
    document_responses = {}
    for doc_id, chunk_list in grouped_chunks.items():
        document_responses[doc_id] = get_document_answer(doc_id, chunk_list, question, llm)
    
    # Synthesize themes across documents
    themes = synthesize_themes(document_responses, llm)
    
    return {
        "document_responses": document_responses,
        "themes": themes
    }