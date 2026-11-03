"""Check the whole selected-word RMS contract and exact finite controls."""

import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analysis as A

SOURCE = "research/p104-helper470-twin-rung-removal/WORD.json.gz"


def authenticate(raw, pin):
    A.need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source hash")


def tiny_weights(events):
    rows = [[Q(1), Q(0)], [Q(0), Q(1)], [Q(0), Q(0)]]
    weights = []
    for event in events:
        op, r = event[:2]
        a, c = sum(map(abs, rows[r])), Q(1)
        if op in {"INIT", "CLEAR"}:
            rows[r] = [Q(0), Q(0)]
        elif op != "MOVE":
            q = Q(event[-2])
            if op == "SCALE":
                a, c = abs(q) * a, abs(q)
                rows[r] = [q*v for v in rows[r]]
            elif op == "COPY":
                rows[r] = [q*v for v in rows[event[2]]]
            else:
                a += abs(q) * sum(map(abs, rows[event[2]]))
                c += abs(q)
                rows[r] = [x+q*y for x, y in zip(rows[r], rows[event[2]])]
        weights.append((a, c))
    return weights, rows


def transition(state, event):
    values = list(state)
    op, r = event[:2]
    allowance = abs(values[r])
    if op in {"INIT", "CLEAR"}:
        values[r] = Q(0)
    elif op == "MOVE":
        pass
    else:
        q = Q(event[-2])
        if op == "SCALE":
            allowance *= abs(q)
            values[r] *= q
        elif op == "COPY":
            values[r] = q * values[event[2]]
        else:
            allowance += abs(q) * abs(values[event[2]])
            values[r] += q * values[event[2]]
    return values, allowance


def distribution(initial, events, u):
    states = {tuple(map(Q, initial)): Q(1)}
    for event in events:
        next_states = {}
        for state, probability in states.items():
            values, allowance = transition(state, event)
            signs = (-1, 1) if event[0] in A.ROUNDED else (0,)
            for sign in signs:
                changed = list(values)
                changed[event[1]] += sign * u * allowance
                key = tuple(changed)
                next_states[key] = next_states.get(key, Q(0)) + probability / len(signs)
        states = next_states
    A.need(sum(states.values()) == 1, "probability mass")
    return states


def finite_checks(rho):
    fixtures = [
        [["ADD", 0, 1, "1/2", 0], ["ADD", 0, 1, "1/2", 0]],
        [["SCALE", 0, "1/2", 0], ["ADD", 1, 0, "-2", 0], ["MOVE", 0, 0, 1, False]],
        [["INIT", 2, 0], ["COPY", 2, 0, "1", 0], ["MOVE", 2, 0, 1, True],
         ["ADD", 1, 2, "1", 0], ["CLEAR", 2, 0], ["SCALE", 1, "-1", 0]],
        [["SCALE", 0, "-2", 0], ["ADD", 0, 1, "3/4", 0],
         ["SCALE", 1, "1/2", 0], ["ADD", 1, 0, "-1/2", 0]],
    ]
    cases = endpoints = 0
    for events in fixtures:
        word = {"public": 2, "owned_fields": 1, "program": events}
        weights, exact_rows = tiny_weights(events)
        peaks, scores, coefficients = A.forward(word, weights)
        A.need(A.transpose(word, weights) == (scores, coefficients), "tiny transfer agreement")
        j, k = [A.sqrt_upper(x[0]) for x in peaks[:2]]
        u = Q(1, 64)
        A.need(u*k < 1, "tiny feedback stability")
        for pair in product(range(-1, 2), repeat=2):
            initial = (*pair, 0)
            states = distribution(initial, events, u)
            exact = [sum(x*y for x, y in zip(row, pair)) for row in exact_rows]
            scale = max(map(abs, pair))
            for r in range(3):
                mean = sum(probability*state[r] for state, probability in states.items())
                variance = sum(probability*(state[r]-exact[r])**2 for state, probability in states.items())
                a, b = [A.sqrt_upper(x) for x in scores[r][:2]]
                bound = scale*u*(a+b*u*j/(1-u*k))
                A.need(mean == exact[r] and variance <= bound*bound, "adaptive exact moment bound")
                if scale == 0:
                    A.need(variance == 0 and all(state[r] == 0 for state in states), "zero-scale induction")
            endpoints += len(states)
            cases += 1

    u = Q(1, 4)
    scale_twice = [["SCALE", 0, "1", 0]] * 2
    fresh = distribution((1, 0, 0), scale_twice, u)
    variance = sum(p*(state[0]-1)**2 for state, p in fresh.items())
    A.need(variance == 2*u*u+u**4 > 2*u*u, "actual-input feedback is necessary")
    reused_mean = ((1-u)**2+(1+u)**2)/2
    A.need(reused_mean == 1+u*u != 1, "reused seed must not qualify as conditional mean zero")
    A.need((1+u)**2 != 1, "biased defects must not qualify")
    erased = [Q(0), Q(0), Q(1)]
    erased, _ = transition(erased, ["ADD", 0, 2, "1", 0])
    erased, _ = transition(erased, ["CLEAR", 2, 0])
    A.need(erased == [1, 0, 0], "exported error survives local reset")
    copied, _ = transition([Q(2), Q(0), Q(7)], ["COPY", 2, 0, "1", 0])
    A.need(copied[2] == 2 and copied[2] != 9, "COPY overwrites")
    excursion = Q(1, 4)
    erased, _ = transition([Q(1), Q(0), Q(1)+excursion], ["CLEAR", 2, 0])
    A.need(excursion > 0 and erased == [1, 0, 0], "a prefix excursion can vanish at exit")
    probability_bound = 770*rho*rho/(1 << 10)
    A.need(probability_bound < 1, "zero-scale counterexample has a strict bound")
    zero_errors = [Q(0)]*770
    A.need(int(max(zero_errors) >= 0) == 1 > probability_bound, "old non-strict zero-threshold corollary is false")
    A.need(int(max(zero_errors) > 0) == 0, "strict zero-threshold correction")
    for numerator in range(100):
        for denominator in range(1, 10):
            value = Q(numerator, denominator)
            bound = A.sqrt_upper(value)
            A.need(bound*bound >= value and (bound == 0 or (bound-1)**2 < value), "integer square-root ceiling")
    return {"adaptive_cases": cases, "terminal_states": endpoints, "sqrt_cases": 900,
            "controls": ["actual-input feedback", "reused randomness", "biased defects",
                         "exported reset error", "COPY overwrite", "non-strict zero threshold",
                         "strict zero threshold", "erased prefix excursion"],
            "zero_scale_failed_old_bound": probability_bound}


