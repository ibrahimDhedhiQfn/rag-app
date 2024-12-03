from flask import Flask, request, jsonify, Response
from retrieve import retrieve
from generate import generate_response
import re
import os  # Import os for clearing the terminal

app = Flask(__name__)

# Function to clean any unwanted escape sequences (like terminal formatting)
def clean_output(output: str) -> str:
    # Removes ANSI escape codes (cursor and formatting control codes)
    return re.sub(r'\x1b[^m]*m', '', output)

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  # 'cls' for Windows, 'clear' for Unix-based systems

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
        for word in generate_response(query, retrieved_data):
            cleaned_word = clean_output(word)
            yield cleaned_word  # SSE format for streaming

    # Return the response as a streaming Response
    return Response(generate_stream(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
