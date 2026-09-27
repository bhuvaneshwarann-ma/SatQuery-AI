# SatQuery AI — independent project review

> Historical review. Corrections and current verification are recorded in [current implementation](docs/current_implementation.md).

Review date: 26 September 2026. Scope: application architecture, API, routing, inference, geospatial validation, training/evaluation, frontend state, configuration, and tests.

## Overall assessment

SatQuery AI is a substantial local research/demo application with four specialist execution paths and a deterministic multi-tool workflow. The separation of frontend, API, orchestration, and model wrappers is useful. However, several outputs currently overstate what their underlying computation supports, and important data-contract bugs can produce incorrect summaries. It is not ready for public multi-user deployment or operational geospatial decisions.

The strongest contribution is integration: routing natural-language tasks to specialist tools and presenting artifacts and traces in one interface. The project does not yet demonstrate improved model quality from its custom adaptation or validated optical–SAR fusion.

## Verification performed

| Check | Result |
|---|---|
| Frontend production build | Passed: TypeScript and Vite |
| Frontend lint | Completed with 12 warnings, no reported errors |
| Router unit tests | 11/11 passed using available Python 3.14 |
| Python syntax | All 51 Python files under backend, ai, and training parsed successfully |
| Backend test inventory | 42 test methods present; this is not a fresh 42/42 pass |
| Remaining backend/model tests | Blocked: .venv launcher points to an unavailable Python 3.12 executable; system Python lacks torch, Pillow, tifffile, FastAPI, and transformers |
| Targeted router probes | Confirmed explicit VQA counting bypass, threshold default 0.40, and cross-tool parameter warnings |
| Training split inspection | 17 training and 4 validation examples; three image paths shared across both splits |

No model weights were downloaded, no training or expensive benchmark runs were started, and no application source was changed. The previously staged change to docs/results/change_detection_execution_artifact.jpg was preserved. Visual browser behavior was not tested; frontend findings below are source-based.

## Architecture and actual capabilities

- React 19/TypeScript/Vite interface: analysis, results, history, scene explorer, model catalog, and static evaluation pages.
- FastAPI: health, tool registry, multipart analysis, and publicly served result artifacts.
- Deterministic regex router: VQA, grounding/counting, temporal differencing, optical–SAR statistics, and a fixed three-stage compound plan.
- VQA: AdaptLLM Qwen2.5-VL with an optional project LoRA adapter loaded per request.
- Grounding: pretrained Grounding DINO with box/text thresholds; counting uses returned box count.
- Change detection: pretrained ResNet18 feature distances, per-image-pair normalization, and thresholding. A decoder class exists but is disabled in the active inference path.
- Optical–SAR: intensity statistics, correlation, threshold overlay, plus a newly initialized neural network whose weights are not loaded from a trained checkpoint.
- Persistence: browser localStorage for history and local filesystem for uploads/artifacts; no server-side user/job database.

## High-priority findings

### 1. Optical–SAR neural scores are untrained and provenance can be falsely asserted

Sources: ai/inference/optical_sar.py:285, :301, :338.

Every call constructs a fresh DualStreamOpticalSARFusionNetwork without loading learned weights. Its mean output is presented as a joint synergy score. The reported gain is (1 - abs(Pearson correlation)) × 100, so unrelated images can receive a very high “gain”; this does not measure improved task performance. The displayed overlay is an intensity threshold composite, not the neural output.

Provenance is inferred from the filename. Worse, unverified_sar enters the answer branch labeled “Genuine satellite radar.” Renaming a normal image with “sentinel” also changes its classification. Estimated dB values are computed from an 8-bit display image without sensor calibration metadata.

Action: present these as descriptive image statistics only; remove gain/ablation claims until measured on a downstream task. Preserve unknown provenance and require dataset/sensor metadata for verification. Train and evaluate a network before reporting its outputs as learned fusion.

### 2. Compound analysis can report success after a failed specialist

Source: backend/app/services/orchestration_service.py:574–750.

Only stage 1 failure stops execution. Grounding or VQA errors can flow into a final SUCCESS response and a MEDIUM confidence result. Missing detector confidence receives a default score of 0.5. This hides incomplete execution from the frontend and saved history.

Action: propagate failed stages and use a clear partial-result or failure contract; do not manufacture confidence for absent results.

### 3. Temporal narrative does not see the temporal pair

Source: backend/app/services/orchestration_service.py:609–619.

The VQA prompt asks what changed between two dates, but run_vqa receives only T2. Neither T1, the change mask, nor grounded regions are passed to the model. Grounding runs on T1 independently and is not intersected with changed regions. Evidence is collected together, but the narrative is not actually conditioned on the combined evidence.

