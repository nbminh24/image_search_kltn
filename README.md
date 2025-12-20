# Image Search Service

Microservice tìm kiếm sản phẩm thời trang qua hình ảnh sử dụng Swin Transformer và FAISS.

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Copy file `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
DATABASE_URL=postgresql://postgres:Mimikyu1204@db.sdviskalbqirwlrpvmrp.supabase.co:5432/postgres
API_KEY=your-secret-api-key-here
MODEL_NAME=microsoft/swin-tiny-patch4-window7-224
FAISS_INDEX_PATH=./data/faiss_index.bin
METADATA_PATH=./data/metadata.npy
```

### 3. Chạy Indexing (Lần đầu tiên)

Trích xuất vector từ database và build FAISS index:

```bash
python indexing.py
```

**Lưu ý:**
- Quá trình này có thể mất 30-60 phút với 40,000 ảnh
- Cần kết nối internet để download ảnh từ CDN
- Model sẽ tự động download lần đầu (~100MB)
- Kết quả lưu trong folder `./data/`

### 4. Khởi động Service

```bash
python main.py
```

Hoặc dùng uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Service sẽ chạy tại: `http://localhost:8000`

## API Endpoints

### 1. Health Check

```bash
GET http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "indexed_images": 35420
}
```

### 2. Search Image

```bash
POST http://localhost:8000/search
Headers:
  X-API-Key: your-secret-api-key-here
Body (multipart/form-data):
  file: <image_file>
```

Response:
```json
{
  "success": true,
  "results": [
    {
      "product_id": 123,
      "image_url": "https://cdn.example.com/image.jpg",
      "distance": 0.234,
      "similarity_score": 0.95
    }
  ],
  "query_time_ms": 245
}
```

### 3. Reload Index

Reload FAISS index sau khi chạy lại indexing:

```bash
POST http://localhost:8000/reload
Headers:
  X-API-Key: your-secret-api-key-here
```

## Kiến trúc

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐
│   Backend   │─────>│  Image Search    │─────>│  Postgres    │
│  (NestJS)   │      │   Service        │      │              │
└─────────────┘      │  (FastAPI)       │      └──────────────┘
                     │                  │
                     │  - Swin Trans.   │
                     │  - FAISS Index   │
                     └──────────────────┘
```

## Logic Deduplication

Service tìm 50 kết quả gần nhất, sau đó lọc trùng theo `product_id`:

```python
seen_products = set()
unique_results = []

for result in raw_results:
    if result['product_id'] not in seen_products:
        seen_products.add(result['product_id'])
        unique_results.append(result)
    
    if len(unique_results) >= 10:
        break
```

## Production Notes

### Resource Requirements
- RAM: ~2GB (model + FAISS index)
- Storage: ~500MB (index + metadata)
- CPU/GPU: Hỗ trợ cả hai (GPU nhanh hơn 10-20x)

### Deployment
```bash
# Docker
docker build -t image-search-service .
docker run -p 8000:8000 --env-file .env image-search-service
```

### Monitoring
- Endpoint `/health` để health check
- Log query time trong response: `query_time_ms`

## Troubleshooting

### Lỗi: "FAISS index not found"
→ Chạy `python indexing.py` trước

### Lỗi: "Database connection failed"
→ Kiểm tra `DATABASE_URL` trong `.env`

### Lỗi: "Unauthorized"
→ Kiểm tra header `X-API-Key`

### Indexing chậm
→ Dùng GPU nếu có, hoặc giảm timeout download ảnh
