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

    # Stream response from Llama 2
    for chunk in call_llama2(prompt):
        yield chunk
