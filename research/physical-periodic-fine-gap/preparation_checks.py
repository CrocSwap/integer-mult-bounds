"""External source-page checks against the independent original-matrix oracle.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
This is verification code, not an online preparation or execution primitive.
The supplied oracle uses Gauss-Jordan inverse subblocks, not producer Schur LU.
"""
from fractions import Fraction as Q


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def rejected(name, operation, expected):
    try:
        operation()
    except ValueError as error:
        need(str(error) == expected, name + ": wrong rejection")
        return name
    raise ValueError(name + ": negative control escaped")


def check_bank(bank, matrix, permutation, band, precision):
    n, step = len(matrix), 2*band+1
    need(len(bank) == n*step, "complete padded source bank")
    unit = 1 << precision
    for i in range(n):
        for offset in range(-band, band+1):
            j = i + offset
            exact = matrix[permutation[i]][permutation[j]] if 0 <= j < n else Q()
            actual = Q(bank[i*step+offset+band], unit)
            need(abs(actual) <= abs(exact) and abs(actual-exact) < Q(1, unit),
                 "source bank inward coefficient error")


def run(producer, run_coefficients, folded_pages, make_reference, oracle):
    receipts, controls = [], []
    cases = (((17, 1, 2, 2, 3, 96), 24), ((7, 2, 2, 1, 3, 96), 16))
    for parameters, target in cases:
        reference = make_reference(parameters)
        source_identity = reference.description_hash
        bundle = producer.prepare(reference, 1, target,
                                  run_coefficients=run_coefficients,
                                  folded_pages=folded_pages)
        p = bundle.plan
        selected, runs, boundary, matrix, block, difference = oracle.original_geometry(reference)
        need(tuple(selected) == bundle.selected and tuple(boundary) == bundle.boundary_indices,
             "independently derived original coordinate geometry")
        need(tuple(int(reference.source_at.get(q) is not None)
                   for q in range(reference.target_size)) == bundle.target_mask,
             "source-address-derived target mask")
        need(tuple(tuple(row) for row in matrix) == bundle.exact["A"],
             "all original Reference entries, including omitted offsets")
        inverse_a, inverse_b = oracle.inverse(matrix), oracle.inverse(block)
        sb = oracle.inverse([[inverse_b[i][j] for j in boundary] for i in boundary])
        sa = oracle.inverse([[inverse_a[i][j] for j in boundary] for i in boundary])
        k = [[difference[i][j] for j in boundary] for i in boundary]
        for name, actual in (("SB", sb), ("SA", sa), ("K", k)):
            need(tuple(tuple(row) for row in actual) == bundle.exact[name],
                 "inverse-subblock original " + name)
        m = len(boundary)
        permutation = []
        for left in range((m+1)//2):
            permutation.append(left)
            if m-1-left != left:
                permutation.append(m-1-left)
        check_bank(bundle.sb_coefficients, sb, permutation, p.band, p.f)
        check_bank(bundle.k_coefficients, k, permutation, p.band, p.f)
        need(bundle.folded_plan["permutation"] == permutation,
             "same original fold for matrix and inverse pages")
        need(reference.description_hash == source_identity and tuple(parameters) == p.source_spec,
             "fixed Reference identity retained")
        need(p.ideal_complex_error <= Q(1, 1 << target)
             and p.complex_error < p.ideal_complex_error,
             "separately charged original and ideal budgets")

        # An exact adversarial original RHS makes the second input exceed one.
        rhs = [Q()] * len(matrix)
        rhs[0], rhs[-1] = Q(1), Q(-1)
        expected = oracle.action(inverse_a, rhs)
        correction = oracle.action(k, [expected[i] for i in boundary])
        corrected = list(rhs)
        for index, value in zip(boundary, correction):
            corrected[index] -= value
        corrected_radius = max(map(abs, corrected))
        need(corrected_radius > 1 and corrected_radius <= p.run_radius,
             "strictly enlarged second-call actual radius is funded")

        wrong = list(bundle.k_coefficients)
        removed = 0
        for i in range(m):
            for offset in range(-p.band, p.band+1):
                j = i + offset
                if 0 <= j < m and abs(boundary[permutation[i]]-boundary[permutation[j]]) > p.source_size//2:
                    position = i*(2*p.band+1)+offset+p.band
                    removed += bool(wrong[position])
                    wrong[position] = 0
        need(removed > 0, "nonzero period-cut coefficients exercised")
        controls.append(rejected("omit_period_cut_bank_"+str(p.source_size),
            lambda: check_bank(wrong, k, permutation, p.band, p.f),
            "source bank inward coefficient error"))
        need(p.f >= max(run.native.plan.f for run in bundle.runs),
             "exact output upconversion grid")
        if p.source_size == 7:
            need([run.n for run in bundle.runs] == [2,4,1]
                 and len({run.native.plan.f for run in bundle.runs}) > 1,
                 "short terminal run uses genuinely different native precision")
        receipts.append(dict(source=list(parameters), source_identity=source_identity,
            run_headers=[run.header for run in bundle.runs], common_precision=p.f,
            common_width=p.W, maximum_scalar_width=p.maximum_scalar_width,
            source_matrix_entries=len(matrix)**2, boundary_size=m,
            period_cut_bank_entries=removed, second_radius=float(corrected_radius),
            funded_second_radius=p.run_radius, reference_error=float(p.complex_error),
            ideal_error=float(p.ideal_complex_error), target=target,
            page_receipt=bundle.receipt()))

    # The omitted tail is fixed: high entry precision alone cannot fund t=24.
    underfunded = make_reference((7, 2, 2, 1, 3, 96))
    controls.append(rejected("fixed_tail_underfunded_at_higher_target",
        lambda: producer.prepare(underfunded, 1, 24,
                                 run_coefficients=run_coefficients,
                                 folded_pages=folded_pages),
        "fixed Reference error exceeds run allocation"))
    return dict(cases=receipts, negative_controls=controls,
                oracle_method="original matrices; Gauss-Jordan inverse subblocks")
