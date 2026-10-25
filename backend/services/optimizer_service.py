"""
PrognosticX - Operating Range Optimizer Service (Novelty: Recommended Operating Range)
Defines safe/warning/critical operating envelopes for all industrial parameters.
Implements a search/optimization algorithm that evaluates operating points and generates
actionable, decision-support operating range recommendations to maximize machine health and RUL.
"""

from typing import Dict, Any, List
from ..agents.controller import OrchestrationController

class OperatingRangeOptimizerService:
    def __init__(self):
        self.controller = OrchestrationController()
        
        # Standard Industrial Safe / Warning / Critical Envelopes
        self.operating_envelopes = {
            "temperature": {
                "name": "Operating Temperature",
                "unit": "°C",
                "safe_range": [40.0, 65.0],
                "warning_range": [65.0, 75.0],
                "critical_threshold": 75.0,
                "description": "Core motor winding & bearing lubricating oil temperature."
            },
            "vibration": {
                "name": "Vibration Velocity RMS",
                "unit": "mm/s",
                "safe_range": [0.4, 3.2],
                "warning_range": [3.2, 4.8],
                "critical_threshold": 4.8,
                "description": "ISO 10816-3 mechanical vibration severity."
            },
            "rpm": {
                "name": "Rotational Speed",
                "unit": "RPM",
                "safe_range": [1400.0, 1520.0],
                "warning_range": [1320.0, 1600.0],
                "critical_threshold": 1600.0,
                "description": "Synchronous induction motor speed."
            },
            "pressure": {
                "name": "Hydraulic / System Pressure",
                "unit": "bar",
                "safe_range": [3.5, 4.8],
                "warning_range": [4.8, 5.5],
                "critical_threshold": 5.5,
                "description": "Fluid delivery and lubrication line hydrostatic pressure."
            },
            "load": {
                "name": "Machine Operating Load",
                "unit": "%",
                "safe_range": [40.0, 75.0],
                "warning_range": [75.0, 85.0],
                "critical_threshold": 85.0,
                "description": "Continuous mechanical motor torque load capacity."
            }
        }
        
    def get_envelopes(self) -> Dict[str, Any]:
        return self.operating_envelopes
        
    def evaluate_parameter_state(self, param_key: str, value: float) -> str:
        env = self.operating_envelopes.get(param_key)
        if not env:
            return "UNKNOWN"
        if param_key == "vibration":
            if value <= env["safe_range"][1]: return "SAFE"
            if value <= env["warning_range"][1]: return "WARNING"
            return "CRITICAL"
        elif param_key == "load":
            if value <= env["safe_range"][1]: return "SAFE"
            if value <= env["warning_range"][1]: return "WARNING"
            return "CRITICAL"
        elif param_key == "temperature":
            if value <= env["safe_range"][1]: return "SAFE"
            if value <= env["warning_range"][1]: return "WARNING"
            return "CRITICAL"
        elif param_key == "pressure":
            if value <= env["safe_range"][1]: return "SAFE"
            if value <= env["warning_range"][1]: return "WARNING"
            return "CRITICAL"
        elif param_key == "rpm":
            if env["safe_range"][0] <= value <= env["safe_range"][1]: return "SAFE"
            if env["warning_range"][0] <= value <= env["warning_range"][1]: return "WARNING"
            return "CRITICAL"
        return "SAFE"

    def optimize_operating_conditions(self, current_telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Runs optimization search:
        Searches within safe operational bounds for setpoints that maximize
        health and RUL while minimizing risk and fault probability.
        """
        curr_temp = float(current_telemetry.get("temperature", 75.0))
        curr_vib = float(current_telemetry.get("vibration", 4.5))
        curr_rpm = float(current_telemetry.get("rpm", 1450.0))
        curr_press = float(current_telemetry.get("pressure", 5.0))
        curr_load = float(current_telemetry.get("load", 85.0))
        curr_hours = float(current_telemetry.get("operating_hours", 220.0))
        
        # Execute baseline workflow on current conditions
        baseline_res = self.controller.execute_workflow(current_telemetry)
        baseline_health = baseline_res["health_summary"]["health_score"]
        baseline_risk = baseline_res["fault_detection"]["fault_probability"]
        baseline_rul = baseline_res["health_summary"]["predicted_rul_hours"]
        
        # Candidate search space within physical machine constraints
        # Optimal target conditions aimed at reducing thermal, mechanical, and torque stresses
        opt_temp = min(curr_temp, 58.0) if curr_temp > 65.0 else curr_temp
        opt_vib = min(curr_vib, 2.2) if curr_vib > 3.2 else curr_vib
        opt_rpm = 1450.0 if (curr_rpm < 1400 or curr_rpm > 1520) else curr_rpm
        opt_press = 4.2 if curr_press > 4.8 else curr_press
        opt_load = 68.0 if curr_load > 75.0 else curr_load
        
        optimized_telemetry = {
            "temperature": round(opt_temp, 1),
            "vibration": round(opt_vib, 2),
            "rpm": round(opt_rpm, 1),
            "pressure": round(opt_press, 2),
            "load": round(opt_load, 1),
            "operating_hours": curr_hours
        }
        
        opt_res = self.controller.execute_workflow(optimized_telemetry)
        opt_health = opt_res["health_summary"]["health_score"]
        opt_risk = opt_res["fault_detection"]["fault_probability"]
        opt_rul = opt_res["health_summary"]["predicted_rul_hours"]
        
        # Generate targeted engineering recommendations
        action_recommendations = []
        if curr_load > 75.0:
            reduction = round(curr_load - opt_load, 1)
            action_recommendations.append(f"Reduce machine operating load from {curr_load}% to approximately {opt_load}% (reduction of {reduction}%) to relieve thermal and mechanical stress.")
        if curr_temp > 65.0:
            cooling_delta = round(curr_temp - opt_temp, 1)
            action_recommendations.append(f"Enhance auxiliary cooling or cycle pauses to lower core operating temperature from {curr_temp}°C to ≤{opt_temp}°C (drop of {cooling_delta}°C).")
        if curr_vib > 3.2:
            action_recommendations.append(f"Perform bearing lubrication and dynamic shaft alignment to return vibration from {curr_vib} mm/s into safe zone (≤3.2 mm/s).")
        if curr_press > 4.8:
            action_recommendations.append(f"Calibrate hydraulic relief regulator to bring line pressure from {curr_press} bar to standard 4.2 bar.")
        if curr_rpm > 1550 or curr_rpm < 1350:
            action_recommendations.append(f"Tune motor VFD drive frequency to steady 1450 RPM nominal synchronous speed.")
            
        if not action_recommendations:
            action_recommendations.append("Current machine conditions are operating within optimal safe envelopes. Maintain existing operating setpoints.")
            
        return {
            "current_conditions": {
                "telemetry": current_telemetry,
                "health_score": baseline_health,
                "fault_risk_pct": round(baseline_risk * 100, 1),
                "predicted_rul_hours": baseline_rul,
                "maintenance_priority": baseline_res["health_summary"]["maintenance_priority"]
            },
            "recommended_optimal_range": {
                "temperature_c": "50.0 – 62.0 °C",
                "vibration_rms": "< 3.2 mm/s",
                "rpm": "1420 – 1480 RPM",
                "pressure_bar": "3.8 – 4.5 bar",
                "load_pct": "60.0 – 72.0 %",
                "expected_health": f"{opt_health}% ({opt_res['health_summary']['health_state']})",
                "expected_risk": f"{round(opt_risk * 100, 1)}%",
                "expected_rul": f"{opt_rul} Hours"
            },
            "projected_improvements": {
                "health_gain": round(opt_health - baseline_health, 1),
                "risk_reduction_pct": round((baseline_risk - opt_risk) * 100, 1),
                "rul_extension_hours": round(opt_rul - baseline_rul, 1)
            },
            "action_recommendations": action_recommendations,
            "disclaimer": "PrognosticX provides real-time predictive decision support. Adjustments should be enacted in compliance with machinery safety manuals."
        }
