"""
PrognosticX - Remaining Useful Life (RUL) Prediction Agent
Estimates equipment remaining lifespan, non-linear degradation trajectories,
estimated time to critical condition, and machine health score (0-100).
"""

from typing import Dict, Any

class RULPredictionAgent:
    def __init__(self, design_lifespan: float = 3000.0):
        self.agent_name = "RUL Prediction Agent"
        self.design_lifespan = design_lifespan
        
    def estimate(self, sensor_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Input: sensor readings
        Output: predicted RUL, degradation curve, time to critical, health score
        """
        temp = float(sensor_data.get("temperature", 55.0))
        vib = float(sensor_data.get("vibration", 1.8))
        rpm = float(sensor_data.get("rpm", 1450.0))
        press = float(sensor_data.get("pressure", 4.2))
        load = float(sensor_data.get("load", 65.0))
        hours = float(sensor_data.get("operating_hours", 200.0))
        
        # 1. Physics-based Stress Acceleration Factor (Arrhenius & Vibration Power Law)
        # Temp reference: 60°C; Vibration reference: 2.5 mm/s; Load reference: 70%
        thermal_stress = max(0.0, (temp - 60.0) / 10.0) ** 1.35
        vibration_stress = max(0.0, (vib - 2.5) / 1.0) ** 1.45
        load_stress = max(0.0, (load - 70.0) / 15.0) ** 1.20
        pressure_stress = max(0.0, (press - 4.5) / 1.5) ** 1.10
        
        acceleration_factor = 1.0 + (thermal_stress * 0.9) + (vibration_stress * 1.4) + (load_stress * 0.6) + (pressure_stress * 0.4)
        
        # 2. Base remaining life from operating hours
        base_life_remaining = max(10.0, self.design_lifespan - hours)
        
        # 3. Dynamic RUL in operating hours
        predicted_rul = round(max(0.0, base_life_remaining / acceleration_factor), 1)
        
        # 4. Estimated Time to Critical Condition (RUL threshold where health drops to critical < 25%)
        # Critical condition typically occurs when remaining safe margin is depleted (~15-25% of active RUL)
        if acceleration_factor > 2.5:
            time_to_critical = round(max(2.0, predicted_rul * 0.22), 1)
        elif acceleration_factor > 1.5:
            time_to_critical = round(max(10.0, predicted_rul * 0.35), 1)
        else:
            time_to_critical = round(max(24.0, predicted_rul * 0.50), 1)
            
        # 5. Health Score Calculation (0 - 100)
        # Derived from: 100 - (Operational Wear + Environmental Stress Penalties)
        wear_penalty = min(40.0, (hours / self.design_lifespan) * 40.0)
        stress_penalty = min(60.0, (acceleration_factor - 1.0) * 22.0)
        health_score = round(max(0.0, min(100.0, 100.0 - wear_penalty - stress_penalty)), 1)
        
        # 6. Health State Classification
        if health_score >= 90:
            health_state = "Excellent"
            health_color = "emerald"
        elif health_score >= 75:
            health_state = "Good"
            health_color = "green"
        elif health_score >= 50:
            health_state = "Warning"
            health_color = "amber"
        elif health_score >= 25:
            health_state = "Critical"
            health_color = "orange"
        else:
            health_state = "Severe"
            health_color = "rose"
            
        # 7. Projected degradation trend over next 5 inspection checkpoints
        trend_points = []
        curr_health = health_score
        curr_hours = 0
        step_hours = max(10.0, round(predicted_rul / 5.0, 1))
        for step in range(6):
            trend_points.append({
                "future_hours": round(curr_hours, 1),
                "predicted_health": round(curr_health, 1)
            })
            curr_hours += step_hours
            curr_health = max(0.0, curr_health - (curr_health * 0.18 * (acceleration_factor / 1.5)))
            
        return {
            "agent": self.agent_name,
            "predicted_rul_hours": predicted_rul,
            "time_to_critical_hours": time_to_critical,
            "health_score": health_score,
            "health_state": health_state,
            "health_color": health_color,
            "acceleration_factor": round(acceleration_factor, 2),
            "degradation_trend": trend_points,
            "confidence_band": {
                "lower_bound_rul": round(max(0, predicted_rul * 0.88), 1),
                "upper_bound_rul": round(predicted_rul * 1.12, 1)
            }
        }
