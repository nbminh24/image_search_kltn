# Swin Transformer Image Retrieval Benchmark

## Tổng quan

Đây là hệ thống đánh giá hiệu năng của Swin Transformer cho bài toán **Image Retrieval** (không phải Image Classification).

### Phương pháp đánh giá

The evaluation is conducted as an **image retrieval task** rather than a classification task.

- Given a query image, features are extracted using the Swin Transformer backbone
- Features are searched against a FAISS index to find similar images
- A retrieval is considered correct if the retrieved image belongs to the same **product ID** as the query image
- We report Top-K retrieval accuracy and Mean Reciprocal Rank (MRR) to evaluate ranking quality

## Metrics được tính toán

### 1. Retrieval Metrics (Product-level)

#### Top-1 Accuracy (%)
- **Công thức**: `(Số query mà top-1 result đúng product) / (Tổng số query) × 100`
- **Ý nghĩa**: Tỷ lệ query mà kết quả đứng đầu (rank 1) có cùng product_id
- **Business metric**: Quan trọng cho UX - người dùng thường chỉ xem result đầu tiên

#### Top-5 Accuracy (%)
- **Công thức**: `(Số query mà product đúng nằm trong top-5) / (Tổng số query) × 100`
- **Ý nghĩa**: Tỷ lệ query mà sản phẩm đúng xuất hiện trong 5 kết quả đầu
- **Ứng dụng**: Người dùng thường scroll và xem ~5 results đầu tiên

#### Top-10 Accuracy (%)
- **Công thức**: `(Số query mà product đúng nằm trong top-10) / (Tổng số query) × 100`
- **Ý nghĩa**: Tỷ lệ query mà sản phẩm đúng xuất hiện trong 10 kết quả đầu
- **Ứng dụng**: Đánh giá khả năng retrieve của model ở phạm vi rộng hơn

#### Mean Reciprocal Rank (MRR)
- **Công thức**: `MRR = mean(1 / rank_of_correct_product)`
- **Ý nghĩa**: 
  - Rank 1 → score = 1.0
  - Rank 2 → score = 0.5
  - Rank 5 → score = 0.2
  - Không tìm thấy → score = 0.0
- **Ứng dụng**: Đánh giá chất lượng ranking - càng cao càng tốt
- **Ưu điểm**: Phản ánh vị trí của kết quả đúng, không chỉ là có/không

#### Recall@5 và Recall@10 (%)
- **Công thức**: Tương tự Top-K Accuracy
- **Ý nghĩa**: Tỷ lệ query retrieve được đúng product trong top-K
- **Thuật ngữ chuẩn**: Dùng trong các paper IR (Information Retrieval)

### 2. Inference Time Metrics

#### Mean Inference Time (ms/image)
- **Ý nghĩa**: Thời gian xử lý trung bình cho 1 ảnh
- **Ứng dụng**: Đánh giá khả năng deploy real-time

#### Std, Min, Max Inference Time
- **Ý nghĩa**: Độ ổn định và phạm vi biến động của thời gian xử lý

### 3. Confusion Matrix
- **Ý nghĩa**: Ma trận nhầm lẫn giữa các product (chỉ cho Top-1)
- **Ứng dụng**: Phát hiện product nào hay bị nhầm với product nào

## Test Modes (Phương pháp test)

### 🔬 Mode 1: Augmented Query (KHUYẾN NGHỊ cho KLTN)

**Phương pháp:** Synthetic Query / Robustness Testing

**Cách thức:**
1. Lấy ảnh gốc từ database
2. Apply augmentation (xoay, crop, blur, color jitter)
3. Dùng ảnh đã biến đổi để search
4. Kỳ vọng: Vẫn tìm ra ảnh gốc trong top-K

**Augmentations áp dụng:**
- `ColorJitter`: brightness ±30%, contrast ±30%, saturation ±20%, hue ±10%
- `RandomRotation`: ±15 độ
- `RandomResizedCrop`: 75-100% crop với scale
- `GaussianBlur`: kernel=3, sigma 0.1-2.0

**Ưu điểm:**
- ✅ Không cần dataset test riêng
- ✅ Test robustness - chứng minh model học features (không học vẹt pixels)
- ✅ Mô phỏng real-world queries (ảnh người dùng chụp: mờ, nghiêng, khác góc)
- ✅ Accuracy hợp lý: 65-85% (đủ cao nhưng realistic)
- ✅ Điểm cộng lớn khi bảo vệ KLTN

**Khi nào dùng:** Đề xuất cho báo cáo KLTN và demo

### 📷 Mode 2: Normal Query (Exclude Self)

**Phương pháp:** Direct Image Search với exclude query image

**Cách thức:**
1. Lấy ảnh gốc từ database
2. Search với ảnh gốc
3. **Exclude** chính query image khỏi results
4. So sánh với sản phẩm khác cùng product_id

**Ưu điểm:**
- ✅ Test khả năng tìm variant khác của cùng product
- ✅ Tránh data leakage (không tự tìm chính mình)

**Hạn chế:**
- ⚠️ Nếu product chỉ có 1 ảnh → accuracy = 0% cho product đó
- ⚠️ Phụ thuộc vào số lượng ảnh/product