Action: pass both dates and relevant spatial evidence to a supported paired-image workflow, or restrict the VQA output to a T2 scene description. Remove the “verified scene change description” claim.

### 4. Evidence is overwritten by subsequent requests

Sources: ai/inference/change_detection.py:352; ai/inference/grounding.py:185; ai/inference/optical_sar.py:335.

Each tool writes one fixed artifact filename. Historical results point to that same URL, so later analyses replace earlier evidence. This also risks cross-user image disclosure if deployed publicly. Browser caching can show stale evidence.

Action: use a request/job ID and immutable per-run artifact paths, with a retention policy and access controls where users are involved. Store runtime artifacts outside the documentation folder.

### 5. Single-tool summaries read the wrong evidence fields

Source: backend/app/services/orchestration_service.py:416, :452.

Change detection returns changed_pixels, but the orchestrator reads changed_pixel_count. Optical–SAR returns high_backscatter_count and radar_dominant_anomalies, but the orchestrator reads radar_anomaly_pixel_count. Nonzero detections therefore become zero in some summaries, confidence inputs, and traces. Similar mismatches exist in the older AnalysisService.

Action: define shared typed evidence contracts and validate actual executor responses through orchestration tests.

### 6. Claimed default threshold differs from executed threshold

Sources: backend/app/agent/registry.py:121; backend/app/services/orchestration_service.py:432, :717.

The router supplies 0.40 by default. The executor fallback, README, limitations, and clean execution trace describe 0.30. A direct router probe confirmed the normal API route supplies 0.40. The trace remains 0.30 even for a user-specified threshold.

Action: centralize defaults and record the effective executor parameter in every trace/report.

### 7. Geospatial checks do not establish co-registration

Source: backend/app/services/geospatial_service.py, validate_pair_compatibility and _parse_geokeys.

Equal-sized ordinary images are labeled co_registered=True with 100% overlap even though location is unknown. GeoTIFF pairs may pass with only 80% overlap; affine transforms, resolution equality, and grid origin are not checked. Missing CRS can pass. The transformation matrix tag is collected but not interpreted, so rotated rasters are not correctly handled. The tolerance_ratio argument is unused.

Action: distinguish matching dimensions from verified alignment. Require compatible CRS, transform, resolution, and extent for pixelwise comparison; report alignment as unknown when metadata is absent. Explicitly handle reprojection/resampling or require pre-aligned inputs.

### 8. Training does not mask non-answer tokens

Source: training/train_vqa_lora.py:197–199.

Labels are copied directly from input_ids and passed to the model. The comment promises user-token masking, but no masking happens. Loss therefore includes prompt and image placeholder tokens, not just assistant answer tokens.

Action: mask user, image, padding, and other non-target positions with the ignore index before loss calculation. Check supervised token positions on a tiny example before retraining.

### 9. Before/after comparison is not controlled and baseline metrics are misread

Source: training/evaluate_vqa.py:105–123, :163–166.

The evaluator expects aggregate_metrics.macro_token_f1 and aggregate_metrics.mean_latency_ms. The saved baseline instead uses mean_token_f1 and runtime.average_per_sample_ms. Consequently, the comparison falls back to constants, including 4,250 ms instead of the stored 50,110.82 ms. Baseline category accuracies are hard-coded rather than recalculated from samples.

The adapted evaluator uses 65,536 pixels, while its generated report advertises 200,704–401,408 pixels. It loads historical baseline results rather than rerunning the baseline with the same current settings. Comparability is therefore not established.

Action: run baseline and adapter in one evaluation pipeline with identical inputs, preprocessing, decoding, scoring, hardware, and provenance. Missing measurements should be unavailable, not default numeric values.

### 10. Public API lacks essential resource and filesystem boundaries

Sources: backend/app/api/routes.py; backend/app/services/upload_service.py; backend/app/main.py.

The analysis endpoint accepts arbitrary server filesystem paths without confinement to approved sample/upload directories. Accessible local images can be analyzed and potentially copied into public evidence artifacts. Uploads are copied without an application byte limit; successful uploads and earlier uploads in failed requests have no cleanup lifecycle. There is no authentication, rate limit, bounded job queue, or request ownership.

The asyncio lock serializes work only inside one server process. Multiple workers can still execute models concurrently, and one large raster can exhaust memory even under serialization. The README's zero-OOM guarantee is unsupported.

Action: replace server paths with approved asset IDs, limit bytes/pixels/query size and queue depth, add upload cleanup, and use a GPU worker queue if deploying beyond a local demo. CORS is not authentication.

## Additional correctness and maintainability issues

