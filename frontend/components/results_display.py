import streamlit as st

class ResultsDisplay:
    def __init__(self, results):
        self.results = results
        
    def _display_themes(self, themes):
        """Display identified themes"""
        if not themes:
            st.info("No common themes identified")
            return
            
        st.subheader("📊 Key Themes")
        
        for i, theme in enumerate(themes, 1):
            with st.expander(f"Theme {i}: {theme.get('theme', 'Unnamed Theme')}"):
                st.write(theme.get('description', 'No description available'))
                
                st.write("**Documents:**")
                doc_list = theme.get('documents', [])
                if doc_list:
                    for doc in doc_list:
                        st.markdown(f"- {doc}")
                else:
                    st.write("No document references")
    
    def _display_document_responses(self, doc_responses):
        """Display responses for each document"""
        if not doc_responses:
            st.info("No document responses available")
            return
            
        st.subheader("📄 Document Analysis")
        
        for doc_id, response_data in doc_responses.items():
            with st.expander(f"Document: {doc_id}"):
                st.markdown(response_data.get('response', 'No response available'))
                
                citations = response_data.get('citations', [])
                if citations:
                    st.write("**Citations:**")
                    citation_text = []
                    for citation in citations:
                        page = citation.get('page', 'N/A')
                        para = citation.get('paragraph', 'N/A')
                        citation_text.append(f"Page {page}, Paragraph {para}")
                    
                    st.write(", ".join(citation_text))
    
    def render(self):
        """Render the results display component"""
        st.header("Research Results")
        
        # Display themes
        themes = self.results.get('themes', [])
        self._display_themes(themes)
        
        # Display document responses
        doc_responses = self.results.get('document_responses', {})
        self._display_document_responses(doc_responses)
        
        # Export options
        st.subheader("Export Options")
        if st.button("Export Results (CSV)"):
            # This would be implemented with additional code to format and download results
            st.info("Export functionality not implemented yet")