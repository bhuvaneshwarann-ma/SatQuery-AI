# SatQuery AI

A local satellite-image analysis workbench with a React/TypeScript interface, FastAPI gateway, deterministic task routing, and four specialist tools.

## Current capabilities and limits

| Tool | Implementation | Output and limits |
|---|---|---|
| VQA | AdaptLLM Qwen2.5-VL-3B | Single-image answer; no calibrated confidence |
| Grounding/counting | Grounding DINO | Clipped, deduplicated boxes; counts are detector outputs, not guaranteed true counts |
| Change detection | Pretrained ResNet18 feature distances | Unsupervised thresholded differences; active decoder is disabled |
| Optical/SAR | Display-image intensity statistics | Pearson correlation and intensity overlay; no learned fusion, calibrated dB, or improvement claim |

Compound requests run change detection, grounding on T1, and a scene description of T2. The narrative does not claim verified temporal reasoning. Failed stages fail the workflow. Non-georeferenced image pairs have **unknown alignment**, even when their dimensions match.

Results have immutable artifact names. Uploads are deleted after request processing. History stores bounded image thumbnails locally. The Evaluation page reads completed measured results from the backend rather than hard-coded metrics.

## Starting the installed app

Run `./start-local.ps1` in PowerShell from the project folder. It starts both services in persistent hidden processes and writes logs to `scratch/server-logs`. Then open http://127.0.0.1:5173. Run it again after a computer restart; existing listening services are left running.

## Local setup

The verified environment uses Python 3.12.10. Exact installed versions are recorded in `requirements-lock.txt`; frontend versions are in `frontend/package-lock.json`. The GPU lockfile is specific to this Windows/CUDA environment. For a different platform, install an appropriate PyTorch build and validate a separate lockfile.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm ci
npm run dev -- --host 127.0.0.1 --port 5173
```

In a separate terminal from the project root:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

The frontend development server proxies `/api` to the backend. For a built frontend, configure a same-origin reverse proxy for `/api`; a static file host alone does not provide the API.

Set environment variables in the launching shell. `.env.example` is a reference; the application does not load it automatically. VQA uses the baseline by default. Set `VQA_LORA_ADAPTER_DIR` explicitly to opt into an evaluated adapter; no improvement is assumed.

## Validation

```powershell
.venv\Scripts\python.exe -m unittest discover -s backend/tests -p "test_*.py"
cd frontend
npm run build
npm run lint
```

The fast suite skips three model integration tests. To include those, set `SATQUERY_MODEL_TESTS=1` before running the suite. Models may need cached weights, substantial memory, and network access for initial retrieval. Serialization does not guarantee against OOM.

## Training and controlled comparison

```powershell
.venv\Scripts\python.exe training/data/prepare_vqa.py
.venv\Scripts\python.exe training/data/validate_vqa.py
.venv\Scripts\python.exe training/train_vqa_lora.py
.venv\Scripts\python.exe training/evaluate_vqa.py
```

Training now supervises assistant tokens only and keeps related scenes in one split. Existing checkpoints are never overwritten: choose a new `output_dir` for another training run. The corrected checkpoint is `training/checkpoints/satquery_vqa_lora_corrected`.

The curated corpus has only two scene groups, yielding 5 training and 16 validation questions with the current seeded split. This is a small pipeline demonstration, not a generalization benchmark. The controlled evaluator runs baseline and adapted inference on the same 20 RSVQA examples, with identical preprocessing and scoring. Outputs: `results/vqa_controlled_comparison.json` and `.md`. Failure counts and timing scope are explicit. Historical before/after files used inconsistent settings and must not be treated as a controlled comparison.

## Storage and deployment boundaries

- API images: up to 20 MiB each, 4 million pixels; entire request limited to 61 MiB.
- Query: up to 4,000 characters; up to four admitted analysis requests, serialized in one process.
- Direct server paths: confined to bundled `data/samples`; other images must be uploaded.
- Upload staging: `data/uploads`, cleaned when processing finishes.
- Evidence: `data/artifacts`, retained until explicitly removed. Run the maintenance tool in dry-run mode before applying retention cleanup.
- No authentication or user isolation: bind to loopback and use one worker. Public hosting requires authenticated ownership, protected artifact delivery, and a dedicated bounded GPU worker queue.

See `docs/current_implementation.md` for the current engineering status. Earlier phase/freeze/audit documents are historical snapshots and may describe superseded behavior or claims.