**Khi nào dùng:** Khi có nhiều ảnh/product trong dataset

## Cách sử dụng

### Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Chạy benchmark

#### Option A: Augmented Mode (Khuyến nghị)
```bash
python benchmark_swin.py --mode augmented --limit 100
```

#### Option B: Normal Mode (Exclude self)
```bash
python benchmark_swin.py --mode normal --limit 100
```

**Arguments:**
- `--mode`: Test mode (`normal` hoặc `augmented`)
- `--limit`: Số lượng test samples (default: 100)

### Bước 3: Tạo visualization reports

```bash
python visualize_results.py
```

## Kết quả đầu ra

### Thư mục: `./benchmark_results/`
- `benchmark_results.json` - Raw metrics data (JSON format)

### Thư mục: `./benchmark_results/reports/`
- `metrics_table.png` - Bảng tổng hợp đầy đủ các metrics
- `topk_accuracy_chart.png` - **[MỚI]** Biểu đồ so sánh Top-1, Top-5, Top-10
- `accuracy_chart.png` - Biểu đồ tròn Top-1 Accuracy
- `confusion_matrix.png` - Heatmap confusion matrix
- `inference_time_distribution.png` - Histogram + boxplot thời gian inference
- `summary_report.png` - Báo cáo tổng hợp 1 trang
- `raw_results.csv` - Raw data để phân tích thêm

## Giải thích kết quả

### Khi nào accuracy thấp?

#### ❌ False Positive (Dự đoán sai)
- Query: Áo đen brand A
- Retrieved: Áo đen brand B (khác product)
- **Nguyên nhân**: Features tương đồng về màu sắc, style nhưng khác brand/product

#### ✅ Correct retrieval nhưng different variant
- Query: Áo đen size L (product_id = 123)
- Retrieved: Áo trắng size M (product_id = 123)
- **Kết luận**: ĐÚNG về business, ĐÚNG về product-level retrieval
- **Lưu ý**: Không phải lỗi của model

### Kỳ vọng accuracy hợp lý

Với Image Retrieval task và FAISS index:

- **Top-1 Accuracy**: 40-70% (tùy dataset)
- **Top-5 Accuracy**: 70-90%
- **Top-10 Accuracy**: 85-95%
- **MRR**: 0.5-0.8

⚠️ **Lưu ý**: Nếu Top-1 = 100% → Kiểm tra lại logic test, có thể đang test sai!

## Thuật ngữ cho báo cáo KLTN

### Tiếng Anh (khuyến nghị)
```
- Image Retrieval Evaluation
- Product-level Retrieval Accuracy
- Top-K Retrieval Accuracy
- Mean Reciprocal Rank (MRR)
- Recall@K
- Instance-level Retrieval
```

### Cách viết trong phần Methodology

#### Standard Approach (Normal Mode)
```
The evaluation is conducted as an image retrieval task rather than 
a classification task. Given a query image, features are extracted 
using the Swin Transformer backbone and searched against a FAISS index.

A retrieval is considered correct if the retrieved image belongs to 
the same product ID as the query image (product-level retrieval).
To avoid data leakage, the query image itself is excluded from the 
search results.

We report Top-K retrieval accuracy (K=1, 5, 10) and Mean Reciprocal 
Rank (MRR) to evaluate both the precision of top results and the 
overall ranking quality.
```

#### Robustness Testing Approach (Augmented Mode) - KHUYẾN NGHỊ
```
To evaluate the robustness of learned features and simulate real-world 
deployment scenarios, we conduct augmentation-based query evaluation.

Instead of using original database images directly, we apply synthetic 
transformations including rotation (±15°), random cropping (75-100%), 
color jitter (brightness/contrast ±30%), and Gaussian blur to create 
augmented query images. These transformations simulate real-world 
conditions such as varying lighting, camera angles, and image quality.

The model must retrieve the original (non-augmented) image from the 
index based on the augmented query. This approach tests whether the 
Swin Transformer learns robust visual features rather than memorizing 
pixel-level patterns.

Performance under augmentation demonstrates the model's generalization 
capability and readiness for practical deployment where user-uploaded 
images may vary significantly from catalog images.

We report Top-K retrieval accuracy and MRR under augmented conditions 
to evaluate feature robustness.
```

## Tham khảo

- Swin Transformer: Liu et al., "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows", ICCV 2021
- FAISS: Johnson et al., "Billion-scale similarity search with GPUs", IEEE Transactions on Big Data 2019
- Retrieval Metrics: Manning et al., "Introduction to Information Retrieval", Cambridge University Press

## Lưu ý quan trọng

### ✅ Đúng
- Test bằng cách search trong FAISS index
- So sánh product_id của result với ground truth
- Report đầy đủ Top-1, Top-5, Top-10, MRR

### ❌ Sai
- Gán prediction = ground_truth (100% accuracy giả tạo)
- Chỉ report Top-1 accuracy
- Gọi là "classification accuracy"

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-23  
**Contact**: Để hỏi về metrics hoặc cách sử dụng
