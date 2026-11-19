"""Independently replay the R16 exact identities, ranks and full saved roster."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
from time import process_time
import sys

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
sys.path.insert(0, str(HERE))
from verify_pulses import (E, F, P, SENDER as S, RELAY as C, RECEIVER as T,
                          HEAD, WORD, LAYOUT, adjoint, chart_banks_and_dependencies,
                          content_hash, propagate, read, need)

PRIME = 1000000007


def expand_difference(left, right, forms, ordered):
    """Read source scalar identities literally by reverse coefficient accumulation."""
    pending = defaultdict(Q)
    for k, coefficient in left.items():
        pending[int(k)] += Q(coefficient)
    for k, coefficient in right.items():
        pending[int(k)] -= Q(coefficient)
    for node in reversed(ordered):
        coefficient = pending.pop(node, 0)
        if coefficient:
            for donor, factor in forms[node]:
                pending[donor] += factor * coefficient
    need(not any(pending.values()), "exact arbitrary-input identity")


def modular_rows(forms, order, count, moves):
    """Materialize exact finite-field rows independently of the primary rank solver."""
    need(all(PRIME % divisor for divisor in range(2, isqrt(PRIME) + 1)), "alternate diagnostic modulus is prime")
    rows = {~i: {i: 1} for i in range(count)}
    for k in order:
        if k not in moves:
            continue
        v = defaultdict(int)
        for donor, q in forms[k]:
            coefficient = q.numerator * pow(q.denominator, -1, PRIME) % PRIME
            for i, x in rows[donor].items():
                v[i] += coefficient*x
        rows[k] = {i: e % PRIME for i, e in v.items() if e % PRIME}
    return rows


def rank(rows):
    """Sparse modular row elimination with descending coordinate pivots."""
    pivots = {}
    for vector in sorted(rows, key=len):
        row = dict(vector)
        while row:
            i = max(row)
            v = row[i]
            if i not in pivots:
                inverse = pow(v, -1, PRIME)
                pivots[i] = {j: value * inverse % PRIME for j,value in row.items()}
                break
            for j,e in pivots[i].items():
                value = (row.get(j, 0) - v*e) % PRIME
                if value:
                    row[j] = value
                else:
                    row.pop(j, None)
    return len(pivots)


def verify_intersection(bound, expected_rank, stock, fixed, forms, schedule, mod):
    need(bound["rank_rational"] == expected_rank and len(fixed) == 907, "the claimed exact upper rank")
    selected = set(bound["chosen_source"])
    excess = set(stock)-selected
    need(len(fixed)+len(selected) == expected_rank and
         selected <= set(stock) and set(fixed).isdisjoint(stock), "source-bound independent generator count")
    need(rank([mod[k] for k in fixed+list(selected)]) == expected_rank,
         "alternate-prime nonzero minor matching the rational rank upper bound")
    relations = bound["exact_dependencies"]
    need({r["omitted"] for r in relations} == excess and len(relations) == len(excess), "one exact lift per remaining source generator")
    support = set()
    for row in relations:
        left = {int(k):Q(v) for k,v in row["source_expression"].items()}
        right = {int(k):Q(v) for k,v in row["receiver_expression"].items()}
        missed = row["omitted"]
        need(left.get(missed) == 1 and set(left) <= selected | {missed} and set(right) <= set(fixed),
             "triangular spanning identity in the original chart stocks")
        expand_difference(left, right, forms, schedule)
        support.update(right)
    need(sorted(support) == bound["receiver_support"], "exact receiver support from the whole intersection")
    return support


def main():
    manifest = read(HERE / "ARCHIVE-SOURCES.json")
    source_files = {item["path"]: item for item in manifest["files"]}
    evidence_files = manifest["evidence_sha256"]
    need(manifest["head"] == HEAD and set(source_files) == {"source/WORD.json.gz", "source/LAYOUT.json.gz"},
         "complete source archive inventory")
    required_evidence = {"WITNESSES.json", "evidence/FUTURE-ROSTER.json", "evidence/R16-SERVER.json",
                         "evidence/REVIEW-PRIMAL.json", "evidence/SCREEN.json", "evidence/VERIFIED.json"}
    need(set(evidence_files) == required_evidence, "complete evidence archive inventory")
    for path, item in source_files.items():
        raw = (HERE / path).read_bytes()
        need(len(raw) == item["bytes"] and sha256(raw).hexdigest() == item["sha256"],
             f"source archive byte mismatch at {path}")
    for path in sorted(evidence_files):
        need(sha256((HERE / path).read_bytes()).hexdigest() == evidence_files[path],
             f"evidence archive byte mismatch at {path}")
    word, layout = read(HERE / "source/WORD.json.gz"), read(HERE / "source/LAYOUT.json.gz")
    cases = read(EVIDENCE / "SCREEN.json")
    server = read(EVIDENCE / "R16-SERVER.json")
    need(content_hash(word) == WORD == cases["source"]["word_sha256"]
         and content_hash(layout) == LAYOUT == cases["source"]["layout_sha256"]
         and cases["source"]["head"] == HEAD and cases["source"]["r16_server_receipt"] == server["receipt"]["id"],
         "pinned exact archived assets and server receipt")
    need(cases["source"]["probe_input_sha256"] == evidence_files["WITNESSES.json"]
         and cases["source"]["roster_sha256"] == evidence_files["evidence/FUTURE-ROSTER.json"]
         and cases["source"]["r16_server_sha256"] == evidence_files["evidence/R16-SERVER.json"],
         "screen bound to the exact frozen roster, probes and price receipt")
    need(server["report"]["source_candidate_sha256"] == WORD
         and server["report"]["target"] == cases["source"]["target"]
         and server["report"]["required_saving"] == cases["source"]["required_saving"],
         "original 48-call target price binding")
    moves, forms, ordered = adjoint(word)
    n = len(word["initial"])
    banks, bits, an = chart_banks_and_dependencies(word, moves, forms, ordered)
    ban = bits[E] | bits[F]
    A = [k for k in banks[T] if not an[k] & ban]
    U = [k for k in banks[S] if not an[k] & ban]
    V = [k for k in banks[C] if not an[k] & ban]
    need(cases["source_banks"] == {"receiver": A, "rank_six": U, "first_recoded": V}
         and len(A) == 907 and len(U) == 4 and len(V) == 5, "full literal stocks and causal exclusions")
    need(n == 1289 and word["frames"] == layout["frames"], "exact original arbitrary owner coordinates")
    witness = read(HERE / "WITNESSES.json")
    q1, q2 = (propagate(forms, ordered, n, dict(witness[key]["coordinates"])) for key in ("r14_pulse", "r15_pulse"))
    need(q1[F] == q2[F] == -960 and all(not q1[k] and not q2[k] for k in A)
         and all(not q1[k] for k in U) and all(not q2[k] for k in V), "exact off-span probe equations")
    mod = modular_rows(forms, ordered, n, moves)
    need(rank([mod[k] for k in A]) == 907, "receiver has 907 independent arbitrary directions over Q")
    su = verify_intersection(cases["rank_six_intersection"], 910, U, A, forms, ordered, mod)
    sv = verify_intersection(cases["first_recoded_intersection"], 909, V, A, forms, ordered, mod)
    need(su == {P}, "H6 can only restore the original 99128 line in the target receiver span")
    try:
        expand_difference({100967: "1", 100945: "-1/2"}, {P: "2"}, forms, ordered)
    except SystemExit as error:
        need(str(error) == "exact arbitrary-input identity", "invalid doubled-restoration control")
    else:
        raise SystemExit("doubled restoration coefficient passed unexpectedly")
    others = read(EVIDENCE / "FUTURE-ROSTER.json")["first_pulse_causal_source_roster"]
    ids = set(r["ingress"] for r in others)
    need(len(ids) == len(cases["cases"]) == 126 and ids == {r["ingress"] for r in cases["cases"]}, "all 126 original paid geometries")
    results = Counter()
    for case in cases["cases"]:
        k, producer = case["ingress"], case["sender"]
        need(moves[k] == (producer,T) and k in A and k != P, "actual fixed-grade original ingress")
        available = [i for i in banks[producer] if not an[i] & (ban|bits[k])]
        responses = [(q1[i],q2[i]) for i in available]
        transported = {int(i):Q(a) for i,a in case["diagonal_form"].items()}
        if transported:
            need(set(transported) <= set(available) and all(sum(coef * probe[i] for i,coef in transported.items()) == 1
                 for probe in (q1,q2)), "exact equal-nonzero value from genuine causal producer stocks")
            need(k not in sv and case["status"] == "exact quotient rank at most two",
                 "the required old second payload is absent from the first recoded chart's receiver intersection")
        else:
            seed = next(((x,y) for x,y in responses if x or y), None)
            need(seed is not None and seed[0] != seed[1] and
                 all(x*seed[1] == y*seed[0] for x,y in responses)
                 and case["status"] == "exact probe exclusion", "non-diagonal exact collinear source readouts")
        results[case["status"]] += 1
    need(results == cases["quotient_outcomes"], "replay every exact stopped row")
    verify_report = dict(source=cases["source"], input_result_sha256=evidence_files["evidence/SCREEN.json"],
                         alternate_prime=PRIME, exact_rational_rank_receiver=907, exact_rational_rank_receiver_union_768=910,
                         exact_rational_rank_receiver_union_508=909, intersections=[sorted(su),sorted(sv)],
                         exact_replayed_outcomes=dict(results), verified_cases=126)
    archived = read(EVIDENCE / "VERIFIED.json")
    archived.pop("cpu_seconds")
    need(archived == verify_report, "exact adjoint replay receipt differs from the frozen result")
    print("independent exact lower ranks", 907, 910, 909, "prime", PRIME)
    print("rational intersections", sorted(su), sorted(sv))
    print("replayed", sum(results.values()), dict(results), "cpu", round(process_time(),2))
    print("PASS_R16_ADJOINT_CERTIFICATES")


if __name__ == "__main__":
    main()
