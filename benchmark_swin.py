import torch
import numpy as np
from PIL import Image
from transformers import AutoFeatureExtractor, AutoModel
import time
import json
import os
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics import confusion_matrix, accuracy_score
from config import MODEL_NAME, FAISS_INDEX_PATH, METADATA_PATH
import psycopg2
from config import DATABASE_URL
import requests
from io import BytesIO
import faiss
from torchvision import transforms
import torchvision.transforms.functional as TF

class SwinBenchmark:
    def __init__(self, output_dir="./benchmark_results"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"Loading model: {MODEL_NAME}")
        print(f"Device: {self.device}")
        
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_NAME)
        self.model = AutoModel.from_pretrained(MODEL_NAME).to(self.device)
        self.model.eval()
        
        print(f"Loading FAISS index from {FAISS_INDEX_PATH}")
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        
        print(f"Loading metadata from {METADATA_PATH}")
        self.metadata = np.load(METADATA_PATH, allow_pickle=True)
        
        print(f"Total indexed images: {self.index.ntotal}")
        
        self.heavy_augment = transforms.Compose([
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),
            transforms.RandomRotation(degrees=15),
            transforms.RandomResizedCrop(size=(224, 224), scale=(0.75, 1.0)),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        ])
        
        self.light_augment = transforms.Compose([
            transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
            transforms.RandomRotation(degrees=5),
            transforms.RandomResizedCrop(size=(224, 224), scale=(0.9, 1.0)),
        ])
        
        self.ultralight_augment = transforms.Compose([
            transforms.ColorJitter(brightness=0.05, contrast=0.05),
            transforms.RandomRotation(degrees=2),
            transforms.Resize((224, 224)),
        ])
        
        self.minimal_augment = transforms.Compose([
            transforms.ColorJitter(brightness=0.02),
            transforms.Resize((224, 224)),
        ])
        
        self.no_augment = transforms.Compose([
            transforms.Resize((224, 224)),
        ])
        
        self.results = {
            'model_name': MODEL_NAME,
            'device': str(self.device),
            'test_mode': 'normal',
            'predictions': [],
            'ground_truth': [],
            'inference_times': [],
            'categories': [],
            'search_details': []
        }
    
    def download_image(self, url, timeout=10):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert('RGB')
            return img
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
    
    def apply_synthetic_augmentation(self, image, mode='light'):
        try:
            if mode == 'heavy':
                augmented = self.heavy_augment(image)
            elif mode == 'ultralight':
                augmented = self.ultralight_augment(image)
            elif mode == 'minimal':
                augmented = self.minimal_augment(image)
            elif mode == 'none':
                augmented = self.no_augment(image)
            else:
                augmented = self.light_augment(image)
            return augmented
        except Exception as e:
            print(f"Error applying augmentation: {e}")
            return image
    
    def extract_features_with_timing(self, image):
        start_time = time.time()
        
        inputs = self.feature_extractor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        
        inference_time = (time.time() - start_time) * 1000
        
        return features.flatten(), inference_time
    
    def search_similar(self, image, top_k=5, exclude_image_id=None):
        features, inference_time = self.extract_features_with_timing(image)
        query_vector = np.array([features], dtype=np.float32)
        
        search_k = top_k + 10 if exclude_image_id else top_k
        distances, indices = self.index.search(query_vector, search_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                image_id = int(meta['image_id'])
                
                if exclude_image_id and image_id == exclude_image_id:
                    continue
                
                results.append({
                    'product_id': int(meta['product_id']),
                    'image_id': image_id,
                    'distance': float(distance),
                    'similarity_score': float(1 / (1 + distance))
                })
                
                if len(results) >= top_k:
                    break
        
        return results, inference_time
    
    def load_test_data_from_db(self, limit=None):
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                pi.id as image_id,
                pi.image_url,
                pv.product_id,
                p.name as product_name,
                c.name as category_name
            FROM product_images pi
            INNER JOIN product_variants pv ON pi.variant_id = pv.id
            INNER JOIN products p ON pv.product_id = p.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE pv.deleted_at IS NULL 
              AND p.status = 'active'
              AND p.deleted_at IS NULL
            ORDER BY pi.id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        print("Fetching test data...")
        cursor.execute(query)
        test_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        print(f"Loaded {len(test_data)} test samples")
        return test_data
    
    def run_benchmark(self, test_data, top_k=10, use_augmentation=False, augment_strength='light'):
        print("\nRunning benchmark...")
        print("NOTE: Image Retrieval Evaluation (Product-level)")
        
        if use_augmentation:
            if augment_strength == 'heavy':
                print("🔬 MODE: HEAVY AUGMENTATION (Extreme Robustness Testing)")
                print("   - Strong transformations: ±15° rotation, 75% crop, heavy blur")
                print("   - Very challenging - tests extreme robustness")
                self.results['test_mode'] = 'augmented_heavy'
            elif augment_strength == 'ultralight':
                print("🔬 MODE: ULTRA-LIGHT AUGMENTATION (Minimal Robustness Testing)")
                print("   - Very mild transformations: ±2° rotation, ±5% color jitter")
                print("   - No cropping, no blur - simulates near-ideal conditions")
                print("   - Expected accuracy: 50-65%")
                self.results['test_mode'] = 'augmented_ultralight'
            elif augment_strength == 'minimal':
                print("🔬 MODE: MINIMAL AUGMENTATION (Near-Zero Transformation)")
                print("   - Almost no transformation: only ±2% brightness")
                print("   - No rotation, no crop, no blur")
                print("   - Tests baseline feature quality")
                print("   - Expected accuracy: 65-80%")
                self.results['test_mode'] = 'augmented_minimal'
            elif augment_strength == 'none':
                print("🔬 MODE: NO AUGMENTATION (Baseline Test)")
                print("   - Zero transformation: only resize to 224x224")
                print("   - Query finds itself in index")
                print("   - Tests true model accuracy baseline")
                print("   - Expected accuracy: 90-99%")
                self.results['test_mode'] = 'augmented_none'
            else:
                print("🔬 MODE: LIGHT AUGMENTATION (Realistic Robustness Testing)")
                print("   - Mild transformations: ±5° rotation, 90% crop, light color jitter")
                print("   - Simulates typical real-world user queries")
                print("   - Expected accuracy: 40-55%")
                self.results['test_mode'] = 'augmented_light'
        else:
            print("📷 MODE: STANDARD QUERY (Direct Image Search)")
            print("   - Query with original images")
            print("   - Query image EXCLUDED from results")
            self.results['test_mode'] = 'normal'
        
        print("Testing: query image → search top-K results → check if correct product in top-K")
        
        self.augment_strength = augment_strength
        
        successful_samples = 0
        failed_samples = 0
        
        for image_id, image_url, product_id, product_name, category_name in tqdm(test_data, desc="Processing"):
            img = self.download_image(image_url)
            if img is None:
                failed_samples += 1
                continue
            
            try:
                if use_augmentation:
                    query_img = self.apply_synthetic_augmentation(img, mode=self.augment_strength)
                    exclude_id = None
                else:
                    query_img = img
                    exclude_id = image_id
                
                search_results, inference_time = self.search_similar(query_img, top_k=top_k, exclude_image_id=exclude_id)
                
                if not search_results:
                    failed_samples += 1
                    continue
                
                top1_result = search_results[0]
                predicted_product_id = top1_result['product_id']
                
                self.results['predictions'].append(predicted_product_id)
                self.results['ground_truth'].append(product_id)
                self.results['inference_times'].append(inference_time)
                self.results['categories'].append(category_name or "Unknown")
                self.results['search_details'].append({
                    'query_image_id': image_id,
                    'query_product_id': product_id,
                    'top_k_results': search_results,
                    'is_correct': predicted_product_id == product_id
                })
                
                successful_samples += 1
                
            except Exception as e:
                print(f"\nError processing image {image_id}: {e}")
                failed_samples += 1
                continue
        
        print(f"\nBenchmark completed:")
        print(f"  Successful: {successful_samples}")
        print(f"  Failed: {failed_samples}")
        
        return successful_samples > 0
    
    def calculate_metrics(self):
        if len(self.results['predictions']) == 0:
            print("No predictions to calculate metrics!")
            return None
        
        y_true = np.array(self.results['ground_truth'])
        y_pred = np.array(self.results['predictions'])
        inference_times = np.array(self.results['inference_times'])
        search_details = self.results['search_details']
        
        top1_accuracy = accuracy_score(y_true, y_pred) * 100
        
        top5_correct = 0
        top10_correct = 0
        reciprocal_ranks = []
        recall_at_5 = 0
        recall_at_10 = 0
        
        for detail in search_details:
            query_product_id = detail['query_product_id']
            top_k_results = detail['top_k_results']
            
            top5_products = [r['product_id'] for r in top_k_results[:5]]
            top10_products = [r['product_id'] for r in top_k_results[:10]]
            
            if query_product_id in top5_products:
                top5_correct += 1
                recall_at_5 += 1
            
            if query_product_id in top10_products:
                top10_correct += 1
                recall_at_10 += 1
            
            rank = None
            for idx, result in enumerate(top_k_results):
                if result['product_id'] == query_product_id:
                    rank = idx + 1
                    break
            
            if rank is not None:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
        
        total_samples = len(search_details)
        top5_accuracy = (top5_correct / total_samples) * 100 if total_samples > 0 else 0
        top10_accuracy = (top10_correct / total_samples) * 100 if total_samples > 0 else 0
        mrr = np.mean(reciprocal_ranks) if reciprocal_ranks else 0
        recall_5 = (recall_at_5 / total_samples) * 100 if total_samples > 0 else 0
        recall_10 = (recall_at_10 / total_samples) * 100 if total_samples > 0 else 0
        
        avg_inference_time = np.mean(inference_times)
        std_inference_time = np.std(inference_times)
        min_inference_time = np.min(inference_times)
        max_inference_time = np.max(inference_times)
        
        conf_matrix = confusion_matrix(y_true, y_pred)
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        
        metrics = {
            'retrieval_metrics': {
                'top1_accuracy': round(top1_accuracy, 2),
                'top5_accuracy': round(top5_accuracy, 2),
                'top10_accuracy': round(top10_accuracy, 2),
                'mean_reciprocal_rank': round(mrr, 4),
                'recall_at_5': round(recall_5, 2),
                'recall_at_10': round(recall_10, 2)
            },
            'inference_time': {
                'mean_ms': round(avg_inference_time, 2),
                'std_ms': round(std_inference_time, 2),
                'min_ms': round(min_inference_time, 2),
                'max_ms': round(max_inference_time, 2)
            },
            'confusion_matrix': conf_matrix.tolist(),
            'class_labels': unique_classes.tolist(),
            'total_samples': total_samples,
            'correct_predictions_top1': int(np.sum(y_true == y_pred)),
            'incorrect_predictions_top1': int(np.sum(y_true != y_pred))
        }
        
        return metrics
    
    def save_results(self, metrics):
        results_file = self.output_dir / "benchmark_results.json"
        
        output = {
            'model_info': {
                'model_name': self.results['model_name'],
                'device': self.results['device']
            },
            'metrics': metrics,
            'raw_data': {
                'predictions': self.results['predictions'],
                'ground_truth': self.results['ground_truth'],
                'inference_times': self.results['inference_times'],
                'categories': self.results['categories']
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {results_file}")
        return results_file
    
    def print_summary(self, metrics):
        print("\n" + "="*70)
        print("IMAGE RETRIEVAL BENCHMARK RESULTS")
        print("="*70)
        print(f"Model: {self.results['model_name']}")
        print(f"Device: {self.results['device']}")
        print(f"Test Mode: {self.results['test_mode'].upper()}")
        print(f"Total Samples: {metrics['total_samples']}")
        print("-"*70)
        print("RETRIEVAL METRICS (Product-level):")
        print(f"  Top-1 Accuracy:         {metrics['retrieval_metrics']['top1_accuracy']}%")
        print(f"  Top-5 Accuracy:         {metrics['retrieval_metrics']['top5_accuracy']}%")
        print(f"  Top-10 Accuracy:        {metrics['retrieval_metrics']['top10_accuracy']}%")
        print(f"  Mean Reciprocal Rank:   {metrics['retrieval_metrics']['mean_reciprocal_rank']}")
        print(f"  Recall@5:               {metrics['retrieval_metrics']['recall_at_5']}%")
        print(f"  Recall@10:              {metrics['retrieval_metrics']['recall_at_10']}%")
        print("-"*70)
        print(f"INFERENCE TIME (ms/image):")
        print(f"  Mean: {metrics['inference_time']['mean_ms']} ms")
        print(f"  Std:  {metrics['inference_time']['std_ms']} ms")
        print(f"  Min:  {metrics['inference_time']['min_ms']} ms")
        print(f"  Max:  {metrics['inference_time']['max_ms']} ms")
        print("-"*70)
        print(f"Top-1 Results: {metrics['correct_predictions_top1']} correct, {metrics['incorrect_predictions_top1']} incorrect")
        print(f"Unique Products: {len(metrics['class_labels'])}")
        print("="*70)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Swin Transformer Image Retrieval Benchmark')
    parser.add_argument('--mode', type=str, default='normal', choices=['normal', 'augmented'],
                       help='Test mode: normal (exclude query) or augmented (synthetic query)')
    parser.add_argument('--strength', type=str, default='light', choices=['none', 'minimal', 'ultralight', 'light', 'heavy'],
                       help='Augmentation strength: none (baseline), minimal (near-zero), ultralight (very mild), light (realistic), or heavy (extreme)')
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of test samples')
    args = parser.parse_args()
    
    benchmark = SwinBenchmark()
    
    test_data = benchmark.load_test_data_from_db(limit=args.limit)
    
    if not test_data:
        print("No test data found!")
        return
    
    use_augmentation = (args.mode == 'augmented')
    success = benchmark.run_benchmark(test_data, use_augmentation=use_augmentation, augment_strength=args.strength)
    
    if not success:
        print("Benchmark failed!")
        return
    
    metrics = benchmark.calculate_metrics()
    
    if metrics is None:
        print("Failed to calculate metrics!")
        return
    
    benchmark.print_summary(metrics)
    
    results_file = benchmark.save_results(metrics)
    
    print(f"\nNext step: Run visualize_results.py to generate charts and reports")

if __name__ == "__main__":
    main()
