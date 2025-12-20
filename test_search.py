import requests
import sys
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

print(f"[DEBUG] API_KEY loaded: '{API_KEY}'")

def test_health():
    print("Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_search(image_path: str):
    print(f"Testing search with image: {image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(
            f"{API_URL}/search",
            files=files,
            headers=headers
        )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Query time: {data['query_time_ms']}ms")
        print(f"Results count: {len(data['results'])}\n")
        
        print("All results:")
        for i, result in enumerate(data['results'], 1):
            print(f"{i}. Product ID: {result['product_id']}")
            print(f"   Similarity: {result['similarity_score']:.4f}")
            print(f"   Distance: {result['distance']:.4f}")
            print(f"   Image: {result['image_url']}")
            print()
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_health()
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_search(image_path)
    else:
        print("Usage: python test_search.py <image_path>")
