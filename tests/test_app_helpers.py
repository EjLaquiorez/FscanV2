"""Tests for pure helpers in app.py (no Flask request)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import app as app_module


def test_allowed_file_accepts_common_types():
    assert app_module.allowed_file("a.jpg") is True
    assert app_module.allowed_file("x.PNG") is True
    assert app_module.allowed_file("noext") is False
    assert app_module.allowed_file("evil.exe") is False


def test_extract_fruit_name_strips_ripeness():
    assert app_module.extract_fruit_name("Banana Ripe") == "Banana"
    assert app_module.extract_fruit_name("Mango Overripe") == "Mango"
    assert app_module.extract_fruit_name("Pineapple Unripe") == "Pineapple"
    assert app_module.extract_fruit_name("") == "Unknown"
