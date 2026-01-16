"""
Generate freshness confidence comparison graph for Visual, Chemical, and Bimodal frameworks.
"""

import matplotlib.pyplot as plt
import os

# Data values - Bimodal has higher confidence due to feature fusion
frameworks = ['Visual', 'Chemical', 'Bimodal']
confidence_scores = [0.75, 0.80, 0.92]

# Create figure with appropriate size
plt.figure(figsize=(8, 6))

# Create bar chart
bars = plt.bar(frameworks, confidence_scores, color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.8)

# Customize the chart
plt.title('Freshness Confidence Comparison', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Framework Mode', fontsize=12, fontweight='bold')
plt.ylabel('Confidence Score', fontsize=12, fontweight='bold')

# Set y-axis limits and ticks (0 to 1.0 for confidence scores)
plt.ylim(0.0, 1.0)
plt.yticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

# Add grid for better readability
plt.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels on top of bars
for bar, value in zip(bars, confidence_scores):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f'{value:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Create docs directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
os.makedirs(output_dir, exist_ok=True)

# Save the graph
output_path = os.path.join(output_dir, 'confidence_comparison.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight', format='png')
print(f"Graph saved to: {output_path}")

plt.close()
