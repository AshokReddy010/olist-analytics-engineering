"""CI check: the committed dashboard data must match a fresh export from the models (to a small tolerance,
since parallel aggregation can change the last digits of an average)."""
import json
import math
import sys
from pathlib import Path


def diff(a, b, path="$"):
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return f"{path}: keys differ"
        return next((d for k in a if (d := diff(a[k], b[k], f"{path}.{k}"))), None)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: {len(a)} vs {len(b)} items"
        return next((d for i, (x, y) in enumerate(zip(a, b, strict=True)) if (d := diff(x, y, f"{path}[{i}]"))), None)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return None if math.isclose(a, b, rel_tol=1e-4, abs_tol=1e-6) else f"{path}: {a} vs {b}"
    return None if a == b else f"{path}: {a!r} vs {b!r}"


committed = json.loads(Path(sys.argv[1]).read_text())
fresh = json.loads(Path(sys.argv[2]).read_text())
problem = diff(committed, fresh)
if problem:
    print(f"::error::site/data/olist.json is stale ({problem}); run python scripts/export_web.py and commit")
    sys.exit(1)
print("dashboard data matches the models")
