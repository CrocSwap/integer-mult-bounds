"""Run one exact signed copy or the unchanged phase census on the installed package."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent.parent / "p104-compact-rounded-partitions"
COPY_COUNTS = ((6, 52608, 282576, 4480128, 16), (474, 52608, 281568, 353930112, 15))

# Exact edits of the installed verifier's fixture only. Native code is unchanged.
EDITS = (
    ("def check():", "def check(copy_index):\n    import retimed_supplier"),
    ("    fields={i:RayField(stock) for i in range(len(sizes))}", """
    sizes = tuple(sizes)
    count = len(w.targets)
    first, last = copy_index * count, (copy_index + 1) * count
    middle = len(w.paid) + SPLITS
    selected_paid = tuple(paid)[:middle] if copy_index == 0 else tuple(paid)[middle:]
    assert len(sizes) == 2 * count == 105216 and len(paid) == 564144

    class Owners(dict):
        checking = False

        def check_key(self, key):
            # The native scratch allocator uses tuple tokens, distinct from
            # the original numbered owners.
            if self.checking and isinstance(key, int):
                assert first <= key < last, "Cross-copy owner access"

        def __getitem__(self, key):
            self.check_key(key)
            return super().__getitem__(key)

        def __setitem__(self, key, value):
            self.check_key(key)
            return super().__setitem__(key, value)

        def pop(self, key, *args):
            self.check_key(key)
            return super().pop(key, *args)

    fields = Owners({i: RayField(stock) for i in range(len(sizes))})"""),
    ("        exact=tuple(final_ray(i) for i in origins)", """
        if copy != copy_index:
            exp[owner] = fields[owner].data
            continue
        exact=tuple(final_ray(i) for i in origins)"""),
    ("    it=Raw(w,raw).native(jobs,columns)", """
    assert retimed_supplier.SCALES == SCALES
    retimed_supplier.SCALES = (SCALES[copy_index],)
    fields.checking = True
    it=Raw(w,raw).native(jobs[first:last],columns)"""),
    ("    for grade in paid:", "    for grade in selected_paid:"),
    ("    assert set(fields)==set(range(len(sizes))) and all(f.live and f.writes>0 for f in fields.values())", """
    fields.checking = False
    retimed_supplier.SCALES = SCALES
    assert set(fields) == set(range(len(sizes)))
    assert all(f.live and (f.writes > 0) == (first <= i < last) for i, f in fields.items())"""),
    ("    assert all(nonzero.values())", """
    assert nonzero[widths[1-copy_index]] == 0
    actual = (widths[copy_index], count, completed, columns*sum(sizes[first:last]),
              nonzero[widths[copy_index]])
    assert actual == COPY_COUNTS[copy_index], actual
    selected_owner = pawn + copy_index * count
    exact_output = sha256(repr(fields[selected_owner].data).encode("ascii")).hexdigest()
    assert stock[1] == 115056, stock"""),
    ("    print(\"PASS_SCALED_POSITIVE_RAW\")", """
    assert writes == 71808 and stock[0] == 0, (writes, stock)
    print("COPY_RESULT", json.dumps({"copy": copy_index, "columns": actual[0],
          "owners": actual[1], "paid": actual[2], "output_axes": actual[3],
          "nonzero_called": actual[4], "writes": writes, "peak_handles": stock[1],
          "exact_output_sha256": exact_output, "released": stock[0]}, sort_keys=True))"""),
    ('if __name__=="__main__":\n    check()', ""),
)

SOURCE_FILES = (
    "COMPACT-PRICE.json", "PEER-SOURCE.json", "RESULT.json", "integer-prototype.py",
    "peer8055.tar.gz", "prepare.py", "verify.py",
)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def check_union(receipts):
    if len(receipts) != 3:
        raise ValueError("Both signed copies and the phase receipt are required")
    data = {row["mode"]: row for row in receipts}
    if set(data) != {"0", "1", "phase"}:
        raise ValueError("Distinct signed copies and the unchanged phase census are required")
    inputs = data["phase"]["inputs_sha256"]
    if any(row["inputs_sha256"] != inputs for row in data.values()):
        raise ValueError("Projection receipts have different source pins")
    copies = [data[str(i)]["result"] for i in range(2)]
    keys = ("columns", "owners", "paid", "output_axes", "nonzero_called")
    for i, row in enumerate(copies):
        if row["copy"] != i or tuple(row[k] for k in keys) != COPY_COUNTS[i] or row["released"] != 0:
            raise ValueError("A signed projection is missing its exact owner or paid coverage")
    paid, owners, axes, writes = (sum(row[key] for row in copies) for key in
                                  ("paid", "owners", "output_axes", "writes"))
    assert (paid, owners, axes, writes) == (564144, 105216, 358410240, 143616)
    phase = data["phase"]["result"]
    assert (phase["native_graphs_per_copy"], phase["all_copy_delta_at_residue_2"],
            phase["all_copy_delta_at_residue_0"]) == (48, 189072, 0)
    return {"paid": paid, "owners": owners, "output_axes": axes, "owner_writes": writes,
            "phase": phase, "inputs_sha256": inputs}


def project(work, runtime, mode):
    if mode == "phase":
        result = subprocess.check_output(
            [sys.executable, "-IB", str(work / "check_phase_passes.py"), str(runtime)])
        report = json.loads(result)
        assert report["all_copy_delta_at_residue_2"] == 189072
        assert report["all_copy_delta_at_residue_0"] == 0
        assert report["one_real_graph_callbacks"] == {
            "columns=16,bundle=1": {"all_phase_calls": 80165, "returned_paid": 5674},
            "columns=158,bundle=1": {
                "all_phase_calls": 84104, "nonzero_constant_at_zero": 3939, "returned_paid": 5674,
            },
            "columns=158,bundle=2": {"all_phase_calls": 80165, "returned_paid": 5674},
        }
        print("PHASE_RESULT", json.dumps(report, sort_keys=True), flush=True)
        return report

    index = int(mode)
    source = work / "check_gaussian.py"
    original = source.read_text()
    amended = original
    for before, after in EDITS:
        if amended.count(before) != 1:
            raise ValueError(f"Expected one exact fixture point: {before}")
        amended = amended.replace(before, after)
    projected = work / "check_projected_gaussian.py"
    projected.write_text(
        "from hashlib import sha256\nimport json\n"
        + f"COPY_COUNTS = {COPY_COUNTS!r}\n"
        + amended + f"\ncheck({index})\n"
    )
    child = subprocess.Popen(
        [sys.executable, "-IB", str(projected), str(runtime)],
        stdout=subprocess.PIPE, text=True,
    )
    receipt = []
    with child.stdout:
        for line in child.stdout:
            print(line, end="", flush=True)
            if line.startswith("COPY_RESULT "):
                receipt.append(json.loads(line.removeprefix("COPY_RESULT ")))
    if child.wait() or len(receipt) != 1:
        raise ValueError("The exact signed projection failed")
    assert source.read_text() == original
    return receipt[0]


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("0", "1", "phase", "union"))
    parser.add_argument("--receipts", nargs=3, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    assert __debug__
    if args.mode == "union":
        if args.receipts is None:
            parser.error("union requires --receipts")
        receipts = [json.loads(path.read_bytes()) for path in args.receipts]
        report = check_union(receipts)
        damaged = json.loads(json.dumps(receipts))
        next(row for row in damaged if row["mode"] == "1")["result"]["paid"] -= 1
        try:
            check_union(damaged)
        except ValueError:
            pass
        else:
            raise ValueError("Dropped paid event was not rejected")
        print("PASS_COMPACT_NUMERICAL_UNION", json.dumps(report, sort_keys=True))
        return
    with TemporaryDirectory(prefix="compact-signed-projection-") as folder:
        root = Path(folder)
        peer, work, runtime = (root / name for name in ("peer", "work", "runtime"))
        runpy.run_path(str(PACKAGE / "verify.py"))["restore"](peer)
        prepare = runpy.run_path(str(PACKAGE / "prepare.py"))
        prepare["materialize"](peer, PACKAGE / "COMPACT-PRICE.json",
                               PACKAGE / "integer-prototype.py", work)
        subprocess.run([sys.executable, "-IB", str(work / "bootstrap.py"), str(runtime)], check=True)
        inputs = {f"research/{PACKAGE.name}/{name}": digest(PACKAGE / name) for name in SOURCE_FILES}
        inputs.update({f"working/{name}": digest(work / name) for name in
                       ("check_gaussian.py", "check_phase_passes.py")})
        result = {"mode": args.mode, "inputs_sha256": inputs, "result": project(work, runtime, args.mode)}
        line = json.dumps(result, sort_keys=True)
        print("PASS_COMPACT_NUMERICAL_PROJECTION", line, flush=True)
        if args.out is not None:
            args.out.write_text(line + "\n")


if __name__ == "__main__":
    main()
