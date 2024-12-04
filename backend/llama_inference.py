import subprocess
import shlex
import re  # For regex-based cleaning

# Function to query Ollama (Llama 2)
def call_llama2(query, conversation_history=""):
    try:
        # Construct the formatted input
        formatted_input = f"""<<SYS>>
You are a conversational and persuasive sales assistant. Your primary goal is to sell products effectively while maintaining a friendly and approachable tone. Speak like a natural human, with casual and engaging language, as if you're having a conversation with a friend.

Key characteristics of your responses:
1. Always prioritize understanding the customer's needs and offer tailored suggestions.
2. Keep your tone warm, helpful, and slightly enthusiastic to encourage interest in the product.
3. Provide clear and concise information, avoiding technical jargon unless necessary.
4. When discussing products, highlight their unique benefits and how they solve the customer's problems.
5. Always keep the conversation focused on the product or its related features, avoiding irrelevant topics.

Example response style:
- Customer: "What can you tell me about this product?"
- Assistant: "Sure thing! This product is perfect if you're looking for [specific feature/benefit]. It's super easy to use, and customers love it for [another benefit]. Would you like me to tell you more about how it works?"

Remember, your purpose is to guide the customer toward a purchase while ensuring they feel valued and understood.
<</SYS>>

{conversation_history}

[INST]
User: {query}
[/INST]
Assistant:"""
        
        # Log the constructed input
        print(f"Formatted input sent to Llama 2:\n{formatted_input}")
        
        # Run the Ollama command
        result = subprocess.Popen(
            ['ollama', 'run', 'llama2-uncensored', formatted_input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Stream the output
        try:
            full_response = ""  # To accumulate the cleaned response
            for line in iter(result.stdout.readline, ''):  # Read line by line
                if line:  # Check if the line is not empty
                    # Clean the line to remove unwanted system tokens and formatting
                    line = clean_output(line)
                    full_response += line + " "  # Accumulate the cleaned response

            # Yield the final cleaned response once the process is complete
            yield full_response.strip()

        finally:
            # Ensure the process is finished and errors are handled
            result.stdout.close()
            result.stderr.close()
            result.wait()  # Wait for the process to finish

            # Check for any errors from stderr
            if result.returncode != 0:
                error_message = f"Error occurred: {result.stderr.read().strip() if result.stderr else 'Unknown error'}"
                yield error_message

    except Exception as e:
        # Handle exceptions
        print(f"Exception occurred: {e}")
        yield str(e)

# Function to clean the response
def clean_output(output: str) -> str:
    # Remove ANSI escape codes (cursor and formatting control codes)
    output = re.sub(r'\x1b[^m]*m', ' ', output)

    # Remove system tokens like [INST], <<SYS>>, and other unwanted parts
    output = re.sub(r'\[INST\].*?Answer:|<<SYS>>.*?<</SYS>>', '', output)

    # Remove any extra spaces that may have been introduced
    output = re.sub(r'\s+', ' ', output).strip()

    return output
