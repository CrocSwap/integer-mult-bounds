"""Exercise the fitted outer remainder and high roles with the old primitive forbidden."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))


def complete_endpoint(engine, remainder, body_atoms=2):
    from unittest.mock import patch
    import bitstream
    from cardinal_counts import Count
    from check_join import body
    import compact_outer
    import compact_nodes
    from provenance import Provenance
    from records import Tape
    from words import BLANK

    width = 3 + body_atoms + remainder
    size = 1 << width
    payload = Tape()
    for i in range(size * size):
        payload.append(((13 * i) ^ (i >> 5) ^ (i >> 9) ^ 0x4f) & 1)
    payload.rewind()
    initial = body(payload)
    provenance = Provenance(len(initial))
    provenance.mark(payload)
    call_order = []
    real_swap = compact_outer.atom_swap
    inner = {"run_peel":0, "block":0}
    inner_swap = compact_nodes.atom_swap
    def root_record(source, ring, q, before, middle, suffix, factory):
        if factory.__self__ is not engine.runtime.pool:
            raise AssertionError("wrong physical root scratch owner")
        frame = sys._getframe(1)
        while frame is not None and frame.f_code.co_name not in inner:
            frame = frame.f_back
        if frame is None:
            raise AssertionError("unexpected root atom path")
        inner[frame.f_code.co_name] += 1
        return inner_swap(source, ring, q, before, middle, suffix, factory)
    def record(source, ring, q, before, middle, suffix, factory):
        if ring.arena is engine.banks[1]:
            call_order.append("high")
        elif ring.arena is engine.banks[2]:
            call_order.append("remainder")
        else:
            raise AssertionError("unexpected fitted outer numerical bank")
        if factory.__self__ is not engine.pool:
            raise AssertionError("wrong fitted scratch owner")
        return real_swap(source, ring, q, before, middle, suffix, factory)
    def reject(*_args, **_kwargs):
        raise AssertionError("original q-by-q bucket primitive is reachable")
    def plan():
        values = dict(width=1, depth=1, stock=6, rows=8, borrowed=3, body=body_atoms, remainder=remainder)
        return dict(fits=True, **{k: Count.literal(v) for k, v in values.items()})
    def observe(event, _padded, _returned):
        if event == "after":
            call_order.append("root")
    engine.observe = observe
    original = Count.literal(width)
    one = Count.literal(1)
    try:
        with patch.object(bitstream, "digit_swap", reject), \
             patch.object(compact_outer, "atom_swap", record), \
             patch.object(compact_nodes, "atom_swap", root_record), provenance.installed():
            output = engine.execute_plan(payload, original, one, one, one, plan)
            got = body(output)
            masks = provenance.masks(output, len(got))
            if len(got) != size * size:
                raise AssertionError("complete fitted output length")
            for a in range(size):
                for b in range(size):
                    new, old = a * size + b, b * size + a
                    if got[new] != initial[old] or masks[new] != 1 << old:
                        raise AssertionError("fitted independent column permutation")
            if body(payload) != initial or payload.head != output.head or payload.head != 1:
                raise AssertionError("borrowed source and returned heads")
            expected = (["remainder"] if remainder else []) + ["root", "root", "high"]
            if body_atoms % 2 == 1 and not inner["run_peel"]:
                raise AssertionError("odd node skipped its physical peel")
            if expected != call_order or not engine.closed or not engine.runtime.closed:
                raise AssertionError("fitted schedule or ownership")
            if any(not all(bit == BLANK for bit in tape.cells)
                   for tape in (*engine.pool.tapes,*engine.runtime.pool.tapes,
                                *engine.runtime.roles.values(),*engine.runtime.handoff.values())):
                raise AssertionError("fitted scratch erasure")
            output.clear()
    finally:
        payload.clear()
        original.close()
        one.close()
    return len(initial), call_order, inner


def large_radix_swap():
    from unittest.mock import patch
    import bitstream
    from cardinal_counts import Count
    from check_join import body
    from compact_outer import swap_chunks
    from physical_words import PhysicalArena
    from provenance import Provenance
    from records import Tape
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from words import Ring
    # q^2 exceeds even the new *outer* reserve. All payload operations use 24 roles.
    q = 23
    pool = ScratchPool(24)
    arena = PhysicalArena(48)
    maximum = Count.literal(q)
    before, middle, suffix = [Count.literal(i) for i in (1,2,1)]
    arena.prepare(maximum)
    modulus = arena.load(maximum)
    ring = Ring(modulus)
    field = Tape()
    for i in range(2*q*q):
        field.append((i ^ (i >> 4) ^ (i >> 8)) & 1)
    field.rewind()
    initial = body(field)
    provenance = Provenance(len(initial))
    provenance.mark(field)
    def reject(*_args, **_kwargs):
        raise AssertionError("large radix requested an old q-by-q primitive")
    try:
        with patch.object(bitstream, "digit_swap", reject), \
             sealed_constructors(), pool.install(), provenance.installed():
            result = swap_chunks(field,ring,q,before,middle,suffix,pool.acquire)
            got = body(result.physical)
            masks = provenance.masks(result.physical,len(got))
            for a in range(q):
                for g in range(2):
                    for b in range(q):
                        i,j=(2*a+g)*q+b,(2*b+g)*q+a
                        if got[i]!=initial[j] or masks[i] != 1<<j:
                            raise AssertionError("real large radix field permutation")
            result.clear()
            pool.empty()
    finally:
        ring.close()
        arena.free(modulus)
        arena.erase_owned()
        for value in (before,middle,suffix,maximum):
            value.close()
        field.clear()
    return len(initial),q,pool.peak


def proper_fitted_remainder(native):
    """Reach the true remainder branch through public encoded selection at ell < w."""
    from unittest.mock import patch
    import bitstream
    import compact_outer
    from cardinal_counts import Count
    from compact_execution import CompactOrdinary
    from encoded import Profile, select
    from records import Tape
    profile = Profile(numerator=1,denominator=574,dimension=2,child_rank=1,row_factor=1)
    engine = CompactOrdinary(2,native.binding,native.runtime.topology,native.runtime.programs,
                             capacity=128,profile=profile,fixture_index_floor=64)
    original,one=Count.literal(101),Count.literal(1)
    plan=select(original,2,profile)
    witness={"width":2,"depth":6,"stock":96**6,"rows":1<<40,"borrowed":40,"body":30,"remainder":1}
    try:
        if not plan["fits"]:
            raise AssertionError("public fitted geometry not admitted")
        for key,value in witness.items():
            expected=Count.literal(value)
            if not plan[key].equals(expected):
                raise AssertionError("public selected geometry " + key)
            expected.close()
    finally:
        for key,value in plan.items():
            if key != "fits":
                value.close()
    hits=[]
    run=compact_outer.atom_swap
    def track(source,ring,q,before,middle,suffix,factory):
        if ring.arena is not engine.banks[2]:
            raise AssertionError("first physical field is the remainder")
        hits.append("remainder")
        return run(source,ring,q,before,middle,suffix,factory)
    def forbidden(*_args,**_kwargs):
        raise AssertionError("old radix bucket on the admitted fitted branch")
    try:
        with patch.object(bitstream,"digit_swap",forbidden), patch.object(compact_outer,"atom_swap",track):
            engine.run(Tape(),original,one,one,one)
    except ValueError as error:
        if str(error)!="opaque single payload bit" or hits!=["remainder"]:
            raise
    else:
        raise AssertionError("admitted geometry accepted a truncated payload")
    finally:
        original.close()
        one.close()
    return witness["width"],witness["remainder"],witness["body"],hits


def original_is_rejected(native):
    from compact_execution import CompactOrdinary
    from ordinary import Ordinary
    class OriginalFitted(CompactOrdinary):
        fitted = Ordinary.fitted
    old = OriginalFitted(2,native.binding,native.runtime.topology,native.runtime.programs,
                         capacity=128,fixture_index_floor=64)
    try:
        complete_endpoint(old,1)
    except AssertionError as error:
        if str(error) == "original q-by-q bucket primitive is reachable":
            return str(error)
        raise
    raise AssertionError("negative control missed a raw outer atom")


def production_prime_ingress():
    from contextlib import ExitStack
    from cardinal_counts import Count
    from compact_banks import ReservedArena
    from compact_execution import CompactOrdinary
    from compact_ordinary import Q
    from compact_outer import CompactFitted, swap_chunks
    from ordinary import outer, ring_from_count
    from records import Tape
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors

    if CompactOrdinary.fitted is not CompactFitted.fitted:
        raise AssertionError("production still uses the raw outer scheduler")
    peaks = []
    for use_compact in (False, True):
        with ExitStack() as cleanup:
            maximum, unit = Count.literal(Q), Count.literal(1)
            cleanup.callback(maximum.close)
            cleanup.callback(unit.close)
            ring = ring_from_count(ReservedArena(32), maximum, cleanup)
            pool = ScratchPool(512)
            payload = Tape()
            args = (payload, ring, Q, unit, unit, unit)
            try:
                with sealed_constructors(), OuterScope(pool).installed():
                    if use_compact:
                        swap_chunks(*args, pool.acquire)
                    else:
                        outer.swap_chunks(*args)
            except ValueError as error:
                expected = "opaque single payload bit" if use_compact else "fixed scratch role inventory exhausted"
                if str(error) != expected:
                    raise
            else:
                raise AssertionError("empty high field accepted")
            peaks.append(pool.peak)
    if peaks[0] != 512 or peaks[1] >= 20:
        raise AssertionError("high field scratch count")
    return peaks


if __name__ == "__main__":
    from compact_ordinary import load_cohort
    load_cohort()
    from verify_compact_control import fixture
    print("source_Q_high_ingress_old_new_peaks",production_prime_ingress(),flush=True)
    print("larger_than_outer_pool",large_radix_swap(),flush=True)
    engine=fixture()
    print("original_negative_control",original_is_rejected(engine),flush=True)
    print("public_fitted_short_input",proper_fitted_remainder(engine),flush=True)
    print("fitted_no_tail",complete_endpoint(engine,0),flush=True)
    print("fitted_with_tail",complete_endpoint(engine,1),flush=True)
    if "--odd-body" in sys.argv[1:]:
        print("fitted_odd_body",complete_endpoint(engine,0,3),flush=True)
