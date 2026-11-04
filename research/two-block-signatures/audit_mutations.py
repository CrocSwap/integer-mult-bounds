#!/usr/bin/env python3
"""Run positive controls and introduce one semantic fault per private copy."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
PRIMARY, CENSUS = "verify.py", "census_check.py"
# Use one exact substitution per source fault. Reject only the named diagnostic.
FAULTS = [
    ("oversubscribed pivots", "signatures.py", "if u < 0 or w < 0:", "if u < -1 or w < -1:", CENSUS, "binary space census disagrees"),
    ("ignore A saturation", "signatures.py", "if (p-v.aa-v.ma == 0) != (q-v.bb-v.bm == 0):", "if False:", CENSUS, "binary space census disagrees"),
    ("ignore B saturation", "signatures.py", "if (q-v.bb-v.mb == 0) != (p-v.aa-v.am == 0):", "if False:", CENSUS, "binary space census disagrees"),
    ("only one slack for an isolated bit", "signatures.py", "(v.am and v.mb) or (v.ma and v.bm)", "(v.am or v.mb) or (v.ma or v.bm)", CENSUS, "binary space census disagrees"),
    ("admit odd one-row core", "signatures.py", 'return "ok" if v.am or v.ma else "binary one A"', 'return "ok"', CENSUS, "binary space census disagrees"),
    ("admit odd one-column core", "signatures.py", 'return "ok" if v.mb or v.bm else "binary one B"', 'return "ok"', CENSUS, "binary space census disagrees"),
    ("apply binary exception to F4", "signatures.py", 'binary=field == "F2"', 'binary=field in ("F2","F4")', PRIMARY, "binary 1x1"),
    ("ignore ternary pivot scalar", "signatures.py", '"F3": 2 if u*w%3 == 1 else 1', '"F3": 1', PRIMARY, "constructed witness is singular"),
    ("keep both core entries", "signatures.py", 'if field == "F2" and u*w % 2:', 'if False:', PRIMARY, "constructed witness is singular"),
    ("reverse reader block", "binary_oracle.py", "2*spread(full^e,n)", "spread(full^e,n)", CENSUS, "binary space census disagrees"),
    ("transpose cofactor incorrectly", "matching_oracle.py", "cofactors[j][i] |=", "cofactors[i][j] |=", CENSUS, "oracle reported a forbidden mask"),
    ("retain intersecting spaces", "ternary_oracle.py", "if a & b:", "if False:", CENSUS, "ternary complement multiplicity"),
    ("omit monomial orbit weight", "ternary_oracle.py", "total[key] += weight*count", "total[key] += count", CENSUS, "ternary total pair count"),
    ("omit doubly saturated patterns", "counts.py", " + both(p)*both(q)", " + 0", PRIMARY, "ordinary count formula differs"),
    ("miss one odd side", "counts.py", '"binary one B":odd_side(q,p)', '"binary one B":0', PRIMARY, "exception count formula differs"),
    ("drop coefficient basis multiplicity", "zero_one_census.py", "hist[key] += weight*bases[upper]*number",
     "hist[key] += weight", "zero_one_census.py", "zero-one literal four-port census"),
    ("reduce rational complement modulo two", "zero_one_census.py", "if not sum(c*lower[j] for j,c in dual):",
     "if not sum(c*lower[j] for j,c in dual) % 2:", "zero_one_census.py", "zero-one literal four-port census"),
    ("corrupt prior source", "source/6691-PROOF.md", "## Lemma 1:", "## Altered lemma:", PRIMARY, "retained source hash"),
]
DATA_FAULTS = [
    ("flatten separating tariff", "PRICE-CERTIFICATES.json", PRIMARY, "price does not strictly separate"),
    ("perturb convex weights", "PRICE-CERTIFICATES.json", PRIMARY, "convex combination differs from profile"),
    ("erase signed matrix entry", "SIX-PORTS.json", PRIMARY, "stored witness certificate differs"),
    ("inflate ternary multiplicity", "SIX-PORTS.json", CENSUS, "stored per-label multiplicity differs"),
]


def change_data(name, original):
    data = json.loads(original)
    if name == "flatten separating tariff":
        next(row for row in data if "prices" in row)["prices"] = [1]*7
    elif name == "perturb convex weights":
        next(row for row in data if "mixture" in row)["mixture"][0]["weight"] += 1
    elif name == "erase signed matrix entry":
        data[0]["rational"][0] = "......"
    else:
        data[0]["pairs_per_label_F2_F3"][1] += 1
    return json.dumps(data).encode()


def invoke(root, entry, optimize):
    extra = ["-O"] if optimize else []
    return subprocess.run([sys.executable,"-I",*extra,"-W","error","-B",str(root/entry)],cwd=root,
                          capture_output=True,text=True,encoding="utf-8",timeout=120)


def test_fault(root, name, filename, original, faulty, entry, why):
    (root/filename).write_bytes(faulty)
    for opt in (False, True):
        proc = invoke(root,entry,opt)
        last = proc.stderr.strip().splitlines()[-1:] or [""]
        if proc.returncode == 0 or last[0] != "ValueError: "+why:
            raise ValueError(f"{name} optimized={opt}: expected {why!r}, got {last[0]!r}")
    (root/filename).write_bytes(original)
    return [name,why]


def audit():
    results = []
    with tempfile.TemporaryDirectory(prefix="two-ports-") as tmp:
        root = Path(tmp)
        for f in PACKAGE.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                dest = root/f.relative_to(PACKAGE)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(f,dest)
        for entry in (PRIMARY,CENSUS,"zero_one_census.py"):
            positives = []
            for opt in (False,True):
                proc = invoke(root,entry,opt)
                if proc.returncode:
                    raise ValueError(proc.stderr[-600:])
                positives.append(json.loads(proc.stdout))
            if positives[0] != positives[1]:
                raise ValueError("private-copy positive receipts differ")
        for name,filename,old,new,entry,why in FAULTS:
            raw = (root/filename).read_bytes()
            if raw.count(old.encode()) != 1:
                raise ValueError("ambiguous mutation target "+name)
            results.append(test_fault(root,name,filename,raw,raw.replace(old.encode(),new.encode()),entry,why))
        for name,filename,entry,why in DATA_FAULTS:
            raw = (root/filename).read_bytes()
            results.append(test_fault(root,name,filename,raw,change_data(name,raw),entry,why))
    return dict(status="PASS_TWO_BLOCK_MUTATIONS", positive_controls=6, rejected_probes=2*len(results), faults=results)


if __name__ == "__main__":
    print(json.dumps(audit(),sort_keys=True))
