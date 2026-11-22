"""Install the frequency-weighted producer in the authenticated signed multiplier."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from subprocess import run
import sys

HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent / "tiered-native-multiplier"


def install(destination):
    path = Path(destination).resolve()
    pins = json.loads((HERE / "SOURCES.json").read_bytes())
    for name, digest in pins["local_sources"].items():
        if sha256((HERE / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Unexpected weighted producer input: {name}")
    run(
        [sys.executable, "-IB", str(PREDECESSOR / "bootstrap.py"), str(path)],
        check=True,
    )
    for phase in ("before", "after"):
        for name, digests in pins["runtime_images"].items():
            if sha256((path / name).read_bytes()).hexdigest() != digests[phase]:
                raise ValueError(f"Unexpected {phase} image for {name}")
        if phase == "before":
            run(
                ["git", "apply", "--no-index", str(HERE / "runtime.patch")],
                cwd=path,
                check=True,
            )
            for name in ("grades.py", "typed_raw.py", "typed_transport.py"):
                copyfile(HERE / name, path / name)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    install(parser.parse_args().destination)
