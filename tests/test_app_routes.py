"""Flask route tests with mocked YOLO."""
import io
import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest

import app as app_module
from models.chemical_simulator import ChemicalSimulator
from models.fusion_engine import FusionEngine


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_detect_no_file_returns_400(client):
    rv = client.post("/api/detect")
    assert rv.status_code == 400
    body = rv.get_json()
    assert body["success"] is False


def test_detect_yolo_missing_returns_500(client, monkeypatch):
    monkeypatch.setattr(app_module, "yolo_detector", None)
    data = {
        "image": (io.BytesIO(b"\xff\xd8\xff\xd9"), "test.jpg"),
    }
    rv = client.post("/api/detect", data=data, content_type="multipart/form-data")
    assert rv.status_code == 500


def test_detect_happy_path_mocked(client, monkeypatch, tmp_path):
    mock_yolo = MagicMock()
    mock_yolo.detect.return_value = [
        {
            "bbox": [0, 0, 50, 50],
            "class_name": "Banana Ripe",
            "confidence": 0.92,
        }
    ]
    mock_yolo.save_annotated_image = MagicMock()

    monkeypatch.setattr(app_module, "yolo_detector", mock_yolo)
    monkeypatch.setattr(
        app_module,
        "chemical_simulator",
        ChemicalSimulator(noise_sigma=0.0, temp_coeff=0.0, humidity_coeff=0.0),
    )
    monkeypatch.setattr(app_module, "fusion_engine", FusionEngine())
    monkeypatch.setattr(app_module, "db_handler", None)

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x01\x01"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    data = {"image": (io.BytesIO(png), "tiny.png")}
    rv = client.post(
        "/api/detect",
        data=data,
        content_type="multipart/form-data",
    )
    assert rv.status_code == 200, rv.get_data(as_text=True)
    body = rv.get_json()
    assert body["success"] is True
    assert "scan_id" in body
    assert body["results"]["total_fruits"] == 1
    assert "trl_disclaimer" in body["results"]
    mock_yolo.save_annotated_image.assert_called_once()


def test_sensitivity_test_applies_e0_factor(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "chemical_simulator",
        ChemicalSimulator(noise_sigma=0.0, temp_coeff=0.0, humidity_coeff=0.0),
    )
    monkeypatch.setattr(app_module, "fusion_engine", FusionEngine())
    rv = client.post(
        "/api/sensitivity-test",
        json={"fruit_type": "mango", "hours_since_harvest": 24, "temperature": 25},
    )
    assert rv.status_code == 200
    body = rv.get_json()
    assert body["success"] is True
    assert "variations" in body
    labels = {v["parameter_variation"] for v in body["variations"]}
    assert "E0_plus_20" in labels
    hi = next(v for v in body["variations"] if v["parameter_variation"] == "E0_plus_20")
    lo = next(v for v in body["variations"] if v["parameter_variation"] == "E0_minus_20")
    assert hi["ethylene_ppm"] >= lo["ethylene_ppm"]
