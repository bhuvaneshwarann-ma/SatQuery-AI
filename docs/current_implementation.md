# Current implementation — 27 September 2026

This document and the root README supersede earlier phase, freeze and audit status documents. PROJECT_REVIEW_2026-09-26.md records the original findings; it is not the current defect list.

## Completed corrections

1. Evidence field names and threshold defaults are consistent. The trace reports effective parameters. Artifacts use unique UUID filenames in data/artifacts. Tool failures propagate without fabricated zero detections or success/confidence.
2. Numerical queries cannot bypass grounding via an explicit VQA selection. Boxes are clipped, invalid coordinates removed, and overlapping duplicates suppressed. Compound plan parameters stay with their owning tools. Paired VQA receives both observations; single-image VQA remains explicitly single-observation.
3. GeoTIFF pairs require matching CRS and affine grids, including rotation. Unreferenced equal-sized pairs carry an explicit unknown-alignment warning. API paths are confined to bundled samples. Uploads have byte/pixel limits and are removed in a finally block. Total body size and admitted request counts are bounded. Runtime artifacts are never served from documentation.
4. Optical/SAR execution uses descriptive intensity statistics. The untrained fusion score, fabricated gain, uncalibrated physical dB estimate, and filename-based genuine-sensor claim have been removed. VQA confidence is unavailable; unchanged area and correlation are not accuracy scores.
5. Training masks prompt/padding tokens and verifies the token prefix. Scene groups do not overlap between training and validation. The new checkpoint preserves the legacy adapter. The evaluator measures both variants using identical inputs, decoding and scoring; no fallback baseline metrics are used. Resume verifies checkpoint/manifest/settings and completed sample pairs.
6. The existing Python 3.12 environment was verified, not rebuilt. requirements-lock.txt records its exact dependencies; requirements.txt pins direct dependencies. pip check found no broken requirements. Fast tests are separated from optional downloaded-model checks.
7. History saves bounded persistent thumbnails; previously stored expired blob URLs are discarded. Mode changes clear stale parameters/irrelevant inputs. Unknown tool statuses are errors. Timer-generated execution stages were removed. The Evaluation page reads a completed report through /api/evaluation. Raw and compact execution traces remain distinct.
8. The legacy AnalysisService delegates to the same orchestrator, avoiding divergent policy. Explicitly configured adapters fail visibly when unavailable instead of silently falling back to a different model.
9. Temporal multi-tool execution now passes T1 and T2 to paired VQA with change and grounding cues. Optical/SAR execution now measures candidate optical regions in the co-located SAR image and passes both images plus those measurements to paired VQA. These are evidence-grounded workflows; semantic accuracy and physical SAR calibration still require benchmark validation.
10. TIFF ingestion is bounded by decoded size, supports explicit zero-based band mappings, records nodata/display-stretch metadata, and preserves SHA-256 input provenance. Evaluation mode requires approved PNG/JPEG hashes or verified pair grids. Results can be exported as Markdown or JSON from the Results page.

## Verification

- Full backend suite: **63 tests passed**, including real Grounding DINO, ResNet change detection, and optical/SAR execution. No integration skips in the full run.
- Frontend production build: passed. Lint: no errors; 12 pre-existing style/hook warnings remain after removing the new unnecessary dependency warning.
- Dependency consistency: pip check passed.
- Corrected training: completed on CPU, one epoch, five examples, two optimizer steps; final logged answer-token loss 3.5008. This is not an accuracy measure.
- Controlled benchmark: all 40 generations completed with zero failures. Baseline exact match 30.0%, adapted 35.0%; token F1 0.3012 and 0.3512. See results/vqa_controlled_comparison.json and .md. Eighteen paired results were checkpointed before an interruption and the last two were resumed with the same settings and adapter. Intermediate .progress files are not final results.
- Browser: application and analysis form loaded. End-to-end browser submission/history reload was not fully verified; backend integration checks and frontend compilation passed.
- Focused regression suite after paired workflow changes: **65 tests passed**, with 3 optional model tests skipped unless `SATQUERY_MODEL_TESTS=1`.

## Deliberate limits

The application remains a local, single-user, single-worker demo. No public deployment, authentication or cross-user access control is claimed. The per-process lock is not a multi-worker GPU scheduler and does not guarantee no OOM. Artifact names are unguessable but that is not authorization.

The curated corpus contains only two scene groups. The current seeded split has five training and sixteen held-out questions. More independent scenes and stronger geographic/content leakage auditing are needed. No model improvement is assumed; baseline inference remains the default until an adapter is explicitly selected. BigEarthNet.txt metadata is documented as an external source; its paired Sentinel image archive is not bundled in this repository.

Non-georeferenced pairs are accepted for pixel-grid exploration with unknown alignment; they are not automatically registered. TIFF display conversion is not a complete radiometric/geospatial processing pipeline. Grounded object counts can still have false positives, misses and residual duplicates. Multi-tool outputs are independent evidence summaries, not validated attribution of changes to individual boxes.

Artifacts remain on disk for reproducibility. Preview retention cleanup using:

```powershell
.venv\Scripts\python.exe -m backend.maintenance --older-than-days 30
```

Add --apply only to delete the listed generated files. No cleanup of pre-existing user artifacts was performed during this work. The previously staged documentation image and legacy adapter were preserved.
