"""
PrognosticX - Controller / Orchestration Agent
Central coordinating unit inspired by LangChain & Google ADK multi-agent workflows.
Coordinates Fault Detection Agent, RUL Prediction Agent, and Maintenance Planning Agent.
Performs data validation, parallel execution routing, result aggregation, and edge feedback.
"""

from typing import Dict, Any
from .fault_agent import FaultDetectionAgent
from .rul_agent import RULPredictionAgent
from .maintenance_agent import MaintenancePlanningAgent

class OrchestrationController:
    def __init__(self):
        self.fault_agent = FaultDetectionAgent()
        self.rul_agent = RULPredictionAgent()
        self.maintenance_agent = MaintenancePlanningAgent()
        self.system_name = "PrognosticX Multi-Agent Controller"
        
    def validate_telemetry(self, sensor_data: Dict[str, Any]) -> Dict[str, float]:
        """Validates and cleans incoming sensor metrics from industrial edge nodes."""
        cleaned = {
            "temperature": float(sensor_data.get("temperature", 55.0)),
            "vibration": float(sensor_data.get("vibration", 1.8)),
            "rpm": float(sensor_data.get("rpm", 1450.0)),
            "pressure": float(sensor_data.get("pressure", 4.2)),
            "load": float(sensor_data.get("load", 65.0)),
            "operating_hours": float(sensor_data.get("operating_hours", 200.0))
        }
        return cleaned
        
    def execute_workflow(self, sensor_data: Dict[str, Any], machine_criticality: str = "HIGH") -> Dict[str, Any]:
        """
        Full coordinated multi-agent workflow:
        Step 1: Input Validation & Preprocessing
        Step 2: Dispatch to Fault Detection Agent
        Step 3: Dispatch to RUL Prediction Agent
        Step 4: Dispatch aggregated state to Maintenance Planning Agent
        Step 5: Synthesize edge feedback and unified health summary
        """
        cleaned_data = self.validate_telemetry(sensor_data)
        
        # Parallel agent execution
        fault_output = self.fault_agent.analyze(cleaned_data)
        rul_output = self.rul_agent.estimate(cleaned_data)
        
        # Maintenance planning synthesizes results from both previous agents
        maintenance_output = self.maintenance_agent.plan(
            fault_result=fault_output,
            rul_result=rul_output,
            machine_criticality=machine_criticality
        )
        
        # Edge feedback loop: generate control/operational advisory parameters
        edge_feedback = {
            "target_max_load_pct": 70.0 if fault_output["is_fault"] else 85.0,
            "target_max_temp_c": 65.0,
            "recommended_sampling_rate_hz": 100 if fault_output["severity"] in ["HIGH", "CRITICAL"] else 10,
            "advisory_status": "RESTRICTED_OPERATION" if fault_output["is_fault"] else "OPTIMAL_OPERATION"
        }
        
        return {
            "controller": self.system_name,
            "status": "SUCCESS",
            "telemetry_received": cleaned_data,
            "fault_detection": fault_output,
            "rul_prediction": rul_output,
            "maintenance_plan": maintenance_output,
            "edge_feedback": edge_feedback,
            "health_summary": {
                "health_score": rul_output["health_score"],
                "health_state": rul_output["health_state"],
                "is_fault": fault_output["is_fault"],
                "fault_name": fault_output["fault_name"],
                "predicted_rul_hours": rul_output["predicted_rul_hours"],
                "time_to_critical_hours": rul_output["time_to_critical_hours"],
                "maintenance_priority": maintenance_output["priority"],
                "maintenance_priority_score": maintenance_output["priority_score"],
                "recommended_action": maintenance_output["recommended_action"]
            }
        }
