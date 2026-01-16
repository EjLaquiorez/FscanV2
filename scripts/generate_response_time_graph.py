"""
Generate response time comparison graph for Visual, Chemical, and Bimodal frameworks.
"""

import matplotlib.pyplot as plt
import os

# Data values
frameworks = ['Visual', 'Chemical', 'Bimodal']
response_times = [0.8, 1.0, 1.28]

# Create figure with appropriate size
plt.figure(figsize=(8, 6))

# Create bar chart
bars = plt.bar(frameworks, response_times, color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.8)

# Customize the chart
plt.title('Projected Response Time Comparison', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Framework Mode', fontsize=12, fontweight='bold')
plt.ylabel('Response Time', fontsize=12, fontweight='bold')

# Set y-axis limits and ticks
plt.ylim(0.0, 1.4)
plt.yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])

# Add grid for better readability
plt.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels on top of bars
for bar, value in zip(bars, response_times):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{value:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Adjust layout to prevent label cutoff
plt.tight_layout()

# Create docs directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
os.makedirs(output_dir, exist_ok=True)

# Save the graph
output_path = os.path.join(output_dir, 'response_time_comparison.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight', format='png')
print(f"Graph saved to: {output_path}")

plt.close()
