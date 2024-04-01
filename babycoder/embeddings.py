import os
import csv 
import shutil
import openai
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Union, Any, Optional
from transformers import GPT2TokenizerFast
from dotenv import load_dotenv
import time

# Heavily derived from OpenAi's cookbook example

load_dotenv()

# the dir is the ./playground directory
REPOSITORY_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "playground")

class Embeddings:
    def __init__(self, workspace_path: str):
        if not os.path.isdir(workspace_path):
            raise ValueError("workspace_path must be a valid directory path")

        self.workspace_path = workspace_path
        openai.api_key = os.getenv("OPENAI_API_KEY", "")

        if openai.api_key == "":
            raise ValueError("OPENAI_API_KEY environment variable not found")

        self.DOC_EMBEDDINGS_MODEL = f"text-embedding-ada-002"
        self.QUERY_EMBEDDINGS_MODEL = f"text-embedding-ada-002"

        self.SEPARATOR = "\n* "

        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.separator_len = len(self.tokenizer.tokenize(self.SEPARATOR))

    def compute_repository_embeddings(self):
        playground_data_path = os.path.join(self.workspace_path, 'playground_data')

        if not os.path.isdir(playground_data_path):
            os.makedirs(playground_data_path)

        # Delete the contents of the playground_data directory but not the directory itself
        # This is to ensure that we don't have any old data lying around
        for filename in os.listdir(playground_data_path):
            file_path = os.path.join(playground_data_path, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {str(e)}")

        # extract and save info to csv
        info = self.extract_info(REPOSITORY_PATH)
        self.save_info_to_csv(info)

        df = pd.read_csv(os.path.join(self.workspace_path, 'playground_data\\repository_info.csv'))
        df = df.set_index(["filePath", "lineCoverage"])
        self.df = df
        context_embeddings = self.compute_doc_embeddings(df)
        self.save_doc_embeddings_to_csv(context_embeddings, df, os.path.join(self.workspace_path, 'playground_data\\doc_embeddings.csv'))

        try:
            self.document_embeddings = self.load_embeddings(os.path.join(self.workspace_path, 'playground_data\\doc_embeddings.csv'))
        except:
            pass

    def extract_info(self, REPOSITORY_PATH) -> List[Tuple[str, Tuple[int, int], str]]:
        LINES_PER_CHUNK = 60

        for root, dirs, files in os.walk(REPOSITORY_PATH):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        contents = f.read()
                except:
                    continue

                lines = contents.split("\n")
                lines = [line for line in lines if line.strip()]
                chunks = [
                        lines[i:i+LINES_PER_CHUNK]
                        for i in range(0, len(lines),
