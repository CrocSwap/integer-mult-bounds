"""Compare the portable snapshot with Git blobs from the pinned PRs and main."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
parser = ArgumentParser(description=__doc__)
parser.add_argument("checkout", type=Path)
args = parser.parse_args()
manifest = json.loads((here / "inputs/origins.json").read_text())
sources = json.loads((here / "SOURCES.json").read_text())
runtime = manifest["members"]
for name, receipt in runtime.items():
    content = subprocess.check_output(
        ["git", "-C", str(args.checkout), "show", receipt["commit"] + ":" + name]
    )
    if sha256(content).hexdigest() != receipt["sha256"]:
        raise ValueError("The source blob differs for " + name)
prior = sources["retained_scalar_kernel"]
content = subprocess.check_output(
    ["git", "-C", str(args.checkout), "show", prior["ref"] + ":" + prior["original"]]
)
if (here / prior["path"]).read_bytes() != content or sha256(content).hexdigest() != prior["sha256"]:
    raise ValueError("The bounded scalar source differs")
if (
    sha256((here / "inputs/runtime.tar.gz").read_bytes()).hexdigest()
    != sources["immutable_input_archive_sha256"]
):
    raise ValueError("The runtime archive differs from its source record")
print(
    "PASS_PINNED_STOCK_SOURCES",
    len(runtime),
    "members",
    len({r["sha256"] for r in runtime.values()}),
    "unique blobs and the C scalar source",
)
