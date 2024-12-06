from flask import Flask, request, jsonify, Response
import json
from retrieve import retrieve
from generate import generate_response
import re
import os  # Import os for clearing the terminal
from sentence_transformers import SentenceTransformer
import faiss
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Paths to embedding files
INDEX_PATH = './datasets/index.faiss'
DATA_PATH = './datasets/data.json'

# Function to clean any unwanted escape sequences (like terminal formatting)
def clean_output(output: str) -> str:
    # Removes ANSI escape codes (cursor and formatting control codes)
    return re.sub(r'\x1b[^m]*m', ' ', output)

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  # 'cls' for Windows, 'clear' for Unix-based systems
    
def save_to_json(query, response, file_path='./datasets/data.json'):
    """
    Save query-response pair to a JSON file, appending to the file if it exists.
    
    Parameters:
        query (str): The user query.
        response (str): The generated response.
        file_path (str): The path of the JSON file. Defaults to 'data.json'.
    """
    # Data to store in JSON
    data = {
        "question": query,
        "answer": response
    }

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Check if the file already exists
    if os.path.exists(file_path):
        # Read the existing data
        with open(file_path, 'r') as f:
            old_data = json.load(f)
    else:
        # If the file doesn't exist, start with an empty list
        old_data = []
    
    # Append the new data to the old data
    old_data.append(data)
    
    # Save the updated data to the file
    with open(file_path, 'w') as f:
        json.dump(old_data, f, indent=4)


# Function to update FAISS index and metadata
def update_embeddings(new_data):
    try:
        # Load existing FAISS index and metadata
        if os.path.exists(INDEX_PATH) and os.path.exists(DATA_PATH):
            # Load existing FAISS index
            index = faiss.read_index(INDEX_PATH)

            # Load existing metadata
            with open(DATA_PATH, 'r') as f:
                data = json.load(f)
        else:
            # Create a new FAISS index if it doesn't exist
            index = None
            data = []

        # Create embeddings for the new data
        texts = [f"Question: {item['question']} Answer: {item['answer']}" for item in new_data]
        new_embeddings = model.encode(texts)

        # If index does not exist, create a new one
        if index is None:
            index = faiss.IndexFlatL2(new_embeddings.shape[1])  # L2 similarity

        # Add new embeddings to the index
        index.add(new_embeddings)

        # Append new data to the metadata
        data.extend(new_data)

        # Save updated FAISS index
        faiss.write_index(index, INDEX_PATH)

        # Save updated metadata
        with open(DATA_PATH, 'w') as f:
            json.dump(data, f)

        print("Embeddings updated successfully!")
        return {"status": "success", "message": "Embeddings updated."}
    except Exception as e:
        print(f"Error in updating embeddings: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/chat', methods=['POST'])
def chat():
    # Clear the terminal for a fresh view
    clear_screen()
    
    # Log the start of a new query processing
    print("Processing new query...")
    
    # Get user query
    query = request.json['query']
    
    # Retrieve relevant data
    retrieved_data = retrieve(query)

    # Generate a response
    # response = generate_response(query, retrieved_data)
    
    # # Clean the response to remove unwanted escape characters
    # cleaned_response = clean_output(response)
    
    # # Return cleaned response
    # return jsonify({'response': cleaned_response})

    def generate_stream():
        response_chunks = []  # To accumulate the chunks of the response
        try:
            for word in generate_response(query, retrieved_data):
                cleaned_word = clean_output(word)
                response_chunks.append(cleaned_word)  # Append the word to the list
                
                # Log each chunk to the terminal (optional)
                print(f"Streaming chunk: {cleaned_word}")
                
                # Yield each cleaned word (for streaming purposes)
                yield cleaned_word  # SSE format for streaming
        except Exception as e:
            yield f"Error occurred during response generation: {str(e)}"
            
        # After generating the full response, save and update embeddings
        full_response = " ".join(response_chunks)
        print(f"Full Response: {full_response}")
        save_to_json(query, full_response)
         # Update embeddings with the new query and response
        new_data = [{"question": query, "answer": full_response}]
        update_embeddings(new_data)  # Update the FAISS index and metadata
    # Return the response as a streaming Response
    return Response(generate_stream(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
