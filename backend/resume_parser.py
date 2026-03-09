import os
import PyPDF2
import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Need to download the model if not found
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def extract_email(text):
    """Extracts the first email found in the text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extracts a phone number from the text."""
    phone_pattern = r'\(?\b[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_name(text):
    """Tries to extract a name using spaCy NER. Assumes name is often at the top."""
    # Process only the first few lines to find a name
    first_few_lines = "\\n".join(text.split('\\n')[:10])
    doc = nlp(first_few_lines)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def parse_resume(pdf_path):
    """Main function to parse the resume file."""
    text = extract_text_from_pdf(pdf_path)
    
    # Be more forgiving; even if text is empty or corrupted,
    # we don't return a 500 error. Let's just return what we have.
    if not text:
        text = "Could not extract text from this PDF. It may be an image-only PDF."
        
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text)
    
    return {
        "text": text,
        "email": email,
        "phone": phone,
        "name": name
    }
