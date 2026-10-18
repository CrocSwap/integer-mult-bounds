"""Finite evidence and fault controls; Python integers occur only in checkers."""
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import selected_binding as selected


def bindings():
    result = selected.compile_selected()
    data, functions = selected.inputs(), selected.phase_functions()
    rejected = []
    for name in ("owner", "stage", "native_frame", "entry_translation", "duplicate_owner"):
        changed = deepcopy(data)
        if name == "owner":
            changed[0]["calls"][0]["owners"][119][0] = 118
        elif name == "stage":
            changed[0]["calls"][0]["stage"] = 1
        elif name == "native_frame":
            changed[2]["start"][169] = 1
        elif name == "entry_translation":
            changed[3]["recipes"][57]["stage_alignment"][0]["entry_Y"] = 1
        else:
            changed[0]["calls"][0]["owners"][0][0] = changed[0]["calls"][0]["owners"][1][0]
        try:
            selected.validate(*changed, functions)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("selected source mutation accepted: "+name)
    bases = [tuple(functions["basis"](q)) for q in (21, 56)]
    for columns in bases:
        selected.need(all(((a & b).bit_count() & 1) == (i == j)
                          for i, a in enumerate(columns) for j, b in enumerate(columns)), "idle bases pass Gram")
    # basis() returns columns, whereas mv() takes rows.
    relative_e0 = selected.mv(selected.transpose(bases[0], 73), selected.mv(bases[1], 1))
    selected.need(relative_e0 == 47, "wrong idle chart passes Gram but changes the coordinate")
    wrong = dict(functions, rho=lambda q, stage: tuple(functions["basis"](q)))
    try:
        selected.validate(*data, wrong)
    except ValueError as error:
        selected.need("data chart" in str(error), "wrong idle chart rejection boundary")
        rejected.append("idle_basis")
    else:
        raise ValueError("idle chart accepted")
    def forbidden_basis(_q):
        raise ValueError("stage-zero data route used idle basis")
    functions["basis"] = forbidden_basis
    selected.validate(*data, functions)
    return dict(binding=result, source_controls=rejected, wrong_idle_e0=relative_e0,
                stage_zero_needs_no_idle_basis=True)


def hoist():
    # This finite group is a control model, not the selected O(73,2) cover.
    cover, families = 5, 4
    initial = [[Fraction(11*f+7*g-19, 8) for g in range(cover)] for f in range(families)]
    shifts = (0, 0, 2, 4)
    def slots(d, broken=False):
        return [(f, (d+shifts[f])%cover if not (broken and f == 0) else 0) for f in range(families)]
    supports = [set(slots(d)) for d in range(cover)]
    selected.need(all(not supports[d]&supports[e] for d in range(cover) for e in range(d)), "disjoint model supports")
    def prefix(bank, d, broken=False):
        (tf, tg), (sf, sg), *_ = slots(d, broken)
        bank[tf][tg] = (bank[sf][sg]-bank[tf][tg])/2
    def tail(bank, d, broken=False):
        (tf, tg), (sf, sg), (hf, hg), (jf, jg) = slots(d, broken)
        # Dirty helper coupling makes same-packet order matter.
        bank[hf][hg] += 3*bank[tf][tg]
        bank[tf][tg] += bank[jf][jg]-bank[hf][hg]
        bank[sf][sg] -= 2*bank[tf][tg]
    def execute(hoisted, broken=False):
        bank = deepcopy(initial)
        if hoisted:
            for d in range(cover):
                prefix(bank, d, broken)
        for d in range(cover):
            if not hoisted:
                prefix(bank, d, broken)
            tail(bank, d, broken)
        return bank
    expected = execute(False)
    selected.need(expected == execute(True), "finite prefix-tail factorization")
    selected.need(execute(False, True) != execute(True, True), "nonbijective route control")
    wrong_alignment = deepcopy(initial)
    common_alignment = deepcopy(initial)
    for d in range(cover):
        wrong_alignment[0][d] = (initial[1][(d+1)%cover]-initial[0][d])/2
        prefix(common_alignment, d)
    selected.need(wrong_alignment != common_alignment, "unequal whole-family chart control")
    return dict(cover=cover, families=families, disjoint_packets=True,
                result=[[str(x) for x in row] for row in expected],
                nonbijective_route_rejected=True, unequal_chart_rejected=True)


def runtime():
    import prefix_sources
    prefix_sources.activate()
    from bank_engine import PrefixEngine, selected_extent
    from cardinal_counts import Count
    from check_support import no_decode
    from scalar_test_support import body, closed_work, fill, packet, snapshot
    from records import Tape
    from scratch_pool import ScratchPool
    from session import OuterScope, borrowed_count, borrowed_tape, erase_marker, sealed_constructors
    from signed_linear import CoefficientDomainError
    from words import BLANK, need
    return locals()


def closed(engine, api, output=True):
    api["closed_work"](engine, output)
    api["closed_work"](engine.scalar, True)


