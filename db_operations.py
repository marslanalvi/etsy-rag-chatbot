def upsert_documents_into_db(collection, chunked_documents):
    for doc in chunked_documents:
        print("==== Inserting chunks into db;;; ====")
        collection.upsert(
            ids=[doc["id"]], 
            documents=[doc["text"]], 
            embeddings=[doc["embedding"]],
            metadatas=[{"source": doc["id"].split("_chunk")[0]}]
        )

def get_document_ids_in_collection(collection):
    """Get all document IDs currently in the collection"""
    try:
        # Get all IDs from the collection
        result = collection.get()
        return result.get("ids", [])
    except Exception as e:
        print(f"Error retrieving document IDs: {e}")
        return []
