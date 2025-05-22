# backend/app/services/text_extraction.py
import os
from typing import List, Dict, Optional

import pdf2image
import pytesseract
import pdfplumber
import numpy as np
import cv2
from pdf2image import convert_from_path

from app.core import config

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extracts text from a PDF. For each page:
      - If it has searchable text, use pdfplumber.
      - Otherwise, render to image and OCR with pytesseract after preprocessing.

    Returns a list of dicts:
      [{ "page": 1, "text": "..." }, ...]
    """
    pages = []
    doc_id = os.path.basename(pdf_path)
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            
            # If little to no text was extracted, the page might be a scanned image
            if len(text.strip()) < 20:
                # Convert page to high-quality image
                image = convert_from_path(
                    pdf_path, 
                    dpi=config.OCR_DPI, 
                    first_page=i, 
                    last_page=i
                )[0]

                # Convert to OpenCV format
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

                # Preprocess image: binarization and denoising
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                thresh = cv2.medianBlur(thresh, 3)

                # OCR with pytesseract
                text = pytesseract.image_to_string(thresh, lang="eng")

            pages.append({
                "doc_id": doc_id,
                "page": i,
                "text": text
            })
    
    return pages

def extract_text_from_pdfs(pdf_paths: List[str]) -> List[Dict]:
    """
    Extracts text from multiple PDFs.
    
    Returns a list of dicts:
      [{ "doc_id": "file.pdf", "page": 1, "text": "..." }, ...]
    """
    all_pages = []
    for path in pdf_paths:
        pages = extract_text_from_pdf(path)
        all_pages.extend(pages)
    
    return all_pages