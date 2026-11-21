"""Compare runtime sources and independent reviewers with their original Git objects."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from upstream import install


def verify(repo):
    _, installed, _, source = install()
    pins = []
    tri = json.loads((HERE / "inputs/triangular.json").read_bytes())
    for file, digest in tri["sha256"].items():
        pins.append(
            (
                HERE / "inputs/triangular" / file,
                digest,
                tri["commit"],
                tri["directory"] + "/" + file,
            )
        )
    middle = json.loads((HERE / "inputs/triangular/inputs/retained.json").read_bytes())
    for file, item in middle["members"].items():
        pins.append((installed / file, item["sha256"], middle["commit"], item["path"]))
    oldest = json.loads((installed / "inputs/origins.json").read_bytes())
    for file, item in oldest["members"].items():
        pins.append((source / file, item["sha256"], item["commit"], file))
    for file, item in json.loads((HERE / "inputs/review.json").read_bytes()).items():
        pins.append((HERE / "inputs/review" / file, item["sha256"], item["commit"], item["path"]))
    pins.append(
        (
            HERE / "strong-bit.json.gz",
            "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326",
            "fb9b6a7b0d27da1cf98430893a3016bf811e2aa4",
            "research/p104-live-relative-gain/BINARY-CANDIDATE.json.gz",
        )
    )
    for name, digest in json.loads((HERE / "inputs/complex-source.json").read_bytes()).items():
        pins.append(
            (
                HERE / "inputs/complex-source" / name,
                digest,
                "fb9b6a7b0d27da1cf98430893a3016bf811e2aa4",
                "research/p104-live-relative-gain/" + name,
            )
        )
    for file, digest, revision, name in pins:
        data = subprocess.check_output(["git", "-C", str(repo), "show", revision + ":" + name])
        if sha256(data).hexdigest() != digest or data != file.read_bytes():
            raise ValueError(f"The source differs at {revision}:{name}")
    print("PASS_NATIVE_SCALE_SOURCE_BINDINGS", len(pins))


if __name__ == "__main__":
    verify(Path(sys.argv[1]))
