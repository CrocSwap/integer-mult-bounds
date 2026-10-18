"""Read-only, stdlib-only certificate and signed lifting-reduction replay."""

import hashlib
import json
import random
import types
from pathlib import Path

import lattice

HERE = Path(__file__).resolve().parent


def read_json(path):
    lattice.need(path.stat().st_size <= 100_000, "JSON size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def load_basis():
    witness = read_json(HERE / "HNF7.json")
    lattice.need(
        set(witness) == {"rank", "rows"}
        and type(witness["rank"]) is int
        and witness["rank"] == 7,
        "witness schema",
    )
    sparse = witness["rows"]
    lattice.need(type(sparse) is list and len(sparse) == 256, "sparse rows")
    rows = []
    for row in sparse:
        lattice.need(type(row) is list and len(row) <= 256, "sparse row size")
        dense = [0] * 256
        previous = -1
        for entry in row:
            lattice.need(type(entry) is list and len(entry) == 2, "sparse entry")
            j, x = entry
            lattice.need(
                type(j) is type(x) is int and previous < j < 256 and x != 0,
                "sparse column order",
            )
            dense[j] = x
            previous = j
        rows.append(dense)
    return lattice.validate_basis(rows)


def predecessor():
    pin = read_json(HERE / "PREDECESSOR.json")
    source = (HERE / "vendor/lifting.py").read_bytes()
    lattice.need(
        hashlib.sha256(source).hexdigest() == pin["sha256"], "predecessor hash"
    )
    lattice.need(
        pin["head"] == "b12bbaeb5ca2e83f15433fc2dd0ba3b766595281", "predecessor head"
    )
    module = types.ModuleType("pinned_lifting")
    exec(compile(source, "pinned_lifting.py", "exec"), module.__dict__)
    return module


def gaussian(value):
    return list(zip(value[::2], value[1::2], strict=True))


def flatten(value):
    return [x for pair in value for x in pair]


def reference(value, rank, old, inverse=False):
    n = 1 << rank
    plan = [(j, 0) for j in range(n)]
    return flatten(old.kernel(gaussian(value), rank, plan, plan, inverse=inverse))


def check_columns(basis, old):
    rng = random.Random(1043033)
    x = [rng.randrange(-1024, 1024) for _ in range(256)]
    forward, backward = lattice.lift(x, 7), lattice.lift(x, 7, inverse=True)
    image = lattice.prefix_member(basis, 7)
    for j in range(256):
        z = [row[j] for row in basis]
        uz = [row[j] for row in image]
        actual = reference([a + b for a, b in zip(x, z, strict=True)], 7, old)
        lattice.need(
            actual == [a + b for a, b in zip(forward, uz, strict=True)],
            "forward basis shift",
        )
        actual = reference(
            [a + b for a, b in zip(x, uz, strict=True)], 7, old, inverse=True
        )
        lattice.need(
            actual == [a + b for a, b in zip(backward, z, strict=True)],
            "inverse image shift",
        )
        scalar = [16 * int(i == j) for i in range(256)]
        lattice.need(lattice.canonical(scalar, basis) == [0] * 256, "uniform inclusion")
    return 256


def check_signed(basis, old):
    rng = random.Random(343)
    count = 0
    for bits in (1, 4, 17, 257, 2048, 4090):
        for _ in range(3):
            value = [rng.getrandbits(bits) * rng.choice((-1, 1)) for _ in range(256)]
            expected = reference(value, 7, old)
            lattice.need(lattice.split(value, basis) == expected, "signed split")
            remainder = lattice.canonical([x % 16 for x in value], basis)
            lattice.need(
                lattice.canonical(value, basis) == remainder, "low-bit extraction"
            )
            lattice.need(
                lattice.lift(expected, 7, inverse=True) == value, "paired return"
            )
            count += 1
    return count


def check_wrapped(basis, old):
    """Four blocks with synthetic monomial wrappers, not a native recipe replay."""
    left = [((137 * j + 43) % 512, j % 4) for j in range(512)]
    right = [((29 * j + 71) % 512, (j // 3) % 4) for j in range(512)]
    rng = random.Random(512)
    for bits in (7, 1024):
        value = [
            (
                rng.getrandbits(bits) - rng.getrandbits(bits),
                rng.getrandbits(bits) - rng.getrandbits(bits),
            )
            for _ in range(512)
        ]
        expected = old.kernel(list(value), 7, left, right)
        inside = old.permute(value, right)
        result = []
        for start in range(0, 512, 128):
            result.extend(
                gaussian(lattice.split(flatten(inside[start : start + 128]), basis))
            )
        lattice.need(old.permute(result, left) == expected, "wrapped four-block split")
        lattice.need(
            old.kernel(list(expected), 7, left, right, inverse=True) == value,
            "wrapped paired return",
        )
    return 2


def check_small(old):
    import itertools

    count = 0
    for value in itertools.product(range(-1, 2), repeat=4):
        value = list(value)
        for inverse in (False, True):
            lattice.need(
                lattice.lift(value, 1, inverse) == reference(value, 1, old, inverse),
                "literal signed pair",
            )
            count += 1
    z = [0] * 256
    z[0] = 8
    try:
        lattice.ideal(z, 7)
    except ValueError:
        pass
    else:
        raise ValueError("half-integral translation was accepted")
    # Integrality alone is insufficient already at rank two.
    a = [1] + [0] * 7
    shift = [2] + [0] * 7
    actual = lattice.lift([u + v for u, v in zip(a, shift, strict=True)], 2)
    predicted = [
        u + v for u, v in zip(lattice.lift(a, 2), lattice.ideal(shift, 2), strict=True)
    ]
    lattice.need(actual != predicted, "integer final image is not a prefix certificate")
    return count


def compute():
    basis = load_basis()
    old = predecessor()
    counts = [lattice.index_counts(rank) for rank in range(1, 8)]
    lattice.need(
        [sum(row) for row in counts] == [2, 6, 15, 34, 75, 161, 343], "index sequence"
    )
    diagonal = [basis[i][i] for i in range(256)]
    return dict(
        status="PASS_P104_COUPLED_LIFTING_RESIDUES",
        rank_stage_counts=counts,
        rank7_index_log2=343,
        scalar_index_log2=1024,
        four_block_index_log2=1372,
        scalar_four_block_index_log2=4096,
        diagonal_counts={str(v): diagonal.count(v) for v in (1, 2, 4, 8, 16)},
        basis_columns=check_columns(basis, old),
        signed_fixtures=check_signed(basis, old),
        wrapped_fixtures=check_wrapped(basis, old),
        signed_pair_cases=check_small(old),
        inverse_lattice="U(Gamma), not Gamma",
    )


def main():
    actual = compute()
    expected = read_json(HERE / "RESULT.json")
    lattice.need(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "typed result receipt mismatch",
    )
    print(json.dumps(actual, indent=2))


if __name__ == "__main__":
    main()
