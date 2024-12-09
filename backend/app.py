from flask import Flask, request, jsonify, Response
import json
import logging
from retrieve import retrieve
from generate import generate_response
import re
import os
from sentence_transformers import SentenceTransformer
import faiss
from flask_cors import CORS

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Paths to embedding files
INDEX_PATH = './datasets/index.faiss'
DATA_PATH = './datasets/data.json'

# Function to clean any unwanted escape sequences (like terminal formatting)
def clean_output(output: str) -> str:
    return re.sub(r'\x1b[^m]*m', ' ', output)

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to save query-response pairs to a JSON file
def save_to_json(query, response, file_path='./datasets/data.json'):
    data = {"question": query, "answer": response}
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            old_data = json.load(f)
    else:
        old_data = []
    old_data.append(data)
    with open(file_path, 'w') as f:
        json.dump(old_data, f, indent=4)

# Function to update FAISS index and metadata
def update_embeddings(new_data):
    try:
        if os.path.exists(INDEX_PATH) and os.path.exists(DATA_PATH):
            index = faiss.read_index(INDEX_PATH)
            with open(DATA_PATH, 'r') as f:
                data = json.load(f)
        else:
            index = None
            data = []

        texts = [f"Question: {item['question']} Answer: {item['answer']}" for item in new_data]
        new_embeddings = model.encode(texts)

        if index is None:
            index = faiss.IndexFlatL2(new_embeddings.shape[1])

        index.add(new_embeddings)
        data.extend(new_data)
        faiss.write_index(index, INDEX_PATH)
        with open(DATA_PATH, 'w') as f:
            json.dump(data, f)
        logging.info("Embeddings updated successfully!")
        return {"status": "success", "message": "Embeddings updated."}
    except Exception as e:
        logging.error(f"Error in updating embeddings: {e}")
        return {"status": "error", "message": str(e)}

# Home route
@app.route('/')
def home():
    return "Welcome to the Flask Application! Use the /chat endpoint to interact."

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    clear_screen()
    logging.info("Processing new query...")
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({'error': 'Query is required.'}), 400

        retrieved_data = retrieve(query)

        def generate_stream():
            response_chunks = []
            try:
                for word in generate_response(query, retrieved_data):
                    cleaned_word = clean_output(word)
                    response_chunks.append(cleaned_word)
                    logging.debug(f"Streaming chunk: {cleaned_word}")
                    yield cleaned_word
            except Exception as e:
                yield f"Error occurred during response generation: {str(e)}"

            full_response = " ".join(response_chunks)
            logging.info(f"Full Response: {full_response}")
            save_to_json(query, full_response)
            new_data = [{"question": query, "answer": full_response}]
            update_embeddings(new_data)

        return Response(generate_stream(), content_type='text/event-stream')

    except Exception as e:
        logging.error(f"Error in /chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)