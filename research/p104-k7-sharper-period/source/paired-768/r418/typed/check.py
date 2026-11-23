"""Check the full installed typed return seeded at exact helper 173."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from shutil import disk_usage
import signal
import sys
from tempfile import gettempdir

NODE, SEED, CONTROL = 104493, 173, 164
ORACLE_SHA = "41a48b4b9641963b3d1f7ac64210d82fdefd6632b95ac0388e1799d99f6fe050"
PINS = {
    "strong_complex.py": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
    "typed_raw.py": "0c268432c9d48798c17d927f2d900b5e69dfc6585166cd71f253913e389c3b47",
    "check_nonzero_eight.py": "e0955bbbdef1a19668cc62fc1f500574705fc484224e571c47426793a6ec631a",
}
ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def product(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def fourier(data, rank):
    """Independent convolution with the rank-r Gaussian kernel on each ray."""
    scalar, rays = data
    kernel_factor = ((1, 0), (1, 1), (0, 2), (-2, 2))[rank % 4]
    power = (-4) ** (rank // 4)
    kernel_factor = tuple(power*x for x in kernel_factor)
    output = []
    for ray in rays:
        real, imag = [0]*512, [0]*512
        for idx, phase in enumerate(ray):
            if phase >= 0:
                for flip in range(1 << rank):
                    a, b = ROOTS[(phase - flip.bit_count()) % 4]
                    real[idx ^ flip] += a
                    imag[idx ^ flip] += b
        vector = tuple(zip(real, imag, strict=True))
        pivot = next(z for z in vector if z != (0, 0))
        lookup = {product(pivot, q): i for i, q in enumerate(ROOTS)}
        output.append(tuple(-1 if q == (0, 0) else lookup[q] for q in vector))
        scalar = product(scalar, product(pivot, kernel_factor))
    den = 1 << (rank*len(rays))
    assert all(x % den == 0 for x in scalar)
    return tuple(x//den for x in scalar), tuple(output)


def expected(oracle, kind, origin, scalar, phase):
    records = oracle["kind_oracles"][str(kind)]
    assert tuple(r["basis"] for r in records) == origin
    if phase != "terminal":
        scale = int(oracle["pre_child_global_factor"])
        scalar = tuple(scale*v for v in scalar)
    for r in records:
        scalar = product(scalar, tuple(map(Fraction, r[phase]["pivot"])))
    assert all(v.denominator == 1 for v in scalar)
    return tuple(map(int, scalar)), tuple(tuple(r[phase]["phases"]) for r in records)


def read_oracle(path):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == ORACLE_SHA
    return json.loads(data)


def run(runtime, kind, oracle_path):
    for name, digest in PINS.items():
        assert sha256((runtime/name).read_bytes()).hexdigest() == digest, name
    if min(disk_usage(runtime).free, disk_usage(gettempdir()).free) < 8*1024**3:
        raise RuntimeError("The 8 GiB native reserve is unavailable")
    sys.path.insert(0, str(runtime))
    from upstream import install

    install()
    from band_product import production_supplier
    from check_nonzero_eight import Axes, Field, WitnessRaw, addresses, basis, diagonal, rot
    from periodic import Job
    from typed_raw import TypedRaw

    class RayField(Field):
        def blank(self):
            return RayField(self.stock)

        def phase(self, op, suffix):
            if self.data is None:
                return
            z, rays = self.data
            base = op(0) % 4
            z = rot(z, base)
            single = tuple((op(x)-base) % 4 for x in addresses(0, len(rays)))
            output = []
            for col, ray in enumerate(rays):
                assert all((op(x)-base) % 4 == t for x, t in zip(
                    addresses(col, len(rays)), single, strict=True))
                value, phase = diagonal(ray, single)
                output.append(value)
                z = rot(z, phase)
            self.data = z, tuple(output)

    producer = production_supplier(1024, 10**18)
    atlas, word = producer.physical, producer.word
    assert atlas.layout["source_labels"][SEED] == SEED and SEED not in atlas.main
    assert atlas.layout["source_labels"][CONTROL] == CONTROL and CONTROL in atlas.main
    assert (atlas.graph["initial"][SEED], atlas.graph["final"][SEED]) == (3, 127)
    assert atlas.moves[NODE] == (365, 529) and atlas.forms[NODE] == ((94870, 1),)
    assert dict(atlas.forms[94870])[~SEED] == -2
    clock, call = next((i, row[1]) for i, row in enumerate(atlas.instructions()) if row[0] == "NATIVE")
    seed_tag = ("helper", clock, call, SEED)
    assert all(p.tag != ("helper", clock, call, CONTROL) for p in word.targets)
    owner, = (i for i, p in enumerate(word.targets) if p.tag == seed_tag)
    assert word.targets[owner].rank == 9
    chosen = ("return", clock, call, NODE)
    spec = producer.recipe.types()[kind]
    columns = 2*(1+kind)
    oracle = read_oracle(oracle_path)
    origins = tuple((37*i+11+17*kind) % 512 for i in range(columns))
    initial = ((3 if not kind else -7) << 2048, (5 if not kind else 2) << 2048)
    before_paid = expected(oracle, kind, origins, initial, "before_paid")
    after_paid = expected(oracle, kind, origins, initial, "after_paid_before_left")
    terminal = expected(oracle, kind, origins, initial, "terminal")
    assert fourier(before_paid, 5) == after_paid

    class Observed(WitnessRaw):
        trace = None

        def raw(self, bound, width):
            assert width == columns
            for tag, job in super().raw(bound, width):
                if tag != chosen:
                    yield tag, job
                    continue
                assert self.trace is None and self.fields[owner] is original[owner]
                assert tuple(job.axes) == tuple(range(5*columns))
                loan = self.fields[job.owner]
                assert job.owner not in original and loan.data is not None
                assert loan.data == before_paid
                yield tag, job
                assert self.fields[job.owner] is loan and loan.data == after_paid
                self.trace = (job.owner, loan, len(job.axes))

    stock = [0, 0]
    fields = {i: RayField(stock) for i in range(len(spec.targets))}
    original = fields.copy()
    jobs = [Job(i, range(2*k)) for i, k in enumerate(spec.targets)]
    fields[owner].data = initial, tuple(basis(i) for i in origins)
    assert fourier(fields[owner].data, 9) == terminal
    raw = Observed(atlas, fields, Axes(), low=0, bundle=1, slots=2*306)
    it = TypedRaw(word, raw).native(jobs, 2+kind)
    live = 0
    for rank in spec.paid:
        job = next(it)
        assert len(job.axes) == 2*rank
        field = fields[job.owner]
        if field.data is not None:
            live += 1
            for axis in job.axes:
                field.paid(axis)
    assert next(it, None) is None and raw.trace is not None
    token, loan, axes = raw.trace
    assert token not in fields and not loan.live
    assert fields.keys() == original.keys() and all(fields[i] is f for i, f in original.items())
    assert {i: f.data for i, f in fields.items() if f.data is not None} == {owner: terminal}
    assert all(f.writes and f.live for f in fields.values())
    for field in fields.values():
        field.retire()
    assert stock[0] == 0
    return dict(kind=kind, columns=columns, seed_tag=seed_tag, observed_tag=chosen,
                paid_axes=axes, original_owners=len(original), nonzero_paid=live,
                exact_terminal=True, bad_seed_164_absent=True, retired_relay_scratch=True)


def timeout(_sig, _frame):
    raise TimeoutError("The installed typed-return probe reached its 100-second cap")


if __name__ == "__main__":
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("--runtime", type=Path, required=True)
    p.add_argument("--kind", type=int, choices=(0, 1), required=True)
    p.add_argument("--oracle", type=Path, default=Path(__file__).resolve().parent.parent /
                   "oracle/RECEIPT.json")
    args = p.parse_args()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(100)
    try:
        print(json.dumps(run(args.runtime.resolve(), args.kind, args.oracle), indent=2))
    finally:
        signal.alarm(0)
