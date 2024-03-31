import os
import re
import sys
from typing import Dict, List, Any
import importlib
import pinecone
import openai

def can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def import_openai() -> None:
    if not can_import("openai"):
        print("\033[91m\033[1m"+"OpenAI library not found. Please install it to use OpenAI functionality.\nInstall:  pip install openai")
        sys.exit(1)
    global openai
    openai = importlib.import_module("openai")

def import_pinecone() -> None:
    if not can_import("pinecone"):
        print("\033[91m\033[1m"+"Pinecone storage requires package pinecone-client.\nInstall:  pip install -r extensions/requirements.txt")
        sys.exit(1)
    global pinecone
    pinecone = importlib.import_module("pinecone")

class PineconeResultsStorage:
    def __init__(self, openai_api_key: str, pinecone_api_key: str, pinecone_environment: str, llm_model: str, llama_model_path: str, results_store_name: str, objective: str):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_environment = pinecone_environment
        self.llm_model = llm_model
        self.llama_model_path = llama_model_path
        self.results_store_name = results_store_name
        self.objective = objective
        self.namespace = re.sub(re.compile('[^\x00-\x7F]+'), '', objective)

        openai.api_key = self.openai_api_key
        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_environment)

        self.check_pinecone_index()

    def check_pinecone_index(self) -> None:
        if self.results_store_name not in pinecone.list_indexes():
            self.create_pinecone_index()

        self.index = pinecone.Index(self.results_store_name)
        index_stats_response = self.index.describe_index_stats()
        assert self.dimension == index_stats_response['dimension'], f"Dimension of the index ({index_stats_response['dimension']}) does not match the dimension of the LLM embedding ({self.dimension})"

    def create_pinecone_index(self) -> None:
        dimension = 1536 if not self.llm_model.startswith("llama") else 5120
        metric = "cosine"
        pod_type = "p1"

        pinecone.create_index(
            self.results_store_name, dimension=dimension, metric=metric, pod_type=pod_type
        )

    def add(self, task: Dict[str, str], result: str, result_id: int) -> None:
        vector = self.get_embedding(result)
        self.index.upsert(
            [(result_id, vector, {"task": task["task_name"], "result": result})], namespace=self.namespace
        )

    def query(self, query: str, top_results_num: int) -> List[Dict[str, Any]]:
        query_embedding = self.get_embedding(query)
        results = self.index.query(query_embedding, top_k=top_results_num, include_metadata=True, namespace=self.namespace)
        sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
        return [{"task": item.metadata["task"], "score": item.score} for item in sorted_results]
