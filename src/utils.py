import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

DATASET_NAME = "events-state-ds-aug8"  # change if you want separate staging/prod sets
DATASET_ID = "bae9bb4c-7c25-4427-9b0e-d013da94f281"  # existing dataset ID

def ls_client() -> Client:
    """
    Reads LANGSMITH_API_KEY / LANGSMITH_ENDPOINT from env
    """
    return Client()