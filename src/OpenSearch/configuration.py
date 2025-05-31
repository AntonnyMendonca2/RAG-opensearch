from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
load_dotenv()

class OpenSearchIterations:
    def __init__(self):
        self.index_name = os.getenv("index_name")
        self.elasticsearch_url = os.getenv("elasticsearch_url")
        self.elasticsearch_apikey = os.getenv("elasticsearch_apikey")

        self.client = Elasticsearch(
            self.elasticsearch_url,
            api_key=self.elasticsearch_apikey
        )

        self.index_source_fields = {
            f"{self.index_name}": [
                "conteudo",
                "titulo"
            ]
        }

    def creating_map(self):
        self.client.indices.create(
            index=self.index_name,
            mappings={
                    "properties": {
                    "titulo": { "type": "text" },
                    "conteudo": { "type": "text" },
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        )
    
    def index_content(self, docs):
        try:
            helpers.bulk(self.client, docs)
            return "sucesso!"
        except Exception as e:
            print("Erro geral ao indexar:", e)

    def get_elasticsearch_results(self, query):
        es_query = {
            "retriever": {
                "standard": {
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "conteudo"
                            ]
                        }
                    }
                }
            },
            "size": 3
        }

        result = self.client.search(index=self.index_name, body=es_query)
        return result["hits"]["hits"]
        
if __name__ == "__main__":
    op = OpenSearchIterations()
    op.creating_map()