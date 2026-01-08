"""
ChromaDB vector database setup and operations
"""
import chromadb
from chromadb.config import Settings
import json
from config import CHROMA_DB_PATH, COLLECTION_NAME


def initialize_chromadb():
    """Initialize ChromaDB client and collection"""
    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Loaded existing collection: {COLLECTION_NAME}")
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Sales and marketing data for report generation"}
        )
        print(f"Created new collection: {COLLECTION_NAME}")
    
    return client, collection


def load_data_to_vectordb(collection, sales_data, marketing_data):
    """Load sales and marketing data into ChromaDB"""
    documents = []
    metadatas = []
    ids = []
    
    # Process sales data
    for sale in sales_data:
        doc_text = sale["description"]
        documents.append(doc_text)
        metadatas.append({
            "type": "sales",
            "id": sale["id"],
            "product": sale["product"],
            "category": sale["category"],
            "revenue": str(sale["revenue"]),
            "units_sold": str(sale["units_sold"]),
            "region": sale["region"],
            "quarter": sale["quarter"],
            "customer_segment": sale["customer_segment"],
            "sales_rep": sale["sales_rep"]
        })
        ids.append(f"sales_{sale['id']}")
    
    # Process marketing data
    for campaign in marketing_data:
        doc_text = campaign["description"]
        documents.append(doc_text)
        metadatas.append({
            "type": "marketing",
            "id": campaign["id"],
            "campaign_name": campaign["campaign_name"],
            "channel": campaign["channel"],
            "budget": str(campaign["budget"]),
            "impressions": str(campaign["impressions"]),
            "clicks": str(campaign["clicks"]),
            "conversions": str(campaign["conversions"]),
            "quarter": campaign["quarter"],
            "target_segment": campaign["target_segment"]
        })
        ids.append(f"marketing_{campaign['id']}")
    
    # Add documents to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Loaded {len(documents)} documents into ChromaDB")
    return len(documents)


def query_vectordb(collection, query_text, n_results=5, filter_dict=None):
    """Query the vector database"""
    query_params = {
        "query_texts": [query_text],
        "n_results": n_results
    }
    
    if filter_dict:
        query_params["where"] = filter_dict
    
    results = collection.query(**query_params)
    
    return results


def get_collection_stats(collection):
    """Get statistics about the collection"""
    count = collection.count()
    return {
        "total_documents": count,
        "collection_name": collection.name
    }


def clear_collection(client, collection_name):
    """Clear all data from collection"""
    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted collection: {collection_name}")
    except:
        print(f"Collection {collection_name} does not exist")


if __name__ == "__main__":
    # Test the vector database setup
    client, collection = initialize_chromadb()
    stats = get_collection_stats(collection)
    print(f"Collection stats: {stats}")

