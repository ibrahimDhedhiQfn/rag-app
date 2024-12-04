from llama_inference import call_llama2  # Import your function
import re  # For regex-based cleaning

def generate_response(query, retrieved_data):
    """
    Generates a response based on the retrieved data.
    """
    if retrieved_data:
        # Construct context by joining relevant answers
        context = " ".join([f"Answer: {item['answer']}" for item in retrieved_data])
        prompt = f"Using the following information: {context}, answer this question: {query}"
    else:
        prompt = query  # No relevant data, use query only

    # Stream response from Llama 2
    full_response = ""  # To accumulate the full response

    # Generate chunks from Llama 2 response
    for chunk in call_llama2(prompt):
        full_response += chunk

    # Clean the full response before yielding
    cleaned_response = clean_output(full_response)

    # Yield the cleaned response
    yield cleaned_response

# Function to clean the response (same as before)
def clean_output(output: str) -> str:
    # Remove unwanted system tokens like [INST] or <<SYS>>
    output = re.sub(r'\[INST\].*?Answer:|<<SYS>>.*?<</SYS>>', '', output)

    # Remove any extra spaces that may have been introduced
    output = re.sub(r'\s+', ' ', output).strip()

    return output
