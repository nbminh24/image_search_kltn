import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/swin-tiny-patch4-window7-224")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index.bin")
METADATA_PATH = os.getenv("METADATA_PATH", "./data/metadata.npy")

print(f"[CONFIG] API_KEY loaded: '{API_KEY}'")
