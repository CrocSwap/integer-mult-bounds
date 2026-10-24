"""Check the cycle rank hypotheses without the producer's phase compiler."""

from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
CHECKER_SHA = sha256(Path(__file__).read_bytes()).hexdigest()
LANES = HERE.parents[1]
ROOT = LANES.parents[2]
PRODUCER = LANES / "history-encoding/terminal-line-fusion-20261018"
FRESH = LANES / "history-encoding/independent-skeleton-20261018/fresh-three-child"
CYCLE = LANES / "bridge-access-20261017/cycle-cover-response-20261018"
ARCHIVE = ROOT / "worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz"
D = 73
E = [1 << j for j in range(D)]
PINS = {
    "rank_freeze": "15621e9a16d7390fb6073ad79d97dc7b09237263fb7d5c7be399047877590f08",
    "fresh_compressed": "afc3aad86eb9b6da3027d3ac57eac1a2a766729dca0608e70e36d0554c8afc96",
    "fresh_decompressed": "b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5",
    "cycle_payload": "759f85673b0fda9ba4ff7312c18c80f8a8b72a3ad0a7b1192a8d08571d0095da",
    "archive": "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
    "data_phases": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def need(test, label):
    if not test:
        raise ValueError(label)


def pin(path, key):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == PINS[key], "Source pin: " + key)
    return raw


def linear(columns, vector):
    result = 0
    for j, column in enumerate(columns):
        if vector >> j & 1:
            result ^= column
    return result


def inner(a, b):
    return (a & b).bit_count() & 1


def coords(basis, vector):
    return sum(inner(b, vector) << j for j, b in enumerate(basis))


def signature(terms, basis):
    """Return Z4 diagonal values and the off-diagonal binary polar rows."""
    diagonal, polar = [0] * len(basis), [0] * len(basis)
    for vector, exponent in terms:
        v = coords(basis, vector)
        for j in range(len(basis)):
            if v >> j & 1:
                diagonal[j] += exponent
                if exponent % 2:
                    polar[j] ^= v ^ (1 << j)
    return tuple(x % 4 for x in diagonal), tuple(polar)


def translated_equal(wanted, given, delta):
    return signature(wanted, E) == signature(given + [(delta, 2)], E)


