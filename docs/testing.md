# Testing

Run the fast suite from the repository root:

```powershell
.venv\Scripts\python.exe -m unittest discover -s backend/tests -p "test_*.py"
```

Three model integration cases are skipped unless SATQUERY_MODEL_TESTS=1. Fast tests cover routing, counting, stage failures, evidence fields, threshold telemetry, immutable artifact naming, geospatial shifts, unknown alignment, upload limits, cleanup, queue capacity, path confinement, and trace serialization. Specialists are mocked only where model execution is not the subject of the test. A small real optical/SAR statistics test requires no downloaded weights.

Run npm run build and npm run lint from frontend. Lint warnings are reported separately from errors. Tests do not establish scientific model accuracy. The controlled VQA comparison is a separate experiment using a completed corrected adapter.
## SIH representative demonstrations

Validate all five problem-statement examples without model loading:

```powershell
.venv\Scripts\python.exe scripts\run_sih_demo.py
```

Run the actual specialists when the local model environment is ready:

```powershell
.venv\Scripts\python.exe scripts\run_sih_demo.py --run-models
```

The output records the selected tools, task plan, parameters and final result for each query. The model run is deliberately opt-in because a full sequence loads several large specialists.

## Prescribed benchmark workflow

Prepare manifests from the official files supplied by the dataset owners:

```powershell
python scripts/prepare_prescribed_benchmarks.py --cdvqa-root <CDVQA_TEST_ROOT> --sen1-2-root <SEN1_2_ROOT> --isro-root <AUTHORISED_ISRO_ROOT>
python scripts/run_prescribed_evaluations.py --include-blocked
```

The evaluator refuses to convert missing annotations into zero scores. CDVQA
requires its answer and direction annotations, SEN1-2 requires reference
regions for class metrics, and ISRO mode validates pair compatibility because
the official judging annotations are hidden.

Before submitting to SIH, run the release readiness check:

```powershell
python scripts\sih_release_check.py
```

It reports missing external manifests and the missing official judging table explicitly.
