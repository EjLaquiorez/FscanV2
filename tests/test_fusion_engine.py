"""FusionEngine unit tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

from models.fusion_engine import FusionEngine


def test_fuse_single_agreement_uses_alpha_beta():
    fe = FusionEngine(alpha=0.7, beta=0.3, delta=0.15)
    r = fe.fuse_single(0.8, 0.75)
    assert r["has_conflict"] is False
    assert abs(r["fusion_score"] - (0.7 * 0.8 + 0.3 * 0.75)) < 1e-6


def test_fuse_single_conflict_yolo_high_reweights():
    fe = FusionEngine(delta=0.15)
    r = fe.fuse_single(0.95, 0.3)
    assert r["has_conflict"] is True
    assert r["resolution_strategy"] == "yolo_dominant"


def test_batch_fuse_mismatched_lengths_raises():
    fe = FusionEngine()
    with pytest.raises(ValueError, match="Mismatch"):
        fe.batch_fuse([{"confidence": 0.5}], [])


def test_classify_ripeness_three_bins():
    fe = FusionEngine()
    assert fe._classify_ripeness(0.85) == "Unripe"
    assert fe._classify_ripeness(0.70) == "Ripe"
    assert fe._classify_ripeness(0.50) == "Overripe"
    assert fe._classify_freshness(0.85) == "Unripe"  # alias
