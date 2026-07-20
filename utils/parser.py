import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text content from a PDF file using PyMuPDF (fitz) and cleans it.
    
    Args:
        pdf_path (str): The absolute path to the PDF file.
        
    Returns:
        str: The extracted and cleaned text content.
    """
    text = ""
    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        
        # Iterate through pages and extract text
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        
        # Close document
        doc.close()
        
        # Clean the extracted text
        text = clean_text(text)
        
    except Exception as e:
        print(f"Error during PDF text extraction: {e}")
        raise ValueError(f"Failed to parse PDF file: {str(e)}")
        
    return text

def clean_text(text: str) -> str:
    """
    Cleans raw text by removing excessive whitespace, non-printable characters,
    and normalizing spaces.
    
    Args:
        text (str): Raw string.
        
    Returns:
        str: Cleaned string.
    """
    if not text:
        return ""
    
    # Replace non-breaking spaces and tabs with normal spaces
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    
    # Remove control characters and non-printable characters (except newline)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    
    # Collapse multiple spaces into a single space
    text = re.sub(r' +', ' ', text)
    
    # Normalize multiple newlines into max double newlines to preserve structure
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # Trim leading and trailing whitespace per line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()
