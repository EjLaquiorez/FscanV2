"""ChemicalSimulator unit tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models.chemical_simulator import ChemicalSimulator, ChemicalReading


def test_simulate_returns_dataclass_with_timestamp():
    sim = ChemicalSimulator(noise_sigma=0.0, temp_coeff=0.0, humidity_coeff=0.0)
    r = sim.simulate("mango", hours_since_harvest=1.0, temperature=25.0, humidity=80.0)
    assert isinstance(r, ChemicalReading)
    assert r.timestamp
    assert "T" in r.timestamp or "-" in r.timestamp
    assert 0.0 <= r.normalized_proxy <= 1.0


def test_e0_factor_increases_signal_with_fixed_noise():
    sim = ChemicalSimulator(noise_sigma=0.0, temp_coeff=0.0, humidity_coeff=0.0)
    low = sim.simulate("mango", 24.0, 25.0, 80.0, e0_factor=1.0)
    high = sim.simulate("mango", 24.0, 25.0, 80.0, e0_factor=1.5)
    assert high.ethylene_ppm >= low.ethylene_ppm


def test_unknown_fruit_maps_to_unknown_params():
    sim = ChemicalSimulator(noise_sigma=0.0, temp_coeff=0.0, humidity_coeff=0.0)
    r = sim.simulate("Dragonfruit Xyz", 10.0, 25.0, 80.0)
    assert r.simulation_params["fruit_type"] == "unknown"


def test_batch_simulate_length_matches():
    sim = ChemicalSimulator(noise_sigma=0.0)
    dets = [{"fruit_type": "banana"}, {"fruit_type": "mango"}]
    out = sim.batch_simulate(dets, base_hours=12.0)
    assert len(out) == 2
