import psycopg2
import numpy as np
import faiss
import torch
from PIL import Image
import requests
from io import BytesIO
from transformers import AutoFeatureExtractor, AutoModel
from tqdm import tqdm
import os
from config import DATABASE_URL, MODEL_NAME, FAISS_INDEX_PATH, METADATA_PATH

def download_image(url: str, timeout: int = 10) -> Image.Image:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert('RGB')
        return img
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def extract_features(image: Image.Image, feature_extractor, model, device) -> np.ndarray:
    inputs = feature_extractor(images=image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    
    return features.flatten()

def build_index():
    print("Loading model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME).to(device)
    model.eval()
    
    print(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'hidden'}")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            pi.id as image_id,
            pi.image_url,
            pv.product_id
        FROM product_images pi
        INNER JOIN product_variants pv ON pi.variant_id = pv.id
        INNER JOIN products p ON pv.product_id = p.id
        WHERE pv.deleted_at IS NULL 
          AND p.status = 'active'
          AND p.deleted_at IS NULL
        ORDER BY pi.id
    """
    
    print("Fetching images from database...")
    cursor.execute(query)
    images = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Found {len(images)} images to index")
    
    vectors = []
    metadata = []
    failed_count = 0
    
    for image_id, image_url, product_id in tqdm(images, desc="Extracting features"):
        img = download_image(image_url)
        if img is None:
            failed_count += 1
            continue
        
        try:
            vector = extract_features(img, feature_extractor, model, device)
            vectors.append(vector)
            metadata.append({
                'image_id': int(image_id),
                'product_id': int(product_id),
                'image_url': image_url
            })
        except Exception as e:
            print(f"\nError processing image {image_id}: {e}")
            failed_count += 1
            continue
    
    print(f"\nSuccessfully processed {len(vectors)} images")
    print(f"Failed: {failed_count} images")
    
    if len(vectors) == 0:
        print("No vectors to index!")
        return
    
    vectors_array = np.array(vectors, dtype=np.float32)
    dimension = vectors_array.shape[1]
    
    print(f"Building FAISS index (dimension: {dimension})...")
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors_array)
    
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    
    print(f"Saving index to {FAISS_INDEX_PATH}...")
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    print(f"Saving metadata to {METADATA_PATH}...")
    np.save(METADATA_PATH, metadata)
    
    print("Indexing complete!")
    print(f"Total vectors: {index.ntotal}")

if __name__ == "__main__":
    build_index()
