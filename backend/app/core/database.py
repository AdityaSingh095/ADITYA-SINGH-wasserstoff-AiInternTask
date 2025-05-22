# backend/app/core/database.py
import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
import os
from app.core import config

def dict_factory(cursor, row):
    """Convert database row objects to dictionaries"""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(config.DATABASE_URL.replace("sqlite:///", ""))
    conn.row_factory = dict_factory
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        is_processed BOOLEAN DEFAULT FALSE,
        processing_error TEXT,
        page_count INTEGER,
        metadata TEXT,
        embedding_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create a trigger to update the updated_at timestamp
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_documents_timestamp
    AFTER UPDATE ON documents
    FOR EACH ROW
    BEGIN
        UPDATE documents SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END;
    ''')
    
    conn.commit()
    conn.close()

# Document functions
def save_document(
    filename: str, 
    original_filename: str, 
    file_path: str, 
    file_type: str, 
    file_size: int
) -> int:
    """Save document metadata to database and return the document ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO documents (filename, original_filename, file_path, file_type, file_size)
    VALUES (?, ?, ?, ?, ?)
    ''', (filename, original_filename, file_path, file_type, file_size))
    
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return doc_id

def update_document_status(doc_id: int, is_processed: bool, page_count: Optional[int] = None, error: Optional[str] = None):
    """Update document processing status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    update_values = {"is_processed": is_processed}
    if page_count is not None:
        update_values["page_count"] = page_count
    if error is not None:
        update_values["processing_error"] = error
    
    set_clause = ", ".join([f"{k} = ?" for k in update_values.keys()])
    values = list(update_values.values())
    values.append(doc_id)
    
    cursor.execute(f"UPDATE documents SET {set_clause} WHERE id = ?", values)
    
    conn.commit()
    conn.close()

def update_document_embedding(doc_id: int, embedding_path: str):
    """Update document embedding path"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE documents SET embedding_path = ? WHERE id = ?", 
        (embedding_path, doc_id)
    )
    
    conn.commit()
    conn.close()

def get_document(doc_id: int) -> Optional[Dict]:
    """Get document by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    document = cursor.fetchone()
    
    conn.close()
    return document

def get_all_documents() -> List[Dict]:
    """Get all documents"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
    documents = cursor.fetchall()
    
    conn.close()
    return documents

def get_documents_by_ids(doc_ids: List[int]) -> List[Dict]:
    """Get documents by IDs"""
    if not doc_ids:
        return []
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    placeholders = ",".join(["?"] * len(doc_ids))
    cursor.execute(f"SELECT * FROM documents WHERE id IN ({placeholders})", doc_ids)
    documents = cursor.fetchall()
    
    conn.close()
    return documents

# Initialize the database on module import
init_db()