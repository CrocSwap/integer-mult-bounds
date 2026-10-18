"""Finite semantic evidence and exact rational cost checks."""
from fractions import Fraction
from hashlib import sha256
import json
import random

from model import Executor, SOURCE, CORE, OLD, collector, character, shift
from sources import need


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def direct_monomial(values, recipe, multiplicity):
    """Independent address-formula oracle, without the compiled gate word."""
    output = [None]*len(values)
    m = len(recipe["matrix_rows"])
    for address, value in enumerate(values):
        destination, phase = 0, multiplicity*recipe["phase"]
        for column in range(multiplicity):
            x = sum(((address >> (i*multiplicity+column))&1) << i for i in range(m))
            y = recipe["offset"] ^ sum(((row & x).bit_count()&1) << i for i, row in enumerate(recipe["matrix_rows"]))
            for i in range(m):
                destination |= ((y >> i)&1) << (i*multiplicity+column)
                if (x >> i)&1:
                    phase += recipe["linear_Z4"][i]
                    for j in range(i+1, m):
                        phase += 2*((x >> j)&1)*((recipe["quadratic_rows"][i] >> j)&1)
        need(output[destination] is None, "actual affine bijection")
        output[destination] = OLD["rot"](value, phase)
    return output


def binding():
    receipts = []
    for index, recipe in zip((2031, 2033), SOURCE["recipes"]):
        for side in ("right", "left"):
            record = recipe[side]
            word = SOURCE["binary_word"](record)
            for address in range(512):
                changed = address
                for op, target, source in word:
                    if op == "flip" or (changed >> source)&1:
                        changed ^= 1 << target
                expected = record["offset"] ^ sum(((row & address).bit_count()&1) << i for i, row in enumerate(record["matrix_rows"]))
                need(changed == expected, "compiled actual affine map")
            receipts.append(dict(event=index, side=side, cnot=sum(op == "add" for op, _, _ in word),
                                 toggles=sum(op == "flip" for op, _, _ in word), recipe_sha256=digest(record)))
    need((receipts[0]["cnot"], receipts[0]["toggles"], receipts[1]["cnot"], receipts[1]["toggles"]) == (11, 7, 8, 0),
         "actual outbound wrapper invoice")
    # Independent ideal-column check of the paired native boundary.
    recipes = SOURCE["recipes"]
    plans = [(OLD["plan"](recipe["left"]), OLD["plan"](recipe["right"])) for recipe in recipes]
    for column in range(512):
        vector = [(0, 0)]*512
        vector[column] = (1, 0)
        sent = OLD["exact"](vector, 7, *plans[0])
        returned = OLD["exact"](sent, 7, *plans[1])
        need(returned == [(a << 14, b << 14) for a, b in vector], "actual ideal native pair on every column")
    return dict(actual_events=[2025, 2039], transports=[2031, 2033], wrappers=receipts,
                ideal_pair_columns=512, affine_addresses=2048)


def intervals():
    cases = 0
    for n in range(1, 9):
        for start in range(n):
            for stop in range(start+1, n+1):
                axes = tuple(range(start, stop))
                for suffix in range(n+1):
                    for spacing in (1, 2, 3):
                        engine = Executor(n, 64, d=2, spacing=spacing, suffix=suffix)
                        blocks, direct = engine.split_axes(axes)
                        need(sorted([axis for block in blocks for axis in block]+list(direct)) == list(axes), "actual interval partition")
                        need(all(axis >= suffix for block in blocks for axis in block), "coefficient suffix inactive")
                        need(len(blocks) <= Fraction(len(axes), 2)+spacing, "uniform block count including tail")
                        need(len(direct) < suffix+spacing, "interval deferred-axis bound")
                        cases += 1
    return dict(interval_plans=cases, active_offsets_supported=True, payload_transpose=False)


def algebra():
    receipts = []
    for n, target, control in ((2, (1,), (0,)), (2, (0,), (1,)),
                                (6, (0, 1), (4, 5)), (6, (4, 5), (1, 2)),
                                (9, (6, 7, 8), (0, 1, 2))):
        engine = Executor(n, 160)
        values = [((index*31)%257-128, (index*19)%251-125) for index in range(1 << n)]
        before = list(values)
        for controls in (control, None):
            got = engine.address_gate(values, target, controls)
            expected = []
            for index in range(len(values)):
                old = index
                for j, axis in enumerate(target):
                    if controls is None or (index >> controls[j])&1:
                        old ^= 1 << axis
                expected.append(values[old])
            need(got == expected and values == before, "exact dense address permutation and source preservation")
        for inverse in (False, True):
            dirty = CORE.encode([(7-index, 2*index-3) for index in range(len(values))], 160)
            got = engine.dense_linear(values, dirty, target, 160, inverse)
            expected = CORE.xor_words(dirty, CORE.encode(CORE.scaled(values, target, inverse), 160))
            need(got == expected, "both exact scaled orientations on arbitrary dirty target")
        receipts.append(dict(n=n, target=target, control=control, counts=engine.counts))
    engine = Executor(2, 64)
    witness = [(0, 0), (0, 0), (0, 0), (1, 0)]
    expected = [witness[index ^ (((index >> 0)&1) << 1)] for index in range(4)]
    unguarded = engine.address_word(witness, (1,), (0,))
    need(unguarded != expected, "unguarded CNOT control")
    guarded = engine.address_word(shift(witness, 2), (1,), (0,))
    wrong_phase = shift(character(guarded, (0,), negative=True), -2)
    need(wrong_phase != expected, "omitted linear phase changes exact permutation")
    return dict(cases=receipts, unguarded=dict(input=witness, actual=unguarded, expected=expected),
                omitted_phase_rejected=True)


