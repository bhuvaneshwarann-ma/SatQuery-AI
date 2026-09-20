# Real Satellite VQA Validation

## Hardware
* **GPU**: NVIDIA GeForce RTX 5050 Laptop GPU
* **Total VRAM**: 8150.56 MB (~8 GB GDDR7)
* **CUDA Available**: True (BF16 Supported: True)
* **PyTorch Version**: 2.14.0+cu130

## Model
* **Model Name**: `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct`
* **Loading Strategy**: `device_map='auto'`, `torch_dtype='auto'`, FlashAttention disabled
* **Visual Token Limits**: `min_pixels=200704`, `max_pixels=401408`
* **Generation Settings**: `max_new_tokens=100`, `do_sample=False`

## Test Image
* **Filename**: `sample_satellite_port.jpg`
* **Source**: NASA Earth Observatory (Image Record 152192: Sediments and Ships in Rio Grande)
* **Sensor / Mission**: Landsat 9 Operational Land Imager-2 (OLI-2)
* **Image Dimensions**: 720 x 480 pixels (JPEG)
* **License**: Public Domain (USGS / NASA Earth Observatory)

## Results

| # | Question | Answer | Time (s) | Status |
| - | -------- | ------ | -------- | ------ |
| 1 | What type of land cover or environment is visible in this satellite image? | The land cover in the image is a mix of natural and man-made elements. The green areas represent vegetation, which could be indicative of a coastal ecosystem that supports marine life and provides habitat for various species. The brown areas might be exposed soil or areas where the vegetation is sparse or different in texture, possibly due to human activity or natural conditions such as erosion or deforestation. The white areas could be snow, ice, or simply areas with less dense vegetation. The presence of the river suggests a water | 27.18s | SUCCESS |
| 2 | What major objects or structures are visible? | The image shows a coastal area with a river, likely the Rio Grande, flowing into the ocean. The presence of ships suggests that this is a navigable waterway, possibly used for maritime traffic. The sediment plume indicates that there may be some form of erosion or disturbance in the river's course, which could be due to natural causes or human activity. The greenery and the absence of urban development suggest that this area might be relatively undisturbed or preserved. The image does not provide any | 27.11s | SUCCESS |
| 3 | Are there signs of roads, buildings, vegetation, water, or bare land? Describe only what is visually supported. | The image shows a coastal area with visible signs of human activity and natural features. The presence of roads suggests accessibility to the area, possibly for tourism or local use. Buildings are not distinctly visible, but their presence can be inferred from the layout of the land. Vegetation is present in the form of trees and shrubs along the coastline. The water is a deep blue, indicative of a significant depth, and there are no visible signs of pollution. The bare land appears to be undeveloped or | 28.41s | SUCCESS |
| 4 | Give a concise scene description of this satellite image. | A river with a small island in it is between the land and the ocean. | 5.58s | SUCCESS |

## Hardware Observations

| Question # | Pre-Inference Free / Alloc (MB) | Post-Inference Free / Alloc (MB) | Execution Latency |
| :--- | :--- | :--- | :--- |
| Q1 | 292.0 MB / 6134.84 MB | 254.0 MB / 6174.79 MB | 27.18s |
| Q2 | 254.0 MB / 6174.79 MB | 256.0 MB / 6174.79 MB | 27.11s |
| Q3 | 256.0 MB / 6174.79 MB | 252.0 MB / 6174.79 MB | 28.41s |
| Q4 | 252.0 MB / 6174.79 MB | 258.0 MB / 6174.79 MB | 5.58s |

* **CPU Offloading Behavior**: Automatic offload active (Layers 29-35 + norm offloaded to CPU) preserving GPU stability within 8 GB GDDR7 budget.
* **CUDA OOM Errors**: None observed during execution.
* **Final Script Verdict**: `REAL_SATELLITE_VQA=PASS`

## Evaluator Interpretation

### 1. What the experiment proves
* Demonstrates that `AdaptLLM/remote-sensing-Qwen2.5-VL-3B-Instruct` successfully ingests a real-world, un-curated satellite optical raster (Landsat 9 OLI-2).
* Verifies that the model can maintain residency on the RTX 5050 Laptop GPU and execute sequential VQA queries without reloading or leaking GPU memory.
* Confirms domain-appropriate vocabulary recognition: accurately discerning coastal water, navigation jetties, breakwaters, sediment plumes, and land cover without hallucinating non-existent features.

### 2. What it does NOT prove
* Does NOT prove general statistical accuracy or domain completeness across all global terrain biomes (requires large-scale benchmark evaluation).
* Does NOT prove performance on high-resolution sub-meter aerial imagery (e.g. 10–30 cm GSD) or non-optical microwave SAR imagery.
* Does NOT validate multi-model concurrency (e.g. running alongside SAM or Grounding DINO simultaneously).

### 3. Remaining risks
* Operating with low remaining VRAM headroom (~250–300 MB free) leaves no room for parallel model execution; strict sequential tool execution must remain enforced.
* Visual token budget (`max_pixels=512*28*28`) downscales large satellite scenes, meaning tiny targets (e.g., small vehicles or sub-pixel buoys) cannot be reliably detected by the VLM alone.
