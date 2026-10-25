"""
PrognosticX - Simulation Service (Novelty: Machine Health Simulator & What-If Engine)
Allows operators to simulate parameter deviations (Temp, Vibration, RPM, Pressure, Load, Hours)
and immediately computes the impact on Health Score, Fault Probability, RUL, and Priority.
Computes parameter sensitivity and provides side-by-side Before/After evaluation.
"""

from typing import Dict, Any
from ..agents.controller import OrchestrationController

class SimulationService:
    def __init__(self):
        self.controller = OrchestrationController()
        
        # Predefined Industrial Operating Scenarios
        self.scenarios = {
            "normal": {
                "name": "Normal Operation",
                "description": "Balanced industrial nominal state with normal load and cooling.",
                "telemetry": {"temperature": 54.0, "vibration": 1.7, "rpm": 1450.0, "pressure": 4.2, "load": 62.0, "operating_hours": 210.0}
            },
            "overheating": {
                "name": "Overheating / Cooling Impairment",
                "description": "Cooling pump failure or radiator blockage causing severe heat rise.",
                "telemetry": {"temperature": 86.5, "vibration": 2.9, "rpm": 1420.0, "pressure": 4.8, "load": 92.0, "operating_hours": 235.0}
            },
            "high_vibration": {
                "name": "High Vibration / Shaft Misalignment",
                "description": "Coupling imbalance or mechanical looseness generating excessive vibration.",
                "telemetry": {"temperature": 62.0, "vibration": 6.8, "rpm": 1360.0, "pressure": 4.4, "load": 74.0, "operating_hours": 240.0}
            },
            "overload": {
                "name": "Heavy Operational Overload",
                "description": "Excessive mechanical feed-rate pushing motor beyond rated continuous load.",
                "telemetry": {"temperature": 79.0, "vibration": 3.8, "rpm": 1390.0, "pressure": 5.8, "load": 98.0, "operating_hours": 260.0}
            },
            "bearing_degradation": {
                "name": "Bearing Spalling Degradation",
                "description": "Fatigue spalling on the inner raceway with high frequency vibration harmonics.",
                "telemetry": {"temperature": 68.0, "vibration": 7.9, "rpm": 1310.0, "pressure": 4.5, "load": 75.0, "operating_hours": 280.0}
            },
            "electrical_imbalance": {
                "name": "Electrical VFD Voltage Imbalance",
                "description": "Harmonic distortion and phase asymmetry causing erratic RPM fluctuations.",
                "telemetry": {"temperature": 64.0, "vibration": 2.3, "rpm": 1640.0, "pressure": 4.3, "load": 88.0, "operating_hours": 250.0}
            }
        }
        
    def get_preset_scenario(self, scenario_key: str) -> Dict[str, Any]:
        return self.scenarios.get(scenario_key.lower(), self.scenarios["normal"])
        
    def run_what_if_simulation(self, current_telemetry: Dict[str, float], simulated_telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Executes actual ML pipeline on both current and simulated conditions,
        generating a side-by-side comparison and parameter sensitivity breakdown.
        """
        curr_res = self.controller.execute_workflow(current_telemetry)
        sim_res = self.controller.execute_workflow(simulated_telemetry)
        
        curr_health = curr_res["health_summary"]["health_score"]
        sim_health = sim_res["health_summary"]["health_score"]
        health_delta = round(sim_health - curr_health, 1)
        
        curr_rul = curr_res["health_summary"]["predicted_rul_hours"]
        sim_rul = sim_res["health_summary"]["predicted_rul_hours"]
        rul_delta = round(sim_rul - curr_rul, 1)
        
        curr_risk = round(curr_res["fault_detection"]["fault_probability"] * 100, 1)
        sim_risk = round(sim_res["fault_detection"]["fault_probability"] * 100, 1)
        risk_delta = round(sim_risk - curr_risk, 1)
        
        # Calculate Parameter Sensitivities (which modified parameter drove the change most)
        sensitivities = []
        param_labels = {
            "temperature": ("Temperature", "°C", 1.2),
            "vibration": ("Vibration", "mm/s", 8.5),
            "load": ("Load", "%", 0.6),
            "pressure": ("Pressure", "bar", 3.0),
            "rpm": ("Rotational Speed", "RPM", 0.05)
        }
        
        for p_key, (label, unit, weight) in param_labels.items():
            c_val = float(current_telemetry.get(p_key, 0.0))
            s_val = float(simulated_telemetry.get(p_key, 0.0))
            diff = s_val - c_val
            if abs(diff) > 0.01:
                # Contribution to health change: negative diff in stress improves health
                impact_score = -1.0 * diff * weight
                sensitivities.append({
                    "parameter": label,
                    "unit": unit,
                    "current": c_val,
                    "simulated": s_val,
                    "delta": round(diff, 2),
                    "impact_direction": "IMPROVEMENT" if impact_score > 0 else "DEGRADATION",
                    "estimated_impact_points": round(abs(impact_score), 1)
                })
                
        # Sort by impact points descending
        sensitivities.sort(key=lambda x: x["estimated_impact_points"], reverse=True)
        
        return {
            "comparison": {
                "before": {
                    "health_score": curr_health,
                    "health_state": curr_res["health_summary"]["health_state"],
                    "fault_risk_pct": curr_risk,
                    "fault_name": curr_res["health_summary"]["fault_name"],
                    "rul_hours": curr_rul,
                    "time_to_critical_hours": curr_res["health_summary"]["time_to_critical_hours"],
                    "maintenance_priority": curr_res["health_summary"]["maintenance_priority"]
                },
                "after": {
                    "health_score": sim_health,
                    "health_state": sim_res["health_summary"]["health_state"],
                    "fault_risk_pct": sim_risk,
                    "fault_name": sim_res["health_summary"]["fault_name"],
                    "rul_hours": sim_rul,
                    "time_to_critical_hours": sim_res["health_summary"]["time_to_critical_hours"],
                    "maintenance_priority": sim_res["health_summary"]["maintenance_priority"]
                },
                "delta": {
                    "health_score_delta": health_delta,
                    "rul_hours_delta": rul_delta,
                    "fault_risk_delta": risk_delta,
                    "net_assessment": "OVERALL IMPROVEMENT" if health_delta > 0 else ("NO CHANGE" if health_delta == 0 else "DEGRADATION DETECTED")
                }
            },
            "parameter_sensitivities": sensitivities,
            "simulated_full_results": sim_res
        }