def original():
    rng = random.Random(3109)
    receipts = []
    for n, axes, outer in ((4, (0, 1, 2, 3), 3), (6, (2, 3, 4, 5), 2),
                            (9, tuple(range(7)), 3)):
        for bits in (8, 257):
            values = [(rng.randrange(-(1 << bits), 1 << bits), rng.randrange(-(1 << bits), 1 << bits)) for _ in range(1 << n)]
            engine = Executor(n, bits+80, outer=outer)
            got = engine.original_lift(values, axes)
            literal = list(values)
            for axis in axes:
                for index in range(len(values)):
                    if not (index >> axis)&1:
                        other = index ^ (1 << axis)
                        literal[index], literal[other] = OLD["pair"](literal[index], literal[other])
            need(got == literal, "original consecutive floor word, not changed inner order")
            need(engine.original_lift(got, axes, True) == values, "original-order inverse")
            receipts.append(dict(n=n, axes=axes, bits=bits, counts=engine.counts, output_sha256=digest(got)))
    return dict(cases=receipts, unchanged_integer_map=True)


def consumers():
    recipe = SOURCE["recipes"][0]
    receipts = []
    for bits, beta, mode in ((7, 0, "ordinary"), (7, 12, "ordinary"), (70, 8, "cancellation"), (7, 8, "zero")):
        n = 512
        base = [(((j*31)%257-128)*(1 << bits), ((j*17)%251-125)*(1 << bits)) for j in range(n)]
        sources = [list(base), [(-a, -b) for a, b in base], [(0, 0)]*n, [(0, 0)]*n, [(0, 0)]*n]
        if mode != "zero":
            sources[2] = [(1 if j == 0 else 0, -1 if j == 7 else 0) for j in range(n)] if mode == "cancellation" else \
                         [(j%5-2, j%7-3) for j in range(n)]
        query = [(j%13-6, j%11-5) for j in range(n)]
        before = digest([sources, query])
        engine = Executor(9, bits+beta+120)
        got = collector(engine, sources, query, 3, beta, recipe)
        expected = OLD["collector"](sources, query, 3, beta, OLD["plan"](recipe["left"]), OLD["plan"](recipe["right"]))
        for key in ("query", "grid", "private", "sent", "returned", "entrance"):
            need(got[key] == expected[key], "literal actual collector equality: "+key)
        need(digest([sources, query]) == before, "five arbitrary dirty inputs and entrance query unchanged")
        need(engine.counts["address_gates"] == 52 and engine.counts["address_oracles"] == 104,
             "four actual wrapper gate count")
        need(engine.counts["dense_linear_oracles"] == 24 and engine.counts["fast_lifts"] == 464,
             "nested actual collector oracle count")
        receipts.append(dict(bits=bits, beta=beta, mode=mode, grid=got["grid"],
                             query_sha256=digest(got["query"]), counts=engine.counts))
    synthetic = dict(matrix_rows=[3, 1, 4], offset=5, phase=3,
                     linear_Z4=[1, 2, 3], quadratic_rows=[2, 4, 0])
    tensor = []
    for multiplicity in (1, 2, 3):
        n = 3*multiplicity
        values = [(j*3-17, j*7-23) for j in range(1 << n)]
        engine = Executor(n, 192)
        got = engine.monomial(values, synthetic, multiplicity)
        need(got == direct_monomial(values, synthetic, multiplicity), "full repeated-column phase/address map")
        need(engine.monomial(got, synthetic, multiplicity, True) == values, "dense tensor wrapper inverse")
        tensor.append(dict(multiplicity=multiplicity, n=n, output_sha256=digest(got)))
    return dict(actual_collector=receipts, synthetic_tensor=tensor,
                scope="lambda1 actual collector and small synthetic tensor wrappers; direct semantic backend, not fast physical timing")


def costs():
    epsilon, spacing, sigma = Fraction(997, 1000), Fraction(1, 500), Fraction(599, 600)
    q = epsilon*(spacing+sigma)
    gamma = (1+q)/2
    gain = 1-gamma
    powers = dict(original_core=1+gamma, full_inner_groups=2-epsilon*(1-sigma),
                  short_inner_groups=2+q-gamma, outer_tail=1+q,
                  inner_narrow=1+epsilon, outer_narrow=1+gamma,
                  record_scans=3-gamma-epsilon, chunk_scans=2-gamma+epsilon*spacing)
    need(gain == Fraction(8003, 6000000), "original-order saving")
    need(epsilon < gamma < epsilon*(1+spacing) < 1, "outer block lies in intended source regime")
    need(all(value <= 1+gamma for value in powers.values()), "complete core time ledger")
    need(2*gamma > max(1+epsilon*sigma, 2*epsilon, 1), "outer narrow history sets conservative peak")
    need(2-epsilon*(1-sigma) < 1+gamma, "dense wrapper fits original core tariff")
    selected = Fraction(836330098538459, 500000000000000000)
    frozen = Fraction(5*3070+4*3542+32778, 73*832)
    forgiven_selected = 1+(76524*selected-104)/Fraction(73*832)
    need(frozen == Fraction(599, 584) and frozen > 1 and forgiven_selected > 1, "retained frozen-consumer rejection")
    need(76524*gain-104 < 0, "do not overextend the forgiven linear screen to the new smaller saving")
    return dict(gamma=str(gamma), saving=str(gain), time_powers={key:str(value) for key, value in powers.items()},
                clean_space_power=str(2*gamma), frozen_zero_saving_bill=str(frozen),
                forgiven_at_selected=str(forgiven_selected), new_supplier=False)
