"""
Statistical Validation Components
Implements Bootstrap CI and McNemar's Test per thesis Section 3.6
"""
import numpy as np
from scipy import stats
from scipy.stats import pearsonr
from typing import List, Dict, Tuple, Optional
from sklearn.utils import resample


class StatisticalValidator:
    """
    Statistical rigor for performance claims
    """
    
    def __init__(self, n_bootstrap: int = 1000, random_state: int = 42):
        self.n_bootstrap = n_bootstrap
        self.random_state = random_state
        np.random.seed(random_state)
    
    def bootstrap_confidence_interval(self, 
                                      data: List[float], 
                                      confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate bootstrap confidence interval for accuracy or other metrics
        
        Args:
            data: List of accuracy scores (0-1) or other metric values
            confidence: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            (mean, lower_bound, upper_bound)
        """
        if not data or len(data) < 2:
            return 0.0, 0.0, 0.0
        
        bootstrap_means = []
        n_samples = len(data)
        
        for _ in range(self.n_bootstrap):
            # Resample with replacement
            sample = resample(data, random_state=self.random_state)
            bootstrap_means.append(np.mean(sample))
        
        alpha = (1 - confidence) / 2
        lower = np.percentile(bootstrap_means, alpha * 100)
        upper = np.percentile(bootstrap_means, (1 - alpha) * 100)
        mean = np.mean(data)
        
        return float(mean), float(lower), float(upper)
    
    def mcnemar_test(self, 
                     yolo_correct: List[bool], 
                     fusion_correct: List[bool],
                     continuity_correction: bool = True) -> Dict:
        """
        McNemar's test for paired classifier comparison
        Tests if fusion improvement over YOLO is statistically significant
        
        Args:
            yolo_correct: List of boolean correctness for YOLO-only
            fusion_correct: List of boolean correctness for Fusion
            continuity_correction: Apply continuity correction (conservative)
            
        Returns:
            Dict with chi2, p_value, significance flag, and contingency table
        """
        if len(yolo_correct) != len(fusion_correct):
            raise ValueError("Input lists must have same length")
        
        n = len(yolo_correct)
        
        # Build contingency table
        # n01: YOLO wrong, Fusion correct (improvements)
        # n10: YOLO correct, Fusion wrong (degradations)
        n01 = sum((not y) and f for y, f in zip(yolo_correct, fusion_correct))
        n10 = sum(y and (not f) for y, f in zip(yolo_correct, fusion_correct))
        n11 = sum(y and f for y, f in zip(yolo_correct, fusion_correct))  # Both correct
        n00 = sum((not y) and (not f) for y, f in zip(yolo_correct, fusion_correct))  # Both wrong
        
        # Discordant pairs (relevant for test)
        discordant = n01 + n10
        
        if discordant == 0:
            return {
                'chi2': 0.0,
                'p_value': 1.0,
                'significant': False,
                'n01': n01,
                'n10': n10,
                'n11': n11,
                'n00': n00,
                'improvement_count': 0,
                'degradation_count': 0,
                'net_improvement': 0,
                'note': 'No discordant pairs - classifiers identical'
            }
        
        # Calculate test statistic
        if continuity_correction:
            # Edwards continuity correction (more conservative)
            chi2 = (abs(n01 - n10) - 1) ** 2 / discordant
        else:
            chi2 = (n01 - n10) ** 2 / discordant
        
        # Two-tailed p-value
        p_value = 1 - stats.chi2.cdf(chi2, df=1)
        
        return {
            'chi2': float(chi2),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'alpha': 0.05,
            'n01': n01,  # Fusion fixes YOLO errors (good)
            'n10': n10,  # Fusion breaks YOLO correct (bad)
            'n11': n11,  # Both correct
            'n00': n00,  # Both wrong
            'total_samples': n,
            'discordant_pairs': discordant,
            'improvement_count': n01,
            'degradation_count': n10,
            'net_improvement': n01 - n10,
            'improvement_rate': n01 / n if n > 0 else 0,
            'continuity_correction': continuity_correction
        }
    
    def cross_modal_consistency(self, 
                               visual_confidences: List[float], 
                               chemical_proxies: List[float]) -> Dict:
        """
        Calculate Pearson correlation between modalities (thesis: r = 0.78)
        
        Returns:
            Correlation stats and interpretation
        """
        if len(visual_confidences) < 2:
            return {
                'correlation': 0.0,
                'p_value': 1.0,
                'r_squared': 0.0,
                'interpretation': 'Insufficient data'
            }
        
        try:
            r, p = pearsonr(visual_confidences, chemical_proxies)
            
            # Interpretation guide
            abs_r = abs(r)
            if abs_r >= 0.9:
                interp = "Very strong"
            elif abs_r >= 0.7:
                interp = "Strong"
            elif abs_r >= 0.5:
                interp = "Moderate"
            elif abs_r >= 0.3:
                interp = "Weak"
            else:
                interp = "Very weak/None"
            
            return {
                'correlation': float(r),
                'p_value': float(p),
                'r_squared': float(r**2),
                'interpretation': interp,
                'n_samples': len(visual_confidences),
                'significant': p < 0.05
            }
        except Exception as e:
            return {
                'error': str(e),
                'correlation': 0.0,
                'p_value': 1.0
            }
    
    def calculate_metrics(self, 
                         y_true: List[str], 
                         y_pred: List[str],
                         average: str = 'weighted') -> Dict:
        """
        Calculate precision, recall, F1 from true and predicted labels
        """
        from sklearn.metrics import precision_recall_fscore_support, accuracy_score
        
        accuracy = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average=average, zero_division=0
        )
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'support': support.tolist() if hasattr(support, 'tolist') else support
        }
    
    def sensitivity_analysis_summary(self, 
                                    baseline_accuracy: float,
                                    varied_accuracies: List[float],
                                    variation_labels: List[str]) -> Dict:
        """
        Summarize sensitivity analysis results (Section 4.1.6)
        """
        accuracies = [baseline_accuracy] + varied_accuracies
        min_acc = min(accuracies)
        max_acc = max(accuracies)
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies)
        
        # Check if stays above 84.5% (thesis requirement)
        robust = min_acc >= 0.845
        
        return {
            'baseline': baseline_accuracy,
            'min_accuracy': min_acc,
            'max_accuracy': max_acc,
            'mean_accuracy': mean_acc,
            'std_deviation': std_acc,
            'variation_range': max_acc - min_acc,
            'meets_robustness_criteria': robust,
            'criteria_threshold': 0.845,
            'variations_tested': variation_labels,
            'all_accuracies': accuracies
        }