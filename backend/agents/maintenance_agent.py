"""
PrognosticX - Maintenance Planning Agent
Integrates Fault Detection and RUL predictions to compute transparent maintenance priority score (0-100),
generate actionable work orders, prescribe maintenance windows, and enforce confidence-aware policies.
"""

from typing import Dict, Any, List

class MaintenancePlanningAgent:
    def __init__(self):
        self.agent_name = "Maintenance Planning Agent"
        
    def plan(self, 
             fault_result: Dict[str, Any], 
             rul_result: Dict[str, Any], 
             machine_criticality: str = "HIGH") -> Dict[str, Any]:
        """
        Calculates 0-100 Priority Score based on:
        - Fault Severity (weight: 35%)
        - RUL Depletion / Risk (weight: 25%)
        - Health Score Deficit (weight: 20%)
        - Machine Criticality (weight: 20%)
        """
        is_fault = fault_result.get("is_fault", False)
        fault_name = fault_result.get("fault_name", "Normal Operation")
        severity = fault_result.get("severity", "NORMAL")
        confidence = fault_result.get("confidence", 0.90)
        
        rul_hours = rul_result.get("predicted_rul_hours", 2000.0)
        time_to_critical = rul_result.get("time_to_critical_hours", 500.0)
        health_score = rul_result.get("health_score", 90.0)
        
        # 1. Fault Severity Factor (0 - 35 points)
        if severity == "CRITICAL":
            fault_pts = 35.0
        elif severity == "HIGH":
            fault_pts = 26.0
        elif severity == "MEDIUM":
            fault_pts = 16.0
        else:
            fault_pts = 4.0
            
        # 2. RUL Risk Factor (0 - 25 points)
        if rul_hours < 100 or time_to_critical < 24:
            rul_pts = 25.0
        elif rul_hours < 350 or time_to_critical < 72:
            rul_pts = 18.0
        elif rul_hours < 800:
            rul_pts = 11.0
        else:
            rul_pts = 3.0
            
        # 3. Health Score Deficit (0 - 20 points)
        # Higher score deficit -> higher priority
        health_deficit = max(0.0, 100.0 - health_score)
        health_pts = min(20.0, (health_deficit / 100.0) * 20.0)
        
        # 4. Machine Criticality Factor (0 - 20 points)
        crit_map = {"CRITICAL": 20.0, "HIGH": 15.0, "MEDIUM": 10.0, "LOW": 5.0}
        crit_pts = crit_map.get(machine_criticality.upper(), 15.0)
        
        # Total Priority Score (0 - 100)
        raw_score = fault_pts + rul_pts + health_pts + crit_pts
        priority_score = round(max(0.0, min(100.0, raw_score)), 1)
        
        # Priority Tier
        if priority_score >= 81:
            priority_tier = "CRITICAL"
            badge_color = "red"
            suggested_window = "Immediate shutdown / Within 4 Hours"
        elif priority_score >= 61:
            priority_tier = "HIGH"
            badge_color = "amber"
            suggested_window = "Within 12 - 24 Hours (Next Shift)"
        elif priority_score >= 31:
            priority_tier = "MEDIUM"
            badge_color = "blue"
            suggested_window = "Within 3 - 5 Days"
        else:
            priority_tier = "LOW"
            badge_color = "green"
            suggested_window = "Next Scheduled Routine Maintenance"
            
        # Recommendations & Actionable Guidance based on identified fault & stresses
        checklist = []
        if fault_name == "Bearing Fault":
            action = "Inspect radial bearing raceway, check lubrication oil viscosity, and test vibration harmonics."
            reason = f"Bearing fault signature detected with elevated vibration. Time to critical condition estimated at {time_to_critical}h."
            checklist = ["Check bearing housing temperature", "Inspect lubrication grease for metal particulates", "Verify shaft alignment with laser tool", "Check foundation mounting bolt torque"]
        elif fault_name == "Thermal Overload":
            action = "Reduce machine load to <70%, inspect heat exchanger cooling fan and radiator fins."
            reason = f"Thermal overload pattern detected. High core temperature accelerating thermal degradation."
            checklist = ["Inspect coolant fluid levels and pump pressure", "Clear dust accumulation from ventilation vents", "Verify motor winding resistance", "Inspect ambient ventilation"]
        elif fault_name == "Gearbox Wear":
            action = "Perform gearbox oil flush, inspect gear teeth backlash and hydraulic pressure regulator."
            reason = f"Gearbox wear detected with hydraulic pressure surge and acoustic vibration harmonics."
            checklist = ["Check gear tooth wear and pitting", "Replace gear lube filter element", "Inspect drive coupling elastomer", "Verify pressure relief valve calibration"]
        elif fault_name == "Electrical Imbalance":
            action = "Inspect 3-phase supply voltage balance, motor inverter VFD drive parameters, and rotor windings."
            reason = f"Rotational speed instability and electrical load imbalance detected."
            checklist = ["Measure 3-phase current balance (<5% deviation)", "Inspect VFD inverter pulse width modulation", "Check slip rings and carbon brushes", "Verify ground fault integrity"]
        else:
            action = "Continue normal operations. Routine automated sensor logging and monitoring active."
            reason = f"All telemetry metrics within normal operational bounds. Machine Health is {health_score}%."
            checklist = ["Verify sensor connectivity", "Routine visual inspection of machine exterior", "Confirm oil level dipstick"]
            
        # 5. Confidence-Aware Decision Protocol
        if confidence >= 0.85:
            decision_policy = "AUTOMATIC_RECOMMENDATION_APPROVED"
            policy_desc = f"High model confidence ({confidence*100:.1f}%). System automated maintenance order generation permitted."
        elif confidence >= 0.60:
            decision_policy = "HUMAN_VERIFICATION_REQUIRED"
            policy_desc = f"Moderate model confidence ({confidence*100:.1f}%). Recommend on-site technician physical verification before stoppage."
        else:
            decision_policy = "ADDITIONAL_TELEMETRY_REQUESTED"
            policy_desc = f"Low model confidence ({confidence*100:.1f}%). Supplemental vibration spectrum analysis and historical log replay recommended."
            
        return {
            "agent": self.agent_name,
            "priority": priority_tier,
            "priority_score": priority_score,
            "badge_color": badge_color,
            "suggested_maintenance_window": suggested_window,
            "recommended_action": action,
            "primary_reason": reason,
            "inspection_checklist": checklist,
            "score_breakdown": {
                "fault_severity_points": fault_pts,
                "rul_risk_points": rul_pts,
                "health_deficit_points": round(health_pts, 1),
                "criticality_points": crit_pts
            },
            "confidence_policy": {
                "level": decision_policy,
                "description": policy_desc,
                "confidence_score": confidence
            }
        }
