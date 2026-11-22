"""Run the two first independent exterior births through the actual typed decoder and Raw48."""

from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction as Q
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from band_product import production_supplier
from periodic import Job
from transport import Measure, Source, ceil, axes
from unpowered_price import certify
from typed_transport import TypedPlan
from typed_raw import TypedRaw

sys.path.append(str(Path(__file__).resolve().parent))
from check_raw import Axes, WitnessRaw, RayField, basis, final_ray, rot


def run():
    M = 8192
    L = 10
    U = 12
    V = 2**48
    R = M
    K = 1
    c = Q(17145637167, 2**42)
    dens = Measure(1 - c, V, 64 * M.bit_length())
    producer = production_supplier(1024, 10**18)
    a, w = producer.physical, producer.word
    types = producer.recipe.types()
    hist_t = Counter()
    hist_p = Counter()
    ids = defaultdict(list)
    for t, spec in enumerate(types):
        for i, k in enumerate(spec.targets):
            hist_t[k] += spec.multiplicity
            ids[t, k].append(i)
        for r in spec.paid:
            hist_p[r] += spec.multiplicity
    _, cells = certify(c, (hist_t, hist_p))
    assert cells == producer.recipe.cells
    # All true interior intervals are empty in [10,12). Every incoming replica
    # considered below is a real exterior occurrence or an original blank.
    assert 4 * U < 5 * L

    # Reconstruct the installed source-width prefix by paid occurrence. Identical
    # grades have identical grant sizes, but different occurrences own separate rows.
    class FirstReplicas(TypedPlan):
        """Project two independent exterior births from the single test bin."""

        def __init__(self):
            self.n, self.types, self.ticks, self.rounds, self.bands = (
                M,
                types,
                K,
                R,
                range(L, U, 2),
            )
            self.delay = {L: 1}
            self.count = {(L, 0): 1, (L, 1): 1}
            self.sources, self.receive, self.send = {}, {}, {}

    p = FirstReplicas()
    full_counts = tuple(ceil(spec.multiplicity * dens.mass(L, U)[1]) for spec in types)
    first = set()
    base = 0
    for kind, spec in enumerate(types):
        chunks = {r: [] for r in set(spec.paid)}
        for (r, k), share in cells.items():
            if r not in chunks:
                continue
            left = max(U, Q(L * k, r))
            right = Q(U * k, r)
            mass = dens.mass(left, right)[0]
            for b, other in enumerate(types):
                if not ids[b, k]:
                    continue
                grant = int(
                    spec.multiplicity * mass * share * other.multiplicity / hist_t[k]
                )
                size = (L - 8) * k
                period = 4 * ceil(Q(M, 4 * size))
                if grant:
                    chunks[r].append((b, k, grant, period))
        sizes = {
            r: sum(len(ids[b, k]) * grant * (R // period) for b, k, grant, period in cs)
            for r, cs in chunks.items()
        }
        for r in spec.paid:
            if any((b, k) not in first for b, k, grant, period in chunks[r]):
                current = base
                for b, k, grant, period in chunks[r]:
                    for i in ids[b, k] if (b, k) not in first else ():
                        p.sources[L, b, i] = [Source(0, grant, current, period)]
                        current += grant * (R // period)
                    if (b, k) in first:
                        current += len(ids[b, k]) * grant * (R // period)
                    first.add((b, k))
                assert current == base + sizes[r]
            base += sizes[r]
    assert len(p.sources) == sum(len(s.targets) for s in types)
    p.source_width = base
    p.width = 1 << (4096 * base - 1).bit_length()
    # All other true replicas are independent at this width since there are no
    # interior edges. Their omission renumbers frame identifiers only.
    assert min(full_counts) > 1
    clock, call = next(
        (i, row[1]) for i, row in enumerate(a.instructions()) if row[0] == "NATIVE"
    )
    pawn = next(
        i for i, tag in enumerate(w.targets) if tag.tag == ("helper", clock, call, 1544)
    )
    true = {}
    stock = [0, 0]
    fields = {}
    for kind, s in enumerate(types):
        for i, k in enumerate(s.targets):
            [ext] = p.sources[L, kind, i]
            owner = ext.base
            assert owner not in fields
            fields[owner] = RayField(stock)
            true[owner] = (2 * k, ext.period)

    @cache
    def placement(size, period):
        # Exercise the permitted bijection of the caller's physical row axes.
        # This choice makes the two known nonzero stabilizer tensors canonical.
        seq = tuple(axes(M, size, period, 0))
        claimed = set(seq)
        assert len(claimed) == size
        reverse = [0] * M
        for j, q in enumerate(seq):
            reverse[q] = j
        pos = size
        for q in range(M):
            if q not in claimed:
                reverse[q] = pos
                pos += 1
        assert pos == M
        return tuple(reverse)

    class Rows:
        def __getitem__(self, i):
            return Job(i, placement(*true[i]))

    expected = {}
    for kind, s in enumerate(types):
        cols = 2 * (1 + kind)
        [e] = p.sources[L, kind, pawn]
        origins = tuple((37 * i + 11 + 17 * kind) % 512 for i in range(cols))
        z = ((3 if not kind else -7) << 2048, (5 if not kind else 2) << 2048)
        fields[e.base].data = z, tuple(basis(i) for i in origins)
        output = tuple(final_ray(i) for i in origins)
        z = rot(z, sum(phase for v, phase in output))
        expected[e.base] = (
            (z[0] // 16**cols, z[1] // 16**cols),
            tuple(v for v, phase in output),
        )
    physical = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=M)
    adapter = TypedRaw(w, physical)
    bills = [0, 0]

    class Machine:
        native = staticmethod(adapter.native)

        def leaf(self, job):
            (i,) = job.axes
            bills[0] += 1
            f = fields[job.owner]
            if f.data is not None:
                f.paid(i)
                bills[1] += 1

        @staticmethod
        def zero(exemplar):
            raise AssertionError(
                "All tested genuine first replicas received exterior fields"
            )

        retire_zero = staticmethod(physical.retire)

    p.decode(Rows(), 0, 0, Machine(), p.events())
    assert (
        bills[0] == p.leaves_per_epoch
        and {i: f.data for i, f in fields.items() if f.data is not None} == expected
    )
    assert len(fields) == sum(len(s.targets) for s in types) and all(
        f.writes and f.live for f in fields.values()
    )
    for f in fields.values():
        f.retire()
    assert stock[0] == 0
    print(
        "PASS_EXTERIOR_TYPED_RAW",
        full_counts,
        p.source_width.bit_length(),
        len(fields),
        sum(len(s.paid) for s in types),
        bills,
        stock,
    )


if __name__ == "__main__":
    run()
