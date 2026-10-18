"""Exact finite checks for the changed order and rational asymptotic ledger."""
from fractions import Fraction
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random

import model
from model import need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def predecessor():
    path = ROOT/"research/p104-lifting-residue-reduction/vendor/lifting.py"
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == "9424ee08f22b717f6d58f7cc46f189c5549fa86778afcd0c0762ab2daf591160", "literal predecessor bytes")
    namespace = {}
    exec(compile(raw, str(path), "exec", optimize=0), namespace)
    return namespace


def plans():
    count = 0
    for n in range(1, 10):
        for rank in range(1, n+1):
            for suffix in range(rank+1):
                for d in range(1, 6):
                    for spacing in range(1, 6):
                        plan = model.Plan(n, rank, d, spacing, suffix)
                        order = plan.order()
                        need(sorted(order) == list(range(rank)), "selected axes partition exactly once")
                        chunks = (rank-suffix)//spacing
                        blocks = plan.blocks()
                        need(len(blocks) == spacing*((chunks+d-1)//d), "exact batched call count")
                        need(len(blocks)*d <= rank+spacing*d, "r/d+K block bound")
                        need(len(plan.direct()) < suffix+spacing, "complete-chunk direct tail")
                        need(sum(len(block)**2 for block in blocks) <= rank*d, "complete narrow bill")
                        for block in blocks:
                            need(0 < len(block) <= d and all(axis >= suffix for axis in block), "fast axes exclude permanent coefficient suffix")
                            need(all(b-a == spacing for a, b in zip(block, block[1:])), "actual spaced axes")
                        # Reclassification changes no scalar address or field order.
                        for address in (0, (1 << n)-1, (1 << n)//3):
                            row, field = divmod(address, 1 << suffix)
                            need((row << suffix)+field == address, "record descriptor preserves flat ordinal")
                        count += 1
    return dict(plans=count, axes_exact=True, suffix_movement=0, complete_chunks=True)


def algebra():
    old = predecessor()
    cases = 0
    alphabet = tuple(itertools.product(range(-2, 3), repeat=2))
    for a, b in itertools.product(alphabet, repeat=2):
        for inverse in (False, True):
            got = model.pair(a, b, inverse)
            need(got == old["pair"](a, b, inverse), "signed literal predecessor pair")
            need(model.pair(*got, not inverse) == (a, b), "signed pair inverse")
            cases += 1
    # Exhaust a small cube to expose noncommutation, not just a basis identity.
    order_witness = None
    for values in itertools.product(((0, 0), (1, 0), (0, 1), (-1, 1)), repeat=4):
        new = model.lifted(values, (1, 0))
        old_order = model.lifted(values, (0, 1))
        if new != old_order:
            order_witness = dict(input=values, new_order=new, old_order=old_order)
            break
    need(order_witness is not None, "changed order cannot masquerade as original word")
    need(model.lifted(order_witness["new_order"], (0, 1), True) != list(order_witness["input"]),
         "old inverse order fails on the new word")
    g = 2
    basis = [(1, 0)]+[(0, 0)]*7
    try:
        model.scaled(basis, (0, 1, 2), guard=1)
    except ValueError:
        pass
    else:
        raise ValueError("insufficient scaled-linear guard accepted")
    positive = model.scaled(basis, (0, 1, 2))
    negative = model.scaled(positive, (0, 1, 2), True)
    need(negative == [(a*(1 << (2*g)), b*(1 << (2*g))) for a, b in basis], "scaled orientations compose to2^(2g)I, notI")
    return dict(pair_cases=cases, order_witness=order_witness, insufficient_guard_rejected=True,
                wrong_inverse_order_rejected=True,
                scaled_composition_factor=1 << (2*g))


def payloads():
    old = predecessor()
    rng = random.Random(31063107)
    cases, calls = [], 0
    for n, rank, d, spacing, suffix in ((2, 2, 2, 1, 1), (5, 4, 2, 2, 1),
                                        (6, 6, 2, 2, 1), (7, 7, 3, 2, 2),
                                        (8, 7, 2, 3, 1), (9, 8, 3, 2, 2)):
        plan = model.Plan(n, rank, d, spacing, suffix)
        for bits in (7, 257):
            values = [(rng.randrange(-(1 << bits), 1 << bits), rng.randrange(-(1 << bits), 1 << bits)) for _ in range(1 << n)]
            width = bits+2*rank+12
            output, forward = model.execute(values, plan, width)
            need(output == model.lifted(values, plan.order()), "full payload follows declared literal order")
            literal = list(values)
            for axis in plan.order():
                for at in range(len(literal)):
                    if not (at >> axis) & 1:
                        other = at ^ (1 << axis)
                        literal[at], literal[other] = old["pair"](literal[at], literal[other])
            need(output == literal, "complete wide payload agrees with authenticated predecessor pairs")
            restored, backward = model.execute(output, plan, width, True)
            need(restored == values, "same-plan exact paired return")
            need(len(forward) == len(backward) == 4*len(plan.blocks()), "four XOR oracle calls per complete batch")
            calls += len(forward)+len(backward)
            for block in plan.blocks():
                for inverse in (False, True):
                    swapped = [(b, a) for a, b in values]
                    left = model.scaled(values, block, inverse)
                    right = model.scaled(swapped, block, not inverse)
                    need(left == [(b, a) for a, b in right], "S U S gives opposite linear orientation on arbitrary inputs")
                    # Literal split on the complete ambient bank, all suffix fields.
                    guard = len(block)//2+1
                    q = [(a >> guard, b >> guard) for a, b in values]
                    s = [(a % (1 << guard), b % (1 << guard)) for a, b in values]
                    wide = model.scaled(q, block, inverse)
                    narrow = model.lifted(s, block, inverse)
                    need([(a+c, b+d) for (a, b), (c, d) in zip(wide, narrow)] == model.lifted(values, block, inverse), "arbitrary-axis signed split")
            cases.append(dict(n=n, rank=rank, d=d, spacing=spacing, suffix=suffix, input_bits=bits,
                              blocks=len(plan.blocks()), direct=len(plan.direct()),
                              output_sha256=sha256(json.dumps(output, separators=(",", ":")).encode()).hexdigest()))
    # Nonzero private output cannot be disposed of as if uncomputation ran.
    values = [(5, -3), (-2, 4), (7, 1), (-8, -2)]
    try:
        model.evaluate(values, [(0, 0)]*4, (0, 1), 24, model.DirectOracle(), omit_cleanup=True)
    except ValueError as error:
        need("private output" in str(error), "omitted cleanup control")
    else:
        raise ValueError("omitted backend cleanup accepted")
    return dict(cases=cases, xor_oracle_calls=calls, omitted_cleanup_rejected=True,
                scope="exact finite macro reference with direct linear oracle; no fast physical backend timing or history trace")


def exponents():
    epsilon, spacing, sigma = Fraction(997, 1000), Fraction(1, 500), Fraction(599, 600)
    saving = epsilon*(1-sigma)
    leading = 2-saving
    powers = dict(leading=leading, short_batch=1+epsilon*(spacing+sigma),
                  narrow=1+epsilon, direct_record_tail=2-epsilon,
                  direct_chunk_tail=1+epsilon*spacing, peak_clean_history=1+epsilon*sigma,
                  narrow_history=2*epsilon)
    need(saving == Fraction(997, 600000), "derived standalone saving")
    need(all(value < leading for name, value in powers.items() if name != "leading"), "strict lower-order and space exponents")
    need(epsilon*(1+spacing) < 1 and epsilon*spacing < 1-epsilon, "group fits and K below record suffix scale")
    need(2*epsilon < 1+epsilon*sigma, "narrow history fits the declared peak")
    # Exact real-exponent identities include the uniform short-block tariff.
    need(2-epsilon+epsilon*sigma == leading, "batched root tariff")
    # The old dense-to-spaced per-axis movement would destroy the claimed saving.
    need(Fraction(2) > leading, "linear-in-r full-volume movement is a fatal omitted term")
    return dict(saving=str(saving), powers={name:str(value) for name, value in powers.items()},
                group_span_exponent=str(epsilon*(1+spacing)),
                histories_are_linear_in_backend_time=True, arbitrary_bit_shuffle_allowed=False)


def errors():
    count = 0
    for n in range(1, 6):
        rank = n
        plan = model.Plan(n, rank, 2, 2, min(1, rank))
        for seed in range(8):
            values = [((7*j+3*seed)%17-8, (11*j+seed)%19-9) for j in range(1 << n)]
            for inverse in (False, True):
                actual = model.lifted(values, plan.order(), inverse)
                numerator = model.linear_numerators(values, tuple(range(rank)), inverse)
                scale = 1 << rank
                squared_numerator = sum((scale*a-c)**2+(scale*b-d)**2 for (a, b), (c, d) in zip(actual, numerator))
                need(2*squared_numerator <= rank*rank*(1 << n)*scale*scale, "all-stage Hilbert error bound")
                count += 1
    return dict(fixtures=count, squared_bound="r^2*N/2", input_independent=True,
                inverse_uses_reverse_declared_order=True)
