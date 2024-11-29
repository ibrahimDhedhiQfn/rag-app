import subprocess
import shlex

# Function to query Ollama (Llama 2)
def call_llama2(query):
    try:
        # Log the query being passed to Llama 2
        print(f"Query sent to Llama 2: {query}")
        
        # Escape the query string to avoid shell interpretation issues
        escaped_query = shlex.quote(query)

        # Run the Ollama command to get a response
        result = subprocess.run(
            ['ollama', 'run', 'llama2-uncensored', escaped_query],  # Add '--text' to pass query as text
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'  # Explicitly set UTF-8 encoding
        )
        
        # Check if there's any error in the stderr
        if result.returncode != 0:
            error_message = f"Error occurred: {result.stderr.strip() if result.stderr else 'Unknown error'}"
            print(error_message)
            return error_message
        
        # Log the output and return the response from Llama 2
        cleaned_output = result.stdout.strip()

        # Optionally limit the output size if it's too long
        max_output_length = 1000
        if len(cleaned_output) > max_output_length:
            cleaned_output = cleaned_output[:max_output_length] + '...'

        print(f"Response from Llama 2: {cleaned_output}")
        return cleaned_output  # Return the clean response
    except Exception as e:
        # Handle any exception and return the error
        print(f"Exception occurred: {e}")
        return str(e)
