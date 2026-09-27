"""Exercise VQA response construction without loading model weights."""
import unittest
from unittest.mock import MagicMock, patch

import torch
from transformers import BatchEncoding
from ai.inference.vqa import run_vqa


class VQAResponseTests(unittest.TestCase):
    def run_mocked(self, error=None):
        processor = MagicMock()
        processor.return_value = BatchEncoding({"input_ids": torch.tensor([[1, 2]])})
        processor.batch_decode.return_value = ["A port."]
        model = MagicMock(device="cpu")
        model.generate.return_value = torch.tensor([[1, 2, 3]])
        model.generate.side_effect = error
        with patch.dict("os.environ", {"VQA_LORA_ADAPTER_DIR": ""}), \
             patch("ai.inference.vqa.AutoProcessor.from_pretrained", return_value=processor), \
             patch("ai.inference.vqa.Qwen2_5_VLForConditionalGeneration.from_pretrained", return_value=model), \
             patch("ai.inference.vqa.process_vision_info", return_value=([], None)), \
             patch("ai.inference.vqa.extract_vqa_rich_evidence", return_value=("A port.", "A port.", [])):
            return run_vqa("data/samples/sample_satellite_port.jpg", "what is image")

    def test_success_with_unavailable_confidence(self):
        result = self.run_mocked()
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["answer"], "A port.")
        self.assertIsNone(result["confidence"])
        self.assertIsNone(result["metadata"]["confidence_score"])

    def test_inference_failure_has_visible_message(self):
        result = self.run_mocked(RuntimeError("Generation unavailable"))
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("Generation unavailable", result["answer"])


if __name__ == "__main__":
    unittest.main()
