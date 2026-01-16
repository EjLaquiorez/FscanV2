"""
Generate fusion formulation flowchart diagram with improved graphics and alignment.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import numpy as np

# Create figure with appropriate size
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 12)
ax.set_ylim(0, 13)
ax.axis('off')

# Define colors
color_yolo = '#3498db'  # Blue
color_nir = '#e74c3c'    # Red
color_fusion = '#2ecc71' # Green
color_process = '#f39c12' # Orange
color_output = '#9b59b6'  # Purple
color_conf = '#e67e22'   # Dark Orange

# Title
title = ax.text(6, 12.2, 'Bimodal Fusion Framework for Freshness Classification', 
                ha='center', va='center', fontsize=20, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.3))

# ========== INPUT LAYER ==========
# YOLO Input Box
yolo_box = FancyBboxPatch((0.8, 9.5), 2.8, 1.5, 
                          boxstyle="round,pad=0.15", 
                          facecolor=color_yolo, 
                          edgecolor='black', 
                          linewidth=2.5,
                          alpha=0.85)
ax.add_patch(yolo_box)
ax.text(2.2, 10.4, 'YOLO Detection', ha='center', va='center', 
        fontsize=13, fontweight='bold', color='white')
ax.text(2.2, 10.0, '(Visual Modality)', ha='center', va='center', 
        fontsize=10, color='white', style='italic')
ax.text(2.2, 9.7, 'C_YOLO, R_YOLO', ha='center', va='center', 
        fontsize=11, color='white', family='monospace')

# NIR Input Box
nir_box = FancyBboxPatch((8.4, 9.5), 2.8, 1.5, 
                         boxstyle="round,pad=0.15", 
                         facecolor=color_nir, 
                         edgecolor='black', 
                         linewidth=2.5,
                         alpha=0.85)
ax.add_patch(nir_box)
ax.text(9.8, 10.4, 'NIR Analysis', ha='center', va='center', 
        fontsize=13, fontweight='bold', color='white')
ax.text(9.8, 10.0, '(Chemical Modality)', ha='center', va='center', 
        fontsize=10, color='white', style='italic')
ax.text(9.8, 9.7, 'C_NIR, R_NIR', ha='center', va='center', 
        fontsize=11, color='white', family='monospace')

# Arrows from inputs to fusion (offset vertically to avoid overlap)
arrow1 = FancyArrowPatch((3.6, 10.4), (4.8, 10.1), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=3, color='black', zorder=5,
                         connectionstyle='arc3,rad=0.1')
ax.add_patch(arrow1)

arrow2 = FancyArrowPatch((8.4, 10.4), (7.2, 10.1), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=3, color='black', zorder=5,
                         connectionstyle='arc3,rad=-0.1')
ax.add_patch(arrow2)

# ========== FUSION ENGINE ==========
fusion_box = FancyBboxPatch((4.8, 8.3), 2.4, 1.7, 
                            boxstyle="round,pad=0.2", 
                            facecolor=color_fusion, 
                            edgecolor='black', 
                            linewidth=3.5,
                            alpha=0.9)
ax.add_patch(fusion_box)
ax.text(6, 9.5, 'Fusion Engine', ha='center', va='center', 
        fontsize=15, fontweight='bold', color='white')
ax.text(6, 9.1, 'Feature Integration', ha='center', va='center', 
        fontsize=11, color='white', style='italic')
ax.text(6, 8.7, 'w_YOLO = 0.7  |  w_NIR = 0.3', ha='center', va='center', 
        fontsize=10, color='white', family='monospace')

# ========== PROCESSING STAGES ==========
# Stage 1: Agreement Check
stage1_box = FancyBboxPatch((0.5, 6.2), 4.2, 1.4, 
                            boxstyle="round,pad=0.15", 
                            facecolor=color_process, 
                            edgecolor='black', 
                            linewidth=2.5,
                            alpha=0.85)
ax.add_patch(stage1_box)
ax.text(2.6, 7.1, 'Stage 1: Agreement Check', ha='center', va='center', 
        fontsize=12, fontweight='bold', color='black')
ax.text(2.6, 6.7, 'R_YOLO = R_NIR', ha='center', va='center', 
        fontsize=10, color='black', family='monospace')
ax.text(2.6, 6.4, 'OR |Index(R_YOLO) - Index(R_NIR)| ≤ 1', ha='center', va='center', 
        fontsize=9, color='black', family='monospace')

# Arrow from fusion to stage 1 (curved to avoid overlap)
arrow3 = FancyArrowPatch((5.0, 8.3), (2.6, 7.6), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=2.5, color='black', zorder=5,
                         connectionstyle='arc3,rad=0.2')
ax.add_patch(arrow3)

# Stage 2: Decision Logic
stage2_box = FancyBboxPatch((7.3, 6.2), 4.2, 1.4, 
                            boxstyle="round,pad=0.15", 
                            facecolor=color_process, 
                            edgecolor='black', 
                            linewidth=2.5,
                            alpha=0.85)
ax.add_patch(stage2_box)
ax.text(9.4, 7.1, 'Stage 2: Decision Logic', ha='center', va='center', 
        fontsize=12, fontweight='bold', color='black')
ax.text(9.4, 6.85, 'Case 1: Agreement → Boost confidence (+0.1)', 
        ha='center', va='center', fontsize=9, color='black')
ax.text(9.4, 6.6, 'Case 2: C_YOLO ≥ 0.8 → Trust YOLO', 
        ha='center', va='center', fontsize=9, color='black')
ax.text(9.4, 6.35, 'Case 3: Weighted decision based on confidence', 
        ha='center', va='center', fontsize=9, color='black')

# Arrow from fusion to stage 2 (curved to avoid overlap)
arrow4 = FancyArrowPatch((7.0, 8.3), (9.4, 7.6), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=2.5, color='black', zorder=5,
                         connectionstyle='arc3,rad=-0.2')
ax.add_patch(arrow4)

# ========== CONFIDENCE FUSION ==========
conf_box = FancyBboxPatch((3.5, 4.5), 5, 1.2, 
                          boxstyle="round,pad=0.15", 
                          facecolor=color_conf, 
                          edgecolor='black', 
                          linewidth=2.5,
                          alpha=0.85)
ax.add_patch(conf_box)
ax.text(6, 5.3, 'Confidence Fusion', ha='center', va='center', 
        fontsize=13, fontweight='bold', color='white')
ax.text(6, 4.9, 'C_overall = 0.7 × C_YOLO + 0.3 × C_NIR', 
        ha='center', va='center', fontsize=11, color='white', family='monospace')

# Arrows from stages to confidence (curved to avoid overlap)
arrow5 = FancyArrowPatch((2.6, 6.2), (4.8, 5.7), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=2.5, color='black', zorder=5,
                         connectionstyle='arc3,rad=0.15')
ax.add_patch(arrow5)

arrow6 = FancyArrowPatch((9.4, 6.2), (7.2, 5.7), 
                         arrowstyle='->', mutation_scale=25, 
                         linewidth=2.5, color='black', zorder=5,
                         connectionstyle='arc3,rad=-0.15')
ax.add_patch(arrow6)

# ========== OUTPUT ==========
output_box = FancyBboxPatch((2.5, 2.5), 7, 1.5, 
                             boxstyle="round,pad=0.2", 
                             facecolor=color_output, 
                             edgecolor='black', 
                             linewidth=3.5,
                             alpha=0.9)
ax.add_patch(output_box)
ax.text(6, 3.6, 'Fused Result', ha='center', va='center', 
        fontsize=15, fontweight='bold', color='white')
ax.text(6, 3.2, 'R_final, C_overall, C_ripeness, Quality Score', 
        ha='center', va='center', fontsize=11, color='white', family='monospace')

# Arrow from confidence to output
arrow7 = FancyArrowPatch((6, 4.5), (6, 4.0), 
                         arrowstyle='->', mutation_scale=30, 
                         linewidth=3, color='black', zorder=5)
ax.add_patch(arrow7)

# ========== FORMULA ANNOTATIONS ==========
formula_box1 = FancyBboxPatch((1, 0.5), 4.5, 0.9, 
                              boxstyle="round,pad=0.1", 
                              facecolor='wheat', 
                              edgecolor='black', 
                              linewidth=1.5,
                              alpha=0.7)
ax.add_patch(formula_box1)
ax.text(3.25, 1.1, 'C_overall = w_YOLO × C_YOLO + w_NIR × C_NIR', 
        ha='center', va='center', fontsize=11, 
        family='monospace', fontweight='bold')

formula_box2 = FancyBboxPatch((6.5, 0.5), 4.5, 0.9, 
                              boxstyle="round,pad=0.1", 
                              facecolor='wheat', 
                              edgecolor='black', 
                              linewidth=1.5,
                              alpha=0.7)
ax.add_patch(formula_box2)
ax.text(8.75, 1.1, 'w_YOLO = 0.7  |  w_NIR = 0.3  |  w_YOLO + w_NIR = 1.0', 
        ha='center', va='center', fontsize=10, 
        family='monospace', fontweight='bold')

# ========== LEGEND ==========
legend_elements = [
    mpatches.Patch(facecolor=color_yolo, label='YOLO (Visual)', alpha=0.85, edgecolor='black', linewidth=1.5),
    mpatches.Patch(facecolor=color_nir, label='NIR (Chemical)', alpha=0.85, edgecolor='black', linewidth=1.5),
    mpatches.Patch(facecolor=color_fusion, label='Fusion Engine', alpha=0.85, edgecolor='black', linewidth=1.5),
    mpatches.Patch(facecolor=color_process, label='Decision Logic', alpha=0.85, edgecolor='black', linewidth=1.5),
    mpatches.Patch(facecolor=color_conf, label='Confidence Fusion', alpha=0.85, edgecolor='black', linewidth=1.5),
    mpatches.Patch(facecolor=color_output, label='Output', alpha=0.85, edgecolor='black', linewidth=1.5)
]
legend = ax.legend(handles=legend_elements, loc='upper left', fontsize=10, 
          bbox_to_anchor=(0.02, 0.98), framealpha=0.9, edgecolor='black', 
          fancybox=True, shadow=True)
legend.get_frame().set_linewidth(2)

# Add grid lines for alignment reference (optional - can be removed)
# ax.grid(True, alpha=0.1, linestyle='--')

plt.tight_layout()

# Create docs directory if it doesn't exist
import os
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
os.makedirs(output_dir, exist_ok=True)

# Save the diagram
output_path = os.path.join(output_dir, 'fusion_formulation_diagram.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight', format='png', 
            facecolor='white', edgecolor='none', pad_inches=0.2)
print(f"Fusion diagram saved to: {output_path}")

plt.close()
