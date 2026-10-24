"""Exact caller replay; ordinary and optimized runs compare a frozen receipt.

Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor credit and limits are in README/PROOF. Host arrays accelerate finite
verification; they are not a fixed-tape evaluator or a bit-step cost trace.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = {}
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + row["path"])
        sources[row["path"]] = data
    require(len(sources) == 8, "exact eight-input scope")
    return sources


def module(name, path, data):
    """Compile checked bytes, bypassing predecessor bytecode caches."""
    result = types.ModuleType(name)
    result.__file__ = str(ROOT / path)
    sys.modules[name] = result
    exec(compile(data, result.__file__, "exec"), result.__dict__)
    return result


class InverseSpy:
    def __init__(self):
        self.calls = []
        self.frozen = False

    def __call__(self, value, modulus):
        require(not self.frozen, "modular inverse called after fixed setup")
        self.calls.append((value, modulus))
        return pow(value, -1, modulus)


def digest(values):
    return hashlib.sha256(b"".join(x.to_bytes(4, "little") for x in values)).hexdigest()


def fixed_reconstruction(caller, crt):
    cases = (((3,), 5, 1), ((3, 5), 7, 11), ((11, 13), 17, 19),
             ((3, 5, 7), 11, 13))
    checked = valid = 0
    prefix_mutant = None
    for moduli, target, prefix in cases:
        spy = InverseSpy()
        fixed = caller.FixedCRT(moduli, target, prefix, inverse=spy)
        require(len(spy.calls) == len(moduli) + 1, "m+1 setup inversions")
        spy.frozen = True
        weights = tuple(p*c*a % fixed.product for m, p, c, a in fixed.terms)
        for residues in product(*(range(1 << (m-1).bit_length()) for m in moduli)):
            value = fixed.evaluate(residues)
            expected_valid = all(a < m for a, m in zip(residues, moduli))
            reference = crt.decode_group(residues, moduli) if expected_valid else 0
            require(value.valid == expected_valid and value.k_A == reference,
                    "cached reconstruction agrees with retained decode_group")
            expected = reference * pow(fixed.product*prefix, -1, target) % target
            require(value.offset == expected, "target-prefix offset agrees")
            if expected_valid:
                require(sum(a*w for a, w in zip(residues, weights)) % fixed.product
                        == reference, "fixed-weight identity")
                valid += 1
                wrong = reference * pow(fixed.product, -1, target) % target
                if prefix != 1 and wrong != expected and prefix_mutant is None:
                    prefix_mutant = dict(moduli=moduli, target=target, right_prefix=prefix,
                                         residues=residues, expected=expected, wrong=wrong)
            checked += 1
        require(len(spy.calls) == len(moduli) + 1, "no address-dependent inversions")
    require(prefix_mutant is not None, "nontrivial-prefix discriminator")
    rejected = 0
    for args in (((3, 9), 5), ((3, 5), 5), ((3,), 5, 5)):
        try:
            caller.FixedCRT(*args)
        except ValueError:
            rejected += 1
    require(rejected == 3, "noninvertible fixed data rejected")
    return dict(padded_vectors=checked, valid_vectors=valid,
                setup_inverses_per_case=[2, 3, 3, 4], dynamic_inverses=0,
                wrong_right_prefix=prefix_mutant, noninvertible_setups_rejected=rejected)


def caller_census(caller, crt, allocator, word_module):
    spy = InverseSpy()
    root = caller.RootCaller(crt, allocator, word_module, inverse=spy)
    require(root.setup_inverse_calls == len(spy.calls) == 3, "root fixed setup")
    spy.frozen = True
    require(all((m-1).bit_length() == w for m, w in zip(root.moduli, root.widths)),
            "proper declared prime-modulus widths")
    row = 6
    word = root.word(row)
    values = []
    valid_count = 0
    invalid_mutant = None
    # Direct bit exchange is independent of fragment concatenation in caller.py.
    positions = tuple(root.placement.map_position(i) for i in range(root.L))
    require(sorted(positions) == list(range(root.L)), "placement is a bit permutation")
    require(all(2*root.H <= positions[i] < root.L-root.H
                for lo, hi in root.axes[:3] for i in range(lo, hi)),
            "source coordinates omit u, t and the back field")
    reference_networks = {offset: crt.benes(crt.rotation(32, 17, offset))
                          for offset in range(17)}
    for y in range(1 << root.Y):
        query = root.evaluate(row, y)
        placed = y << root.H
        original = sum(((placed >> (root.L-1-positions[i])) & 1)
                       << (root.L-1-i) for i in range(root.L))
        coordinates = tuple((original >> (root.L-hi)) & ((1 << (hi-lo))-1)
                            for lo, hi in root.axes[:3])
        require(query.coordinates == coordinates, "transported current-axis descriptors")
        value = root.fixed.evaluate(coordinates[:2])
        root.fixed.check_reference(value, crt)
        require((query.valid, query.k_A, query.offset) == (value.valid, value.k_A, value.offset),
                "current caller reconstructs current coordinates")
        reference_bit, reference_table = reference_networks[value.offset][row]
        require(query.local_bit == reference_bit
                and query.bit == reference_table[coordinates[2]],
                "current control agrees with separately constructed retained network")
        valid_count += query.valid
        values.append(query.bit)
        if not query.valid and invalid_mutant is None:
            wrong_offset = (crt.decode_group(query.residues, root.moduli[:2])
                            * root.fixed.target_inverse % root.moduli[2])
            wrong_bit = root.network(wrong_offset)[row][1][query.target]
            if wrong_bit != query.bit:
                invalid_mutant = dict(current_y=y, residues=query.residues,
                                      correct_offset=0, wrong_offset=wrong_offset,
                                      correct_bit=query.bit, wrong_bit=wrong_bit)
    require(invalid_mutant is not None, "invalid-left disabling changes an actual control")
    source = lambda y: (values[y],)
    word.check_source(source)
    # A current-y oracle is finite test storage, not a priced runtime cache.
    inverse_image = [None]*word.size
    repaired = [None]*word.size
    ideal = [None]*word.size
    good = 0
    for address in range(word.size):
        state = word.unpack(address)
        origin = word.run(state, source, inverse=True)
        require(word.run(origin, source) == state, "literal forward after inverse")
        origin_id = word.pack(origin)
        inverse_image[address] = origin_id
        is_good = word.good(state)
        require(word.good(origin) == is_good, "raw good/bad invariance")
        key = word.pack(word.ideal(origin, source))
        require(word.good(word.unpack(key)) == is_good, "ideal good/bad invariance")
        if is_good:
            require(key == address, "raw equals ideal on good set")
            good += 1
        destination = address if is_good else key
        require(repaired[destination] is None, "exceptional repair key injectivity")
        repaired[destination] = origin_id
        ideal_destination = word.pack(word.ideal(state, source))
        require(ideal[ideal_destination] is None, "ideal switch injectivity")
        ideal[ideal_destination] = address
    require(sorted(inverse_image) == list(range(word.size)), "full raw permutation")
    require(repaired == ideal and all(x is not None for x in repaired),
            "complete exceptional key/payload correspondence")
    witnesses = []
    for state in ((0, 1, 4), (1, 1, 4)):
        trace = []
        live = root.source(row, trace)
        origin = word.run(state, live, inverse=True)
        key = word.ideal(origin, live)
        require(len(trace) == 3 and all(x["valid"] for x in trace), "three all-valid query sites")
        require(not word.good(state), "exceptional-address witness")
        stale = root.stale_offset_source(row, trace[0]["offset"])
        wrong_origin = word.run(state, stale, inverse=True)
        wrong_key = word.ideal(wrong_origin, stale)
        require(key != wrong_key, "frozen entry offset produces a wrong repair key")
        require(word.run(origin, root.source(row)) == state, "witness reversibility")
        if state[0] == 0:
            require(origin != wrong_origin and trace[0]["offset"] != trace[1]["offset"],
                    "second inverse-load query discriminator")
        if state[0] == 1:
            require(origin == wrong_origin and trace[0]["offset"] == trace[1]["offset"]
                    and trace[2]["offset"] != trace[1]["offset"], "final T query discriminator")
        witnesses.append(dict(input=state, origin=origin, key=key, query_trace=trace,
                              stale_offset=trace[0]["offset"], stale_origin=wrong_origin,
                              stale_key=wrong_key))
    require(len(spy.calls) == 3, "no query-time inversion across full caller replay")
    return dict(widths=root.widths, moduli=root.moduli, L=root.L, H=root.H, G=root.G,
                K=root.K, row=row, local_bit=root.schedule[row], target_y_bit=word.targets[0],
                source_blocks=root.placement.source_blocks,
                destination_blocks=root.placement.destination_blocks,
                middle_states=len(values), valid_left_middle_states=valid_count,
                invalid_left_middle_states=len(values)-valid_count, word_addresses=word.size,
                good_addresses=good, repaired_bad_addresses=word.size-good,
                back_bit="spectator, omitted from Word; controls omit it by descriptors",
                setup_inverse_calls=spy.calls, dynamic_inverse_calls=0,
                inverse_permutation_sha256=digest(inverse_image),
                repaired_payload_sha256=digest(repaired), invalid_left_mutant=invalid_mutant,
                stale_offset_witnesses=witnesses)


def cost_terms(p, ell):
    q = p+2
    return (768*q*q, 1572864*q**4, 24576*q**3, 24576*q*q*ell**3,
            1200*q*(ell+2)**2*2**ell, 3072*q*ell*4**ell, 3072*q*q*ell)


def budget():
    base_terms = cost_terms(2, 1)
    base_bound = 2**4*4**16
    require(all(8*t <= base_bound for t in base_terms), "seven induction base bounds")
    factors = (Fraction(1), Fraction(1), Fraction(1), Fraction(8), Fraction(32, 9),
               Fraction(8), Fraction(2))
    max_ratio = Fraction(0)
    cases = 0
    for p in range(2, 201):
        q = p+2
        for ell in range(1, 41):
            terms = cost_terms(p, ell)
            bound = 2**(4*ell)*q**16
            require(all(8*t <= bound for t in terms) and sum(terms) <= bound,
                    "refreshed source-table allowance")
            require(all(n <= f*t for n, f, t in zip(cost_terms(p, ell+1), factors, terms)),
                    "ell induction factors")
            require(all(n*q**16 <= t*(q+1)**16
                        for n, t in zip(cost_terms(p+1, ell), terms)), "q monotonic ratios")
            require(4*(ell+2)+8*(ell+2)**2+8*ell <= 25*(ell+2)**2,
                    "corrected per-network polynomial")
            G = 64*(ell+(q-1).bit_length())
            require(sum(terms)*q**48 <= 2**(G-60*ell), "guard amortization")
            max_ratio = max(max_ratio, Fraction(sum(terms), bound))
            cases += 1
    require(max_ratio == Fraction(sum(base_terms), base_bound), "exact maximum at base")
    return dict(domain="p>=2, ell>=1 (proof); p=2..200, ell=1..40 (corroborating grid)",
                grid_cases=cases, query_sites=3, networks_per_axis=6,
                base_terms=base_terms, base_sum=sum(base_terms), base_bound=base_bound,
                maximum_checked_ratio=str(max_ratio),
                scope="conditional source-table tariff only; not complete key/tape cost")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="explicit receipt authoring")
    args = parser.parse_args()
    sources = authenticate()
    loaded = []
    for name, path in (("crt_query_reference", "research/unconditional-batched-crt/check_batched_crt.py"),
                       ("crt_query_placement", "research/crt-reservoir-placement/allocator.py"),
                       ("crt_query_word", "research/crt-arbitrary-source-repair/verify.py")):
        loaded.append(module(name, path, sources[path]))
    path = "research/crt-repair-query-budget/caller.py"
    caller = module("crt_query_caller", path, (ROOT/path).read_bytes())
    crt, allocator, word_module = loaded
    result = dict(status="PASS_CRT_REPAIR_QUERY_BUDGET", authenticated_inputs=len(sources),
                  fixed_reconstruction=fixed_reconstruction(caller, crt),
                  caller=caller_census(caller, crt, allocator, word_module), budget=budget())
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    receipt = PACKAGE/"RESULT.json"
    if args.write_result:
        receipt.write_text(encoded)
    else:
        require(receipt.read_text() == encoded, "frozen RESULT.json differs; no files rewritten")
    print(result["status"])
    print("131072 word addresses; 32768 current middle states; 3 fixed inversions, 0 query inversions")
    print("Three current-state sites; two stale-offset witnesses; conditional ratio "
          + result["budget"]["maximum_checked_ratio"])


if __name__ == "__main__":
    main()
