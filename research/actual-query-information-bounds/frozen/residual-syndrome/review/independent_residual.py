"""Audit the residual formula with source matrices and separate exact examples."""

from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import subprocess
import tarfile

import sympy as s


ROOT = Path(__file__).resolve().parents[5]
REPO = ROOT / "worktrees/k5-centre-sharing"
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
MEMBER = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
HERE = Path(__file__).resolve().parent


def require(value, label):
    if not value:
        raise RuntimeError(label)


def elementary(event, coupling=None):
    a = s.eye(8)
    if event["kind"] == "local":
        i = 2 * event["pair"]
        if event["reverse"]:
            a[i, i + 1] = -1
        else:
            a[i + 1, i] = 1
        if coupling is not None:
            return s.eye(8 * coupling.rows) + s.kronecker_product(a - s.eye(8), coupling)
    elif event["kind"] == "bridge":
        i, j, q = event["dst"], event["src"], event["coefficient"]
        a[2 * i, 2 * j] = q
        a[2 * j + 1, 2 * i + 1] = -q
    elif event["kind"] == "terminal":
        a = s.diag(*[s.Matrix([[0, 1], [-1, 0]]) for _ in range(event["pairs"])])
    return a


def exact_case(recipe, bank_rows, centre_rows, removed):
    dim = centre_rows[0].cols
    width = centre_rows[0].rows
    require(all(r * r.T == 56 * s.eye(width) for r in centre_rows), "Row Gram")
    actual = s.eye(8 * dim)
    ideal = s.eye(8 * dim)
    for event in recipe:
        if event["kind"] == "terminal":
            continue
        if event["kind"] == "local":
            stage = event["stage"]
            r = centre_rows[stage]
            k = s.eye(dim) - r.T * r / 4 if stage in removed else s.eye(dim)
            native = elementary(event, k)
        else:
            native = s.kronecker_product(elementary(event), s.eye(dim))
        actual = native * actual
        ideal = s.kronecker_product(elementary(event), s.eye(dim)) * ideal
    residual = ideal.inv() * actual - s.eye(8 * dim)
    if not removed:
        require(residual.is_zero_matrix, "Empty subset")
        return {"stages": [], "rank": 0}
    v = s.Matrix.vstack(*[s.kronecker_product(bank_rows[i, :], centre_rows[i]) for i in sorted(removed)])
    omega = s.kronecker_product(s.diag(*[s.Matrix([[0, 1], [-1, 0]])] * 4), s.eye(dim))
    gram = v * omega * v.T
    blocks = len(removed)
    lower = s.zeros(blocks * width)
    for i in range(blocks):
        for j in range(i):
            lower[i * width:(i + 1) * width, j * width:(j + 1) * width] = gram[i * width:(i + 1) * width, j * width:(j + 1) * width]
    middle = 4 * s.eye(v.rows) - lower
    require(residual == omega * v.T * middle.inv() * v, "Interaction factorization")
    require(residual.rank() == v.rank(), "No decoder cancellation")
    require(residual != omega * v.T * (4 * s.eye(v.rows) + lower).inv() * v,
            "Wrong triangular sign was not detected")
    null = v.T.nullspace()
    if null:
        basis = s.Matrix.hstack(*null)
        compressed = basis.T * middle * basis
        require(compressed.det() != 0, "Kernel compression")
    return {"stages": sorted(removed), "rank": residual.rank(), "syndrome_nullity": len(null)}


def main():
    raw = subprocess.check_output(["git", "show", BASE + ":" + ARCHIVE], cwd=REPO)
    require(sha256(raw).hexdigest() == "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754", "Archive pin")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        member = archive.extractfile(MEMBER).read()
    require(sha256(member).hexdigest() == "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518", "Controller pin")
    template = json.loads(gzip.decompress(member))
    recipe = template["recipe"]
    omega = s.diag(*[s.Matrix([[0, 1], [-1, 0]])] * 4)
    prefix = s.eye(8)
    rows = []
    for event in recipe:
        if event["kind"] == "local":
            source = 2 * event["pair"] + int(event["reverse"])
            rows.append(s.eye(8)[source, :] * prefix)
        step = elementary(event)
        require(step * omega * step.T == omega, "Source step is not symplectic")
        prefix = step * prefix
    require(prefix == s.eye(8), "Old endpoint")
    v = s.Matrix.vstack(*rows)
    relation = v.T.nullspace()
    require(len(relation) == 1, "Bank relation dimension")
    c = relation[0] / relation[0][0]
    require(list(c) == [1, -1, -1, 1, 1, -1, -1, 1, 1], "Bank relation")
    minors = [v[[i for i in range(9) if i != j], :].det() for j in range(9)]
    require(all(value != 0 for value in minors), "A maximal proper subset is dependent")
    gram = v * omega * v.T
    area = sum(c[i] * c[j] * gram[i, j] for i in range(9) for j in range(i))
    compression = s.Rational(4, 56) * (c.T * c)[0] - area
    require(area == 4 and compression == -s.Rational(47, 14), "Kernel form")
    data_sets = []
    for replica in range(16):
        calls = [call for call in template["calls"] if call["replica"] == replica]
        require([call["stage"] for call in calls] == list(range(9)), "Replica stages")
        families = {owner[0] for call in calls for owner in call["owners"] if owner[0] < 14336}
        require(families == set(range(896 * replica, 896 * (replica + 1))), "Replica data namespace")
        data_sets.append(families)
    require(len(set.union(*data_sets)) == sum(map(len, data_sets)), "Replica data overlap")
    r = s.Matrix([[6, 4, 2, 0, 0, 0], [0, 0, 0, 6, 4, 2]])
    one = s.Matrix([[6, 4, 2, 0, 0, 0], [0, 0, 0, 2, 6, 4]])
    zero = s.Matrix([[2, 6, 4, 0, 0, 0], [0, 0, 0, 2, 6, 4]])
    examples = {}
    for name, alternate, shared in (("two_shared", r, 2), ("one_shared", one, 1), ("none_shared", zero, 0)):
        centres = [r, alternate, r, alternate, r, r, alternate, r, alternate]
        result = exact_case(recipe, v, centres, set(range(9)))
        require(result["syndrome_nullity"] == shared and result["rank"] == 18 - shared, "Common-image rank")
        examples[name] = result
    centres = [r, zero, r, one, zero, r, one, zero, r]
    proper = [exact_case(recipe, v, centres, set(range(9)) - {missing}) for missing in range(9)]
    require(all(item["rank"] == 16 for item in proper), "Maximal proper residual rank")
    per_replica = 72 - s.Rational(8, 183)
    require(s.ceiling(per_replica) == 72 and s.ceiling(16 * per_replica) == 1152, "Whole-array count")
    report = {
        "status": "PASS_INDEPENDENT_RESIDUAL_ALGEBRA_REVIEW",
        "source_base": BASE,
        "controller_member_sha256": sha256(member).hexdigest(),
        "bank_rows": [list(map(int, row)) for row in v.tolist()],
        "bank_relation": list(map(int, c)),
        "maximal_proper_minors": list(map(int, minors)),
        "area": str(area), "compression": str(compression),
        "independent_data_replicas": len(data_sets),
        "data_families_per_replica": 896,
        "exact_examples": examples,
        "maximal_proper_residual_examples": proper,
        "conditional_whole_array_bounds": {"per_replica": 72, "all_replicas": 1152},
        "dependencies_not_reproved": ["Native global normal form", "Routed-projection dimension bound"],
        "scope": "Exact algebra review. No claim about concurrent workspace, native rank cost, or supplier admission.",
    }
    (HERE / "INDEPENDENT-RECEIPT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
