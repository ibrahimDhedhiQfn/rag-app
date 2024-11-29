from flask import Flask, request, jsonify
from retrieve import retrieve
from generate import generate_response
import re

app = Flask(__name__)

# Function to clean any unwanted escape sequences (like terminal formatting)
def clean_output(output: str) -> str:
    # Removes ANSI escape codes (cursor and formatting control codes)
    return re.sub(r'\x1b[^m]*m', '', output)

@app.route('/chat', methods=['POST'])
def chat():
    # Get user query
    query = request.json['query']
    
    # Retrieve relevant data
    retrieved_data = retrieve(query)

    # Generate a response
    
    # Clean the response to remove unwanted escape characters
    cleaned_response = clean_output(response)
    
    # Return cleaned response
    return jsonify({'response': cleaned_response})

if __name__ == "__main__":
    app.run(debug=True)
