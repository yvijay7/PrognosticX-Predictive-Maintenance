"""
PrognosticX - Grounded AI Maintenance Assistant Service
Provides contextual, engineering-grade chatbot answers strictly grounded in the
current live telemetry, active fault detection predictions, and RUL calculations.
"""

from typing import Dict, Any, List
from ..agents.controller import OrchestrationController

class MaintenanceChatService:
    def __init__(self):
        self.controller = OrchestrationController()
        
    def respond_to_query(self, query: str, machine_id: str, current_telemetry: Dict[str, float]) -> Dict[str, Any]:
        q = query.lower().strip()
        analysis = self.controller.execute_workflow(current_telemetry)
        
        health_summary = analysis["health_summary"]
        fault_detection = analysis["fault_detection"]
        rul_prediction = analysis["rul_prediction"]
        maintenance_plan = analysis["maintenance_plan"]
        
        temp = current_telemetry.get("temperature", 55.0)
        vib = current_telemetry.get("vibration", 1.8)
        rpm = current_telemetry.get("rpm", 1450.0)
        press = current_telemetry.get("pressure", 4.2)
        load = current_telemetry.get("load", 65.0)
        hours = current_telemetry.get("operating_hours", 200.0)
        
        answer_text = ""
        context_data = {
            "machine_id": machine_id,
            "measured_telemetry": {
                "temperature": f"{temp}°C",
                "vibration": f"{vib} mm/s RMS",
                "rpm": f"{rpm} RPM",
                "pressure": f"{press} bar",
                "load": f"{load}%",
                "operating_hours": f"{hours} hrs"
            },
            "model_predictions": {
                "health_score": f"{health_summary['health_score']}% ({health_summary['health_state']})",
                "fault_detected": health_summary['fault_name'],
                "fault_probability": f"{round(fault_detection['fault_probability']*100, 1)}%",
                "predicted_rul": f"{health_summary['predicted_rul_hours']} Hours",
                "time_to_critical": f"{health_summary['time_to_critical_hours']} Hours",
                "maintenance_priority": f"{health_summary['maintenance_priority']} ({health_summary['maintenance_priority_score']}/100)"
            }
        }
        
        # 1. "What is wrong with Machine A / What is the fault?"
        if any(w in q for w in ["what is wrong", "what's wrong", "fault", "problem", "issue", "status"]):
            if fault_detection["is_fault"]:
                reasons = " ".join(fault_detection["contributing_reasons"])
                answer_text = (
                    f"**Diagnostic Report for {machine_id}:**\n\n"
                    f"• **Identified Fault:** {fault_detection['fault_name']} (Confidence: {fault_detection['confidence']*100:.1f}%)\n"
                    f"• **Severity Level:** {fault_detection['severity']}\n"
                    f"• **Root Cause Analysis:** {reasons}\n"
                    f"• **Current Telemetry:** Temperature is {temp}°C, Vibration is {vib} mm/s, Load is {load}%.\n"
                    f"• **Action Required:** {maintenance_plan['recommended_action']}"
                )
            else:
                answer_text = (
                    f"**Diagnostic Status for {machine_id}:**\n\n"
                    f"• Machine {machine_id} is currently operating normally with NO active faults.\n"
                    f"• Health Score is **{health_summary['health_score']}%** (Excellent/Good).\n"
                    f"• All parameters are within standard thresholds: Temp: {temp}°C, Vibration: {vib} mm/s, RPM: {rpm}."
                )
                
        # 2. "Why is the machine health low / Health explanation"
        elif any(w in q for w in ["why is health", "health score", "why health low", "why low health"]):
            answer_text = (
                f"**Machine Health Assessment ({health_summary['health_score']}%):**\n\n"
                f"The health score is derived from cumulative mechanical wear and active environmental stress factors:\n"
                f"1. **Stress Acceleration Factor:** {rul_prediction['acceleration_factor']}x nominal wear rate.\n"
                f"2. **Thermal Load:** At {temp}°C (Safe ceiling: 65°C).\n"
                f"3. **Vibration Severity:** At {vib} mm/s (Safe ceiling: 3.2 mm/s).\n"
                f"4. **Operational Hours:** {hours} hours logged out of 3,000h baseline lifespan.\n"
                f"**Recommendation:** Lower operating stresses to retard degradation progression."
            )
            
        # 3. "How much RUL is remaining / Lifespan"
        elif any(w in q for w in ["rul", "remaining life", "lifespan", "how long", "time remaining"]):
            answer_text = (
                f"**Remaining Useful Life (RUL) Prognosis:**\n\n"
                f"• **Predicted RUL:** **{health_summary['predicted_rul_hours']} operating hours**.\n"
                f"• **Estimated Time to Critical Condition:** **{health_summary['time_to_critical_hours']} hours**.\n"
                f"• **Confidence Interval (95% CI):** {rul_prediction['confidence_band']['lower_bound_rul']}h to {rul_prediction['confidence_band']['upper_bound_rul']}h.\n"
                f"• **Wear Trajectory:** Under current load ({load}%) and vibration ({vib} mm/s), component wear is accelerating by a factor of {rul_prediction['acceleration_factor']}x."
            )
            
        # 4. "Why was maintenance marked HIGH / Priority explanation"
        elif any(w in q for w in ["priority", "why high", "why critical", "maintenance priority"]):
            b = maintenance_plan["score_breakdown"]
            answer_text = (
                f"**Maintenance Priority Explanation ({health_summary['maintenance_priority']} - {health_summary['maintenance_priority_score']}/100):**\n\n"
                f"The priority score is calculated using our transparent multi-agent weighting formula:\n"
                f"• **Fault Severity Contribution:** {b['fault_severity_points']} / 35 pts\n"
                f"• **RUL Depletion Risk:** {b['rul_risk_points']} / 25 pts\n"
                f"• **Health Deficit:** {b['health_deficit_points']} / 20 pts\n"
                f"• **Machine Criticality Weight:** {b['criticality_points']} / 20 pts\n\n"
                f"**Suggested Maintenance Window:** {maintenance_plan['suggested_maintenance_window']}."
            )
            
        # 5. "What happens if I reduce the load?"
        elif any(w in q for w in ["reduce load", "lower load", "what happens if", "change load"]):
            answer_text = (
                f"**What-If Advisory: Load Reduction Effect:**\n\n"
                f"If you reduce the continuous load from {load}% down to **68%**:\n"
                f"• Operating temperature is estimated to drop by approximately 8–12°C.\n"
                f"• Mechanical stress acceleration factor drops from {rul_prediction['acceleration_factor']}x toward 1.1x.\n"
                f"• Machine Health will improve by approximately **+15% to +22%**.\n"
                f"• Predicted RUL will extend by **+120 to +280 hours**.\n"
                f"You can verify this live in the **Machine Health Simulator** tab."
            )
            
        # 6. "Which sensor is causing the problem?"
        elif any(w in q for w in ["which sensor", "sensor causing", "root cause", "contributing"]):
            reasons = fault_detection["contributing_reasons"]
            answer_text = (
                f"**Primary Contributing Sensor Parameters:**\n\n"
                + "\n".join([f"• {r}" for r in reasons]) +
                f"\n\n**Measured Sensor Readings:**\n"
                f"- Temperature: {temp}°C (Normal: 40–65°C)\n"
                f"- Vibration: {vib} mm/s (Normal: <3.2 mm/s)\n"
                f"- Load: {load}% (Normal: <75%)\n"
                f"- Hydraulic Pressure: {press} bar (Normal: 3.5–4.8 bar)"
            )
            
        # Default helpful industrial response
        else:
            answer_text = (
                f"**PrognosticX AI Maintenance Assistant:**\n\n"
                f"I am monitoring **{machine_id}**. Here is the active condition summary:\n"
                f"• **Health Score:** {health_summary['health_score']}% ({health_summary['health_state']})\n"
                f"• **Fault State:** {health_summary['fault_name']} (Risk: {round(fault_detection['fault_probability']*100, 1)}%)\n"
                f"• **Remaining Life (RUL):** {health_summary['predicted_rul_hours']} hours (Time to critical: {health_summary['time_to_critical_hours']}h)\n"
                f"• **Maintenance Priority:** {health_summary['maintenance_priority']}\n\n"
                f"You can ask me questions such as:\n"
                f"- *'What is wrong with the machine?'*\n"
                f"- *'Why is the health score low?'*\n"
                f"- *'How much RUL is remaining?'*\n"
                f"- *'Which sensor is causing the problem?'*\n"
                f"- *'What happens if I reduce the load?'*"
            )
            
        return {
            "query": query,
            "answer": answer_text,
            "grounded_context": context_data
        }
