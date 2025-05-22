# Wassteroft Intern Task

This repository contains a full-stack application for document research and querying using modern AI and vector database technologies. The project is organized into a `backend` (FastAPI, ChromaDB, LangChain) and a `frontend` (Streamlit) for interactive document management and semantic search.

## Features

- **Document Upload & Management**: Upload and manage documents (PDFs) via a user-friendly interface.
- **Text Extraction & Embedding**: Extracts text from documents and generates embeddings using state-of-the-art models.
- **Semantic Search**: Query documents using natural language and retrieve relevant passages using vector similarity.
- **API Backend**: FastAPI-based backend for handling uploads, queries, and database operations.
- **Frontend Interface**: Streamlit app for easy interaction, querying, and result visualization.

## Project Structure

```
wassteroft intern task/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   └── services/
│   └── data/
│       ├── embeddings/
│       └── uploads/
│
├── frontend/
│   ├── app.py
│   ├── components/
│   └── utils/
│
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for OCR features)
- [Poppler](https://poppler.freedesktop.org/) (for PDF to image conversion)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/wassteroft-intern-task.git
   cd wassteroft-intern-task
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Backend (FastAPI)

```bash
cd backend/app
uvicorn main:app --reload
```

#### Frontend (Streamlit)

```bash
cd ../../frontend
streamlit run app.py
```

## Usage

- Access the Streamlit UI in your browser (default: `http://localhost:8501`).
- Upload documents, perform semantic queries, and view results.

## Technologies Used

- FastAPI
- Streamlit
- ChromaDB
- LangChain
- Google Generative AI
- HuggingFace Hub
- pdfplumber, pdf2image, pytesseract
- OpenCV, NumPy, Pandas

## License

This project is for educational and demonstration purposes.

---