def stopped_tail(events, stochastic):
    j, k = stochastic["J"], stochastic["K"]
    guard = 16
    exponent = Q(1 << (2*guard), 2*(j+k)**2)
    term = lower = Q(1)
    for degree in range(1, 65):
        term *= exponent/degree
        lower += term
    A.need(lower > 2*events*(1 << 41), "stopped whole-word exponential tail")
    return {"guard": guard, "event_union_size": events,
            "exponential_argument": exponent, "taylor_degree": 64,
            "positive_taylor_lower": lower, "strict_failure_bound": Q(1, 1 << 41),
            "covers": "all fields at all prefixes; B>0, and exact zero error when B=0"}


def run():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in manifest["files"] if row["path"] == SOURCE)
    raw = (HERE.parents[1] / SOURCE).read_bytes()
    authenticate(raw, pin)
    try:
        authenticate(raw+b"changed", pin)
    except ValueError:
        pass
    else:
        raise ValueError("source change accepted")
    word = json.loads(gzip.decompress(raw))
    A.need(word["schema"] == "p104-accumulated-block-composition/2" and word["public"] == 770
           and word["owned_fields"] == 29 and len(word["program"]) == 22803, "selected word identity")
    weights, ideal = A.ideal(word)
    A.need(weights == A.integer_weights(word), "every ideal operand weight: Fraction/integer")
    peaks, scores, coefficients = A.forward(word, weights)
    A.need(A.transpose(word, weights) == (scores, coefficients), "every final coefficient and score: forward/transpose")
    peak_rows = {}
    for i, (value, cut, role) in enumerate(peaks):
        key = (cut, role)
        if key not in peak_rows:
            peak_rows[key] = A.reverse_cut(word, cut, role)[1]
        row = peak_rows[key]
        actual = sum((v*v*weights[j][i]**2 if i < 2 else abs(v)*weights[j][i-2]
                      for j, v in row.items()), Q(0))
        A.need(actual == value, "peak transpose score")
    norm, cut, role = ideal["peak_ideal_norm"]
    A.need(sum(map(abs, A.reverse_cut(word, cut, role)[0].values())) == norm, "peak ideal transpose")
    stochastic = A.guards(peaks, scores, word["public"], True)
    absolute = A.guards(peaks, scores, word["public"], False)
    controls = finite_checks(stochastic["final_rho"])
    return A.encode({
        "schema_version": 1, "status": "PASS_SELECTED_WHOLE_WORD_STOCHASTIC",
        "base_commit": manifest["base_commit"], "source_sha256": pin["sha256"],
        "events": len(word["program"]), "public_fields": word["public"],
        "all_fields": word["public"]+word["owned_fields"], "ideal": ideal,
        "score_order": ["J_squared", "K_squared", "J_absolute", "K_absolute"],
        "prefix_peaks": peaks, "final_scores": scores,
        "final_coefficient_hashes": [A.coefficient_digest(row) for row in coefficients],
        "stochastic": stochastic, "matched_absolute": absolute,
        "stopped_tail": stopped_tail(len(word["program"]), stochastic), "finite_checks": controls,
        "source_corruption_controls": 1, "selected_frontier_changed": False,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output is None:
        A.need(result == json.loads((HERE / "RESULT.json").read_text()), "receipt equality")
    else:
        with args.output.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    print("PASS_SELECTED_WHOLE_WORD_STOCHASTIC", result["events"], "events;",
          result["all_fields"], "final rows; RMS guard", result["stochastic"]["final_guard"],
          "; tail guard", result["stopped_tail"]["guard"], "; absolute guard",
          result["matched_absolute"]["final_guard"])


if __name__ == "__main__":
    main()
