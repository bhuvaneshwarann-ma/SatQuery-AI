# Grounding Validation

## Model
* **Model Name**: `IDEA-Research/grounding-dino-tiny`
* **Architecture**: Swin-T Grounding DINO Zero-Shot Object Detector
* **Configuration**: `box_threshold=0.3`, `text_threshold=0.25`
* **Inference Device**: cuda

## Test Image
* **Filename**: `sample_satellite_port.jpg`
* **Source**: NASA Earth Observatory (Landsat 9 OLI-2, Rio Grande)
* **Dimensions**: 720 x 480 pixels (JPEG)

## Results

| Prompt | Detections | Confidence (Min - Max) | Time (s) | Status |
| :----- | ---------: | ---------------------: | -------: | :----- |
| `ship` | 1 | 0.46 - 0.46 | 1.42s | SUCCESS |
| `boat` | 1 | 0.47 - 0.47 | 0.50s | SUCCESS |
| `river` | 1 | 0.84 - 0.84 | 0.36s | SUCCESS |
| `water` | 1 | 0.78 - 0.78 | 0.37s | SUCCESS |
| `island` | 1 | 0.50 - 0.50 | 0.36s | SUCCESS |

## Hardware Observations
* **VRAM Before Loading**: Free: 7070.0 MB | Alloc: 0.0 MB
* **VRAM After Loading**: Free: 6398.0 MB | Alloc: 660.03 MB
* **VRAM After Inference**: Free: 4708.0 MB | Alloc: 763.11 MB
* **Memory Footprint**: ~660.03 MB allocated on GPU (extremely lightweight)
* **CPU Offloading**: None required (model fits entirely in GPU VRAM)
* **Final Script Verdict**: `GROUNDING_TEST_RESULT=PASS`

## Evidence
Visual grounding with coordinate bounding boxes provides essential spatial proof for SatQuery AI:
1. **Direct Spatial Grounding**: Bounding boxes localize exactly where the user query targets are located on the satellite canvas, eliminating black-box ambiguities.
2. **Dual-Layer Validation**: Textual claims made by the VLM (e.g., 'ships are present') can be programmatically cross-verified against Grounding DINO detections.
3. **Downstream Segmentation Anchor**: Bounding box outputs feed directly as spatial prompt tokens into SAM ViT-B to derive pixel-accurate masks.
4. **Annotated Visual Artifact**: Generated detection visualization is saved at `docs/results/grounding_sample_result.jpg`.

## Limitations
* **Scale Discrepancy**: Small watercraft (<15 pixels in Landsat 30m GSD imagery) can be missed or confused with white-cap wave crests.
* **Amorphous Geographic Boundaries**: Large amorphous features like `water` or `river` encompass sprawling continuous regions better suited for semantic segmentation than rectangular bounding boxes.
* **Threshold Sensitivity**: Standard `box_threshold=0.30` requires careful tuning across varying sensor lighting conditions to prevent false positives in urban clutter.
