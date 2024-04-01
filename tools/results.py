#!/usr/bin/env python3
import os
import argparse
import openai
import pinecone
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is missing from .env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable is missing from .env")

PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
if not PINECONE_ENVIRONMENT:
    raise ValueError("PINECONE_ENVIRONMENT environment variable is missing from .env")

PINECONE_TABLE_NAME = os.getenv("TABLE_NAME", "")
if not PINECONE_TABLE_NAME:
    raise ValueError("TABLE_NAME environment variable is missing from .env")

def query_records(index, query, top_k=1000):
    results = index.query(query, top_k=top_k, include_metadata=True)
    return [f"{task.metadata['task']}:\n{task.metadata['result']}\n------------------" for task in results.matches]

def get_ada_embedding(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model="text-embedding-ada-002")["data"][0]["embedding"]

def main():
    parser = argparse.ArgumentParser(description="Query Pinecone index using a string.")
    parser.add_argument('objective', nargs='*', metavar='<objective>', help='''
    The main objective to search for. If not specified, the objective will be taken from the
    OBJECTIVE environment variable.
    ''')
    args = parser.parse_args()

    openai.api_key = OPENAI_API_KEY
    pinecone.init(api_key=PINECONE_API_KEY)
    index = pinecone.Index(PINECONE_TABLE_NAME)

    query = get_ada_embedding(' '.join(args.objective).strip() or os.getenv("OBJECTIVE", ""))
    retrieved_tasks = query_records(index, query)
    for r in retrieved_tasks:
        print(r)

if __name__ == "__main__":
    main()
