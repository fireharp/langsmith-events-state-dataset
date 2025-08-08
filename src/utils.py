import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DATASET_NAME = "user-events-to-actions"  # change if you want separate staging/prod sets

def ls_client() -> Client:
    """
    Reads LANGSMITH_API_KEY / LANGSMITH_ENDPOINT from env
    """
    return Client()