def fixture(width, count, invalid=None):
    api = runtime()
    values = []
    limit = 1 << (width-1)
    for family in range(14336):
        values.append([((family*37+index*101+family*index) % (2*limit))-limit for index in range(2*count)])
    values[119] = [2*((index%5)-2) for index in range(2*count)]
    values[169] = [2*(2-(index%4)) for index in range(2*count)]
    if invalid == "headroom":
        values[119][-1] = -limit
        values[169][-1] = -limit
    elif invalid == "inexact":
        values[169][-1] = 1
    raw = b"".join(api["packet"](row, width) for row in values)
    expected = deepcopy(values)
    expected[119] = [(y-x)//2 for x, y in zip(values[119], values[169])]
    expected_raw = b"".join(api["packet"](row, width) for row in expected)
    return raw, expected_raw, values


def packets():
    api = runtime()
    engine = api["PrefixEngine"]()
    bank = api["Tape"]()
    results = []
    for width, count in ((17, 1), (18, 3)):
        raw, expected, values = fixture(width, count)
        api["fill"](bank, raw)
        h, n = api["Count"].literal(width), api["Count"].literal(count)
        saved = api["snapshot"]((h, n))
        with api["no_decode"]():
            returned = engine.run(bank, h, n)
        api["need"](api["body"](returned) == expected, "complete bank integer oracle")
        api["need"](api["body"](bank) == raw and bank.head == 1 and api["snapshot"]((h, n)) == saved,
                    "borrowed bank and encoded headers preserved")
        closed(engine, api, False)
        stale = deepcopy(values)
        stale[119] = [x+y//2 for x, y in zip(values[119], values[169])]
        api["need"](b"".join(api["packet"](row, width) for row in stale) != expected, "stale target control")
        # Neither reversed source record order nor the adjacent family is equivalent.
        for source in (list(reversed(values[169])), values[170]):
            wrong = api["packet"]([(y-x)//2 for x, y in zip(values[119], source)], width)
            api["need"](wrong != api["packet"]([(y-x)//2 for x, y in zip(values[119], values[169])], width),
                        "wrong source/order oracle control")
        try:
            engine.run(bank, h, n)
        except ValueError as error:
            api["need"]("previous" in str(error), "protected output reuse guard")
        else:
            raise ValueError("unconsumed bank return accepted")
        with api["no_decode"](), api["sealed_constructors"]():
            engine.commit(bank)
        api["need"](api["body"](bank) == expected and bank.head == 1, "complete bank commit")
        closed(engine, api)
        results.append(dict(width=width, gaussians_per_family=count, bank_bits=len(raw),
                            output_sha256=sha256(expected).hexdigest(), parent_peak=engine.pool.peak,
                            scalar_peak=engine.scalar.pool.peak))
        h.close()
        n.close()
    bank.clear()
    return dict(cases=results, scope="full14336-family generic finite extents; not the full selected cover payload")


def returns():
    api = runtime()
    engine = api["PrefixEngine"]()
    bank = api["Tape"]()
    h, n = api["Count"].literal(4), api["Count"].literal(2)
    saved = api["snapshot"]((h, n))
    for category in ("headroom", "inexact"):
        raw, _, _ = fixture(4, 2, category)
        api["fill"](bank, raw)
        with api["no_decode"]():
            try:
                engine.run(bank, h, n)
            except api["CoefficientDomainError"] as error:
                api["need"](category in str(error), "named prefix rejection")
            else:
                raise ValueError("invalid prefix accepted")
        api["need"](api["body"](bank) == raw and bank.head == 1 and api["snapshot"]((h, n)) == saved,
                    "failed prefix preserves bank and headers")
        closed(engine, api)
    h.close()
    n.close()
    bank.clear()
    # Reuse the same failed engine under a caller with live Counts and payload.
    parent = api["ScratchPool"](32)
    scope = api["OuterScope"](parent)
    raw, expected, _ = fixture(5, 2)
    with api["no_decode"](), api["sealed_constructors"](), scope.installed():
        h, n, sentinel = (api["Count"].literal(x) for x in (5, 2, 12345))
        saved = api["snapshot"]((h, n, sentinel))
        owned = parent.acquire()
        for bit in raw:
            owned.append(bit)
        owned.rewind()
        with scope.suspended():
            engine.run(api["borrowed_tape"](owned), api["borrowed_count"](h), api["borrowed_count"](n))
        engine.commit(owned)
        api["need"](api["body"](owned) == expected and api["snapshot"]((h, n, sentinel)) == saved,
                    "caller-owned commit preserves live descriptors")
        closed(engine, api)
        owned.clear()
        for value in (h, n, sentinel):
            value.close()
        parent.empty()
    for tape in parent.tapes:
        api["erase_marker"](tape)
    api["need"](all(all(bit == api["BLANK"] for bit in tape.cells) for tape in parent.tapes), "empty caller at recursive boundary")
    return dict(named_rejections=["headroom", "inexact"], valid_retry=True, parent_peak=parent.peak,
                prefix_peak=engine.pool.peak, scalar_peak=engine.scalar.pool.peak, live_parent_counts=3)


def extent():
    api = runtime()
    parent = api["ScratchPool"](32)
    scope = api["OuterScope"](parent)
    with api["no_decode"](), api["sealed_constructors"](), scope.installed():
        unused, body = api["Count"].literal(3), api["Count"].literal(5)
        saved = api["snapshot"]((unused, body))
        result = api["selected_extent"](unused, body)
        expected = api["Count"].literal(15*selected.GAMMA)
        from encoded import compare
        api["need"](compare(result, expected) == 0 and api["snapshot"]((unused, body)) == saved,
                    "full cover extent uses encoded multiplication and preserves inputs")
        for value in (unused, body, result, expected):
            value.close()
        parent.empty()
    for tape in parent.tapes:
        api["erase_marker"](tape)
    return dict(cover_bits=selected.GAMMA.bit_length(), gaussian_count_bits=(15*selected.GAMMA).bit_length(),
                unused_rows=3, body_gaussians=5, peak=parent.peak, payload_allocated=False)
