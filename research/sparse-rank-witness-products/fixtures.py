# SPDX-License-Identifier: Apache-2.0
"""Fixed bounded rational interface fixtures, produced by Nick Petalas."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import random
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load the declared Python source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problem(a):
    return {"schema": "rational-rank-problem/v1", "matrix": a}


def dense_fixture():
    """Dense rectangular map with rational row/column scales and rank eight."""
    rng = random.Random(5789)
    left = [[rng.randrange(-4, 5) for _ in range(8)] for _ in range(48)]
    right = [[rng.randrange(-4, 5) for _ in range(64)] for _ in range(8)]
    return problem([
        [str(Q(sum(left[i][k] * right[k][j] for k in range(8)),
               2 ** (i % 5) * 3 ** (j % 4))) for j in range(64)]
        for i in range(48)
    ])
