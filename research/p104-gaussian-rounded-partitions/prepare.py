"""Install the parity-rounded Gaussian target from exact #8054 sources."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile

HEAD = "f6f4ecd5dd717ce2b155dd564469e9693ac90f6d"
PINS = {
    "prepare.py": "775c7ff81f05b7df6d9ad3aa244bbcc539c383be96e1d07855881c53417f9844",
    "RESULT.json": "1315e92c43f0c23a8584beb64217411572a1a2aa1178969ca220ce53073ea8c5",
}
CAMPAIGN_PINS = {
    "prototype.py": "f86a898583ffec816871cd94f8580daa3201d0892185cc0484a1cb77211eceb8",
    "prototype.json": "c9157f73ac7c36aa128dff44f5138d9c31c09a8d89951ffdc3cd9660c40cb237",
    "receipt.json": "38e1e56e529d6371186e8420fc6e5bf03df7bd6fa7cca2ec41dd2cda0d687aad",
    "verified.json": "18cc056fcf09bf52df1a8d4c24df09da97bc119412a13cb5eb10977a75dd3bac",
}
OLD = {
    "installations.py": "983fdc1fd09ec8727d8c573ba171d52a0fc0200437f9233f249a2aa5e7be9503",
    "retimed_supplier.py": "bdc5bf5e5228fe1179951a074508f59a90f6d2634f5af8e2d5a097329e484755",
    "unpowered_price.py": "04cac4d63621c55111d870597f3a84d53786177aea5c2f831b16cbe6a6de188b",
    "check_complete.py": "a73bb6819014f7e61b73ab95bf28ec74d1f1607c0a58ad60315d391ab82557c1",
    "check_installation.py": "dc7552b8585c7ac48d69ca64ddc17747ffda53b1bb00a2c64cacc38a6214a956",
    "check_extended_stop.py": "3d8f1f1181124991e468f69a839f8148910bbe5b1cbd2c1c6a7ac7c80b2c0525",
    "check_positive_word.py": "a88de880627489764668f6a3ec34f4861f61bd49cc74d3547d3ef18ee017dbe4",
    "check_nonzero_eight.py": "adb442191016a90d9d84fda978850c1d40518e62821f41238285b9f42158b34e",
    "transport.py": "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9",
}
EDIT = {
    "installations.py": (
        ("Q(133940467, 2**35)", "Q(4286126377, 2**40)"),
        ('Q(".0038981730255")', 'Q(".0038982016137")'),
    ),
    "retimed_supplier.py": (
        ("from transport import Recipe","from transport import Recipe, paid_axis_count"),
        ("yield job.select(range(width // 2))\n                    yield job.select(range(width // 2, width))",
         "first = paid_axis_count(F(1, 4), width)\n                    yield job.select(range(first))\n                    yield job.select(range(first, width))"),
        ("slots.extend((F(1, 2), F(1, 2)))", "slots.extend((F(1, 4), F(3, 4)))"),
        ('raise ValueError("Each split needs a positive even column count")',
         'raise ValueError("The native word needs a positive even column count")\n        if columns < 4:\n            raise ValueError("Each quarter split needs at least four columns")'),
    ),
    "unpowered_price.py": (
        ("paid[F(1, 2)] = 2012", "paid[F(1, 4)] = 1006\n    paid[F(3, 4)] = 1006"),
        ("    if r == F(1, 2):\n        low, high = power_interval(2, t)\n        return (UNIT * UNIT // high, -(-UNIT * UNIT // low))\n    return power_interval(int(r), t)",
         "    rank = F(r)\n    x, y = power_interval(rank.numerator, t)\n    if rank.denominator == 1:\n        return x, y\n    a, b = power_interval(rank.denominator, t)\n    return UNIT * x // b, -(-UNIT * y // a)"),
    ),
    "check_complete.py": (
        ("assert max(max(targets), max(paid)) <= 1032 and min(paid) >= Q(1, 2)",
         "assert max(max(targets), max(paid)) <= 1032"),
        ("if ambient == 134:\n        assert (factor", "if ambient == 134:\n        assert min(paid) >= Q(1, 2)\n        assert (factor"),
        ("assert ambient == 1224 and cells[448, 1032] == 1\n        assert factor**256 < 2**39",
         "assert ambient == 1224 and cells[448, 1032] == 1\n        assert min(paid) == Q(1, 4) and c.denominator <= 2**40\n        assert (Q(100, 99)**250 > 4 and c < Q(1, 250)\n                and Q(99, 100)*Q(2, 9) > Q(19, 100))\n        assert Q(10) * Q(106, 100) / (Q(996, 1000)*Q(99, 100)*Q(19, 100)) < 64\n        for r, k in cells:\n            error = Q(-1, 2) if r == Q(1, 4) else Q(1, 2) if r == Q(3, 4) else Q(0)\n            assert 8*k - 10*r + min(0, error) >= 0\n            assert 10*k - 8*r + max(0, error) < 10*k and error <= 8*r\n        assert factor**256 < 2**39"),
        ('"gaussian_c_decimal": "0.003898180642863736"', '"gaussian_c_decimal": "0.003898209231010696"'),
        ('"extended_kappa": "0.0038981730255"', '"extended_kappa": "0.0038982016137"'),
        ('(binary["cells"], positive["cells"]) == (24, 54)', '(binary["cells"], positive["cells"]) == (24, 55)'),
    ),
    "check_installation.py": (
        ("105216, 564142, 54", "105216, 564142, 55"),
    ),
    "check_extended_stop.py": (
        ("105216,564142,54", "105216,564142,55"),
        ("F(133940467,2**35)", "F(4286126377,2**40)"),
    ),
    "check_positive_word.py": (
        ("both halves of every split", "both packets of every split"),
        ("from strong_complex import artifacts, word", "from strong_complex import artifacts, word\nfrom transport import paid_axis_count"),
        ("inputs = [Job(i, range(2 * k))", "columns = 6\n    inputs = [Job(i, range(columns * k))"),
        ("slots=2448", "slots=columns * 1224"),
        ("Raw(w, machine).native(inputs, 2)", "Raw(w, machine).native(inputs, columns)"),
        ("len(request.axes) == 2 * grade", "len(request.axes) == paid_axis_count(grade, columns)"),
        ("2*sum(sizes) == 13440384", "columns*sum(sizes) == 40321152"),
        ("len(fields), 2*sum(sizes)", "len(fields), columns*sum(sizes)"),
        ("complete two-column raw path", "complete six-column raw path"),
    ),
    "check_nonzero_eight.py": (
        ("An exact tensor representation makes the 16-column", "An exact tensor representation makes the 48-column"),
        ("from periodic import Job", "from periodic import Job\nfrom transport import paid_axis_count"),
        ("jobs = [Job(i, range(2 * k))", "columns = 6\n    jobs = [Job(i, range(columns * k))"),
        ("enumerate((2, 16))", "enumerate((columns, 8 * columns))"),
        ("slots=2 * 1224", "slots=columns * 1224"),
        ("Raw(w, physical).native(jobs, 2)", "Raw(w, physical).native(jobs, columns)"),
        ("nonzero = {2: 0, 16: 0}", "nonzero = {columns: 0, 8*columns: 0}"),
        ("len(j.axes) == 2 * g", "len(j.axes) == paid_axis_count(g, columns)"),
        ('"independent columns", 2, 16', '"independent columns", columns, 8*columns'),
        ("2 * sum(sizes)", "columns * sum(sizes)"),
        ("2**18,\n        2**144", "2**54,\n        2**432"),
    ),
}


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def replace(path, edits):
    text = path.read_text()
    for old, new in edits:
        if text.count(old) != 1:
            raise ValueError(f"Expected one occurrence of {old!r} in {path.name}")
        text = text.replace(old, new)
    path.write_text(text)


def materialize(source, proof, work):
    for name, pin in PINS.items():
        if digest(source / name) != pin:
            raise ValueError(f"#8054 differs at {name}")
    evidence = {"prototype.py": proof / "prototype.py", "prototype.json": proof / "prototype.json",
                "receipt.json": proof / "price" / "receipt.json", "verified.json": proof / "proof" / "verified.json"}
    for name, path in evidence.items():
        if digest(path) != CAMPAIGN_PINS[name]:
            raise ValueError(f"Round 370 differs at {name}")
    result = json.loads(evidence["receipt.json"].read_text())
    assert result["comparator"] == HEAD and Fraction(result["kappa"]) == Fraction(".0038982016137")

    runpy.run_path(str(source / "prepare.py"))["materialize"](source / "peer8053", work)
    for name, sha in OLD.items():
        if digest(work / name) != sha:
            raise ValueError(f"Materialized #8054 differs at {name}")
    prototype = runpy.run_path(str(evidence["prototype.py"]))
    with tempfile.TemporaryDirectory(prefix="transport-edit-") as temp:
        edited = Path(temp) / "transport.py"
        prototype["patch"](work / "transport.py", edited)
        assert digest(edited) == json.loads(evidence["prototype.json"].read_bytes())["patched"]
        (work / "transport.py").write_bytes(edited.read_bytes())

    for name, edits in EDIT.items():
        replace(work / name, edits)


def install(work, tree):
    sys.path.insert(0, str(work))
    runpy.run_path(str(work / "bootstrap.py"))["install"](tree)
    sys.path.insert(0, str(tree))
    from upstream import install as dependencies
    dependencies()


def generate(work):
    with tempfile.TemporaryDirectory(prefix="quarter-candidate-") as temp:
        install(work, Path(temp) / "tree")
        from check_complete import all_results, ranks, certify
        from collections import Counter
        result = all_results()
        assert Fraction(result["profiles"]["extended"]["kappa"]) == Fraction(".0038982016137")
        positive = result["positive"]
        assert (positive["productive"], positive["paid"], positive["cells"]) == (105216, 564142, 55)
        targets, paid = ranks()
        previous = Counter(paid)
        del previous[Fraction(1, 4)], previous[Fraction(3, 4)]
        previous[Fraction(1, 2)] = 2012
        assert certify(Fraction(4286126377, 2**40), (targets, previous))[0] < 0
    (work / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_PARITY_ROUNDED_GAUSSIAN_PRICE", result["profiles"]["extended"]["kappa"])


def focused(work, mode):
    with tempfile.TemporaryDirectory(prefix="quarter-check-") as temp:
        install(work, Path(temp) / "tree")
        files = {"positive": "check_positive_word.py", "nonzero": "check_nonzero_eight.py"}
        runpy.run_path(str(work / files[mode]), run_name="__main__")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--proof", type=Path)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--run", choices=("cost", "positive", "nonzero"))
    parser.add_argument("--child", action="store_true")
    a = parser.parse_args()
    work = a.work.resolve()
    if a.child:
        if a.run in ("positive", "nonzero"):
            focused(work, a.run)
        else:
            materialize(a.source.resolve(), a.proof.resolve(), work)
            generate(work)
    else:
        proc = subprocess.run([sys.executable, "-IB", __file__, "--child", *sys.argv[1:]], timeout=60)
        if proc.returncode:
            raise SystemExit(proc.returncode)
        if a.run == "cost":
            proc = subprocess.run([sys.executable, "-IB", str(work / "verify.py"), "cost"], timeout=60)
            raise SystemExit(proc.returncode)
