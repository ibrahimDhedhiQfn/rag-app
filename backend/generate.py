from llama_inference import call_llama2  # Import your function

def generate_response(query, retrieved_data):
    """
    Generates a response based on the retrieved data.
    """
    if retrieved_data:
        context = " ".join([f"Answer: {item['answer']}" for item in retrieved_data])
        prompt = f"Using the following information: {context}, answer this question: {query}"
    else:
        prompt = query  # No relevant data, use query only

    # Use Llama 2 to generate the response
    response = call_llama2(prompt)  # Query Llama 2 using the function
    return response