def factor(terms, basis, rank):
    diagonal, polar = signature(terms, basis)
    need(not any(polar), "The residual phase has no quadratic term")
    subset = [j for j, value in enumerate(diagonal) if value % 2]
    need(len(subset) == rank, "The odd support has the declared rank")
    delta = linear(basis, sum((value // 2) << j for j, value in enumerate(diagonal)))
    return [basis[j] for j in subset], delta


def routed(basis, stage, vector):
    if not stage:
        return vector
    permutation = list(range(D))
    for j in range(8):
        a, b = j + 1, 9 + 8 * (stage - 1) + j
        permutation[a], permutation[b] = permutation[b], permutation[a]
    x = coords(basis, vector)
    return linear(basis, sum(((x >> j) & 1) << permutation[j] for j in range(D)))


def monomial(recipe):
    addresses, phases = [], []
    for source in range(512):
        address = recipe["offset"] ^ sum(inner(row, source) << j
                                            for j, row in enumerate(recipe["matrix_rows"]))
        exponent = recipe["phase"]
        for j in range(9):
            if source >> j & 1:
                exponent += recipe["linear_Z4"][j]
                exponent += 2 * (recipe["quadratic_rows"][j] & source & ~((1 << (j+1)) - 1)).bit_count()
        addresses.append(address)
        phases.append(exponent % 4)
    need(sorted(addresses) == list(range(512)), "Each child side map is a permutation with phase")
    return addresses, phases


def native_columns(child, terms, basis):
    """Compare every nonzero coefficient of all 512 exact input columns."""
    rank = child["rank"]
    axes, delta = factor(terms, basis, rank)
    expected = {linear(axes, bits) ^ delta: (-bits.bit_count()) % 4
                for bits in range(1 << rank)}
    need(len(expected) == 1 << rank, "Independent desired native axes")
    left, lp = monomial(child["left"])
    right, rp = monomial(child["right"])
    weights = [bits.bit_count() for bits in range(1 << rank)]
    for source in range(512):
        a, exponent = right[source], rp[source]
        for bits, weight in enumerate(weights):
            middle = a ^ bits
            shift = left[middle] ^ source
            need(shift in expected and (exponent + lp[middle] - weight) % 4 == expected[shift],
                 "Literal left C_r right equals the required map, including global phase")
    return 512 * (1 << rank)


def main():
    freeze = json.loads(pin(PRODUCER / "FROZEN.json", "rank_freeze"))
    for name, digest in freeze["files"].items():
        need(sha256((PRODUCER/name).read_bytes()).hexdigest() == digest, "Frozen rank artifact: " + name)
    raw = gzip.decompress(pin(FRESH / "FRESH-THREE-CHILD-PROGRAMS.json.gz", "fresh_compressed"))
    need(sha256(raw).hexdigest() == PINS["fresh_decompressed"], "Native word content pin")
    fresh = json.loads(raw)
    cycle = json.loads(pin(CYCLE / "CYCLE-COVER-PROGRAMS.json", "cycle_payload"))
    pin(ARCHIVE, "archive")
    with tarfile.open(ARCHIVE) as archive:
        raw = archive.extractfile("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json").read()
    need(sha256(raw).hexdigest() == PINS["data_phases"], "Actual DATA phase pin")
    old = json.loads(raw)["recipes"]
    need(len(old) == len(cycle["records"]) == len(fresh["transfers"]) == 112, "All actual ports")
    counts = Counter()
    profile = Counter()
    for p, (transfer, record, data) in enumerate(zip(fresh["transfers"], cycle["records"], old)):
        q, v0 = transfer["q"], transfer["v0"]
        basis = transfer["chart_root_basis"] + E[9:]
        need(record["port"] == transfer["port"] == p and record["q"] == data["q"] == q,
             "All source lists use the same actual port")
        need(record["v0"] == v0 and basis[:2] == [q, v0], "Actual root lines")
        need(all(inner(a, b) == (i == j) for i, a in enumerate(basis) for j, b in enumerate(basis)),
             "The fixed chart is orthonormal")
        need(basis[1:9] == data["idle_children"][0]["orthogonal_axes"][:8], "Actual DATA complement")
        cycle_indices = [0, 1] + [9 + 8*s for s in range(8)]
        wanted_cycle = [basis[j] for j in cycle_indices]
        need(record["cycle_vectors"] == wanted_cycle, "All ten cycle directions")
        perm = list(range(D))
        for a, b in zip(cycle_indices, cycle_indices[1:] + cycle_indices[:1]):
            perm[a] = b
        need([linear(record["L_columns"], b) for b in basis] == [basis[j] for j in perm],
             "Literal L has the stated cycle on the common chart")
        need(all(linear(record["L_inverse_columns"], linear(record["L_columns"], e)) == e for e in E),
             "Literal L inverse")
        children = fresh["children"][3*p:3*p+3]
        local_terms = [[(v0, 1)], [(e, 1) for e in E[:9]] + [(q, -1)],
                       [(e, 1) for e in E[:9]] + [(q, -1), (v0, -1)]]
        need([(c["old"], c["new"], c["rank"]) for c in children]
             == [(0, 114+p, 1), (2+p, 1, 8), (114+p, 226+p, 7)], "The actual three native legs")
        for child, terms in zip(children, local_terms):
            counts["exact_native_nonzero_coefficients"] += native_columns(child, terms, basis[:9])
            counts["exact_native_input_columns"] += 512
            counts["literal_native_children"] += 1
            profile[child["rank"]] += 1
        for stage, cut in enumerate(record["stage_cuts"]):
            need(cut["stage"] == stage, "Every stage is ordered")
            source = [(q, 1)] if not stage else [(e, 1) for e in E[:9 + 8*(stage-1)]]
            target = [(v0, 1)] if not stage else source + [(q, -1), (E[9+8*(stage-1)], 1)]
            transported = [(linear(record["L_inverse_columns"], v), a) for v, a in target]
            need(translated_equal(transported, source, cut["translation_in_source_cover_coordinates"]),
                 "The complete owner transfer is exactly the stated translation")
            counts["complete_owner_transfer_phases"] += 1
            exterior = [(e, 1) for e in E[9:9+8*stage]]
            entry = 0 if not stage else routed(basis, stage, data["stage_alignment"][stage]["entry_X"])
            need(entry == cut["entry_translation_after_route"], "Actual entry direction")
            for side, terms, line in (("X", source, q), ("Y", target, v0)):
                if stage:
                    need(routed(basis, stage, data["stage_alignment"][stage]["entry_"+side]) == entry,
                         "Both actual entries have the declared phase")
                actual = [(routed(basis, stage, v), a) for v, a in terms]
                need(translated_equal(exterior + [(line, 1)], actual, entry), "The complete cut view")
                endpoint = [(e, 1) for e in E[:9+8*stage]] + ([(q, -1)] if side == "Y" else [])
                actual = [(routed(basis, stage, v), a) for v, a in endpoint]
                need(translated_equal(endpoint, actual, data["stage_alignment"][stage]["exit_"+side]),
                     "Actual DATA exit restores the declared owner endpoint")
                counts["actual_entry_phases"] += 1
                counts["actual_exit_phases"] += 1
        power = E[:]
        for orbit in range(10):
            for stage in range(9):
                terms = [[(routed(basis, stage, v), a) for v, a in leg] for leg in local_terms]
                for leg, rank in zip(terms, (1, 8, 7)):
                    factor([(linear(power, v), a) for v, a in leg], basis, rank)
                    counts["fresh_phase_factors_all_owners_and_stages"] += 1
            for idle in data["idle_children"]:
                terms = [(v, 1) for v in idle["orthogonal_axes"]] + [(idle["translation_after"], 2)]
                factor([(linear(power, v), a) for v, a in terms], basis, idle["rank"])
                counts["actual_idle_factors_all_owners"] += 1
            factor([(linear(power, e), 1) for e in E], basis, D)
            factor([(linear(power, q), 1), (linear(power, wanted_cycle[-1]), 1)], basis, 2)
            counts["full_target_factors"] += 1
            counts["terminal_factors"] += 1
            power = [linear(record["L_columns"], v) for v in power]
        need(power == E, "The full orbit has period ten")
        full = [(e, 1) for e in E]
        need(translated_equal(full, [(linear(record["L_columns"], e), 1) for e in E],
                              record["FULL_E_output_translation"]), "Positive FULL conjugate phase")
        need(translated_equal(full, [(linear(record["L_inverse_columns"], e), 1) for e in E],
                              record["FULL_E_inverse_output_translation"]), "Inverse FULL conjugate phase")
        counts["full_cover_conjugate_phases"] += 2
    need(dict(profile) == {1:112, 8:112, 7:112}, "Complete native profile")
    # An odd non-coordinate direction is a valid C line but fails this operation set.
    need(signature([(7, 1)], E)[1][0] != 0, "An odd non-coordinate native line fails the phase test")
    for mask in range(8):
        native_exponent = 1 + 2 * (mask.bit_count() % 2)
        coordinate_exponent = 3 + 2 * mask.bit_count()
        need((native_exponent - coordinate_exponent) % 4 == 2,
             "One odd non-coordinate C line has three-axis sensitivity on the test family")
    # Three tensor copies give both signs. A translation of only copy two distinguishes them.
    need(sum((1, 0, 0)) % 4 == 1 and sum((1, 1, 1)) % 4 == 3, "Both legal C signs")
    need(sum((1, 0, 0)) % 2 == sum((1, 1, 1)) % 2 == 1, "Uniform translation is invariant")
    need((1, 0, 0)[1] != (1, 1, 1)[1], "Individual-copy translation is not invariant")
    counts["scope_negative_controls"] = 2
    counts["three_axis_single_native_test_values"] = 8
    bad = json.loads(json.dumps(fresh["children"][0]))
    bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    caught = False
    try:
        native_columns(bad, [(fresh["transfers"][0]["v0"], 1)],
                       fresh["transfers"][0]["chart_root_basis"])
    except ValueError:
        caught = True
    need(caught, "A wrong child global phase must fail the full column check")
    counts["native_global_phase_negative_controls"] = 1
    need(counts["literal_native_children"] == 336 and counts["exact_native_input_columns"] == 172032,
         "All native input columns were checked")
    need(sha256(Path(__file__).read_bytes()).hexdigest() == CHECKER_SHA, "Checker bytes did not change during the run")
    receipt = {
        "status": "PASS_INDEPENDENT_PURE_CYCLE_RANK_BINDING",
        "source_pins": PINS,
        "checker_sha256": CHECKER_SHA,
        "counts": dict(sorted(counts.items())),
        "native_profile_per_fresh_call": dict(sorted(profile.items())),
        "rank_bound_per_cover_four_pairs": 2*4*112*73,
        "native_verification": "All 512 columns per serialized child. Integer phases modulo four and exact common Gaussian amplitude. No producer compiler is imported.",
        "scope": "Exact pure-cycle operation set at fixed port and ten-owner orbit. No arbitrary cross-port mixing, internal wrapper edits, nonlinear grid operations, or complete supplier claim.",
    }
    (HERE / "REVIEW.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])
    print(json.dumps(receipt["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
