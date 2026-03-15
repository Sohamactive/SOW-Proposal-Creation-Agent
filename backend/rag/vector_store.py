from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

import time
from typing import List, Dict
from backend.config import settings


class VectorStore:

    def __init__(self):

        self.client = None
        self.collection_name = settings.QDRANT_COLLECTION

    def _get_client(self):

        if self.client is None:
            self.client = QdrantClient(url=settings.QDRANT_URL)

        return self.client

    def _create_collection(self):

        client = self._get_client()

        for attempt in range(5):
            try:
                collections = client.get_collections().collections
                names = [c.name for c in collections]

                if self.collection_name not in names:
                    client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=settings.EMBEDDING_DIMENSION,
                            distance=Distance.COSINE
                        )
                    )

                return
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2)

    def add_documents(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadata: List[Dict]
    ):

        self._create_collection()

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

        self._get_client().upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

    def search(self, query_embedding: List[float], top_k: int = None): #type: ignore

        self._create_collection()

        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        results = self._get_client().query_points(
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

        self._create_collection()

        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K

        results = self._get_client().query_points(
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