"""
SatQuery AI — Unit Tests for Agent Router (Phase 4)
Verifies deterministic routing, input constraint validation, ambiguity detection,
and registry security against arbitrary/unregistered tool requests.
"""

import unittest
import sys
import os

# Ensure backend package is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.agent.schemas import AnalysisRequest, RoutingStatus, TaskType
from backend.app.agent.router import AgentRouter
from backend.app.agent.registry import is_tool_registered


class TestAgentRouter(unittest.TestCase):

    def setUp(self):
        self.sample_img = "data/samples/sample_satellite_port.jpg"
        self.sample_t2 = "data/samples/sample_satellite_port_t2_synthetic.jpg"
        self.sample_sar = "data/samples/sample_satellite_port_proxy_sar.png"

    # Test 1: VQA query with image
    def test_01_vqa_query_with_image(self):
        req = AnalysisRequest(
            query="What is visible in this satellite image?",
            image_path=self.sample_img
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.ROUTED)
        self.assertEqual(res.selected_tool, "VQA")
        self.assertEqual(res.task, TaskType.VQA)
        self.assertIn("image_path", res.provided_inputs)
        self.assertIn("max_new_tokens", res.permitted_parameters)

    # Test 2: Grounding query with image
    def test_02_grounding_query_with_image(self):
        req = AnalysisRequest(
            query="Locate all cargo ships and boats along the coastline.",
            image_path=self.sample_img,
            parameters={"box_threshold": 0.35, "malicious_unpermitted_param": 999}
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.ROUTED)
        self.assertEqual(res.selected_tool, "GROUNDING")
        self.assertEqual(res.task, TaskType.GROUNDING)
        self.assertEqual(res.permitted_parameters["box_threshold"], 0.35)
        self.assertNotIn("malicious_unpermitted_param", res.permitted_parameters)

    # Test 3: Change query with T1 and T2
    def test_03_change_query_with_t1_t2(self):
        req = AnalysisRequest(
            query="What changed between these two images?",
            image_path=self.sample_img,
            second_image_path=self.sample_t2
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.ROUTED)
        self.assertEqual(res.selected_tool, "CHANGE_DETECTION")
        self.assertEqual(res.task, TaskType.CHANGE_DETECTION)
        self.assertIn("image_path", res.provided_inputs)
        self.assertIn("second_image_path", res.provided_inputs)

    # Test 4: Optical-SAR query with optical + SAR
    def test_04_optical_sar_query_with_both(self):
        req = AnalysisRequest(
            query="Compare the optical and SAR images to identify structures through clouds.",
            optical_image_path=self.sample_img,
            sar_image_path=self.sample_sar
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.ROUTED)
        self.assertEqual(res.selected_tool, "OPTICAL_SAR")
        self.assertEqual(res.task, TaskType.OPTICAL_SAR)
        self.assertIn("optical_image_path", res.provided_inputs)
        self.assertIn("sar_image_path", res.provided_inputs)

    # Test 5: Missing image for VQA / Grounding
    def test_05_missing_image(self):
        req = AnalysisRequest(
            query="Where are the ships?",
            image_path=None  # Missing image
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.INVALID_INPUT)
        self.assertEqual(res.selected_tool, "GROUNDING")
        self.assertTrue(any("requires a valid 'image_path'" in err for err in res.validation_errors))

    # Test 6: Missing T2 for Change Detection
    def test_06_missing_second_image_for_change(self):
        req = AnalysisRequest(
            query="Identify new construction between T1 and T2.",
            image_path=self.sample_img,
            second_image_path=None  # Missing T2
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.INVALID_INPUT)
        self.assertEqual(res.selected_tool, "CHANGE_DETECTION")
        self.assertTrue(any("requires post-event image T2" in err for err in res.validation_errors))

    # Test 7: Missing SAR for Optical-SAR
    def test_07_missing_sar_for_optical_sar(self):
        req = AnalysisRequest(
            query="Analyze radar backscatter and optical observations together.",
            optical_image_path=self.sample_img,
            sar_image_path=None  # Missing SAR
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.INVALID_INPUT)
        self.assertEqual(res.selected_tool, "OPTICAL_SAR")
        self.assertTrue(any("requires a SAR radar image" in err for err in res.validation_errors))

    # Test 8: Ambiguous query
    def test_08_ambiguous_query(self):
        req = AnalysisRequest(
            query="analyze this",
            image_path=self.sample_img
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.NEEDS_CLARIFICATION)
        self.assertIsNone(res.selected_tool)
        self.assertIsNotNone(res.clarification_prompt)

    # Test 9: Unsupported / unregistered task override
    def test_09_unsupported_task(self):
        req = AnalysisRequest(
            query="Do 3D terrain reconstruction",
            task="3D_SURFACE_MESH",
            image_path=self.sample_img
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.UNREGISTERED_TOOL)
        self.assertIsNone(res.selected_tool)
        self.assertTrue(any("Unregistered tool" in err for err in res.validation_errors))

    # Test 10: Arbitrary / unregistered tool injection request
    def test_10_arbitrary_unregistered_tool_request(self):
        malicious_task_name = "CUSTOM_SHELL_EXECUTION"
        self.assertFalse(is_tool_registered(malicious_task_name))

        req = AnalysisRequest(
            query="Run system diagnostics",
            task=malicious_task_name,
            image_path=self.sample_img
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.UNREGISTERED_TOOL)
        self.assertIsNone(res.selected_tool)
        self.assertIn("not registered", res.reason)

    # Test 11: Compound multi-tool query: change + grounding + description
    def test_11_compound_multi_tool_change_query(self):
        req = AnalysisRequest(
            query="What changed in the built-up area between these two dates, and where?",
            image_path=self.sample_img,
            second_image_path=self.sample_t2
        )
        res = AgentRouter.route(req)
        self.assertEqual(res.status, RoutingStatus.ROUTED)
        self.assertEqual(res.selected_tool, "MULTI_TOOL")
        self.assertEqual(res.task, TaskType.MULTI_TOOL)
        self.assertIsNotNone(res.task_plan)
        self.assertTrue(res.task_plan.is_multi_tool)
        self.assertEqual(res.task_plan.intent, "CHANGE_ANALYSIS")
        self.assertEqual(res.task_plan.target, "built_up_area")
        self.assertTrue(res.task_plan.requires_temporal_pair)
        self.assertTrue(res.task_plan.requires_spatial_evidence)
        step_tools = [s.tool for s in res.task_plan.plan]
        self.assertEqual(step_tools, ["CHANGE_DETECTION", "GROUNDING", "VQA"])
        self.assertTrue(res.task_plan.policy_validated)


if __name__ == "__main__":
    unittest.main()

