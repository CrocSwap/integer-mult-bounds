"""Exact, read-only normal/optimized corroboration of the scoped theorem.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The dense polynomial oracle forms separate powers, not the online recurrence.
"""
import argparse
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import types

PACKAGE = Path(__file__).resolve().parent


def load_local(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


M = load_local("shrinking_halo_engine", PACKAGE / "engine.py")
S = load_local("shrinking_halo_source", PACKAGE / "source.py")
T = load_local("shrinking_halo_tensor", PACKAGE / "tensor.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rejected(function, label):
    try:
        function()
    except (ValueError, IndexError):
        return label
    raise ValueError("negative control accepted: " + label)


def pair_norm(value):
    return abs(value[0]) + abs(value[1])


def dense_polynomial(matrix, data, terms, normalizer):
    """Independent exact mechanism: explicit successive powers and sum."""
    n = len(data)
    power = tuple((Q(z[0]), Q(z[1])) for z in data)
    total = [list(z) for z in power]
    for _ in range(1, terms):
        following = []
        for row in range(n):
            following.append(tuple(sum((matrix[row][column] * power[column][part]
                                        for column in range(n)), Q(0))
                                   for part in (0, 1)))
        power = tuple(following)
        for row in range(n):
            for part in (0, 1):
                total[row][part] += power[row][part]
    return tuple(tuple(value / normalizer for value in z) for z in total)


def rounded_global(matrix, data, plan):
    """Full-period host comparator, solely to verify exact rounded conformance."""
    n, scale = len(data), 1 << plan.bits
    coefficients = [[M.inward(value, plan.bits) for value in row] for row in matrix]
    current = [(0, 0)] * n
    for _ in range(plan.terms):
        current = [tuple(M.trunc((data[row][part] << (plan.bits - plan.normalizer_shift))
                               + sum(coefficients[row][column] * current[column][part]
                                     for column in range(n)), scale)
                         for part in (0, 1)) for row in range(n)]
    return tuple(current)


def run_line(matrix, data, plan, lower, length, engine=M, table=None, bill=None):
    bill = bill or engine.Bill()
    table = table or engine.prepare_table(plan, lambda r, c: matrix[r][c], "finite exact E", bill)[0]
    before_table = engine.tape_digest(table.tape)
    saved_lower, saved_length = lower - plan.halo, length + 2 * plan.halo
    page = engine.extract_page(table, saved_lower, saved_length, bill)
    values = tuple(data[row % plan.period] for row in range(saved_lower, saved_lower + saved_length))
    source = engine.input_tape(plan, values, bill)
    before_source, before_page = engine.tape_digest(source), engine.tape_digest(page.tape)
    output = engine.apply_line(page, source, lower, length, bill)
    require(output.tape.head == 0 and output.length == length, "owned exact output extent")
    physical_extents = (source.extent, page.tape.extent, output.tape.extent,
                        sum(t.extent for t in output.blank_scratch))
    actual = engine.consume(output)
    require(before_source == engine.tape_digest(source) and source.head == 0,
            "borrowed input bytes/origin")
    require(before_page == engine.tape_digest(page.tape) and page.tape.head == 0,
            "borrowed page bytes/origin")
    require(before_table == engine.tape_digest(table.tape) and table.tape.head == 0,
            "global table bytes/origin")
    require(all(t.head == 0 and not any(t.snapshot()) for t in output.blank_scratch),
            "alternate backing cleanup")
    expected = rounded_global(matrix, data, plan)
    require(actual == tuple(expected[row % plan.period] for row in range(lower, lower + length)),
            "exact full-period rounded conformance")
    rational_data = tuple(tuple(Q(v, 1 << plan.bits) for v in z) for z in data)
    exact = dense_polynomial(matrix, rational_data, plan.terms, 1 << plan.normalizer_shift)
    error = max(pair_norm(tuple(Q(actual[j][part], 1 << plan.bits) -
                               exact[(lower + j) % plan.period][part] for part in (0, 1)))
                for j in range(length))
    require(error <= plan.numeric_error, "proved coefficient/data bound")
    n0 = saved_length
    output_counts = [length + 2 * (plan.terms - k) * plan.halfwidth
                     for k in range(2, plan.terms + 1)]
    expected_products = 2 * plan.band * sum(output_counts)
    expected_roundings = 2 * (n0 + sum(output_counts))
    require(bill.products == expected_products, "complete multiply invoice")
    require(bill.additions == expected_products, "complete accumulation invoice")
    require(bill.roundings == expected_roundings, "all completed data roundings")
    return actual, error, bill, physical_extents


def matrix_cases():
    rng = random.Random(72)
    cases = []
    for case in range(32):
        width = 1 + case % 2
        terms = 1 + case % 4
        n = 2 * (terms - 1) * width + 15 + case % 5
        gap = Q(1 + case % 3, 8)
        bits = 9 + case % 4
        shift = 0
        while (1 << shift) * gap < 1:
            shift += 1
        plan = M.Plan(n, width, bits, terms, shift, gap)
        matrix = [[Q(0) for _ in range(n)] for _ in range(n)]
        holes = {n // 2}
        for row in range(n):
            if row in holes:
                continue
            support = [((row + offset) % n, rng.choice((-1, 1)), rng.randint(1, 7))
                       for offset in range(-width, width + 1)
                       if offset and (row + offset) % n not in holes]
            denominator = sum(weight for _, _, weight in support)
            for column, sign, weight in support:
                matrix[row][column] = sign * (1 - gap) * Q(weight, denominator)
        data = []
        for _ in range(n):
            real = rng.randint(-(1 << bits), 1 << bits)
            imag = rng.randint(-((1 << bits) - abs(real)), (1 << bits) - abs(real))
            data.append((real, imag))
        lower = (-2, n - 3, n // 2 - 1, 1)[case % 4]
        cases.append((matrix, tuple(data), plan, lower, 3))
    return cases


def finite_cases():
    receipts, nonzero_errors = [], 0
    for matrix, data, plan, lower, length in matrix_cases():
        output, error, bill, extents = run_line(matrix, data, plan, lower, length)
        nonzero_errors += int(error > 0)
        receipts.append(dict(period=plan.period, width=plan.halfwidth, terms=plan.terms,
                             bits=plan.bits, lower=lower, length=length, gap=str(plan.gap),
                             output=list(output), nonzero_error=error > 0,
                             bill=bill.record(), resident_extents=list(extents)))
    require(nonzero_errors >= 24, "nontrivial rounding fixtures")
    return receipts, nonzero_errors


def tensor_oracle(matrices, plans, data, rounded):
    """Full canonical tensor, including coordinates outside every local box."""
    sizes = tuple(p.period for p in plans)
    current = dict(data)
    if not rounded:
        current = {key: tuple(Q(v, 1 << plans[0].bits) for v in z)
                   for key, z in current.items()}
    for axis, (matrix, plan) in enumerate(zip(matrices, plans)):
        following = {}
        others = tuple(i for i in range(len(plans)) if i != axis)
        for spectator in itertools.product(*(range(sizes[i]) for i in others)):
            keys = []
            for coordinate in range(sizes[axis]):
                key, other = [], 0
                for i in range(len(plans)):
                    if i == axis:
                        key.append(coordinate)
                    else:
                        key.append(spectator[other]); other += 1
                keys.append(tuple(key))
            line = tuple(current[key] for key in keys)
            values = rounded_global(matrix, line, plan) if rounded else dense_polynomial(
                matrix, line, plan.terms, 1 << plan.normalizer_shift)
            following.update(zip(keys, values))
        current = following
    return current


def tensor_case(matrices, plans, targets, label, tensor_module=T, entry_services=None, source_ids=None):
    bill = M.Bill()
    def prepared():
        for axis, (matrix, plan) in enumerate(zip(matrices, plans)):
            entry = entry_services[axis] if entry_services is not None else (
                lambda r, c, matrix=matrix: matrix[r][c])
            source_id = source_ids[axis] if source_ids is not None else label + "/axis/" + str(axis)
            yield M.prepare_table(plan, entry, source_id, bill)[0]
    archive = T.pack_tables(prepared(), bill)
    archive_before = M.tape_digest(archive.tape)
    layout = T.Layout.make(plans, targets)
    scale = 1 << plans[0].bits
    full_data = {}
    for key in itertools.product(*(range(p.period) for p in plans)):
        code = sum((i + 3) * (x + 1) ** 2 for i, x in enumerate(key))
        real = (code * 173 % (scale // 2)) - scale // 4
        imag = (code * 97 % (scale // 3)) - scale // 6
        full_data[key] = real, imag
    def local_values():
        for offsets in T.coordinate_odometer(layout.lengths):
            canonical = tuple((lo + x) % p.period for lo, x, p in zip(layout.lowers, offsets, plans))
            yield full_data[canonical]
    source = T.rectangle_input(layout, local_values(), bill)
    start_products, start_scans = bill.products, bill.page_scans
    output = tensor_module.apply_tensor(archive, targets, source, bill)
    values = tensor_module.consume_tensor(output)
    require(archive_before == M.tape_digest(archive.tape) and archive.tape.head == 0,
            "tensor preserves global source archive")
    exact = tensor_oracle(matrices, plans, full_data, rounded=False)
    rounded = tensor_oracle(matrices, plans, full_data, rounded=True)
    errors = []
    for key, value in values:
        canonical = tuple(x % p.period for x, p in zip(key, plans))
        require(value == rounded[canonical], "full rounded tensor equality")
        errors.append(pair_norm(tuple(Q(value[part], scale) - exact[canonical][part]
                                      for part in (0, 1))))
    error = max(errors)
    require(error <= sum(p.numeric_error for p in plans), "complete normalized tensor bound")
    require(error > 0, "nonzero tensor rounding defect")
    expected_count = 1
    for _, length in targets:
        expected_count *= length
    require(len(values) == expected_count, "complete target tensor")
    require(len(output.role_extents) == 8, "fixed local physical role count")
    products, scans, live_count = 0, 0, layout.volume
    for axis, (plan, target, receipt) in enumerate(zip(plans, targets, output.axis_receipts)):
        lines = live_count // layout.lengths[axis]
        n = target[1]
        per_line = 2 * plan.band * ((plan.terms - 1) * n +
                                  plan.halfwidth * (plan.terms - 1) * (plan.terms - 2))
        require(receipt["products"] == lines * per_line, "tensor complete product invoice")
        expected_scans = 1 + int((layout.lowers[axis] % plan.period) + layout.lengths[axis] > plan.period)
        require(receipt["page_scans"] == expected_scans, "one page production per axis, not per line")
        require(receipt["radix_passes"] == layout.key_width, "complete sparse radix exposure")
        products += lines * per_line; scans += expected_scans
        live_count = lines * n
    require(bill.products - start_products == products and bill.page_scans - start_scans == scans,
            "complete tensor invoice totals")
    return dict(label=label, dimensions=len(plans), saved_lengths=list(layout.lengths),
                copied_records=layout.volume, target_records=len(values),
                key_width=layout.key_width, fixed_local_tape_roles=8,
                role_extents=list(output.role_extents), total_retained_local_bits=sum(n for _, n in output.role_extents),
                protected_archive_bits=archive.tape.extent, axis_receipts=list(output.axis_receipts),
                output=list(values), numerical_bound=str(sum(p.numeric_error for p in plans)),
                nonzero_error=True, bill=bill.record())


def synthetic_tensors(tensor_module=T):
    result = []
    for dimensions in (2, 3):
        matrices, plans, targets = [], [], []
        for axis in range(dimensions):
            n, width, terms = 11, 1, 2 + axis % 2
            gap = Q(axis + 2, 8)
            plan = M.Plan(n, width, 10, terms, 2, gap)
            matrix = [[Q(0) for _ in range(n)] for _ in range(n)]
            for row in range(n):
                if row == n // 2:
                    continue
                for offset in (-1, 1):
                    column = (row + offset) % n
                    if column != n // 2:
                        matrix[row][column] = (-1 if (row + axis + offset) % 2 else 1) * (1 - gap) / 2
            matrices.append(matrix); plans.append(plan)
            targets.append((-1 if axis % 2 == 0 else n - 2, 2))
        result.append(tensor_case(tuple(matrices), tuple(plans), tuple(targets),
                                 "signed-" + str(dimensions) + "d", tensor_module))
    return result


def reuse_history(engine=M):
    """Long line, short face, long line on exactly the same physical roles."""
    bill = engine.Bill()
    plan = engine.Plan(101, 1, 12, 3, 1, Q(1, 2))
    matrix = [[Q(1, 4) if (c-r) % 101 in (1, 100) else Q(0)
               for c in range(101)] for r in range(101)]
    data = tuple(((r * 73) % 2048 - 1024, (r * 31) % 1024 - 512) for r in range(101))
    table, _ = engine.prepare_table(plan, lambda r, c: matrix[r][c], "reused source", bill)
    page_role = engine.Tape(bill, "reused page")
    source_role = engine.Tape(bill, "reused source")
    iterates = (engine.Tape(bill, "reused iterate 0"), engine.Tape(bill, "reused iterate 1"))
    records = []
    exact = rounded_global(matrix, data, plan)
    for lower, length in ((2, 37), (50, 1), (70, 37)):
        before = bill.record()
        page = engine.extract_page(table, lower-plan.halo, length+2*plan.halo, bill, page_role)
        for row in range(lower-plan.halo, lower+length+plan.halo):
            engine.put_complex(source_role, data[row % 101], plan.data_width)
        source_role.rewind(); source_role.readonly = True
        output = engine.apply_line(page, source_role, lower, length, bill, workspace=iterates)
        values = engine.consume(output)
        require(values == tuple(exact[r % 101] for r in range(lower, lower+length)),
                "long-short-long exact returned values")
        source_role.readonly = False; source_role.clear()
        page_role.readonly = False; page_role.clear()
        roles = (source_role, page_role) + iterates
        require(all(t.head == 0 and t.live_bits == 0 and not any(t.snapshot()) for t in roles),
                "long-short-long retained blank suffix invariant")
        after = bill.record()
        records.append(dict(target_length=length, saved_length=length+2*plan.halo,
                            output=list(values), retained_bits=sum(t.extent for t in roles),
                            writes=after["writes"]-before["writes"],
                            moves=after["moves"]-before["moves"]))
    return records


def backing_history_control():
    correct = reuse_history()
    text = (PACKAGE / "engine.py").read_text()
    require(text.count("occupied = self.live_bits") == 1, "unique historical clear site")
    module = types.ModuleType("_shrinking_counterfactual_highwater")
    sys.modules[module.__name__] = module
    exec(compile(text.replace("occupied = self.live_bits", "occupied = self.extent"),
                 "<counterfactual high-water clearing>", "exec"), module.__dict__)
    counterfactual = reuse_history(module)
    require([x["output"] for x in correct] == [x["output"] for x in counterfactual],
            "counterfactual preserves numerical result")
    require(counterfactual[1]["writes"] > 3 * correct[1]["writes"],
            "historical backing creates a real short-face tariff")
    return dict(correct=correct, counterfactual=counterfactual,
                retained_extent_ratio="41/5", counterfactual_detected=True)


def rectangle_reuse_history():
    bill = M.Bill()
    plans = (M.Plan(17, 1, 10, 2, 1, Q(3, 4)), M.Plan(17, 1, 10, 3, 1, Q(7, 8)))
    matrices = tuple([[Q((1 if axis == 0 else -1), 8 << axis)
                        if (c-r) % 17 in (1, 16) and r != 8 and c != 8 else Q(0)
                       for c in range(17)] for r in range(17)] for axis in range(2))
    def prepared():
        for axis, plan in enumerate(plans):
            yield M.prepare_table(plan, lambda r, c, axis=axis: matrices[axis][r][c],
                                  "rectangle reuse axis " + str(axis), bill)[0]
    archive = T.pack_tables(prepared(), bill)
    workspace = T.TensorWorkspace.create(bill)
    role_ids = {id(t) for t in workspace.roles}
    data = {key: ((13*key[0]+29*key[1]) % 512-256, (31*key[0]+7*key[1]) % 256-128)
            for key in itertools.product(range(17), repeat=2)}
    expected = tensor_oracle(matrices, plans, data, rounded=True)
    history = []
    original_constructor = M.Tape.__init__
    def forbidden_constructor(*args, **kwargs):
        raise ValueError("new tape role inside rectangle reuse history")
    M.Tape.__init__ = forbidden_constructor
    try:
        for targets in (((-1, 7), (4, 5)), ((8, 1), (-1, 2)), ((1, 5), (9, 7))):
            layout = T.Layout.make(plans, targets)
            values = (data[tuple((lo+x) % 17 for lo, x in zip(layout.lowers, offsets))]
                      for offsets in T.coordinate_odometer(layout.lengths))
            before = bill.record()
            source = T.rectangle_input(layout, values, bill, workspace.rectangles[0])
            output = T.apply_tensor(archive, targets, source, bill, workspace=workspace)
            require({id(output.tape)} | {id(t) for t in output.blank_roles} == role_ids,
                    "same eight roles across completed rectangles")
            answer = T.consume_tensor(output)
            require(all(value == expected[tuple(x % 17 for x in key)] for key, value in answer),
                    "long-short-long rectangle exact output")
            require(all(t.head == 0 and t.live_bits == 0 and not any(t.snapshot())
                        for t in workspace.roles), "reused rectangle complete restoration")
            after = bill.record()
            history.append(dict(saved_lengths=list(layout.lengths), copied_records=layout.volume,
                                target_records=len(answer), output=list(answer),
                                retained_bits=sum(t.extent for t in workspace.roles),
                                writes=after["writes"]-before["writes"],
                                moves=after["moves"]-before["moves"],
                                archive_scans=after["page_scans"]-before["page_scans"]))
    finally:
        M.Tape.__init__ = original_constructor
    return dict(fixed_role_count=8, constructors_sealed_during_calls=True, history=history)


def gaussian_cases(raw):
    reference = S.make_reference(raw, (32, 8, 2, 1, 8, 32))
    reference.require_narrow_gap()
    gap = Q((reference.narrow_gap * (1 << 16)).numerator //
            (reference.narrow_gap * (1 << 16)).denominator, 1 << 16)
    shift = 0
    while (1 << shift) * gap < 1:
        shift += 1
    plan = M.Plan(reference.target_size, 2 * reference.spec.source_halfwidth + 2,
                  28, 4, shift, gap)
    require(plan.numeric_error + plan.tail_error < Q(1, 1 << 20),
            "uniform same-reference inverse target")
    prep_bill = M.Bill()
    table, height = M.prepare_table(plan, lambda r, c: S.source_entry(reference, r, c),
                                   reference.description_hash, prep_bill)
    setup = S.source_receipt(reference)
    setup["band_source_calls"] = prep_bill.setup_entries
    setup["stored_coefficient_height"] = height
    setup["table_bits"] = table.tape.extent
    setup["production_bill"] = prep_bill.record()
    # All original source entries, not just the producer's asserted band.
    matrix = [[S.source_entry(reference, r, c) for c in range(plan.period)]
              for r in range(plan.period)]
    omissions, wrap_entries = 0, 0
    holes = tuple(reference.holes)
    for r in range(plan.period):
        for c in range(plan.period):
            distance = min((r - c) % plan.period, (c - r) % plan.period)
            if distance > plan.halfwidth:
                require(matrix[r][c] == 0, "actual complete off-band support")
                omissions += 1
            if abs(r - c) > plan.period // 2 and matrix[r][c]:
                wrap_entries += 1
            if r in holes or c in holes:
                require(matrix[r][c] == 0, "actual identity holes")
    require(wrap_entries > 0 and holes, "actual wrap and holes exercised")
    scale = 1 << plan.bits
    data = tuple(((1 if r % 3 else -1) * (scale // 3 + 17 * r),
                  (-1 if r % 2 else 1) * (scale // 7 - 11 * r))
                 for r in range(plan.period))
    receipts = []
    for lower in (-2, 5, 18):
        output, error, bill, extents = run_line(matrix, data, plan, lower, 5,
                                               table=table, bill=M.Bill())
        require(error > 0, "actual source nonzero numerical error")
        receipts.append(dict(lower=lower, output=list(output), bill=bill.record(),
                             resident_extents=list(extents), nonzero_error=True))
    # An executed wrong branch: suppress genuine across-period E entries.
    dropped = [[Q(0) if abs(r - c) > plan.period // 2 else matrix[r][c]
                for c in range(plan.period)] for r in range(plan.period)]
    wrong, _, _, _ = run_line(dropped, data, plan, -2, 5)
    require(wrong != tuple(map(tuple, receipts[0]["output"])), "dropped-wrap control discriminates")
    # Fresh retained producers, not the dense checker's indexed matrix, supply
    # both actual tensor band tables. They share the same immutable spec.
    producer_reference = S.make_reference(raw, (32, 8, 2, 1, 8, 32))
    producer = lambda r, c: S.source_entry(producer_reference, r, c)
    tensor = tensor_case((matrix, matrix), (plan, plan), ((-1, 4), (5, 3)), "actual-reference-2d",
                         entry_services=(producer, producer),
                         source_ids=(producer_reference.description_hash,) * 2)
    tensor["source_setup"] = S.source_receipt(producer_reference)
    S.clear_reference(producer_reference)
    S.clear_reference(reference)
    require(not reference.entries and not reference.weights and not reference.kernel,
            "setup cache release")
    return dict(setup=setup, period=plan.period, gap=str(gap), holes=list(holes),
                original_matrix_entries=plan.period ** 2, checked_off_band_entries=omissions,
                nonzero_wrap_entries=wrap_entries, target_bits=20,
                numerical_bound=str(plan.numeric_error), tail_bound=str(plan.tail_error),
                lines=receipts, tensor=tensor, dropped_wrap_detected=True)


def negative_controls():
    controls = []
    p = M.Plan(29, 1, 10, 3, 3, Q(1, 8))
    controls.append(rejected(lambda: replace(p, normalizer_shift=2), "unfunded normalization"))
    controls.append(rejected(lambda: replace(p, bits=2), "lost normalized-source precision"))
    controls.append(rejected(lambda: replace(p, halfwidth=15), "nonunique cyclic offsets"))
    controls.append(rejected(lambda: replace(p, gap=0), "missing contraction gap"))
    controls.append(rejected(lambda: M.prepare_table(p, lambda r, c: Q(1, 2),
                                                     "invalid row", M.Bill()), "bad original row gap"))
    controls.append(rejected(lambda: M.input_tape(p, ((1024, 1),), M.Bill()), "oversized actual input"))
    table, _ = M.prepare_table(p, lambda r, c: Q(1, 4) if c == (r + 1) % p.period else Q(0),
                              "control", M.Bill())
    controls.append(rejected(lambda: M.extract_page(table, 0, p.period, M.Bill()),
                             "repeated canonical page coordinate"))
    page = M.extract_page(table, 0, 7, M.Bill())
    source = M.input_tape(p, ((100, -100),) * 7, M.Bill())
    controls.append(rejected(lambda: page.tape.write(1), "immutable coefficient page"))
    controls.append(rejected(lambda: source.write(1), "immutable fixed source"))
    controls.append(rejected(lambda: M.apply_line(page, source, 3, 3, M.Bill()),
                             "prematurely cropped dependency interval"))
    bad = M.input_tape(p, ((0, 0),) * 7, M.Bill())
    bad.readonly = False; bad.write(1); bad.rewind(); bad.readonly = True
    controls.append(rejected(lambda: M.apply_line(page, bad, 2, 3, M.Bill()),
                             "noncanonical negative zero"))
    # Real source-text changes of the consumer, tested against the independent oracle.
    text = (PACKAGE / "engine.py").read_text()
    mutations = [
        ("real += product_real; imag += product_imag", "real -= product_real; imag -= product_imag", "wrong recurrence sign"),
        ("current.walk(-2 * p.halfwidth * record_bits)", "current.walk(-(2 * p.halfwidth + 1) * record_bits)", "wrong neighbor rewind"),
        ("current.clear(); following.rewind()", "current.rewind(); following.rewind()", "missing scratch erasure"),
    ]
    case = matrix_cases()[3]
    for old, new, name in mutations:
        require(text.count(old) == 1, "unique mutation site")
        module = types.ModuleType("_shrinking_mutation_" + str(len(controls)))
        sys.modules[module.__name__] = module
        exec(compile(text.replace(old, new), "<intentional negative control>", "exec"), module.__dict__)
        # Reconstruct the plan in the mutated module; other data stay exact.
        matrix, data, p0, lower, length = case
        pp = module.Plan(**p0.__dict__)
        controls.append(rejected(lambda: run_line(matrix, data, pp, lower, length, module), name))
    tensor_text = (PACKAGE / "tensor.py").read_text()
    for old, new, name in [
        ("order = (axis,) + tuple(j for j in range(len(layout.lengths) - 1, -1, -1) if j != axis)",
         "order = tuple(range(len(layout.lengths)))", "wrong sparse axis exposure"),
        ("emit = catalog_axis == axis and begin <= row < end",
         "emit = catalog_axis == 0 and begin <= row < end", "stale axis coefficient page"),
        ("coordinate = target_lower - layout.lowers[axis] + offset",
         "coordinate = target_lower - layout.lowers[axis] + offset + 1", "shifted returned tensor key"),
    ]:
        require(tensor_text.count(old) == 1, "unique tensor mutation site")
        module = types.ModuleType("_shrinking_tensor_mutation_" + str(len(controls)))
        sys.modules[module.__name__] = module
        exec(compile(tensor_text.replace(old, new), "<intentional tensor control>", "exec"), module.__dict__)
        controls.append(rejected(lambda: synthetic_tensors(module), name))
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    raw = S.authenticated_inputs(PACKAGE)
    finite, nonzero = finite_cases()
    tensors = synthetic_tensors()
    gaussian = gaussian_cases(raw)
    controls = negative_controls()
    history = backing_history_control()
    rectangle_history = rectangle_reuse_history()
    result = dict(schema_version=1, seed=72, claim="scoped written proof and finite tape corroboration",
                  no_new_kappa=True, finite_lines=len(finite), finite_target_outputs=3 * len(finite),
                  nonzero_rounding_lines=nonzero, finite=finite, tensors=tensors, gaussian=gaussian,
                  controls=controls, control_count=len(controls),
                  backing_reuse=history, rectangle_reuse=rectangle_history,
                  program_sha256={name: sha256((PACKAGE/name).read_bytes()).hexdigest()
                                  for name in ("engine.py", "source.py", "tensor.py", "verify.py")},
                  source_sha256={path: sha256(content).hexdigest() for path, content in sorted(raw.items())})
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    receipt = PACKAGE / "RESULT.json"
    if args.write_receipt:
        receipt.write_text(encoded)
    else:
        require(receipt.is_file(), "mandatory exact receipt")
        # Canonical serialization distinguishes booleans from integers recursively.
        require(json.dumps(json.loads(receipt.read_text()), sort_keys=True, separators=(",", ":")) ==
                json.dumps(result, sort_keys=True, separators=(",", ":")), "exact typed receipt")
    print("PASS_SHRINKING_REFERENCE_HALO " + json.dumps(
        dict(finite_lines=len(finite), gaussian_rows=gaussian["period"],
             controls=len(controls), source_entries=gaussian["original_matrix_entries"],
             receipt_sha256=sha256(encoded.encode()).hexdigest(), no_new_kappa=True), sort_keys=True))


if __name__ == "__main__":
    main()
