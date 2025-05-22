import requests
import os
import json
from typing import List, Dict, Optional, Any, Union

# Default API URL - can be overridden with environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")

class APIClient:
    """Client for interacting with the backend API"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
    
    def _handle_response(self, response):
        """Handle API response and errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_msg = error_data["detail"]
            except:
                pass
            raise Exception(f"API Error: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request Error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Error parsing API response")
    
    def get_documents(self) -> Dict:
        """Get all documents"""
        url = f"{self.base_url}/documents"
        response = requests.get(url)
        return self._handle_response(response)
    
    def get_document(self, doc_id: int) -> Dict:
        """Get a specific document by ID"""
        url = f"{self.base_url}/documents/{doc_id}"
        response = requests.get(url)
        return self._handle_response(response)
    
    def upload_document(self, file) -> Dict:
        """Upload a document file"""
        url = f"{self.base_url}/documents/upload"
        files = {"file": (file.name, file, "application/pdf")}
        response = requests.post(url, files=files)
        return self._handle_response(response)
    
    def query_documents(self, question: str, document_ids: Optional[List[int]] = None) -> Dict:
        """Query documents with a question"""
        url = f"{self.base_url}/query"
        payload = {"question": question}
        if document_ids:
            payload["document_ids"] = document_ids
        
        response = requests.post(url, json=payload)
        return self._handle_response(response)
    
    def reprocess_document(self, doc_id: int) -> Dict:
        """Reprocess a document"""
        url = f"{self.base_url}/documents/{doc_id}/process"
        response = requests.post(url)
        return self._handle_response(response)