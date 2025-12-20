from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import faiss
import torch
from transformers import AutoFeatureExtractor, AutoModel
from io import BytesIO
import time
from typing import List, Dict, Any, Optional
from config import API_KEY, MODEL_NAME, FAISS_INDEX_PATH, METADATA_PATH
import os

app = FastAPI(title="Image Search Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.feature_extractor = None
        self.model = None
        self.index = None
        self.metadata = None
        self.is_loaded = False
    
    def load(self):
        if self.is_loaded:
            return
        
        print(f"Loading model: {MODEL_NAME}")
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()
        
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}. Run indexing.py first.")
        
        if not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}. Run indexing.py first.")
        
        print(f"Loading FAISS index from {FAISS_INDEX_PATH}")
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        
        print(f"Loading metadata from {METADATA_PATH}")
        self.metadata = np.load(METADATA_PATH, allow_pickle=True)
        
        self.is_loaded = True
        print(f"Search engine loaded. Total indexed images: {self.index.ntotal}")
    
    def extract_features(self, image: Image.Image) -> np.ndarray:
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        return features.flatten()
    
    def search(self, image: Image.Image, top_k: int = 50) -> List[Dict[str, Any]]:
        query_vector = self.extract_features(image)
        query_vector = np.array([query_vector], dtype=np.float32)
        
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    'product_id': int(meta['product_id']),
                    'image_url': meta['image_url'],
                    'distance': float(distance),
                    'similarity_score': float(1 / (1 + distance))
                })
        
        return results
    
    def deduplicate_by_product(self, results: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        seen_products = set()
        unique_results = []
        
        for result in results:
            product_id = result['product_id']
            if product_id not in seen_products:
                seen_products.add(product_id)
                unique_results.append(result)
            
            if len(unique_results) >= limit:
                break
        
        return unique_results

search_engine = SearchEngine()

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not API_KEY:
        return True
    
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return True

@app.on_event("startup")
async def startup_event():
    try:
        search_engine.load()
    except Exception as e:
        print(f"Error loading search engine: {e}")
        print("Service will start but search will fail until index is built.")

@app.get("/")
async def root():
    return {
        "service": "Image Search Service",
        "version": "1.0.0",
        "status": "running",
        "indexed_images": search_engine.index.ntotal if search_engine.is_loaded else 0
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": search_engine.is_loaded,
        "indexed_images": search_engine.index.ntotal if search_engine.is_loaded else 0
    }

@app.post("/search")
async def search_image(
    file: UploadFile = File(...),
    _: bool = Depends(verify_api_key)
):
    start_time = time.time()
    
    if not search_engine.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Search engine not loaded. Please run indexing.py first."
        )
    
    if file.content_type and not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents)).convert('RGB')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    try:
        raw_results = search_engine.search(image, top_k=50)
        unique_results = search_engine.deduplicate_by_product(raw_results, limit=10)
        
        query_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "success": True,
            "results": unique_results,
            "query_time_ms": query_time_ms
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/reload")
async def reload_index(_: bool = Depends(verify_api_key)):
    try:
        search_engine.is_loaded = False
        search_engine.load()
        return {
            "success": True,
            "message": "Index reloaded successfully",
            "indexed_images": search_engine.index.ntotal
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
