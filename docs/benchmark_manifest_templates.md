# Prescribed benchmark manifest templates

The repository contains a reference-scored runner at `ai/evaluation/prescribed_benchmark_runner.py`. It accepts relative paths under the project root and never turns missing labels into zero scores.

For CDVQA, create a JSON manifest with `task: "CDVQA"` and samples containing `image_path`, `second_image_path`, `query`, `ground_truth`, and optionally `change_direction` (`increased`, `decreased`, or `unchanged`).

For VRSBench, use `task: "VRSBENCH"` with `image_path`, `query`, `ground_truth`; grounding annotations can be retained in `ground_truth_box` and are scored with IoU and recall at 0.5. For SEN1-2 optical/SAR engineering validation, use `task: "OPTICAL_SAR"` with `optical_image_path`, `sar_image_path`, and reference region labels. The application records optical-only, SAR-only and combined evidence in its trace; a metric is reported only when the manifest supplies the corresponding labels.

For sensor-readiness checks, use `task: "ISRO"` and `mode: "readiness"`. This validates that representative Cartosat-2S/RISAT (or approved substitute) rasters are readable, paired, dimension-compatible, and explicitly identified in `sensor_metadata`; it does not require hidden judging annotations and does not claim task accuracy.

Example:

```json
{
  "dataset_name": "CDVQA",
  "source_url": "https://github.com/YZHJessica/CDVQA",
  "version": "test",
  "split": "test",
  "seed": 42,
  "task": "CDVQA",
  "samples": [
    {
      "sample_id": "cdvqa-0001",
      "image_path": "data/benchmarks/cdvqa/t1/0001.png",
      "second_image_path": "data/benchmarks/cdvqa/t2/0001.png",
      "query": "Has the built-up area increased, decreased, or remained unchanged?",
      "ground_truth": "increased",
      "change_direction": "increased"
    }
  ]
}
```

Run it with:

```powershell
.venv\Scripts\python.exe ai\evaluation\prescribed_benchmark_runner.py data/benchmarks/cdvqa/manifest.json --output results/cdvqa_result.json
```

To generate manifests from downloaded official files and run every available
dataset in one pass:

```powershell
python scripts/prepare_prescribed_benchmarks.py --cdvqa-root <CDVQA_TEST_ROOT> --sen1-2-root <SEN1_2_ROOT> --isro-root <AUTHORISED_ISRO_ROOT>
python scripts/run_prescribed_evaluations.py --include-blocked
```

Example readiness manifest:

```json
{
  "dataset_name": "ISRO/SAC representative pair",
  "version": "local-fixture-1",
  "source_url": "https://bhoonidhi.nrsc.gov.in/",
  "task": "ISRO",
  "mode": "readiness",
  "split": "representative_pairs",
  "samples": [{
    "sample_id": "cartosat-risat-001",
    "optical_image_path": "data/fixtures/cartosat_2s_001.tif",
    "sar_image_path": "data/fixtures/risat_001.tif",
    "sensor_metadata": {"optical_sensor": "Cartosat-2S", "sar_sensor": "RISAT"}
  }]
}
```
