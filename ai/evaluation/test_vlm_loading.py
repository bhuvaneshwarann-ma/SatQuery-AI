"""
Controlled Feasibility Test: Remote-Sensing Qwen2.5-VL-3B-Instruct
Target Hardware: NVIDIA GeForce RTX 5050 Laptop GPU (8 GB GDDR7 VRAM)
Environment: Windows, Python 3.12 (.venv), PyTorch CUDA
"""

import gc
import os
import sys
import tempfile
import traceback
import torch
from PIL import Image, ImageDraw


def print_vram_snapshot(label: str):
    """Print current GPU memory allocations if CUDA is available."""
    if not torch.cuda.is_available():
        print(f"[{label}] CUDA unavailable.")
        return
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    allocated_mb = round(torch.cuda.memory_allocated() / (1024 ** 2), 2)
    reserved_mb = round(torch.cuda.memory_reserved() / (1024 ** 2), 2)
    free_mb = round(free_bytes / (1024 ** 2), 2)
    total_mb = round(total_bytes / (1024 ** 2), 2)
    print(f"[{label}] Total: {total_mb} MB | Free: {free_mb} MB | Allocated: {allocated_mb} MB | Reserved: {reserved_mb} MB")


def create_temporary_test_image() -> str:
    """Create a lightweight synthetic remote-sensing style test tile and return path."""
    img_size = (384, 384)
    # Create synthetic scene: green land background, blue water strip, gray road
    img = Image.new("RGB", img_size, color=(34, 139, 34))  # Forest green
    draw = ImageDraw.Draw(img)
    # Draw water canal / river (blue)
    draw.rectangle([0, 140, 384, 220], fill=(30, 144, 255))
    # Draw paved road / runway (gray)
    draw.rectangle([100, 0, 160, 384], fill=(128, 128, 128))
    # Draw a building footprint (white roof)
    draw.rectangle([220, 40, 300, 110], fill=(245, 245, 245))

    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temp_path = temp_file.name
    temp_file.close()
    img.save(temp_path, format="PNG")
    return temp_path


def main():
    print("=" * 70)
    print("  SatQuery AI - Remote-Sensing VLM Hardware Feasibility Test")
    print("=" * 70)

    # 1. Print environment diagnostics
    print("\n--- 1. Environment Diagnostics ---")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"PyTorch Version: {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")

    if not cuda_available:
        print("[ERROR] CUDA is not available. This test requires GPU execution.")
        print("VLM_TEST_RESULT=LOAD_ERROR")
        sys.exit(1)

    gpu_name = torch.cuda.get_device_name(0)
    bf16_supported = torch.cuda.is_bf16_supported()
    free_init, total_init = torch.cuda.mem_get_info()
    free_init_mb = round(free_init / (1024 ** 2), 2)
    total_init_mb = round(total_init / (1024 ** 2), 2)

    print(f"GPU Device: {gpu_name}")
    print(f"BF16 Supported: {bf16_supported}")
    print(f"Total VRAM: {total_init_mb} MB")
    print(f"Free VRAM before loading: {free_init_mb} MB")

    model_id = "AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct"
    model = None
    processor = None
    temp_img_path = None
    current_stage = "INITIALIZATION"

    try:
        # 2. Configure processor conservatively
        current_stage = "PROCESSOR_LOADING"
        print(f"\n--- 2. Loading Processor: {model_id} ---")
        min_pixels = 256 * 28 * 28
        max_pixels = 512 * 28 * 28
        print(f"Configuring token budget: min_pixels={min_pixels}, max_pixels={max_pixels}")

        from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
        from qwen_vl_utils import process_vision_info

        processor = AutoProcessor.from_pretrained(
            model_id,
            min_pixels=min_pixels,
            max_pixels=max_pixels,
        )
        print("Processor loaded successfully.")

        # 3. Load Model with device_map="auto" and torch_dtype="auto"
        current_stage = "MODEL_LOADING"
        print(f"\n--- 3. Loading Model: {model_id} ---")
        print("Loading weights with device_map='auto' and torch_dtype='auto' (FlashAttention NOT enabled)...")

        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto",
        )
        print("Model loading SUCCESS.")

        # 4. Post-loading diagnostics
        print("\n--- 4. Post-Loading VRAM Diagnostics ---")
        print_vram_snapshot("Post-Model-Load")
        device_map = getattr(model, "hf_device_map", None)
        print(f"Model Device Map: {device_map}")

        # 5. Controlled Inference Test
        current_stage = "INFERENCE_PREPARATION"
        print("\n--- 5. Preparing Controlled Inference Test ---")
        temp_img_path = create_temporary_test_image()
        print(f"Created temporary synthetic remote-sensing test image: {temp_img_path}")

        prompt_question = "What objects or land-cover features are visible in this image?"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": temp_img_path},
                    {"type": "text", "text": prompt_question},
                ],
            }
        ]

        text_prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = processor(
            text=[text_prompt],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )

        # Move tensors to the model's device
        target_device = model.device
        inputs = inputs.to(target_device)
        print(f"Input tensors successfully moved to target device: {target_device}")

        # 6. Execute forward pass
        current_stage = "INFERENCE_GENERATION"
        print("\n--- 6. Running Inference Forward Pass ---")
        with torch.inference_mode():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=64,
                do_sample=False,
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )

        answer = output_text[0].strip() if output_text else ""
        print(f"Inference SUCCESS.")
        print(f"Generated Answer:\n\"{answer}\"")

        # 7. Post-inference diagnostics
        print("\n--- 7. Post-Inference VRAM Diagnostics ---")
        print_vram_snapshot("Post-Inference")

        print("\n" + "=" * 70)
        print("Verdict: Feasibility test completed successfully on RTX 5050.")
        print("VLM_TEST_RESULT=PASS")
        print("=" * 70)

    except torch.cuda.OutOfMemoryError as oom_err:
        print("\n" + "!" * 70)
        print("CRITICAL: CUDA Out of Memory encountered!")
        print("VLM_GPU_OOM")
        print(f"Stage where OOM occurred: {current_stage}")
        print(f"Error details: {oom_err}")
        print("!" * 70)

        # Clean up resources
        if model is not None:
            del model
        if processor is not None:
            del processor
        torch.cuda.empty_cache()
        gc.collect()

        print("\nVRAM after emergency cleanup:")
        print_vram_snapshot("Post-OOM-Cleanup")
        print("VLM_TEST_RESULT=GPU_OOM")

    except Exception as err:
        print("\n" + "!" * 70)
        print(f"CRITICAL: Model loading or inference failure at stage [{current_stage}]")
        print(f"Error: {err}")
        traceback.print_exc()
        print("!" * 70)

        if model is not None:
            del model
        if processor is not None:
            del processor
        torch.cuda.empty_cache()
        gc.collect()

        print("VLM_TEST_RESULT=LOAD_ERROR")

    finally:
        # Clean up temporary test image
        if temp_img_path and os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()
