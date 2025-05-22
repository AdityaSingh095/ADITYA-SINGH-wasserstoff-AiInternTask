import streamlit as st
import pandas as pd
from utils.api_client import APIClient

class DocumentManager:
    def __init__(self):
        self.api_client = APIClient()
    
    def _format_file_size(self, size_bytes):
        """Format file size from bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def _load_documents(self):
        """Load documents from API"""
        try:
            response = self.api_client.get_documents()
            documents = response.get("documents", [])
            
            # Format the data for display
            for doc in documents:
                doc["file_size_formatted"] = self._format_file_size(doc["file_size"])
                doc["status"] = "✅ Processed" if doc["is_processed"] else "⏳ Processing"
                if doc["processing_error"]:
                    doc["status"] = "❌ Error"
            
            return documents
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
            return []
    
    def _upload_document(self, uploaded_file):
        """Upload a document through the API"""
        try:
            response = self.api_client.upload_document(uploaded_file)
            st.success(f"Document '{uploaded_file.name}' uploaded successfully! Processing...")
            st.session_state.doc_upload_success = True
            return response
        except Exception as e:
            st.error(f"Error uploading document: {str(e)}")
            return None
    
    def _reprocess_document(self, doc_id):
        """Reprocess a document through API"""
        try:
            self.api_client.reprocess_document(doc_id)
            st.success("Document reprocessing started")
            return True
        except Exception as e:
            st.error(f"Error reprocessing document: {str(e)}")
            return False
    
    def render(self):
        """Render the document manager component"""
        st.header("Document Management")
        
        # Upload section
        st.subheader("Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload PDF documents", 
            type=["pdf"],
            help="Upload PDF documents to analyze"
        )
        
        if uploaded_file is not None:
            if st.button("Upload & Process", type="primary"):
                self._upload_document(uploaded_file)
        
        # Document list section
        st.subheader("Your Documents")
        documents = self._load_documents()
        
        if not documents:
            st.info("No documents found. Upload documents to begin.")
            return
        
        # Create a DataFrame for display
        df = pd.DataFrame(documents)
        display_cols = [
            "id", "original_filename", "file_size_formatted", 
            "status", "page_count", "created_at"
        ]
        rename_cols = {
            "id": "ID",
            "original_filename": "Filename",
            "file_size_formatted": "Size",
            "status": "Status",
            "page_count": "Pages",
            "created_at": "Uploaded"
        }
        
        # Only display columns that exist
        valid_cols = [col for col in display_cols if col in df.columns]
        if valid_cols:
            df_display = df[valid_cols].rename(columns={k: v for k, v in rename_cols.items() if k in valid_cols})
            st.dataframe(df_display, hide_index=True)
        
            # Actions for each document
            st.subheader("Document Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                selected_doc_id = st.selectbox(
                    "Select document",
                    options=documents,
                    format_func=lambda x: f"{x['id']} - {x['original_filename']}"
                )
            
            with col2:
                if st.button("Reprocess Document"):
                    if selected_doc_id:
                        self._reprocess_document(selected_doc_id["id"])
        else:
            st.error("Invalid document data structure")