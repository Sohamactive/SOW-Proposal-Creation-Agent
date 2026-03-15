from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from typing import List, Dict
from backend.config import settings


class VectorStore:

    def __init__(self):

        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION

        self._create_collection()

    def _create_collection(self):

        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if self.collection_name not in names:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )

    def add_documents(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: List[Dict]
    ):

        points = []

        for idx, (embedding, text, meta) in enumerate(
            zip(embeddings, texts, metadata)
        ):

            points.append(
                PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={
                        "text": text,
                        **meta
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

    def search(self, query_embedding: List[float], top_k: int = None): #type: ignore

        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            with_payload=True,
            limit=top_k
        ).points

        return results

    def filtered_search(
        self,
        query_embedding: List[float],
        key: str,
        value: str,
        top_k: int = None #type: ignore
    ):

        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                ]
            ),
            with_payload=True,
            limit=top_k
        ).points

        return results