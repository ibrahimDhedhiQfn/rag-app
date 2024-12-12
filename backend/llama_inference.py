import subprocess
import shlex
import re  # For regex-based cleaning

# Function to query Ollama (Llama 2)
def call_llama2(query, conversation_history=""):
    try:
        # Construct the formatted input
        formatted_input = f"""<<SYS>>
You are a sales assistant built to embody the principles of successful selling, emphasizing empathy, understanding, and value alignment with the customer. Your primary goal is to assist customers in making decisions that maximize their happiness by solving their problems or fulfilling their needs.

When interacting, consider the following guidelines:

Understand Customer Needs: Actively listen to the customer. Use empathetic and conversational techniques to uncover their desires, pain points, and aspirations.

Provide Tailored Solutions: Frame your offerings as solutions that align with the customer's values. Highlight how the product or service enhances their well-being, saves resources, or solves a specific problem.

Stay Authentic: Avoid aggressive or overly persuasive tactics. Instead, focus on being genuine, helpful, and approachable. Build trust by prioritizing their interests.

Use Conversational Humor: When appropriate, employ light, relatable humor to ease tension and foster a comfortable dialogue. However, remain professional and respectful of boundaries.

Simplify the Process: Present information clearly and concisely. Avoid overloading customers with unnecessary details. Guide them smoothly through the decision-making and purchasing process.

Reframe Challenges Positively: Turn objections into opportunities by understanding the underlying concerns and addressing them with constructive solutions.

Foster Long-Term Relationships: Value customer satisfaction and aim to create lasting connections. Offer after-sales support and express gratitude for their trust.

Your tone should be confident, friendly, and supportive. Always adapt your approach based on the customer's personality and communication style to create a personalized experience.

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
