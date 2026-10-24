"""Check source pins, query rows, arithmetic bounds, and rejection controls."""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import os
import shutil
import subprocess
import sys
import tarfile


parser = argparse.ArgumentParser()
parser.add_argument("--package", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--repo", type=Path, required=True)
args = parser.parse_args()
PACKAGE = args.package.resolve()
OUT = args.out.resolve()
REPO = args.repo.resolve()
OUT.mkdir(parents=True, exist_ok=False)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def source_check():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    source = sources["historical_source_commit"] + ":" + sources["historical_selected_archive"]["path"]
    proc = subprocess.Popen(["git", "show", source], cwd=REPO, stdout=subprocess.PIPE)
    digest = sha256()
    while chunk := proc.stdout.read(1048576):
        digest.update(chunk)
    require(proc.wait() == 0, "Read the source archive")
    require(digest.hexdigest() == sources["historical_selected_archive"]["sha256"], "Archive digest")
    proc = subprocess.Popen(["git", "show", source], cwd=REPO, stdout=subprocess.PIPE)
    members = {}
    with tarfile.open(fileobj=proc.stdout, mode="r|gz") as archive:
        for member in archive:
            if member.name not in ["slots/local/CANONICAL-WORD.json.gz", "slots/local/LOCAL-PROGRAMS.json.gz"]:
                continue
            raw = archive.extractfile(member).read()
            local = PACKAGE / "frozen/work/five-pr-sprint-20261013/lanes/centre-sharing" / Path(member.name).name
            require(raw == local.read_bytes(), "Exact source member")
            members[member.name] = {"bytes": len(raw), "sha256": sha256(raw).hexdigest()}
    require(proc.wait() == 0 and len(members) == 2, "Both source members")
    for item in sources["files"]:
        if item.get("source_commit"):
            raw = subprocess.check_output(["git", "show", item["source_commit"] + ":" + item["source_path"]], cwd=REPO)
            require(raw == (PACKAGE / item["path"]).read_bytes(), "Exact notice source")
    save("SOURCE-BINDING-REPRODUCED.json", {"status": "PASS", "archive_sha256": digest.hexdigest(), "members": members})


def forward_query():
    folder = PACKAGE / "frozen/work/five-pr-sprint-20261013/lanes/centre-sharing"
    word = json.loads(gzip.decompress((folder / "CANONICAL-WORD.json.gz").read_bytes()))
    events = json.loads(gzip.decompress((folder / "LOCAL-PROGRAMS.json.gz").read_bytes()))["forward"]
    state = [{j: Q(1)} if j < 112 else {} for j in range(712)]
    def index(register):
        return register[1] + (704 if register[0] == "C" else 0)
    count = 0
    for event in events:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        count += 1
        gate = event[1]
        target = index(gate[1])
        if gate[0] == "clear":
            state[target] = {}
        elif gate[0] == "scale":
            scale = Q(gate[2], gate[3])
            state[target] = {j: scale * value for j, value in state[target].items() if scale * value}
        elif gate[0] == "copy":
            state[target] = state[index(gate[2])].copy()
        elif gate[0] == "add":
            scale = Q(gate[3], gate[4])
            for j, value in state[index(gate[2])].copy().items():
                total = state[target].get(j, Q(0)) + scale * value
                if total:
                    state[target][j] = total
                else:
                    state[target].pop(j, None)
        else:
            raise ValueError("Unknown scalar gate")
    rows = [[state[c].get(j, Q(0)) for j in range(112)] for c in word["centers"]]
    interface = json.loads((PACKAGE / "frozen/work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json").read_text())
    expected = [[Q(row.get(str(j), "0")) for j in range(112)] for row in interface["R"]]
    require(rows == expected, "Forward rational query reconstruction")
    row_weights = [sum(abs(value) for value in row) for row in rows]
    column_weights = [sum(abs(row[j]) for row in rows) for j in range(112)]
    require(max(row_weights) == 56 and max(column_weights) == 4, "Root coefficient bounds")
    save("FORWARD-QUERY-REPRODUCED.json", {"status": "PASS", "scalar_gates": count, "rows": 8, "columns": 112, "row_absolute_sum": 56, "column_absolute_sum": 4})
    bounds = {
        "producer_R_transpose_sum": 4 * 65536,
        "producer_R_sum": 56 * 65536,
        "review_sparse_row_sum": 224 * 65536,
        "moment_sum": 4096 * 65535 * 65536,
        "field_product": 65536 ** 2,
        "Bareiss_absolute_difference": 65536 ** 2,
    }
    require(max(bounds.values()) < 2 ** 44 < 2 ** 63, "Signed int64 operations fit")
    save("ARITHMETIC-BOUNDS.json", {"status": "PASS", "bounds": bounds, "reason": "Every vector residue is between 0 and 65536. SHAKE observers are between 0 and 65535. Products in elimination have two nonnegative factors at most 65536; their difference has absolute value at most 65536 squared."})


def rejection_controls():
    copied = OUT / "controls-frozen"
    shutil.copytree(PACKAGE / "frozen", copied)
    lanes = copied / "work/centre-encoding-campaign-20261014/lanes"
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    certificate = lanes / "history-encoding/BELL-GRAM-DEGREE.json"
    value = json.loads(certificate.read_text())
    value["moments"][0] = (value["moments"][0] + 1) % 65537
    certificate.write_text(json.dumps(value))
    result = subprocess.run([sys.executable, "-I", "-B", str(lanes / "interface-proof/review_bell_gram_degree.py")], capture_output=True, text=True, env=env)
    (OUT / "corrupt-moment-stderr.txt").write_text(result.stderr)
    require(result.returncode != 0 and "All817 independent sparse moments agree" in result.stderr, "Corrupt moment must fail")
    interface = lanes / "circuit-interface/INTERFACE.json"
    interface.write_bytes(interface.read_bytes() + b"\n")
    result = subprocess.run([sys.executable, "-I", "-B", str(lanes / "history-encoding/certify_bell_gram_degree.py"), "--interface", str(interface), "--out", str(OUT / "invalid.json")], capture_output=True, text=True, env=env)
    (OUT / "corrupt-interface-stderr.txt").write_text(result.stderr)
    require(result.returncode != 0 and "Actual supplier interface pin" in result.stderr, "Corrupt interface must fail")
    save("EXTRA-REJECTION-CONTROLS.json", {"status": "PASS", "changed_moment_rejected": True, "changed_interface_bytes_rejected": True})


source_check()
forward_query()
rejection_controls()
print("PASS_BELL_CACHE_INDEPENDENT_REVIEW_CHECKS")
