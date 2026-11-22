"""Execute both physical Gaussian words on finite nonzero product states."""

from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from check_nonzero_eight import (
    Axes,
    WitnessRaw,
    Field,
    addresses,
    basis,
    diagonal,
    final_ray,
    rot,
)
from band_product import production_supplier
from periodic import Job
from typed_raw import TypedRaw


class RayField(Field):
    def blank(self):
        return RayField(self.stock)

    def phase(self, op, suffix):
        if self.data is None:
            return
        z, rays = self.data
        n = len(rays)
        base = op(0) % 4
        z = rot(z, base)
        single = tuple((op(x) - base) % 4 for x in addresses(0, n))
        after = []
        for i, v in enumerate(rays):
            other = addresses(i, n)
            assert all((op(x) - base) % 4 == y for x, y in zip(other, single))
            y, p = diagonal(v, single)
            after.append(y)
            z = rot(z, p)
        self.data = z, tuple(after)


def run():
    producer = production_supplier(1024, 10**18)
    a, w = producer.physical, producer.word
    types = producer.recipe.types()
    for kind, (spec, cols) in enumerate(zip(types, (2, 4))):
        stock = [0, 0]
        fields = {j: RayField(stock) for j in range(len(spec.targets))}
        jobs = [Job(i, range(2 * k)) for i, k in enumerate(spec.targets)]
        clock, call = next(
            (i, row[1]) for i, row in enumerate(a.instructions()) if row[0] == "NATIVE"
        )
        key = ("helper", clock, call, 1544)
        owner = next(i for i, p in enumerate(w.targets) if p.tag == key)
        assert w.targets[owner].rank == 8
        origins = tuple((37 * i + 11 + 17 * kind) % 512 for i in range(cols))
        initial = ((3 if not kind else -7) << 2048, (5 if not kind else 2) << 2048)
        fields[owner].data = initial, tuple(basis(i) for i in origins)
        exact = tuple(final_ray(i) for i in origins)
        z = rot(initial, sum(p for v, p in exact))
        assert all(x % (16**cols) == 0 for x in z)
        after = (z[0] // 16**cols, z[1] // 16**cols), tuple(v for v, p in exact)
        raw = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=2 * 306)
        it = TypedRaw(w, raw).native(jobs, 2 + kind)
        nonzero = 0
        for r in spec.paid:
            job = next(it)
            assert len(job.axes) == 2 * r
            f = fields[job.owner]
            if f.data is not None:
                nonzero += 1
                for axis in job.axes:
                    f.paid(axis)
        assert next(it, None) is None and set(fields) == set(range(len(spec.targets)))
        assert {i: f.data for i, f in fields.items() if f.data is not None} == {
            owner: after
        }
        assert all(f.writes and f.live for f in fields.values()) and nonzero > 0
        writes = sum(f.writes for f in fields.values())
        for f in fields.values():
            f.retire()
        assert stock[0] == 0
        print(
            "PASS_TYPED_RAW48",
            kind,
            "columns",
            cols,
            "paid",
            len(spec.paid),
            "nonzero",
            nonzero,
            "writes",
            writes,
            "peak",
            stock[1],
            flush=True,
        )


if __name__ == "__main__":
    run()
