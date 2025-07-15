from google.generativeai import GenerativeModel, configure
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
import datetime
client = MongoClient("mongodb+srv://sai11112004:test1234@cluster0.cea9kib.mongodb.net/")
db = client["bank_statement_db"]
chunks_collection = db["pdf_chunks"]

def setup_gemini():
    try:
        configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = GenerativeModel('gemini-2.5-flash-preview-05-20')
        return model
    except Exception as e:
        print(f"Error setting up Gemini: {str(e)}")
        return None

def get_relevant_chunks(question):
    try:
        chunks = list(chunks_collection.find({}, {"chunk_text": 1, "_id": 0}))
        return [chunk["chunk_text"] for chunk in chunks]
    except Exception as e:
        print(f"Error retrieving chunks: {str(e)}")
        return []

def chat_with_pdf():
    gemini_model = setup_gemini()
    if not gemini_model:
        return
    
    chat = gemini_model.start_chat(history=[])
    print("\nWelcome to PDF Chat with Gemini! Type '*' to exit.")
    
    while True:
        user_input = input("\nYour question: ").strip()
        
        if user_input.lower() == '*':
            print("Thanks for interacting with the PDF chat! Goodbye!")
            break
            
        if not user_input:
            continue
            
        try:
            
            relevant_chunks = get_relevant_chunks(user_input)
    
            context = "\n".join(relevant_chunks)
        
            prompt = f"""Based on the following context from a PDF document, please answer the question.
            
            Context:
            {context}
            
            Question: {user_input}
            
            Please provide a clear and concise answer based on the context provided."""
            
            response = chat.send_message(prompt)
            
            print("\nAnswer:", response.text)
            
        except Exception as e:
            print(f"Error getting response: {str(e)}")

if __name__ == "__main__":
    chat_with_pdf()
