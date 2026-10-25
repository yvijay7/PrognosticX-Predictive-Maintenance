"""
PrognosticX - Automated Test Pipeline
Verifies preprocessing, fault detection, RUL prediction, maintenance priority scoring,
machine health simulator (What-If), optimizer, and chatbot grounding.
"""

import os
import sys
import unittest

# Add root and backend to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from backend.agents.fault_agent import FaultDetectionAgent
from backend.agents.rul_agent import RULPredictionAgent
from backend.agents.maintenance_agent import MaintenancePlanningAgent
from backend.agents.controller import OrchestrationController
from backend.services.simulation_service import SimulationService
from backend.services.optimizer_service import OperatingRangeOptimizerService
from backend.services.chat_service import MaintenanceChatService

class TestPrognosticXPipeline(unittest.TestCase):
    def setUp(self):
        self.controller = OrchestrationController()
        self.fault_agent = FaultDetectionAgent()
        self.rul_agent = RULPredictionAgent(design_lifespan=3000.0)
        self.maint_agent = MaintenancePlanningAgent()
        self.sim_service = SimulationService()
        self.opt_service = OperatingRangeOptimizerService()
        self.chat_service = MaintenanceChatService()

    def test_nominal_condition(self):
        """Test nominal sensor telemetry results in normal status and high health."""
        normal_data = {
            "temperature": 52.0,
            "vibration": 1.6,
            "rpm": 1450.0,
            "pressure": 4.1,
            "load": 60.0,
            "operating_hours": 150.0
        }
        res = self.controller.execute_workflow(normal_data)
        self.assertFalse(res["fault_detection"]["is_fault"])
        self.assertEqual(res["fault_detection"]["fault_name"], "Normal Operation")
        self.assertGreaterEqual(res["health_summary"]["health_score"], 85.0)
        self.assertIn(res["health_summary"]["maintenance_priority"], ["LOW", "MEDIUM"])

    def test_thermal_overload_fault(self):
        """Test high temperature triggers Thermal Overload and Critical/High priority."""
        hot_data = {
            "temperature": 88.0,
            "vibration": 2.5,
            "rpm": 1420.0,
            "pressure": 4.5,
            "load": 92.0,
            "operating_hours": 200.0
        }
        fault_out = self.fault_agent.analyze(hot_data)
        self.assertTrue(fault_out["is_fault"])
        self.assertEqual(fault_out["fault_name"], "Thermal Overload")
        self.assertIn(fault_out["severity"], ["HIGH", "CRITICAL"])

    def test_bearing_fault_detection(self):
        """Test excessive vibration triggers Bearing Fault."""
        vib_data = {
            "temperature": 60.0,
            "vibration": 6.8,
            "rpm": 1360.0,
            "pressure": 4.3,
            "load": 70.0,
            "operating_hours": 250.0
        }
        fault_out = self.fault_agent.analyze(vib_data)
        self.assertTrue(fault_out["is_fault"])
        self.assertEqual(fault_out["fault_name"], "Bearing Fault")

    def test_rul_and_time_to_critical(self):
        """Test RUL prediction and Time to Critical metrics."""
        stressed_data = {
            "temperature": 80.0,
            "vibration": 4.2,
            "rpm": 1400.0,
            "pressure": 4.6,
            "load": 85.0,
            "operating_hours": 800.0
        }
        rul_out = self.rul_agent.estimate(stressed_data)
        self.assertGreater(rul_out["predicted_rul_hours"], 0)
        self.assertGreater(rul_out["time_to_critical_hours"], 0)
        self.assertLessEqual(rul_out["time_to_critical_hours"], rul_out["predicted_rul_hours"])
        self.assertTrue(0.0 <= rul_out["health_score"] <= 100.0)

    def test_priority_score_bounds(self):
        """Test that maintenance priority score is always normalized 0 to 100."""
        fault = {"is_fault": True, "fault_name": "Bearing Fault", "severity": "CRITICAL", "confidence": 0.95}
        rul = {"predicted_rul_hours": 45.0, "time_to_critical_hours": 12.0, "health_score": 22.0}
        plan = self.maint_agent.plan(fault, rul, machine_criticality="CRITICAL")
        self.assertTrue(0 <= plan["priority_score"] <= 100)
        self.assertEqual(plan["priority"], "CRITICAL")
        self.assertEqual(plan["confidence_policy"]["level"], "AUTOMATIC_RECOMMENDATION_APPROVED")

    def test_what_if_simulator_novelty(self):
        """Test Novelty 1: What-If simulation side-by-side comparison and sensitivities."""
        curr = {"temperature": 85.0, "vibration": 5.2, "rpm": 1400.0, "pressure": 4.9, "load": 90.0, "operating_hours": 300.0}
        sim = {"temperature": 60.0, "vibration": 2.1, "rpm": 1450.0, "pressure": 4.2, "load": 65.0, "operating_hours": 300.0}
        
        sim_res = self.sim_service.run_what_if_simulation(curr, sim)
        comp = sim_res["comparison"]
        self.assertGreater(comp["after"]["health_score"], comp["before"]["health_score"])
        self.assertGreater(comp["after"]["rul_hours"], comp["before"]["rul_hours"])
        self.assertLess(comp["after"]["fault_risk_pct"], comp["before"]["fault_risk_pct"])
        self.assertEqual(comp["delta"]["net_assessment"], "OVERALL IMPROVEMENT")
        self.assertGreater(len(sim_res["parameter_sensitivities"]), 0)

    def test_optimizer_novelty(self):
        """Test Novelty 2: Recommended Operating Range optimizer search."""
        stressed = {"temperature": 82.0, "vibration": 4.6, "rpm": 1350.0, "pressure": 5.4, "load": 88.0, "operating_hours": 250.0}
        opt_res = self.opt_service.optimize_operating_conditions(stressed)
        self.assertGreater(opt_res["projected_improvements"]["health_gain"], 0)
        self.assertGreater(len(opt_res["action_recommendations"]), 0)

    def test_grounded_chatbot(self):
        """Test grounded AI maintenance chatbot."""
        curr = {"temperature": 82.0, "vibration": 2.5, "rpm": 1450.0, "pressure": 4.2, "load": 88.0, "operating_hours": 200.0}
        res = self.chat_service.respond_to_query("What is wrong with Machine A?", "Machine-Alpha", curr)
        self.assertIn("Thermal Overload", res["answer"])
        self.assertIn("82", res["answer"])

if __name__ == "__main__":
    unittest.main()
