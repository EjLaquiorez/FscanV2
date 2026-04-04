"""
FELIX-Inspired Chemical Sensing Simulation (TRL 3)
Based on thesis: Ethylene dynamics E(t) = E₀e^(kt) and NIR proxies
"""
import numpy as np
import math
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ChemicalReading:
    """Structured chemical simulation output"""
    ethylene_ppm: float
    normalized_proxy: float  # Ê(t) in [0,1]
    brix_estimate: float
    moisture_estimate: float
    composite_quality: float
    simulation_params: Dict
    timestamp: str


class ChemicalSimulator:
    """
    Mathematical simulation of chemical sensing (NO physical sensors)
    Implements ethylene emission dynamics and Kubelka-Munk NIR theory
    """
    
    # Fruit-specific parameters from thesis Table 3.2.1
    ETHYLENE_PARAMS = {
        'mango': {'E0': 0.20, 'k': 0.015, 'E_max': 2.0, 'pattern': 'climacteric'},
        'banana': {'E0': 0.30, 'k': 0.025, 'E_max': 3.0, 'pattern': 'climacteric'},
        'pineapple': {'E0': 0.10, 'k': 0.010, 'E_max': 1.5, 'pattern': 'non-climacteric'},
        'cashew': {'E0': 0.15, 'k': 0.012, 'E_max': 1.8, 'pattern': 'climacteric'},
        'cacao': {'E0': 0.05, 'k': 0.008, 'E_max': 1.0, 'pattern': 'fermentation'},
        # Fallback defaults
        'unknown': {'E0': 0.15, 'k': 0.012, 'E_max': 2.0, 'pattern': 'climacteric'}
    }
    
    def __init__(self, 
                 noise_sigma: float = 0.05,  # From Voss et al. (2020)
                 temp_coeff: float = 0.15,    # ±15% temperature sensitivity
                 humidity_coeff: float = 0.05):  # γ = 0.05
        self.noise_sigma = noise_sigma
        self.temp_coeff = temp_coeff
        self.humidity_coeff = humidity_coeff
        self.nominal_temp = 25  # 25°C baseline
        
    def simulate(self, 
                 fruit_type: str, 
                 hours_since_harvest: float = 24.0,
                 temperature: float = 25.0, 
                 humidity: float = 80.0,
                 ripeness_stage: Optional[str] = None,
                 *,
                 e0_factor: float = 1.0,
                 k_factor: float = 1.0,
                 noise_scale: float = 1.0) -> ChemicalReading:
        """
        Generate synthetic chemical indicators
        
        Args:
            fruit_type: mango, banana, pineapple, cashew, cacao
            hours_since_harvest: Time since harvest in hours
            temperature: Ambient temperature in Celsius (nominal 25°C)
            humidity: Relative humidity % (nominal 80%)
            ripeness_stage: Optional hint for validation ('unripe', 'ripe', 'overripe')
            e0_factor: Multiplier on E₀ (e.g. sensitivity / stress tests)
            k_factor: Multiplier on k (rate constant)
            noise_scale: Multiplier on Gaussian noise σ
        """
        # Normalize fruit type
        fruit_key = fruit_type.lower().strip()
        if fruit_key not in self.ETHYLENE_PARAMS:
            fruit_key = 'unknown'
            
        params = self.ETHYLENE_PARAMS[fruit_key]
        E0, k, E_max = params['E0'], params['k'], params['E_max']
        E0_eff = E0 * e0_factor
        k_eff = k * k_factor
        
        # 1. Ethylene Emission Dynamics: E(t) = E₀ * e^(kt)
        E_t = E0_eff * math.exp(k_eff * hours_since_harvest)
        E_t = min(E_t, E_max)  # Cap at physiological maximum
        
        # 2. Add Gaussian sensor noise (σ = 0.05)
        noise = np.random.normal(0, self.noise_sigma * max(0.0, noise_scale))
        
        # 3. Temperature drift effect (β = 0.15 per 10°C deviation)
        temp_drift = 1 + (self.temp_coeff * (temperature - self.nominal_temp) / 10)
        
        # 4. Humidity effect (γ = 0.05 per 20% deviation)
        humidity_effect = 1 + (self.humidity_coeff * (humidity - 80) / 20)
        
        # Apply environmental effects
        E_simulated = E_t * temp_drift * humidity_effect + noise
        E_simulated = max(0.0, min(E_simulated, E_max))  # Clamp to [0, E_max]
        
        # 5. Normalize to [0,1] for fusion (Ê(t))
        # Using E_min = E0_eff * 0.5 as baseline unripe level (tracks scaled E₀)
        E_min = E0_eff * 0.5
        E_hat = (E_simulated - E_min) / (E_max - E_min)
        E_hat = float(np.clip(E_hat, 0.0, 1.0))
        
        # 6. NIR Spectral Simulation (Kubelka-Munk theory)
        nir_data = self._simulate_nir_spectrum(fruit_key, E_hat, ripeness_stage)
        
        return ChemicalReading(
            ethylene_ppm=float(E_simulated),
            normalized_proxy=E_hat,
            brix_estimate=nir_data['brix'],
            moisture_estimate=nir_data['moisture'],
            composite_quality=nir_data['composite'],
            simulation_params={
                'fruit_type': fruit_key,
                'E0': E0,
                'E0_effective': E0_eff,
                'k': k,
                'k_effective': k_eff,
                'e0_factor': e0_factor,
                'k_factor': k_factor,
                'noise_scale': noise_scale,
                'E_max': E_max,
                'hours_since_harvest': hours_since_harvest,
                'temperature': temperature,
                'humidity': humidity,
                'noise_applied': float(noise),
                'temp_drift_factor': float(temp_drift),
                'ripening_pattern': params['pattern']
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _simulate_nir_spectrum(self, fruit_type: str, 
                               ripeness_proxy: float,
                               stage_hint: Optional[str] = None) -> Dict:
        """
        Simulate NIR reflectance spectra (900-1700nm)
        Based on Kubelka-Munk theory: f(R∞) = (1-R∞)² / 2R∞ = k/s
        """
        # Determine ripeness category from proxy or hint
        if stage_hint:
            stage = stage_hint.lower()
        else:
            if ripeness_proxy < 0.3:
                stage = 'unripe'
            elif ripeness_proxy < 0.7:
                stage = 'ripe'
            else:
                stage = 'overripe'
        
        # Fruit-specific NIR characteristics
        fruit_profiles = {
            'mango': {'base_brix': 8, 'max_brix': 18, 'base_moisture': 85},
            'banana': {'base_brix': 10, 'max_brix': 20, 'base_moisture': 83},
            'pineapple': {'base_brix': 9, 'max_brix': 16, 'base_moisture': 85},
            'cashew': {'base_brix': 6, 'max_brix': 12, 'base_moisture': 75},
            'cacao': {'base_brix': 4, 'max_brix': 8, 'base_moisture': 75},
            'unknown': {'base_brix': 8, 'max_brix': 15, 'base_moisture': 80}
        }
        
        profile = fruit_profiles.get(fruit_type, fruit_profiles['unknown'])
        
        if stage == 'unripe':
            brix = np.random.uniform(profile['base_brix'], 
                                    profile['base_brix'] + 3)
            moisture = np.random.uniform(profile['base_moisture'], 
                                        profile['base_moisture'] + 3)
        elif stage == 'ripe':
            brix = np.random.uniform(profile['base_brix'] + 4, 
                                    profile['max_brix'])
            moisture = np.random.uniform(profile['base_moisture'] - 5, 
                                        profile['base_moisture'])
        else:  # overripe
            brix = np.random.uniform(profile['base_brix'] + 2, 
                                    profile['base_brix'] + 5)
            moisture = np.random.uniform(profile['base_moisture'] - 10, 
                                        profile['base_moisture'] - 5)
        
        # Add spectral noise
        brix += np.random.normal(0, 0.5)
        moisture += np.random.normal(0, 1.0)
        
        # Composite quality score (weighted combination)
        # 40% Brix + 40% Moisture + 20% Inverse ripeness (fresher = higher score)
        brix_norm = (brix - profile['base_brix']) / (profile['max_brix'] - profile['base_brix'] + 1)
        moisture_norm = moisture / 100
        freshness_factor = 1 - ripeness_proxy
        
        composite = (0.4 * brix_norm) + (0.4 * moisture_norm) + (0.2 * freshness_factor)
        composite = float(np.clip(composite, 0, 1))
        
        return {
            'brix': round(float(brix), 2),
            'moisture': round(float(moisture), 2),
            'composite': composite
        }
    
    def batch_simulate(self, detections: List[Dict], 
                       base_hours: float = 24.0) -> List[ChemicalReading]:
        """Simulate chemical data for multiple detections"""
        results = []
        for det in detections:
            fruit = det.get('fruit_type', 'unknown').lower()
            # Add variation in hours for each fruit (simulating batch variation)
            hours = base_hours + np.random.uniform(-6, 6)
            result = self.simulate(fruit, hours)
            results.append(result)
        return results


# For import compatibility
create_chemical_simulator = ChemicalSimulator