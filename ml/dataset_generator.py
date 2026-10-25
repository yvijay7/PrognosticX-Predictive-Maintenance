"""
PrognosticX - Industrial Sensor Dataset Generator
Generates realistic run-to-failure and operational sensor telemetry based on
industrial predictive maintenance benchmarks (NASA C-MAPSS / AI4I 2020).
Parameters:
- Temperature (°C)
- Vibration (mm/s RMS)
- Rotational Speed / RPM
- Pressure (bar)
- Load (%)
- Operating Hours / Tool Wear
- Fault Class (0: Normal, 1: Thermal Overload, 2: High Vibration / Bearing Fault, 3: Gearbox Wear, 4: Electrical Imbalance)
- RUL (Remaining Useful Life in hours)
"""

import os
import csv
import math
import random

def generate_industrial_dataset(output_path: str, num_samples: int = 1200):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)
    
    headers = [
        "timestamp_hours",
        "machine_id",
        "temperature_c",
        "vibration_rms",
        "rpm",
        "pressure_bar",
        "load_pct",
        "operating_hours",
        "fault_class",
        "fault_name",
        "rul_hours",
        "health_score"
    ]
    
    rows = []
    
    # 6 simulated machines with degradation cycles
    machines = ["Machine-Alpha", "Machine-Beta", "Machine-Gamma", "Machine-Delta", "Machine-Epsilon", "Machine-Zeta"]
    
    for machine in machines:
        current_hours = random.randint(100, 500)
        total_lifespan = random.randint(2500, 3200)
        
        samples_per_machine = num_samples // len(machines)
        for step in range(samples_per_machine):
            current_hours += random.uniform(1.5, 4.0)
            degradation_ratio = min(1.0, current_hours / total_lifespan)
            
            # Base physics metrics
            base_rpm = 1450 + random.gauss(0, 15)
            base_load = 65 + 15 * math.sin(step / 20.0) + random.gauss(0, 3)
            base_pressure = 4.2 + (base_load / 100.0) * 0.8 + random.gauss(0, 0.1)
            base_temp = 48.0 + (base_load / 100.0) * 22.0 + (degradation_ratio ** 1.8) * 25.0 + random.gauss(0, 1.2)
            base_vibration = 1.8 + (base_rpm / 1500.0) * 0.8 + (degradation_ratio ** 2.2) * 4.5 + random.gauss(0, 0.15)
            
            # Inject intermittent failure modes
            fault_class = 0
            fault_name = "Normal Operation"
            
            # Severe degradation or stress triggers
            rand_anomaly = random.random()
            if degradation_ratio > 0.85 or (step % 45 == 0 and step > 10):
                if rand_anomaly < 0.35 or base_temp > 78:
                    fault_class = 1
                    fault_name = "Thermal Overload"
                    base_temp += random.uniform(14, 25)
                    base_load += random.uniform(10, 20)
                elif rand_anomaly < 0.65 or base_vibration > 4.8:
                    fault_class = 2
                    fault_name = "Bearing Fault"
                    base_vibration += random.uniform(2.5, 5.0)
                    base_rpm += random.uniform(-100, -40)
                elif rand_anomaly < 0.85:
                    fault_class = 3
                    fault_name = "Gearbox Wear"
                    base_vibration += random.uniform(1.8, 3.5)
                    base_pressure += random.uniform(1.2, 2.5)
                else:
                    fault_class = 4
                    fault_name = "Electrical Imbalance"
                    base_rpm += random.uniform(80, 180)
                    base_load += random.uniform(8, 16)
            
            # Cap realistic ranges
            temp_c = round(max(25.0, min(115.0, base_temp)), 2)
            vib_rms = round(max(0.4, min(12.0, base_vibration)), 2)
            rpm = round(max(900.0, min(2200.0, base_rpm)), 1)
            press = round(max(1.5, min(8.5, base_pressure)), 2)
            load = round(max(20.0, min(100.0, base_load)), 1)
            op_hours = round(current_hours, 1)
            
            # Remaining Useful Life calculation
            # Inversely correlated with degradation, temperature, and vibration
            stress_penalty = max(0, (temp_c - 65) * 1.5) + max(0, (vib_rms - 3.5) * 15.0) + max(0, (load - 80) * 1.2)
            true_rul = max(0.0, (total_lifespan - current_hours) - stress_penalty * 2.5)
            true_rul = round(true_rul, 1)
            
            # Health Score (0 - 100)
            health = 100.0 - (degradation_ratio * 45.0) - (stress_penalty * 0.85)
            if fault_class > 0:
                health -= random.uniform(15, 30)
            health = round(max(5.0, min(99.0, health)), 1)
            
            rows.append([
                round(step * 2.0, 1),
                machine,
                temp_c,
                vib_rms,
                rpm,
                press,
                load,
                op_hours,
                fault_class,
                fault_name,
                true_rul,
                health
            ])
            
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} industrial sensor records at {output_path}")

if __name__ == "__main__":
    target = os.path.join(os.path.dirname(__file__), "data", "machine_sensor_dataset.csv")
    generate_industrial_dataset(target)
