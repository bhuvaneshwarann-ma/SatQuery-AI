"""
SatQuery AI — Counting Guardrail & Traceability Regression Tests (Part 3)
Verifies:
1. Pre-routing count queries correctly route to GROUNDING.
2. Canonical VQA queries ("What type of scene is shown?", "Describe the scene") route to VQA.
3. Spatial localization queries ("Locate the ships") route to GROUNDING.
4. Compound multi-tool queries maintain sequential execution intent.
5. Ambiguous queries trigger structured clarification prompts.
6. Counting derives deterministically from len(grounded_boxes) without VLM hallucination.
7. Zero valid detections return transparent zero-detection message.
8. Relevant scientific limitations are cleanly attached.
9. Auditable execution_trace and tools_used metadata are present.
"""

import unittest
from unittest.mock import patch, MagicMock
from backend.app.agent.router import AgentRouter
from backend.app.agent.schemas import AnalysisRequest, RoutingStatus, TaskType
from backend.app.services.orchestration_service import execute_agent_request
from backend.app.agent.output_firewall import OutputFirewall


class TestCountingGuardrailAndTraceability(unittest.TestCase):

    def setUp(self):
        self.sample_img = "data/samples/sample_satellite_port.jpg"
        self.sample_img_t2 = "data/samples/sample_satellite_port_t2_synthetic.jpg"

    def test_01_count_ships_routes_to_grounding(self):
        req = AnalysisRequest(query="How many ships are present?", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "GROUNDING")
        self.assertEqual(selection.task, TaskType.GROUNDING)
        self.assertEqual(selection.task_plan.intent, "OBJECT_COUNTING")
        self.assertEqual(selection.task_plan.target, "ships")

    def test_02_count_buildings_routes_to_grounding(self):
        req = AnalysisRequest(query="How many buildings?", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "GROUNDING")
        self.assertEqual(selection.task_plan.intent, "OBJECT_COUNTING")
        self.assertEqual(selection.task_plan.target, "buildings")

    def test_03_count_vehicles_routes_to_grounding(self):
        req = AnalysisRequest(query="Count the vehicles.", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "GROUNDING")
        self.assertEqual(selection.task_plan.intent, "OBJECT_COUNTING")
        self.assertEqual(selection.task_plan.target, "vehicles")

    def test_04_locate_ships_routes_to_grounding(self):
        req = AnalysisRequest(query="Locate the ships.", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "GROUNDING")
        self.assertEqual(selection.task_plan.intent, "OBJECT_LOCALIZATION")

    def test_05_scene_type_routes_to_vqa(self):
        req = AnalysisRequest(query="What type of scene is shown?", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "VQA")
        self.assertEqual(selection.task, TaskType.VQA)

    def test_06_describe_scene_routes_to_vqa(self):
        req = AnalysisRequest(query="Describe the scene.", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "VQA")
        self.assertEqual(selection.task, TaskType.VQA)

    def test_07_compound_change_query_preserves_multitool(self):
        req = AnalysisRequest(
            query="Compare these two dates, identify where built-up areas changed, and describe the observed change.",
            image_path=self.sample_img,
            second_image_path=self.sample_img_t2,
        )
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.ROUTED)
        self.assertEqual(selection.selected_tool, "MULTI_TOOL")
        self.assertEqual(selection.task, TaskType.MULTI_TOOL)
        steps = [s.tool for s in selection.task_plan.plan]
        self.assertEqual(steps, ["CHANGE_DETECTION", "GROUNDING", "VQA"])

    def test_08_ambiguous_query_triggers_clarification(self):
        req = AnalysisRequest(query="What changed here?", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.NEEDS_CLARIFICATION)
        self.assertTrue(len(selection.clarification_prompt) > 0)
        self.assertIn("compare the images for changes", selection.clarification_prompt.lower())

    def test_09_generic_ambiguous_query_triggers_clarification(self):
        req = AnalysisRequest(query="analyze this", image_path=self.sample_img)
        selection = AgentRouter.route(req)
        self.assertEqual(selection.status, RoutingStatus.NEEDS_CLARIFICATION)

    @patch("backend.app.services.orchestration_service.run_grounding")
    def test_10_counting_derivation_from_grounding_boxes(self, mock_grounding):
        mock_grounding.return_value = {
            "status": "SUCCESS",
            "model": "Grounding DINO Swin-T",
            "answer": "Detected 4 'ships' object(s).",
            "confidence": 0.42,
            "latency_ms": 250.0,
            "evidence_reference": "runs/grounding/test.jpg",
            "evidence": [{
                "annotated_artifact": "runs/grounding/test.jpg",
                "bounding_boxes": [[10, 10, 50, 50], [20, 20, 60, 60], [30, 30, 70, 70], [40, 40, 80, 80]],
            }]
        }
        req = AnalysisRequest(query="How many ships are present?", image_path=self.sample_img)
        res = execute_agent_request(req)

        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.selected_tool, "GROUNDING")
        self.assertEqual(res.answer, "4 ships were detected.")
        self.assertEqual(res.tools_used, ["GROUNDING"])
        self.assertTrue(any("Count is derived from grounding detections" in lim for lim in res.limitations))
        self.assertEqual(len(res.execution_trace), 1)
        self.assertEqual(res.execution_trace[0]["detections"], 4)

    @patch("backend.app.services.orchestration_service.run_grounding")
    def test_11_counting_zero_detections_transparent_message(self, mock_grounding):
        mock_grounding.return_value = {
            "status": "SUCCESS",
            "model": "Grounding DINO Swin-T",
            "answer": "No objects detected.",
            "confidence": 0.0,
            "latency_ms": 250.0,
            "evidence_reference": "runs/grounding/test.jpg",
            "evidence": [{
                "annotated_artifact": "runs/grounding/test.jpg",
                "bounding_boxes": [],
            }]
        }
        req = AnalysisRequest(query="How many ships are present?", image_path=self.sample_img)
        res = execute_agent_request(req)

        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.answer, "No valid ships were detected with the current grounding threshold.")
        self.assertTrue(any("Count is derived from grounding detections" in lim for lim in res.limitations))
        self.assertEqual(res.execution_trace[0]["detections"], 0)

    @patch("backend.app.services.orchestration_service.run_grounding")
    def test_11b_counting_singular_detection(self, mock_grounding):
        mock_grounding.return_value = {
            "status": "SUCCESS",
            "model": "Grounding DINO Swin-T",
            "answer": "Detected 1 'ships' object(s).",
            "confidence": 0.55,
            "latency_ms": 250.0,
            "evidence_reference": "runs/grounding/test.jpg",
            "evidence": [{
                "annotated_artifact": "runs/grounding/test.jpg",
                "bounding_boxes": [[10, 10, 50, 50]],
            }]
        }
        req = AnalysisRequest(query="How many ships are present?", image_path=self.sample_img)
        res = execute_agent_request(req)

        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.answer, "1 ship was detected.")

    def test_12_output_firewall_sanitizes_unsupported_superlatives(self):
        text = "This model achieves 100% accuracy and proven superiority in real-time."
        sanitized, corrections = OutputFirewall.sanitize_unsupported_language(text)
        self.assertNotIn("100% accuracy", sanitized)
        self.assertNotIn("proven superiority", sanitized)
        self.assertNotIn("real-time", sanitized)
        self.assertTrue(len(corrections) >= 3)


if __name__ == "__main__":
    unittest.main()
