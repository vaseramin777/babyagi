import os
import time
import logging
from collections import deque
from typing import Dict, List, Optional
import importlib
import openai
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import tiktoken as tiktoken
import re

# Load environment variables from .env file
load_dotenv()

# Initialize the logger
logging.basicConfig(level=logging.ERROR)

# Initialize the chromadb client
client = chromadb.Client(Settings(anonymized_telemetry=False))

# Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not (LLM_MODEL.startswith("llama") or LLM_MODEL.startswith("human")):
    assert OPENAI_API_KEY, "\033[91m\033[1mOPENAI_API_KEY environment variable is missing from .env\033[0m\033[0m"

RESULTS_STORE_NAME = os.getenv("RESULTS_STORE_NAME", "table_name")
assert RESULTS_STORE_NAME, "\033[91m\033[1mRESULTS_STORE_NAME environment variable is missing from .env\033[0m\033[0m"

INSTANCE_NAME = os.getenv("INSTANCE_NAME", "babyagi")
COOPERATIVE_MODE = os.getenv("COOPERATIVE_MODE", "none")
JOIN_EXISTING_OBJECTIVE = os.getenv("JOIN_EXISTING_OBJECTIVE", "false").lower() == "true"

OBJECTIVE = os.getenv("OBJECTIVE", "")
INITIAL_TASK = os.getenv("INITIAL_TASK", "")

OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.0))

# Extensions support
def can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def load_dotenv_extensions(extensions: str) -> None:
    if can_import("extensions.dotenvext"):
        from extensions.dotenvext import load_dotenv_extensions
        load_dotenv_extensions(extensions)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Llama
def initialize_llama() -> Optional[Tuple[Llama, Llama]]:
    if LLM_MODEL.startswith("llama"):
        if can_import("llama_cpp"):
            from llama_cpp import Llama

            CTX_MAX = 1024
            LLAMA_THREADS_NUM = int(os.getenv("LLAMA_THREADS_NUM", 8))

            llm = Llama(
                model_path=os.getenv("LLAMA_MODEL_PATH", "models/llama-13B/ggml-model.bin"),
                n_ctx=CTX_MAX,
                n_threads=LLAMA_THREADS_NUM,
                n_batch=512,
                use_mlock=False,
            )

            llm_embed = Llama(
                model_path=os.getenv("LLAMA_MODEL_PATH", "models/llama-13B/ggml-model.bin"),
                n_ctx=CTX_MAX,
                n_threads=LLAMA_THREADS_NUM,
                n_batch=512,
                embedding=True,
                use_mlock=False,
            )

            return (llm, llm_embed)
        else:
            print(
                "\033[91m\033[1mLlama LLM requires package llama-cpp. Falling back to GPT-3.5-turbo.\033[0m\033[0m"
            )
    return None

llm, llm_embed = initialize_llama()

# Initialize results storage
def use_chroma() -> DefaultResultsStorage:
    logging.getLogger('chromadb').setLevel(logging.ERROR)
    chroma_persist_dir = "chroma"
    chroma_client = chromadb.PersistentClient(
        settings=chromadb.config.Settings(
            persist_directory=chroma_persist_dir,
        )
    )

    metric = "cosine"
    embedding_function = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY) if not LLM_MODEL.startswith("llama") else LlamaEmbeddingFunction()
    collection = chroma_client.get_or_create_collection(
        name=RESULTS_STORE_NAME,
        metadata={"hnsw:space": metric},
        embedding_function=embedding_function,
    )

    return DefaultResultsStorage(collection)

results_storage = use_chroma()

# Initialize tasks storage
class SingleTaskListStorage:
    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0

    def append(self, task: Dict) -> None:
        self.tasks.append(task)

    def replace(self, tasks
