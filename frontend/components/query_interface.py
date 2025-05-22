import streamlit as st
from utils.api_client import APIClient

class QueryInterface:
    def __init__(self):
        self.api_client = APIClient()
    
    def _load_documents(self):
        """Load documents for selection"""
        #st.write("Processed documents:", processed_docs)
        try:
            response = self.api_client.get_documents()
            documents = response.get("documents", [])
            
            # Filter to only processed documents
            processed_docs = [doc for doc in documents if doc.get("is_processed", False)]
            
            return processed_docs
        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")
            return []
    
    def _handle_query(self, question, selected_doc_ids):
        """Send query to API and update results"""
        if not question.strip():
            st.warning("Please enter a question")
            return None
        
        try:
            results = self.api_client.query_documents(question, selected_doc_ids)
            return results
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")
            return None
    
    def render(self):
        """Render the query interface component"""
        st.header("Research Assistant")
        
        # Document selection
        documents = self._load_documents()
        
        if not documents:
            st.warning("No processed documents available. Upload and process documents first.")
            return
        
        # Multi-select for documents
        doc_options = {doc["id"]: f"{doc['original_filename']} ({doc['page_count']} pages)" 
                      for doc in documents if doc.get("page_count")}
        
        selected_docs = st.multiselect(
            "Select documents to research:",
            options=list(doc_options.keys()),
            format_func=lambda x: doc_options.get(x, str(x)),
            default=None
        )
        
        st.session_state.selected_docs = selected_docs
        
        # Query input
        st.subheader("Ask a Question")
        question = st.text_area(
            "Enter your research question:",
            height=100,
            help="Ask a question about the selected documents"
        )
        
        # Submit button
        if st.button("Research", type="primary"):
            with st.spinner("Analyzing documents..."):
                results = self._handle_query(question, selected_docs)
                if results:
                    st.session_state.query_results = results
                    st.success("Analysis complete!")
                    
        # Example questions
        with st.expander("Example Questions"):
            examples = [
                "What are the key themes across these documents?",
                "Summarize the main points in these documents.",
                "What are the similarities and differences between these documents?",
                "What methodology is discussed in these documents?",
                "What are the limitations mentioned in the research?"
            ]
            
            for ex in examples:
                if st.button(ex, key=f"ex_{ex}"):
                    with st.spinner("Analyzing documents..."):
                        results = self._handle_query(ex, selected_docs)
                        if results:
                            st.session_state.query_results = results
                            st.success("Analysis complete!")