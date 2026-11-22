"""Compare the portable output with the normal bootstrap and weighted constructors."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from compiler_state import bind, construct
from tape_directory import dump, load


def main():
    repository, directory = (Path(name).resolve() for name in sys.argv[1:])
    bootstrap = (
        repository / "research/frequency-weighted-native-multiplier/bootstrap.py"
    )
    with TemporaryDirectory(prefix="native-table-check-") as dirname:
        work = Path(dirname)
        src = work / "source"
        subprocess.run([sys.executable, "-IB", str(bootstrap), str(src)], check=True)
        sys.path.insert(0, str(src))
        original = construct()
        with directory.open("rb") as inp:
            received = bind(load(inp))
        for actual, restored in zip(original[0], received[0], strict=True):
            a, b = actual[-1], restored[-1]
            assert [r.rank_log for r in actual] == [r.rank_log for r in restored]
            assert a.types() == b.types() and a.typed_cells() == b.typed_cells()
            for variants, others in ((a.targets, b.targets), (a.paid, b.paid)):
                assert variants.histogram == others.histogram
                for x, y in zip(variants.variants, others.variants, strict=True):
                    assert x.histogram == y.histogram and list(x) == list(y)
        native = work / "native.dag"
        with native.open("wb") as out:
            count = dump(out, original)
        first = native.read_bytes()
        second = directory.read_bytes()
        assert first == second
        print(
            json.dumps(
                {
                    "native_directory_sha256": hashlib.sha256(first).hexdigest(),
                    "records": count,
                    "bytes": len(first),
                    "typed_cells_per_recipe": 88,
                }
            )
        )


if __name__ == "__main__":
    main()
