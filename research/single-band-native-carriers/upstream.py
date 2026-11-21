"""Load the immutable numerical and routing operations for this construction."""

from functools import cache
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


@cache
def install():
    inputs = HERE / "inputs"
    folder = inputs / "triangular"
    record = json.loads((inputs / "triangular.json").read_bytes())
    for name, digest in record["sha256"].items():
        if sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"The retained source differs at {name}")
    sys.path.insert(0, str(folder))
    from retained import install as open_triangular

    result = open_triangular()
    review = inputs / "review"
    for name, pin in json.loads((inputs / "review.json").read_bytes()).items():
        if sha256((review / name).read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError(f"The source for the Clifford generator or review differs at {name}")
    grade = result[-1] / "research/grade14-native-realization"
    sys.path.extend(map(str, (review, grade, grade / "retained")))
    return result
