"""Check independent source numbering, deadlines and return of all borrowed owners."""

from fractions import Fraction as Q
from collections import Counter
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from typed_transport import TypedPlan, NativeType


def run(freq, ticks, lower, upper, volume, n, rounds, delay):
    types = (NativeType((2,), (1, 1), 1), NativeType((2, 2), (1, 1, 1, 1), freq))
    shares = {
        (0, 1, 1, 2): Q(1),
        (1, 1, 0, 2): Q(1, 2 * freq),
        (1, 1, 1, 2): 1 - Q(1, 2 * freq),
    }
    p = TypedPlan(
        n,
        types,
        shares,
        Q(1),
        lower,
        upper,
        volume,
        ticks,
        rounds,
        delay_base=delay,
        scale_step=Q(2),
        padding=1,
    )
    M = max(p.count.values())
    bands = len(p.bands)

    def frame_info(ident):
        packed, rep = divmod(ident, M)
        packed, typ = divmod(packed, 2)
        birth, offset = divmod(packed, bands)
        band = lower + 2 * offset
        assert rep < p.count[(band, typ)]
        return typ, birth, band, rep

    # Half-open source blocks have no alias even when their integer periods differ.
    ext = sorted(
        (src.base, src.base + src.count * ticks * (rounds // src.period), src)
        for group in p.sources.values()
        for src in group
        if rounds // src.period
    )
    end = 0
    for lo, hi, src in ext:
        assert lo == end and lo < hi
        end = hi
    assert end == p.source_width
    opened = {}
    borrowers = {}
    serials = {}
    kinds = Counter()
    transfers = Counter()
    flats = external = zero = last = peak = depth = close_on_due = child_tail = 0
    periods = Counter()
    for rec in p.events():
        op, ident, *xs = rec
        kind, birth, e, rep = frame_info(ident)
        w = types[kind]
        step = p.delay[e]
        if op == 0:
            assert ident not in opened and xs[0] == e - 8 + kind
            tick = birth
            it = iter(xs[1:])
            origins = []
            d = 1
            for k in w.targets:
                tag = next(it)
                if tag == 1:
                    par, expected, t0, pkind = serials.pop(next(it))
                    assert (
                        t0 == tick and par not in borrowers and expected == k * (e - 8)
                    )
                    borrowers[par] = ident
                    origins.append(par)
                    d = max(d, opened[par][2] + 1)
                    transfers[pkind, kind] += 1
                elif tag == 2:
                    base, size, period = next(it), next(it), next(it)
                    assert size == k * (e - 8) and period == 4 * (-(-n // (4 * size)))
                    assert 0 <= base <= base + rounds // period <= p.source_width
                    if rounds >= period:
                        external += 1
                    periods[period] += 1
                else:
                    assert tag == 0 and next(it) == k * (e - 8)
                    zero += 1
            assert next(it, None) is None
            opened[ident] = [0, origins, d]
            peak = max(peak, len(opened))
            depth = max(depth, d)
        elif op == 1:
            j, parents, d = opened[ident]
            tick = birth + step * j
            assert ident not in borrowers
            serial, size, sel = xs
            assert size == (e - 8) * w.paid[j] and sel <= size
            if sel:
                serials[serial] = (ident, sel, tick, kind)
            flats += size - sel
            if tick >= ticks:
                child_tail += int(sel != 0)
            opened[ident][0] += 1
        else:
            j, parents, d = opened.pop(ident)
            assert j == len(w.paid) and ident not in borrowers
            tick = birth + step * j
            for par in parents:
                assert borrowers.pop(par) == ident
                pk, pb, pe, pr = frame_info(par)
                assert p.delay[pe] >= step
                due = pb + opened[par][0] * p.delay[pe]
                assert tick <= due
                close_on_due += int(tick == due)
            kinds[kind] += 1
        assert tick >= last, (tick, last, op, e, kind)
        last = tick
    assert flats == p.leaves_per_epoch and not (
        opened or borrowers or serials or child_tail
    )
    assert kinds == Counter(
        {a: ticks * sum(v for (e, b), v in p.count.items() if b == a) for a in range(2)}
    )
    assert depth <= 1 + max(b.bit_length() for b in p.bands)
    return dict(
        frequency=freq,
        raw_frames=sum(kinds.values()),
        directed_bindings={str(k): v for k, v in transfers.items()},
        depth=depth,
        peak_simultaneous_frames=peak,
        external_opens=external,
        zeros=zero,
        external_rows=end,
        positive_periods=sorted(periods),
        leaf_axes=flats,
        same_tick_return_before_next_loan=close_on_due,
    )


out = [run(3, 12, 10, 82, 1700, 1024, 96, 4), run(90, 8, 10, 42, 450, 384, 32, 4)]
print(json.dumps(out, indent=2))
