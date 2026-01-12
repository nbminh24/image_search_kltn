import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
from datetime import datetime

class ResultVisualizer:
    def __init__(self, results_file="./benchmark_results/benchmark_results.json"):
        self.results_file = Path(results_file)
        self.output_dir = self.results_file.parent / "reports"
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"Loading results from: {self.results_file}")
        with open(self.results_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.metrics = self.data['metrics']
        self.model_info = self.data['model_info']
        
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = 150
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
    
    def create_metrics_table(self):
        print("\nCreating metrics summary table...")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        retrieval = self.metrics['retrieval_metrics']
        
        table_data = [
            ['Metric', 'Value'],
            ['Model Name', self.model_info['model_name']],
            ['Device', self.model_info['device']],
            ['Total Samples', str(self.metrics['total_samples'])],
            ['', ''],
            ['RETRIEVAL METRICS', ''],
            ['Top-1 Accuracy (%)', f"{retrieval['top1_accuracy']}%"],
            ['Top-5 Accuracy (%)', f"{retrieval['top5_accuracy']}%"],
            ['Top-10 Accuracy (%)', f"{retrieval['top10_accuracy']}%"],
            ['Mean Reciprocal Rank', f"{retrieval['mean_reciprocal_rank']:.4f}"],
            ['Recall@5 (%)', f"{retrieval['recall_at_5']}%"],
            ['Recall@10 (%)', f"{retrieval['recall_at_10']}%"],
            ['', ''],
            ['INFERENCE TIME', ''],
            ['Avg Inference Time (ms)', f"{self.metrics['inference_time']['mean_ms']:.2f}"],
            ['Std Inference Time (ms)', f"{self.metrics['inference_time']['std_ms']:.2f}"],
            ['Min Inference Time (ms)', f"{self.metrics['inference_time']['min_ms']:.2f}"],
            ['Max Inference Time (ms)', f"{self.metrics['inference_time']['max_ms']:.2f}"],
            ['', ''],
            ['Unique Products', str(len(self.metrics['class_labels']))],
        ]
        
        table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                        colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        for i in range(len(table_data)):
            if i == 0:
                table[(i, 0)].set_facecolor('#4CAF50')
                table[(i, 1)].set_facecolor('#4CAF50')
                table[(i, 0)].set_text_props(weight='bold', color='white')
                table[(i, 1)].set_text_props(weight='bold', color='white')
            elif table_data[i][0] == '':
                table[(i, 0)].set_facecolor('#f0f0f0')
                table[(i, 1)].set_facecolor('#f0f0f0')
            elif 'RETRIEVAL' in table_data[i][0] or 'INFERENCE' in table_data[i][0]:
                table[(i, 0)].set_facecolor('#2196F3')
                table[(i, 1)].set_facecolor('#2196F3')
                table[(i, 0)].set_text_props(weight='bold', color='white')
                table[(i, 1)].set_text_props(weight='bold', color='white')
            elif 'Top-1' in table_data[i][0]:
                table[(i, 0)].set_facecolor('#E3F2FD')
                table[(i, 1)].set_facecolor('#E3F2FD')
                table[(i, 0)].set_text_props(weight='bold')
                table[(i, 1)].set_text_props(weight='bold')
        
        plt.title('Swin Transformer - Image Retrieval Benchmark', 
                 fontsize=16, fontweight='bold', pad=20)
        
        output_file = self.output_dir / "metrics_table.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def create_confusion_matrix_heatmap(self, max_classes=50):
        print("\nCreating confusion matrix heatmap...")
        
        conf_matrix = np.array(self.metrics['confusion_matrix'])
        class_labels = self.metrics['class_labels']
        
        if len(class_labels) > max_classes:
            print(f"Too many classes ({len(class_labels)}), showing top {max_classes} by frequency...")
            y_true = np.array(self.data['raw_data']['ground_truth'])
            unique, counts = np.unique(y_true, return_counts=True)
            top_indices = np.argsort(counts)[-max_classes:]
            top_classes = unique[top_indices]
            
            mask = np.isin(class_labels, top_classes)
            indices = np.where(mask)[0]
            
            conf_matrix = conf_matrix[indices][:, indices]
            class_labels = [class_labels[i] for i in indices]
        
        fig, ax = plt.subplots(figsize=(14, 12))
        
        sns.heatmap(conf_matrix, 
                   annot=True if len(class_labels) <= 20 else False,
                   fmt='d',
                   cmap='Blues',
                   square=True,
                   cbar_kws={'label': 'Count'},
                   ax=ax)
        
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
        ax.set_title(f'Confusion Matrix - Swin Transformer\n({len(class_labels)} classes)', 
                    fontsize=14, fontweight='bold', pad=15)
        
        if len(class_labels) <= 30:
            ax.set_xticklabels(class_labels, rotation=45, ha='right')
            ax.set_yticklabels(class_labels, rotation=0)
        else:
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_xlabel('Predicted Label (Product ID)', fontsize=12, fontweight='bold')
            ax.set_ylabel('True Label (Product ID)', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        output_file = self.output_dir / "confusion_matrix.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def create_inference_time_distribution(self):
        print("\nCreating inference time distribution chart...")
        
        inference_times = np.array(self.data['raw_data']['inference_times'])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.hist(inference_times, bins=30, color='#2196F3', alpha=0.7, edgecolor='black')
        ax1.axvline(self.metrics['inference_time']['mean_ms'], 
                   color='red', linestyle='--', linewidth=2, 
                   label=f"Mean: {self.metrics['inference_time']['mean_ms']:.2f} ms")
        ax1.set_xlabel('Inference Time (ms)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Inference Time Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        ax2.boxplot(inference_times, vert=True, patch_artist=True,
                   boxprops=dict(facecolor='#4CAF50', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2),
                   whiskerprops=dict(linewidth=1.5),
                   capprops=dict(linewidth=1.5))
        ax2.set_ylabel('Inference Time (ms)', fontsize=11, fontweight='bold')
        ax2.set_title('Inference Time Box Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        stats_text = f"Mean: {self.metrics['inference_time']['mean_ms']:.2f} ms\n"
        stats_text += f"Std: {self.metrics['inference_time']['std_ms']:.2f} ms\n"
        stats_text += f"Min: {self.metrics['inference_time']['min_ms']:.2f} ms\n"
        stats_text += f"Max: {self.metrics['inference_time']['max_ms']:.2f} ms"
        
        ax2.text(1.35, np.median(inference_times), stats_text,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                verticalalignment='center', fontsize=9)
        
        plt.suptitle('Inference Time Analysis - Swin Transformer', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_file = self.output_dir / "inference_time_distribution.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def create_topk_accuracy_chart(self):
        print("\nCreating Top-K accuracy comparison chart...")
        
        retrieval = self.metrics['retrieval_metrics']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_values = ['Top-1', 'Top-5', 'Top-10']
        accuracies = [
            retrieval['top1_accuracy'],
            retrieval['top5_accuracy'],
            retrieval['top10_accuracy']
        ]
        
        colors = ['#FF5252', '#4CAF50', '#2196F3']
        bars = ax.bar(k_values, accuracies, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{acc:.1f}%',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Retrieval Rank', fontsize=12, fontweight='bold')
        ax.set_title('Top-K Retrieval Accuracy', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_file = self.output_dir / "topk_accuracy_chart.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def create_accuracy_visualization(self):
        print("\nCreating accuracy visualization...")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        accuracy = self.metrics['retrieval_metrics']['top1_accuracy']
        error_rate = 100 - accuracy
        
        colors = ['#4CAF50', '#FF5252']
        explode = (0.1, 0)
        
        wedges, texts, autotexts = ax.pie(
            [accuracy, error_rate],
            labels=['Correct', 'Incorrect'],
            colors=colors,
            autopct='%1.2f%%',
            startangle=90,
            explode=explode,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
        
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
        
        ax.text(0, 0, f'{accuracy}%', 
               ha='center', va='center',
               fontsize=32, fontweight='bold', color='#4CAF50')
        ax.text(0, -0.15, 'Top-1 Accuracy',
               ha='center', va='center',
               fontsize=12, fontweight='bold', color='gray')
        
        plt.title('Top-1 Retrieval Accuracy - Swin Transformer', 
                 fontsize=14, fontweight='bold', pad=20)
        
        output_file = self.output_dir / "accuracy_chart.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def create_summary_report(self):
        print("\nCreating comprehensive summary report...")
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('tight')
        ax1.axis('off')
        
        retrieval = self.metrics['retrieval_metrics']
        
        table_data = [
            ['Metric', 'Value'],
            ['Top-1 Accuracy', f"{retrieval['top1_accuracy']}%"],
            ['Top-5 Accuracy', f"{retrieval['top5_accuracy']}%"],
            ['Top-10 Accuracy', f"{retrieval['top10_accuracy']}%"],
            ['MRR', f"{retrieval['mean_reciprocal_rank']:.4f}"],
            ['Total Samples', str(self.metrics['total_samples'])],
            ['Avg Inference Time', f"{self.metrics['inference_time']['mean_ms']:.2f} ms"],
            ['Unique Products', str(len(self.metrics['class_labels']))],
        ]
        
        table = ax1.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2.5)
        
        for i in range(len(table_data)):
            if i == 0:
                table[(i, 0)].set_facecolor('#2196F3')
                table[(i, 1)].set_facecolor('#2196F3')
                table[(i, 0)].set_text_props(weight='bold', color='white')
                table[(i, 1)].set_text_props(weight='bold', color='white')
            else:
                table[(i, 0)].set_facecolor('#E3F2FD')
                table[(i, 1)].set_facecolor('#F5F5F5')
        
        ax1.set_title('Swin Transformer Performance Summary', 
                     fontsize=16, fontweight='bold', pad=10)
        
        ax2 = fig.add_subplot(gs[1, 0])
        retrieval = self.metrics['retrieval_metrics']
        k_values = ['Top-1', 'Top-5', 'Top-10']
        accuracies = [retrieval['top1_accuracy'], retrieval['top5_accuracy'], retrieval['top10_accuracy']]
        colors = ['#FF5252', '#4CAF50', '#2196F3']
        ax2.bar(k_values, accuracies, color=colors, alpha=0.7)
        ax2.set_ylabel('Accuracy (%)', fontweight='bold')
        ax2.set_title('Top-K Accuracy', fontweight='bold')
        ax2.set_ylim(0, 105)
        ax2.grid(True, alpha=0.3, axis='y')
        
        ax3 = fig.add_subplot(gs[1, 1])
        inference_times = np.array(self.data['raw_data']['inference_times'])
        ax3.hist(inference_times, bins=20, color='#2196F3', alpha=0.7, edgecolor='black')
        ax3.axvline(self.metrics['inference_time']['mean_ms'], 
                   color='red', linestyle='--', linewidth=2)
        ax3.set_xlabel('Inference Time (ms)', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.set_title('Inference Time Distribution', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        ax4 = fig.add_subplot(gs[2, :])
        conf_matrix = np.array(self.metrics['confusion_matrix'])
        if conf_matrix.shape[0] > 30:
            sample_size = 30
            conf_matrix = conf_matrix[:sample_size, :sample_size]
        
        sns.heatmap(conf_matrix, cmap='Blues', square=True, cbar=True, ax=ax4,
                   cbar_kws={'label': 'Count'})
        ax4.set_xlabel('Predicted', fontweight='bold')
        ax4.set_ylabel('True', fontweight='bold')
        ax4.set_title('Confusion Matrix (Sample)', fontweight='bold')
        
        plt.suptitle(f'Swin Transformer Benchmark Report\nModel: {self.model_info["model_name"]}', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        output_file = self.output_dir / "summary_report.png"
        plt.savefig(output_file, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"Saved: {output_file}")
        return output_file
    
    def export_to_csv(self):
        print("\nExporting raw data to CSV...")
        
        df = pd.DataFrame({
            'ground_truth': self.data['raw_data']['ground_truth'],
            'predictions': self.data['raw_data']['predictions'],
            'inference_time_ms': self.data['raw_data']['inference_times'],
            'category': self.data['raw_data']['categories']
        })
        
        df['is_correct'] = df['ground_truth'] == df['predictions']
        
        output_file = self.output_dir / "raw_results.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"Saved: {output_file}")
        return output_file
    
    def generate_all_reports(self):
        print("\n" + "="*60)
        print("GENERATING VISUALIZATION REPORTS")
        print("="*60)
        
        files = []
        
        files.append(self.create_metrics_table())
        files.append(self.create_topk_accuracy_chart())
        files.append(self.create_accuracy_visualization())
        files.append(self.create_confusion_matrix_heatmap())
        files.append(self.create_inference_time_distribution())
        files.append(self.create_summary_report())
        files.append(self.export_to_csv())
        
        print("\n" + "="*60)
        print("ALL REPORTS GENERATED SUCCESSFULLY")
        print("="*60)
        print(f"Output directory: {self.output_dir}")
        print("\nGenerated files:")
        for f in files:
            print(f"  - {f.name}")
        print("="*60)
        
        return files

def main():
    visualizer = ResultVisualizer()
    visualizer.generate_all_reports()

if __name__ == "__main__":
    main()
