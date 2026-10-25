"""
PrognosticX - Fault Detection Agent
Analyzes real-time and simulated multi-sensor telemetry to classify anomalies,
detect machine faults, compute fault probability, and determine contributing sensor metrics.
"""

from typing import Dict, Any, List

class FaultDetectionAgent:
    def __init__(self):
        self.agent_name = "Fault Detection Agent"
        self.classes = [
            "Normal Operation",
            "Thermal Overload",
            "Bearing Fault",
            "Gearbox Wear",
            "Electrical Imbalance"
        ]
        
    def analyze(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Input: sensor readings {temperature, vibration, rpm, pressure, load, hours}
        Output: structured fault detection insight
        """
        temp = float(sensor_data.get("temperature", 55.0))
        vib = float(sensor_data.get("vibration", 1.8))
        rpm = float(sensor_data.get("rpm", 1450.0))
        press = float(sensor_data.get("pressure", 4.2))
        load = float(sensor_data.get("load", 65.0))
        hours = float(sensor_data.get("operating_hours", 200.0))
        
        # Physics-informed multi-class scoring
        scores = [0.0] * 5
        contributing = []
        
        # 0. Normal
        if temp < 65.0 and vib < 3.2 and 1380 <= rpm <= 1550 and press < 4.8 and load < 75.0:
            scores[0] = 0.96
        else:
            penalty = (max(0, temp - 65) * 0.02) + (max(0, vib - 3.2) * 0.12) + (max(0, load - 75) * 0.015)
            scores[0] = max(0.04, 0.90 - penalty)
            
        # 1. Thermal Overload
        if temp >= 75.0:
            scores[1] = min(0.98, 0.65 + (temp - 75.0) * 0.018)
            contributing.append(f"High Temperature ({temp:.1f}°C > 75°C threshold)")
        elif temp >= 68.0 and load >= 80.0:
            scores[1] = 0.55 + (temp - 68.0) * 0.02 + (load - 80.0) * 0.008
            contributing.append(f"Elevated Temperature with high Load ({load:.1f}%)")
            
        # 2. Bearing Fault
        if vib >= 4.5:
            scores[2] = min(0.99, 0.70 + (vib - 4.5) * 0.08)
            contributing.append(f"Severe Vibration RMS ({vib:.2f} mm/s > 4.5 mm/s limit)")
        elif vib >= 3.5:
            scores[2] = 0.45 + (vib - 3.5) * 0.20
            contributing.append(f"Vibration warning drift ({vib:.2f} mm/s)")
            
        # 3. Gearbox Wear
        if press >= 5.2 and vib >= 3.0:
            scores[3] = min(0.95, 0.52 + (press - 5.2) * 0.12 + (vib - 3.0) * 0.08)
            contributing.append(f"Hydraulic pressure surge ({press:.2f} bar) coupled with vibration")
            
        # 4. Electrical Imbalance
        if rpm > 1580 or (rpm < 1320 and vib < 4.0):
            scores[4] = min(0.94, 0.50 + abs(rpm - 1450) * 0.002)
            contributing.append(f"RPM fluctuation outside 1380-1550 window ({rpm:.1f} RPM)")
            
        max_idx = scores.index(max(scores))
        confidence = round(scores[max_idx], 3)
        fault_name = self.classes[max_idx]
        is_fault = (max_idx != 0)
        
        # Severity calculation
        if not is_fault:
            severity = "NORMAL"
        elif confidence > 0.80 or temp > 85 or vib > 5.5:
            severity = "CRITICAL"
        elif confidence > 0.55:
            severity = "HIGH"
        else:
            severity = "MEDIUM"
            
        # Explainability feature importance ranking
        factors = []
        if temp > 65: factors.append({"feature": "Temperature", "value": f"{temp}°C", "impact": "High"})
        if vib > 3.2: factors.append({"feature": "Vibration", "value": f"{vib} mm/s", "impact": "High"})
        if load > 75: factors.append({"feature": "Load", "value": f"{load}%", "impact": "Medium"})
        if press > 4.8: factors.append({"feature": "Pressure", "value": f"{press} bar", "impact": "Medium"})
        if rpm < 1350 or rpm > 1550: factors.append({"feature": "RPM", "value": f"{rpm} rpm", "impact": "Low"})
        
        return {
            "agent": self.agent_name,
            "is_fault": is_fault,
            "fault_class": max_idx,
            "fault_name": fault_name,
            "confidence": confidence,
            "fault_probability": round((1.0 - scores[0]) if is_fault else (1.0 - confidence), 3),
            "severity": severity,
            "contributing_reasons": contributing if contributing else ["All parameters within safe industrial thresholds"],
            "feature_attribution": factors
        }
