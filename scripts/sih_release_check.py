"""Check whether the repository is ready for an official SIH evaluation run."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
required = {
    "CDVQA manifest": ROOT / "data/benchmarks/cdvqa/manifest.json",
    "SEN1-2 manifest": ROOT / "data/benchmarks/sen1_2/manifest.json",
    "ISRO manifest": ROOT / "data/benchmarks/isro/manifest.json",
}
for name, path in required.items():
    print(json.dumps({"check": name, "status": "READY" if path.is_file() else "BLOCKED", "path": str(path)}))
print(json.dumps({"check": "official judging table", "status": "BLOCKED",
                  "reason": "The supplied problem statement contains a placeholder instead of metric weights."}))
print(json.dumps({"check": "clean demonstration", "status": "READY",
                  "command": ".venv\\Scripts\\python.exe scripts\\run_sih_demo.py --run-models"}))
