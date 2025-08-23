from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import hashlib
from environment import load_environment
from chromadb_setup import initialize_chromadb
from document_processing import load_documents_from_directory, preprocess_documents
from embedding_generation import generate_embeddings
from db_operations import upsert_documents_into_db, get_document_ids_in_collection
from query_and_response import query_documents, generate_response
from openai import OpenAI

# Load environment variables
openai_key = load_environment()

# Initialize OpenAI Client
client = OpenAI(api_key=openai_key)

# Initialize ChromaDB
collection = initialize_chromadb(openai_key)

# Cache directory for document hashes
cache_dir = "./cache"
os.makedirs(cache_dir, exist_ok=True)
document_hash_file = os.path.join(cache_dir, "document_hashes.json")

# Function to check if documents need updating
def check_documents_need_updating(documents):
    # Calculate hash for each document
    current_hashes = {}
    for doc in documents:
        doc_hash = hashlib.md5(doc["text"].encode()).hexdigest()
        current_hashes[doc["id"]] = doc_hash
    
    # Load previous hashes if they exist
    previous_hashes = {}
    if os.path.exists(document_hash_file):
        with open(document_hash_file, 'r') as f:
            previous_hashes = json.load(f)
    
    # Compare hashes
    documents_to_process = []
    for doc in documents:
        if doc["id"] not in previous_hashes or previous_hashes[doc["id"]] != current_hashes[doc["id"]]:
            documents_to_process.append(doc)
    
    # Save current hashes
    with open(document_hash_file, 'w') as f:
        json.dump(current_hashes, f)
    
    return documents_to_process

# Load documents
directory_path = "./data"
documents = load_documents_from_directory(directory_path)

# Check if documents need updating
documents_to_process = check_documents_need_updating(documents)

if documents_to_process:
    print(f"Processing {len(documents_to_process)} new or modified documents")
    # Process only new or modified documents
    chunked_documents = preprocess_documents(documents_to_process)
    chunked_documents = generate_embeddings(client, chunked_documents)
    upsert_documents_into_db(collection, chunked_documents)
else:
    print("No new documents to process. Using existing embeddings.")

# Flask application setup
app = Flask(__name__, template_folder="templates", static_folder="static")


# Route to serve the chatbot UI
@app.route("/")
def index():
    """
    Serve the main chatbot page (index.html).
    """
    return render_template("index.html")


# Route to handle user messages
@app.route("/chat", methods=["POST"])
def chat():
    """
    Process user input, query the document collection, and generate a response.
    """
    user_message = request.json.get("message")  # Extract message from frontend
    try:
        # Query the database for relevant documents
        relevant_chunks = query_documents(collection, [user_message])
        
        # Check if we have any relevant chunks
        if not relevant_chunks:
            return jsonify({
                "message": "I don't have information about this in my knowledge base.",
                "sources": [],
                "relevance_score": 0
            })
            
        # Generate a response using the OpenAI API
        response_data = generate_response(client, user_message, relevant_chunks)
        
        # Debug the response data
        print(f"Response data structure: {list(response_data.keys())}")
        print(f"Overall relevance from response: {response_data.get('overall_relevance', 'Not found')}")
        
        # Format sources to include text snippets
        sources = response_data["sources"]
        print(f"Number of sources: {len(sources)}")
        if sources and len(sources) > 0:
            print(f"First source structure: {list(sources[0].keys()) if isinstance(sources[0], dict) else 'Not a dict'}")
        
        # Return the answer, sources with relevance scores and text snippets, and overall relevance
        return jsonify({
            "message": response_data["answer"],
            "sources": response_data["sources"],
            "relevance_score": response_data["overall_relevance"]
        })
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "message": f"An error occurred while processing your request.",
            "sources": [],
            "relevance_score": 0
        }), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