- **Counting bypass:** explicit task=VQA bypasses counting intent detection. Confirmed with “How many ships are there?” The numerical guarantee therefore applies only to some automatic routes. Counting failures can also be rewritten as zero detections because formatting is not gated on successful grounding.
- **Compound parameter handling:** a valid threshold override is checked against every tool. Grounding/VQA produce unpermitted-parameter warnings, which the orchestrator treats as rejection. Preserve parameters per plan step instead of merging them globally.
- **Counting quality:** raw detector boxes are counted without an explicit duplicate suppression/target validation step in the wrapper. Numerical consistency with boxes is not equivalent to correct object counting.
- **History previews:** uploaded previews are blob URLs stored in localStorage. They stop working after reload or after the original URL is revoked. Persist image data or stable asset references.
- **Frontend progress:** stage changes are timer-driven rather than server-reported. Only one of several timers is cleared, allowing stale stage updates after quick completion/failure. Label estimated progress appropriately or stream actual job events.
- **Frontend state:** switching task modes retains parameters and extra images; these can cause unrelated firewall/pair-validation errors. Preset loads also retain existing parameters. UNREGISTERED_TOOL falls into the success branch in executeAnalysis.
- **API schema drift:** routes return JSONResponse directly, bypassing response-model validation. Extra orchestration fields such as tools_used, limitations, and execution_trace are absent from the frontend response interface.
- **Confidence semantics:** VQA evidence categories are extracted from the generated narrative and then compared with that same narrative. This is not independent visual corroboration. Existing “uncalibrated” labeling is helpful, but high heuristic scores must not imply factual verification.
- **Model lifecycle:** heavy models reload for every request. This favors memory release but contributes to latency. The resource_policy module is not used by the active orchestrator to guarantee a memory budget.
- **Configuration:** .env.example uses VQA_ADAPTER_DIR, but inference reads VQA_LORA_ADAPTER_DIR. DEFAULT_CHANGE_THRESHOLD is not wired into the registry. No dotenv loading is visible. Requirements use lower bounds rather than the pinned dependencies claimed in README.
- **Documentation drift:** README describes a decoder in active change inference although use_decoder defaults false; VQA confidence descriptions disagree; frontend benchmark labels say test split while stored results say validation. Deployment documentation includes planned components not present in the runnable project.
- **Scientific artifacts:** change inference labels every input pair “controlled synthetic,” including user-supplied real imagery. Provenance must come from input metadata, not a fixed string.

## Training and benchmark interpretation

Stored training metadata records one epoch on 17 samples and five optimizer steps, with final logged loss 14.3462. Adapter weights exist, but this audit did not independently rerun training or verify weight deltas.

The training and internal validation sets share three image paths. This is image-level leakage between those splits, not evidence of leakage into the separate RSVQA benchmark. Split by scene/image (and related geographic group), not question alone. The blacklist only compares filenames and exact questions, and silently accepts a missing benchmark manifest; that is weaker than a comprehensive non-leakage guarantee.

Stored results report:

| Measurement | Stored value | Interpretation |
|---|---:|---|
| RSVQA baseline exact match | 35%, 7/20 | Small baseline slice |
| Adapted exact match | 30%, 6/20 | One fewer exact answer; no demonstrated overall gain |
| Baseline/adapted token F1 | 0.2525 / 0.3012 | Higher saved F1, but comparison settings require correction |
| LEVIR macro IoU / F1 | 0.0878 / 0.1535 | Weak building-change baseline |

These are repository-stored measurements, not fresh measurements from this review. Small N and mismatched evaluation settings prevent strong claims about adaptation improvement. The API counting guardrail is also a different path from direct VQA counting evaluation.

## What is already useful

- Clear module boundaries and a restricted tool catalog.
- Genuine pretrained-model integration rather than only static responses.
- Readable trace and evidence structures, plus explicit clarification/error states.
- Image verification and several input/parameter checks.
- Reproducible frontend build and passing basic routing tests.
- Explicit small-benchmark and uncalibrated-score disclosures in several places.
- Saved training metadata, model adapter files, and sample-level benchmark outputs provide a basis for stronger verification.

## Recommended order of work

1. Correct evidence keys, effective thresholds, failure propagation, immutable artifact paths, and SAR provenance/score claims.
2. Repair temporal narrative grounding and counting bypasses; preserve per-tool parameters.
3. Strengthen alignment validation and isolate uploaded/server assets with resource limits.
4. Fix training labels, split by scene, and rerun a controlled baseline/adapter comparison before making improvement claims.
5. Repair the Python environment, lock a tested dependency set, and separate fast contract tests from optional GPU integration tests.
6. Add regressions for the specific failures above, then repair history persistence and connect displayed progress/metrics to authoritative data.
7. Consolidate documentation around the verified current implementation and add deployment infrastructure only when moving beyond a local demo.

The immediate priority is trustworthy results and reproducible evaluation. Adding more models or interface features before these corrections would make the project harder to validate.
