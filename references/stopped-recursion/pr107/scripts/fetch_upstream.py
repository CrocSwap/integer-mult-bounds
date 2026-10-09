#!/usr/bin/env python3
"""Fetch the immutable manuscript used by this audit (standard library only)."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "adc7f1241b42e322a6451854ab7e4b4c146bf78a"
PAPER = "preprints/Integer-multiplication-below-n-log-n-September-23-2026"
SECTIONS = ["00-introduction", "01-history", "02-streams", "03-motifs",
            "04-swap", "05-layers", "06-transforms", "07-resampling",
            "08-assembly", "09-exact-arithmetic", "10-transposition",
            "11-grouped-rectangles"]
FILES = {
    "LICENSE": "LICENSE",
    "README.md": PAPER + "/README.md",
    "formalization.yaml": "lean/formalization.yaml",
    "build/main.tex": PAPER + "/build/main.tex",
    "build/references.bib": PAPER + "/build/references.bib",
    **{f"build/sections/{s}.tex": f"{PAPER}/build/sections/{s}.tex" for s in SECTIONS},
    **{f"build/figures/{s}.tex": f"{PAPER}/build/figures/{s}.tex"
       for s in ["proof-map", "multiplication-flow"]},
}


def fetch(item):
    local, remote = item
    url = f"https://raw.githubusercontent.com/openai/math/{COMMIT}/{remote}"
    with urlopen(url, timeout=60) as response:
        data = response.read()
    path = ROOT / "upstream" / local
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError(f"Refusing to overwrite changed upstream file: {path}")
    path.write_bytes(data)
    return local, {"url": url, "sha256": hashlib.sha256(data).hexdigest()}


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as pool:
        files = dict(pool.map(fetch, FILES.items()))
    manifest = {"repository": "https://github.com/openai/math", "commit": COMMIT,
                "paper": PAPER, "files": files}
    (ROOT / "upstream" / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Pinned {len(files)} files at {COMMIT}")
