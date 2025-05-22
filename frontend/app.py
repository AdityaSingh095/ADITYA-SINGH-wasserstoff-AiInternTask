import streamlit as st
from components.document_manager import DocumentManager
from components.query_interface import QueryInterface
from components.results_display import ResultsDisplay

def main():
    st.set_page_config(
        page_title="Document Research & Theme Identification Chatbot",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Document Research & Theme Identification Chatbot")
    
    # Initialize session state
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Documents"
    if "query_results" not in st.session_state:
        st.session_state.query_results = None
    if "selected_docs" not in st.session_state:
        st.session_state.selected_docs = []
    
    # Create tabs
    tab1, tab2 = st.tabs(["Documents", "Research"])
    
    # Documents Tab
    with tab1:
        st.session_state.active_tab = "Documents"
        doc_manager = DocumentManager()
        doc_manager.render()
    
    # Research Tab
    with tab2:
        st.session_state.active_tab = "Research"
        col1, col2 = st.columns([1, 2])
        
        with col1:
            query_interface = QueryInterface()
            query_interface.render()
        
        with col2:
            if st.session_state.query_results:
                results_display = ResultsDisplay(st.session_state.query_results)
                results_display.render()
            else:
                st.info("Ask a question to see results")

if __name__ == "__main__":
    main()