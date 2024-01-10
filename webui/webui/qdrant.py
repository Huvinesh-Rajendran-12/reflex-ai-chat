from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class Qdrant:
    def __init__(self) -> None:
        self.client = QdrantClient(location="localhost", port=6333)
        self.embedding_model = SentenceTransformer("/home/huvi/all-MiniLM-L6-v2/")

    def query(self, question: str):
        query_embedding = self.embedding_model.encode(question)
        search_result = self.client.search(
             collection_name="pdf", query_vector=query_embedding, with_payload=True, limit=2, score_threshold=0.85
        )
        text: str = ""
        for result in search_result:
            text += result.payload["text"]
        return text
 
