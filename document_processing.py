import os
import PyPDF2
import re
from docx import Document  # Import python-docx


def load_documents_from_directory(directory_path):
    """
    Load documents from a directory, supporting .txt, .pdf, and .docx files
    """
    print("==== Loading documents from directory ====")
    documents = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Process text files
        if filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    documents.append({
                        "id": filename,
                        "text": file.read(),
                        "source": filename
                    })
                print(f"Loaded text file: {filename}")
            except Exception as e:
                print(f"Error loading text file {filename}: {str(e)}")

        # Process PDF files
        elif filename.endswith(".pdf"):
            try:
                text = extract_text_from_pdf(file_path)
                if text.strip():  # Only add if text is not empty
                    documents.append({
                        "id": filename,
                        "text": text,
                        "source": filename
                    })
                    print(f"Loaded PDF file: {filename}")
                else:
                    print(f"Warning: PDF file {filename} appears to be empty or unreadable")
            except Exception as e:
                print(f"Error loading PDF file {filename}: {str(e)}")

        # Process .docx files
        elif filename.endswith(".docx"):
            try:
                text = extract_text_from_docx(file_path)
                if text.strip():  # Only add if text is not empty
                    documents.append({
                        "id": filename,
                        "text": text,
                        "source": filename
                    })
                    print(f"Loaded DOCX file: {filename}")
                else:
                    print(f"Warning: DOCX file {filename} appears to be empty or unreadable")
            except Exception as e:
                print(f"Error loading DOCX file {filename}: {str(e)}")

    print(f"Total documents loaded: {len(documents)}")
    return documents


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:  # Only add if text extraction succeeded
                    text += page_text + "\n\n"

        # Clean up text - remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return ""


def extract_text_from_docx(docx_path):
    """
    Extract text content from a DOCX file
    """
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        # Clean up text - remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {str(e)}")
        return ""


def split_text(text, chunk_size=1000, chunk_overlap=20):
    """
    Split text into overlapping chunks of specified size
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks


def preprocess_documents(documents, chunk_size=1000, chunk_overlap=20):
    """
    Preprocess documents by splitting them into chunks with overlap
    """
    chunked_documents = []
    for doc in documents:
        print(f"==== Splitting document {doc['id']} into chunks ====")
        chunks = split_text(doc["text"], chunk_size, chunk_overlap)

        for i, chunk in enumerate(chunks):
            # Skip empty chunks
            if not chunk.strip():
                continue

            chunked_documents.append({
                "id": f"{doc['id']}_chunk{i + 1}",
                "text": chunk,
                "source": doc["source"]
            })

    print(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")
    return chunked_documents
