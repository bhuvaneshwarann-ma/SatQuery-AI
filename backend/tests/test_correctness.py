"""Fast boundary regressions: real orchestration with mocked expensive specialists."""
import asyncio
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image
from fastapi import UploadFile
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.agent.router import AgentRouter
from backend.app.agent.schemas import AnalysisRequest
from backend.app.services.orchestration_service import execute_agent_request
from backend.app.services.geospatial_service import validate_pair_compatibility, GeospatialValidationError
from backend.app.services.upload_service import save_upload_file, resolve_sample_path, cleanup_file
from backend.app.services.artifact_service import new_artifact_path
from ai.inference.optical_sar import classify_sar_modality, run_optical_sar

SAMPLE = "data/samples/sample_satellite_port.jpg"
PAIR = "data/samples/sample_satellite_port_t2_synthetic.jpg"
COMPOUND = "Compare these two dates, identify where buildings changed, and describe the change."


def success(evidence, **extra):
    return dict(status="SUCCESS", model="test", answer="Observed scene", latency_ms=1,
                confidence=None, evidence=[evidence], metadata={}, **extra)


class CorrectnessTests(unittest.TestCase):
    def test_explicit_vqa_cannot_bypass_counting(self):
        result = AgentRouter.route(AnalysisRequest(query="How many ships?", task="VQA", image_path=SAMPLE))
        self.assertEqual(result.selected_tool, "GROUNDING")
        self.assertEqual(result.task_plan.intent, "OBJECT_COUNTING")

    def test_compound_parameters_stay_with_owner(self):
        result = AgentRouter.route(AnalysisRequest(query=COMPOUND, image_path=SAMPLE, second_image_path=PAIR, parameters={"threshold": .6}))
        self.assertEqual(result.validation_errors, [])
        self.assertEqual(result.task_plan.plan[0].parameters["threshold"], .6)
        self.assertNotIn("threshold", result.task_plan.plan[1].parameters)

    def test_effective_threshold_and_changed_pixels(self):
        raw = success({"changed_pixels": 17, "change_percentage": 2.0})
        with patch("backend.app.services.orchestration_service.run_change_detection", return_value=raw):
            result = execute_agent_request(AnalysisRequest(query="What changed between these images?", image_path=SAMPLE, second_image_path=PAIR, parameters={"threshold": .6}))
        self.assertEqual(result.execution_trace[0]["threshold"], .6)
        self.assertEqual(result.confidence["changed_pixels"], 17)

    def test_optical_sar_evidence_names(self):
        with patch("backend.app.services.orchestration_service.run_optical_sar", return_value=success({"cross_modal_correlation": .1, "radar_dominant_anomalies": 9})):
            result = execute_agent_request(AnalysisRequest(query="Analyze SAR", task="OPTICAL_SAR", image_path=SAMPLE, sar_image_path=PAIR))
        self.assertEqual(result.confidence["anomaly_pixels"], 9)
        self.assertIsNone(result.confidence["score"])

    def test_counting_failure_is_not_zero_detection(self):
        raw = dict(status="ERROR", model="test", answer="Weights unavailable", latency_ms=0, evidence=[], metadata={})
        with patch("backend.app.services.orchestration_service.run_grounding", return_value=raw):
            result = execute_agent_request(AnalysisRequest(query="How many ships?", image_path=SAMPLE))
        self.assertEqual(result.status, "ERROR")
        self.assertEqual(result.answer, "Weights unavailable")
        self.assertIsNone(result.confidence)

    def test_failed_compound_stages_propagate(self):
        for failed in ["GROUNDING", "VQA"]:
            with self.subTest(stage=failed):
                change = success({"changed_pixels": 12}, changed_pixels=12, change_percentage=1.0)
                grounding = success({"bounding_boxes": [[1,1,2,2]]}, detections=1)
                vqa = success({})
                (grounding if failed == "GROUNDING" else vqa).update(status="ERROR", answer="Unavailable")
                with patch("backend.app.services.orchestration_service.run_change_detection", return_value=change), patch("backend.app.services.orchestration_service.run_grounding", return_value=grounding), patch("backend.app.services.orchestration_service.run_vqa", return_value=vqa):
                    result = execute_agent_request(AnalysisRequest(query=COMPOUND, image_path=SAMPLE, second_image_path=PAIR))
                self.assertEqual(result.status, "ERROR")
                self.assertIsNone(result.confidence)

    def test_narrative_receives_both_observations(self):
        with patch("backend.app.services.orchestration_service.run_change_detection", return_value=success({}, changed_pixels=0, change_percentage=0)), patch("backend.app.services.orchestration_service.run_grounding", return_value=success({}, detections=0)), patch("backend.app.services.orchestration_service.run_vqa", return_value=success({})) as vqa:
            result = execute_agent_request(AnalysisRequest(query=COMPOUND, image_path=SAMPLE, second_image_path=PAIR))
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(vqa.call_args.kwargs["image_path"], SAMPLE)
        self.assertEqual(vqa.call_args.kwargs["second_image_path"], PAIR)
        self.assertIsNone(result.confidence)

    def test_artifacts_are_unique(self):
        self.assertNotEqual(new_artifact_path("change"), new_artifact_path("change"))

    def test_filename_does_not_verify_sensor(self):
        self.assertEqual(classify_sar_modality("sentinel_picture.jpg"), "unverified_sar")

    def test_sar_returns_statistics_not_random_network_gain(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "sentinel.jpg"
            Image.fromarray(np.full((16,16,3), 80, dtype=np.uint8)).save(image)
            with patch("ai.inference.optical_sar.new_artifact_path", return_value=str(Path(tmp)/"result.jpg")):
                result = run_optical_sar(str(image), str(image))
            self.assertEqual(result["status"], "SUCCESS")
            self.assertIn("Unverified", result["answer"])
            self.assertNotIn("Genuine", result["answer"])
            self.assertNotIn("ablation_study", result["evidence"][0])

    def test_equal_pixels_do_not_establish_registration(self):
        self.assertIsNone(validate_pair_compatibility(SAMPLE, PAIR)["co_registered"])

    def test_shifted_geotiffs_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i in range(2):
                p = Path(tmp)/f"{i}.tif"
                Image.new("RGB", (100,100)).save(p, tiffinfo={33550:(10.,10.,0.),33922:(0.,0.,0.,500000.+i*10,2000000.,0.),34735:(1,1,0,1,3072,0,1,32643)})
                paths.append(str(p))
            with self.assertRaises(GeospatialValidationError) as ctx:
                validate_pair_compatibility(*paths)
            self.assertEqual(ctx.exception.error_code, "GRID_MISMATCH")

    def test_server_path_is_confined(self):
        with self.assertRaises(ValueError):
            resolve_sample_path("README.md")
        self.assertTrue(resolve_sample_path(SAMPLE).endswith("sample_satellite_port.jpg"))

    def test_upload_limit_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp, patch("backend.app.services.upload_service.UPLOAD_DIR", Path(tmp)), patch("backend.app.services.upload_service.MAX_UPLOAD_BYTES", 10):
            with self.assertRaises(ValueError):
                save_upload_file(UploadFile(filename="large.jpg", file=io.BytesIO(b"x"*11)))
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_request_cleanup_after_invalid_second_file(self):
        with tempfile.TemporaryDirectory() as tmp, patch("backend.app.services.upload_service.UPLOAD_DIR", Path(tmp)):
            content = io.BytesIO()
            Image.new("RGB", (8,8)).save(content, "PNG")
            response = TestClient(app).post("/api/analyze", data={"query":"Describe scene"}, files={"image":("ok.png",content.getvalue()),"second_image":("bad.txt",b"bad")})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_oversized_request_rejected_before_parsing(self):
        response = TestClient(app).post("/api/analyze", content=b"x", headers={"content-length":str(70*1024*1024)})
        self.assertEqual(response.status_code, 413)

    def test_queue_admission_bound(self):
        with patch("backend.app.api.routes._pending_requests", 4):
            self.assertEqual(TestClient(app).post("/api/analyze",data={"query":"Describe image"}).status_code,429)

    def test_observable_trace_survives_serialization(self):
        from backend.app.agent.schemas import OrchestrationResult
        result = OrchestrationResult(status="SUCCESS", selected_tool="VQA", model="test", answer="x", observable_execution_trace=[{"step":"ROUTER"}], execution_trace=[{"tool":"VQA"}])
        self.assertEqual(result.to_dict()["observable_execution_trace"], [{"step":"ROUTER"}])

    def test_successful_upload_cleans_staging_and_preserves_contract(self):
        with tempfile.TemporaryDirectory() as tmp, patch("backend.app.services.upload_service.UPLOAD_DIR", Path(tmp)):
            content = io.BytesIO()
            Image.new("RGB", (8, 8)).save(content, "PNG")
            with patch("backend.app.services.orchestration_service.run_vqa", return_value=success({})):
                response = TestClient(app).post("/api/analyze", data={"query":"Describe scene"}, files={"image":("ok.png",content.getvalue())})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["query"], "Describe scene")
            self.assertIn("limitations", response.json())
            self.assertIn("step", response.json()["observable_execution_trace"][0])
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_legacy_service_uses_counting_policy(self):
        from backend.app.services.analysis_service import AnalysisService
        with patch("backend.app.services.orchestration_service.run_grounding", return_value=success({"bounding_boxes": []})):
            result, trace = AnalysisService.analyze(AnalysisRequest(query="How many ships?", task="VQA", image_path=SAMPLE))
        self.assertEqual(result.tool_name, "GROUNDING")
        self.assertIn("No valid ships", result.answer)
        self.assertTrue(trace[0].step)

    def test_training_scenes_are_disjoint(self):
        import json
        def groups(path):
            with open(path) as stream:
                return {"port" if "satellite_port" in row["image"] else row["image"] for row in json.load(stream)}
        train, val = groups("training/data/vqa_train.json"), groups("training/data/vqa_val.json")
        self.assertTrue(train and val)
        self.assertFalse(train & val)
