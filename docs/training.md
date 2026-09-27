# Training and evaluation

Training masks user/prompt/image-prefix and padding positions, supervises assistant answer tokens, verifies exact prompt-prefix token agreement, seeds training, and handles partial gradient-accumulation groups. Existing checkpoints are protected from overwrite.

Related port, synthetic-port and proxy-SAR imagery stay in one group. The current dataset contains only two independent groups: the seeded split is five training questions and sixteen validation questions. A larger scene-diverse corpus is needed before generalization claims. Missing benchmark manifests fail the leakage audit; the existing filename/query checks are not a comprehensive geographic overlap audit.

The evaluator runs the same loaded model with adapters disabled and enabled for each benchmark example. Both paths share resolution, query, decoding and answer normalization. Baseline values are measured rather than filled from constants. Reports include per-sample predictions, failures, environment, manifest hash, and settings. Timing covers generation only, excluding shared preprocessing/model loading.

Legacy adapter and benchmark files remain for provenance. Use results/vqa_controlled_comparison.json for the corrected comparison, and inspect its failure count before interpreting scores. Baseline remains the application default; enabling an adapter requires VQA_LORA_ADAPTER_DIR.
## Reproducible BigEarthNet.txt adaptation

The repository includes a paired S1/S2 manifest preparer and a training config. The annotation parquet and Sentinel image archive are intentionally provisioned by the operator because the archive is large.

```powershell
.venv\Scripts\python.exe training\data\prepare_bigearthnet_txt.py BigEarthNet.txt.parquet Encoded-BigEarthNet --output training/data/bigearthnet_txt_train.json --split train --limit 800
.venv\Scripts\python.exe training\data\prepare_bigearthnet_txt.py BigEarthNet.txt.parquet Encoded-BigEarthNet --output training/data/bigearthnet_txt_validation.json --split validation --limit 40
.venv\Scripts\python.exe training\train_vqa_lora.py --config training/configs/bigearthnet_txt.yaml
```

The preparer groups rows by Sentinel patch, preserves the S1/S2 paths and annotation type, and fails if the requested split is absent. Training masks prompt and padding tokens, so only assistant answers contribute to loss.
