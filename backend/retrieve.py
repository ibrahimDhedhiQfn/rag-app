import faiss
from sentence_transformers import SentenceTransformer
import json

# Load resources
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.read_index('./datasets/index.faiss')
with open('./datasets/data.json', 'r') as f:
    data = json.load(f)

def retrieve(query, top_k=3, threshold=0.7):
    """
    Retrieves the most relevant entries from the dataset.
    """
    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, top_k)

    print(f"Query: {query}")
    print(f"Distances: {D}")
    print(f"Indices: {I}")
    
    results = []
    for dist, idx in zip(D[0], I[0]):
        if dist < threshold:
            results.append(data[idx])
        else:
            print(f"Skipping idx {idx} with distance {dist} > threshold")

    # Debug output to ensure some results are found
    if not results:
        print("No results found within the threshold.")
    return results
