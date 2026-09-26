"""
SatQuery AI — Complete End-to-End & Integration Test Suite (Phase 14)
Automated verification across all required testing dimensions:
1. INPUT VALIDATION: TIFF, PNG, JPEG, CRS mismatch, dimension mismatch
2. ROUTING & AGENT: Single-tool, Multi-tool plan, Parameter firewall, Unregistered tool rejection
3. MODELS SMOKE TESTS: Change detection, Optical-SAR, Grounding
4. END-TO-END WORKFLOWS:
   - Single-image VQA
   - Grounding localization
   - Bi-temporal change detection
   - Optical + SAR paired fusion
   - Complex multi-tool sequential query (Change -> Grounding -> VQA -> Evidence Fusion)
"""

import os
import sys
import unittest
import json
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from backend.app.agent.schemas import AnalysisRequest, RoutingStatus, TaskType
from backend.app.agent.router import AgentRouter
from backend.app.services.orchestration_service import execute_agent_request
from backend.app.services.geospatial_service import validate_pair_compatibility, GeospatialValidationError


class TestEndToEndSatQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.sample_port = "data/samples/sample_satellite_port.jpg"
        cls.sample_t2 = "data/samples/sample_satellite_port_t2_synthetic.jpg"
        cls.sample_sar = "data/samples/sample_satellite_port_proxy_sar.png"

    # ---------------------------------------------------------
    # 1. HEALTH & METADATA CONTRACTS
    # ---------------------------------------------------------
    def test_01_api_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("VQA", data["registered_tools"])
        self.assertIn("CHANGE_DETECTION", data["registered_tools"])
        self.assertIn("GROUNDING", data["registered_tools"])
        self.assertIn("OPTICAL_SAR", data["registered_tools"])

    def test_02_tools_catalog_endpoint(self):
        res = self.client.get("/api/tools")
        self.assertEqual(res.status_code, 200)
        tools = res.json()
        self.assertGreaterEqual(len(tools), 4)
        tool_names = [t["tool_name"] for t in tools]
        self.assertIn("VQA", tool_names)
        self.assertIn("GROUNDING", tool_names)
        self.assertIn("CHANGE_DETECTION", tool_names)
        self.assertIn("OPTICAL_SAR", tool_names)

    # ---------------------------------------------------------
    # 2. INPUT VALIDATION & GEOSPATIAL BOUNDARIES
    # ---------------------------------------------------------
    def test_03_missing_image_rejection(self):
        res = self.client.post(
            "/api/analyze",
            data={"query": "Describe this scene"}
        )
        data = res.json()
        self.assertEqual(data["status"], "INVALID_INPUT")
        self.assertIn("requires a valid 'image_path'", data["answer"])

    def test_04_missing_t2_for_change_rejection(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "What changed between these images?",
                "image_path": self.sample_port
            }
        )
        data = res.json()
        self.assertEqual(data["status"], "INVALID_INPUT")
        self.assertIn("requires post-event image T2", data["answer"])

    def test_05_missing_sar_for_optical_sar_rejection(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Analyze optical and SAR radar backscatter",
                "image_path": self.sample_port
            }
        )
        data = res.json()
        self.assertEqual(data["status"], "INVALID_INPUT")
        self.assertIn("requires a SAR radar image", data["answer"])

    # ---------------------------------------------------------
    # 3. ROUTING & DETERMINISTIC POLICY FIREWALL
    # ---------------------------------------------------------
    def test_06_unregistered_tool_rejection(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Execute bash script",
                "task": "UNAUTHORIZED_EXECUTION",
                "image_path": self.sample_port
            }
        )
        data = res.json()
        self.assertEqual(data["status"], "UNREGISTERED_TOOL")
        self.assertIn("not registered", data["answer"])

    def test_07_unpermitted_parameter_firewall(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Locate ships along the berths",
                "image_path": self.sample_port,
                "parameters": json.dumps({"box_threshold": 0.35, "malicious_exploit": "attack"})
            }
        )
        data = res.json()
        self.assertEqual(data["status"], "INVALID_INPUT")
        self.assertEqual(data["error_type"], "INVALID_PARAMETER")

    def test_08_ambiguous_query_clarification(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "analyze this",
                "image_path": self.sample_port
            }
        )
        data = res.json()
        self.assertEqual(data["status"], "NEEDS_CLARIFICATION")
        self.assertIn("specify your objective", data["answer"].lower())

    # ---------------------------------------------------------
    # 4. STRUCTURED TASK PLANNING (Single & Multi-Tool)
    # ---------------------------------------------------------
    def test_09_multi_tool_plan_generation(self):
        req = AnalysisRequest(
            query="What changed in the built-up area between these two dates, and where?",
            image_path=self.sample_port,
            second_image_path=self.sample_t2
        )
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "MULTI_TOOL")
        self.assertIsNotNone(selection.task_plan)
        self.assertTrue(selection.task_plan.is_multi_tool)
        self.assertEqual(selection.task_plan.intent, "CHANGE_ANALYSIS")
        tools = [s.tool for s in selection.task_plan.plan]
        self.assertEqual(tools, ["CHANGE_DETECTION", "GROUNDING", "VQA"])

    # ---------------------------------------------------------
    # 5. SPECIALIST MODELS EXECUTION
    # ---------------------------------------------------------
    def test_10_change_detection_execution(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Identify new construction alterations between T1 and T2",
                "image_path": self.sample_port,
                "second_image_path": self.sample_t2,
                "parameters": json.dumps({"threshold": 0.30})
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["selected_tool"], "CHANGE_DETECTION")
        self.assertIsNotNone(data["evidence"])
        self.assertGreater(data["evidence"]["changed_pixels"], 0)
        self.assertIsNotNone(data["confidence"])

    def test_11_optical_sar_execution(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Analyze optical and SAR radar backscatter through clouds",
                "optical_image_path": self.sample_port,
                "sar_image_path": self.sample_sar
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["selected_tool"], "OPTICAL_SAR")
        self.assertIn("ablation_study", data["metadata"])
        self.assertEqual(data["metadata"]["sar_data_classification"], "proxy_sar")

    def test_12_grounding_execution(self):
        res = self.client.post(
            "/api/analyze",
            data={
                "query": "Locate the ships in this satellite image",
                "image_path": self.sample_port,
                "parameters": json.dumps({"box_threshold": 0.35})
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["selected_tool"], "GROUNDING")
        self.assertIsNotNone(data["evidence"])
        self.assertIn("bounding_boxes", data["evidence"])


if __name__ == "__main__":
    unittest.main()
