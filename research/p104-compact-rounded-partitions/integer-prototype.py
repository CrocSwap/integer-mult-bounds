"""Check rounded packet sizes in the authenticated event and leaf ledgers."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

WRAPPER = "775c7ff81f05b7df6d9ad3aa244bbcc539c383be96e1d07855881c53417f9844"
TRANSPORT = "98bdb540233794338b426d1b0d0e72cff7fcbbd08be702af0d81e237dbecaae9"

HELPER = '''
def paid_axis_count(rank, columns):
    if rank in (F(1, 4), F(3, 4)):
        if columns < 4 or columns % 2:
            raise ValueError("Expected at least four even columns")
        first = columns // 4
        return first if rank == F(1, 4) else columns - first
    return rank * columns


'''


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def patch(source, destination):
    assert digest(source) == TRANSPORT
    code = source.read_text()
    for old, new in (
        ("class Plan:", HELPER + "class Plan:"),
        ("size = self.paid[j] * (e - 8)", "size = paid_axis_count(self.paid[j], e - 8)"),
        ("self.ticks * self.count[e] * self.paid[j] * (e - 8)",
         "self.ticks * self.count[e] * paid_axis_count(self.paid[j], e - 8)"),
    ):
        assert code.count(old) == 1
        code = code.replace(old, new)
    destination.write_text(code)


def fixture(plan_class, band):
    plan = plan_class.__new__(plan_class)
    plan.bands = range(band, band + 2, 2)
    plan.count = {band: 1}
    plan.delay = {band: 1}
    plan.targets = (1,)
    plan.paid = (Q(1, 4), Q(3, 4))
    plan.ticks = 1
    plan.send = defaultdict(list)
    plan.receive = defaultdict(list)
    plan.sources = defaultdict(list)
    return plan


class Packet:
    def __init__(self, owner, axes):
        self.owner, self.axes = owner, tuple(axes)

    def select(self, indices):
        return Packet(self.owner, (self.axes[i] for i in indices))


class Machine:
    def __init__(self):
        self.live = set()
        self.signed_axes = []

    def zero(self, source):
        assert not self.live
        self.live.add(1)
        return Packet(1, source.axes)

    def retire_zero(self, source):
        self.live.remove(source.owner)

    def native(self, ports, columns):
        job, = ports
        assert len(job.axes) == columns and job.owner in self.live
        half = columns // 4
        yield job.select(range(half))
        yield job.select(range(half, columns))

    def leaf(self, job):
        assert job.owner in self.live and len(job.axes) == 1
        self.signed_axes.extend(job.axes)


def test(old, new, band):
    width = band - 8
    plan = fixture(new, band)
    records = list(plan.events())
    first = width // 4
    count = [row[3] for row in records if row[0] == 1]
    assert count == [first, width - first]
    assert plan.leaves_per_epoch == sum(count) == width
    axes = tuple((-1)**i * (i + 1) for i in range(width))
    rows = (Packet(0, axes),)
    observed = Machine()
    plan.decode(rows, 0, 0, observed, records)
    assert not observed.live and tuple(observed.signed_axes) == axes
    i = next(i for i, row in enumerate(records) if row[0] == 1)
    op, ident, serial, size, selected = records[i]
    records[i] = (op, ident, serial, size + 1, selected)
    try:
        plan.decode(rows, 0, 0, Machine(), records)
    except ArithmeticError as exc:
        assert "wrong rank" in str(exc)
    else:
        raise AssertionError("Paid size corruption accepted")
    try:
        list(fixture(old, band).events())
    except ArithmeticError:
        assert width % 4 == 2
    else:
        assert width % 4 == 0
    return {"band": band, "columns": width, "packet_lengths": count, "leaves": width,
            "preserved_signed_axes_and_owner": True, "corrupted_size_rejected": True}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--unsplit-package", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    package = args.unsplit_package.resolve()
    wrapper = package / "prepare.py"
    assert digest(wrapper) == WRAPPER
    with TemporaryDirectory() as work:
        root = Path(work)
        compiled = root / "source"
        runpy.run_path(str(wrapper))["materialize"](package / "peer8053", compiled)
        source, edited = compiled / "transport.py", root / "transport.py"
        patch(source, edited)
        old = runpy.run_path(str(source))["Plan"]
        new = runpy.run_path(str(edited))["Plan"]
        result = {"source": TRANSPORT, "patched": digest(edited),
                  "scope": "single-owner event, decode, and leaf ledger fixture",
                  "cases": [test(old, new, band) for band in (32768, 32770)]}
    with args.out.open("x") as file:
        json.dump(result, file, sort_keys=True, indent=2)
        file.write("\n")


if __name__ == "__main__":
    main()
