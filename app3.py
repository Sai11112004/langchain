import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from pymongo import MongoClient
import os
import datetime
import traceback

def connect_to_mongodb():
    """Establish connection to MongoDB"""
    try:
        client = MongoClient("mongodb+srv://sai11112004:test1234@cluster0.cea9kib.mongodb.net/")
        db = client["bank_statement_db"]
        chunks_collection = db["pdf_chunks"]
        return chunks_collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

def process_pdf(pdf_path, chunks_collection):
    """Process PDF, split into chunks using LangChain, and store in MongoDB"""
    try:
        
        if not os.path.exists(pdf_path):
            print(f"Error: File not found at {pdf_path}")
            return False

        if not os.access(pdf_path, os.R_OK):
            print(f"Error: File is not readable at {pdf_path}")
            return False

        print(f"Opening PDF file: {pdf_path}")
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Total pages in PDF: {len(pdf.pages)}")
            
            if len(pdf.pages) == 0:
                print("Error: PDF file has no pages")
                return False

            for i, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text() or ""
                    text += page_text
                    print(f"Processed page {i}")
                except Exception as page_error:
                    print(f"Error processing page {i}: {str(page_error)}")
                    continue

        if not text.strip():
            print("Warning: No text was extracted from the PDF")
            return False

        print(f"Total text extracted: {len(text)} characters")
        print("Splitting text into chunks...")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_text(text)
        print(f"Created {len(chunks)} chunks")

        for i, chunk in enumerate(chunks, 1):
            try:
                chunks_collection.insert_one({
                    "pdf_name": os.path.basename(pdf_path),
                    "chunk_text": chunk,
                    "created_at": datetime.datetime.now(),
                    "chunk_number": i
                })
                print(f"Stored chunk {i}/{len(chunks)}")
            except Exception as db_error:
                print(f"Error storing chunk {i}: {str(db_error)}")
                continue

        print(f"\nSuccessfully processed {pdf_path}")
        print(f"Total chunks created and stored: {len(chunks)}")
        return True
    
    except pdfplumber.pdfminer.pdfparser.PDFSyntaxError:
        print("Error: Invalid PDF file format")
        return False
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    pdf_path = "PO-3.pdf"
    chunks_collection = connect_to_mongodb()
    if chunks_collection is None:
        print("Failed to connect to MongoDB. Exiting...")
        return
    if os.path.exists(pdf_path):
        success = process_pdf(pdf_path, chunks_collection)
        if success:
            print("PDF processing completed successfully!")
        else:
            print("PDF processing failed!")
    else:
        print(f"Error: File not found at {pdf_path}")
if __name__ == "__main__":
    main()
  