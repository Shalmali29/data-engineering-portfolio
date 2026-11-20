"""Optional Weaviate BYOV (bring-your-own-vectors) writer."""
import os
import weaviate
from weaviate.classes.config import Configure, DataType, Property


def connect():
    url = os.environ["WEAVIATE_URL"]
    api_key = os.environ["WEAVIATE_API_KEY"]
    return weaviate.connect_to_weaviate_cloud(
        cluster_url=url,
        auth_credentials=weaviate.auth.AuthApiKey(api_key),
    )


def ensure_collection(client, name: str | None = None):
    collection_name = name or os.getenv("WEAVIATE_COLLECTION", "SyntheticProperty")
    if not client.collections.exists(collection_name):
        client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vectorizer.none(),
            properties=[
                Property(name="property_id", data_type=DataType.TEXT),
                Property(name="text", data_type=DataType.TEXT),
                Property(name="city", data_type=DataType.TEXT),
                Property(name="property_type", data_type=DataType.TEXT),
            ],
        )
    return client.collections.get(collection_name)


def insert_documents(collection, documents: list[dict], vectors: list[list[float]]) -> int:
    if len(documents) != len(vectors):
        raise ValueError("Each document must have exactly one embedding vector")
    with collection.batch.dynamic() as batch:
        for document, vector in zip(documents, vectors):
            metadata = document["metadata"]
            batch.add_object(
                properties={
                    "property_id": document["property_id"],
                    "text": document["text"],
                    "city": metadata["city"],
                    "property_type": metadata["property_type"],
                },
                vector=vector,
            )
    return len(documents)
