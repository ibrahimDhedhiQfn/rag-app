import faiss
from sentence_transformers import SentenceTransformer
import json

# Load resources
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('./datasets/index.faiss')
with open('./datasets/data.json', 'r') as f:
    data = json.load(f)

def retrieve(query, top_k=10, threshold=1.2):
    """
    Retrieves the most relevant entries from the dataset.
    Logs similar queries found and whether they are sent to the model or skipped.
    """
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, top_k)

    print(f"Query: {query}")
    print(f"Distances: {D}")
    print(f"Indices: {I}")
    
    results = []
    for dist, idx in zip(D[0], I[0]):
        similar_query = data[idx]  # Get the actual similar query from the dataset
        print(f"Found similar query: {similar_query} (Distance: {dist})")
        
        if dist < threshold:
            print(f"  -> Sent to model (Within threshold)")
            results.append(similar_query)
        else:
            print(f"  -> Skipped (Distance {dist} exceeds threshold)")
    
    # Debug output to ensure some results are found
    if not results:
        print("No results found within the threshold.")
    
    return results
