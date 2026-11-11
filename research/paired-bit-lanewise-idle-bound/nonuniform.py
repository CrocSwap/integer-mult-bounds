"""Directed price for arbitrary separately charged lane-wise BIT IDLE masks."""

from collections import Counter
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


def module(path):
    spec = spec_from_file_location(path.stem, path)
    loaded = module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def run(root):
    assert __debug__
    uniform = module(Path(__file__).with_name("verify.py"))
    caller = uniform.load_json(root, "bit/EFREE-CALLER.json.gz")
    result = uniform.load_json(root, "bit/EFREE-RESULT.json")
    native = uniform.load_json(root, "bit/retained/inputs/BIT-NATIVE-WORD.json.gz")
    gate_key = "bit/independent/interval_gate.py"
    uniform.auth(root, gate_key)
    gate = module(root / gate_key)
    support = [{i for i, d in enumerate(caller["diagonal"]) if s in d["stages"]}
               for s in range(1, 19)]
    assert all(a & b == {0, 19} for a in support[:9] for b in support[9:])
    degrees = [len(a) - 4 for a in support]
    T, P, native_paid, old_masks = uniform.literal_invoice(caller, result, native)
    assert degrees == [sum(s in m for m in old_masks) for s in range(1, 19)]
    N, body = caller["ports"], caller["body_rank"]
    assert (caller["roles"], N, body, len(old_masks), sum(degrees)) == (38, 111, 7, 32, 144)
    assert degrees == list(range(0, 18, 2)) + list(range(16, -2, -2))

    ideal_lengths = sorted(map(len, old_masks), reverse=True)
    uniform.majorant(degrees[:9], degrees[9:], 0, ideal_lengths)
    # For scaled degrees each prefix capacity is linear between multiples
    # of N. Thus repeating each original majorant row N times is exact.
    half_bill = Counter({body * k: N * count for k, count in Counter(ideal_lengths).items()})
    paid_without_head = native_paid + half_bill
    assert P == paid_without_head + Counter({1: 4 * N})
    signed = T.copy()
    signed.subtract(paid_without_head)

    target = uniform.TARGET

    def H(rank):
        return gate.power(rank, target)

    old_free_head = gate.moment(signed, target)
    delta = gate.sub(gate.smul(H(body), 2), H(2 * body))
    assert delta[0] > 0
    min_extra_body = gate.sub(H(9 * body), H(8 * body))
    slack_penalty = gate.sub(min_extra_body, gate.add(gate.exact(5), gate.smul(delta, 9)))
    assert slack_penalty[0] > 0

    active_opposite_pairs = 8 * 8
    shared_per_stage = 2 * N
    saturated_cross_budget = 16 * N
    rank_at_K_zero = 4 * N
    bounds = []
    for K in range(shared_per_stage + 1):
        cross_credit = gate.smul(delta, min(active_opposite_pairs*K, saturated_cross_budget))
        bound = gate.sub(gate.add(old_free_head, cross_credit), H(rank_at_K_zero+K))
        assert bound[1] < 0
        bounds.append((K, bound))
    best_K, best_bound = max(bounds, key=lambda item:item[1][1])
    assert best_K == 28
    assert all(bound[1] < best_bound[0] for K,bound in bounds if K != best_K)
    assert H(rank_at_K_zero+shared_per_stage+1)[0] > H(rank_at_K_zero+shared_per_stage)[1]

    # Positive baseline price control. Giving all cross-mask credit without
    # any extra head-rank debit makes the relaxed upper positive.
    free_sharing = gate.add(gate.sub(old_free_head, H(rank_at_K_zero)),
                            gate.smul(delta,saturated_cross_budget))
    assert free_sharing[0] > 0
    return {
        "status": "PROVED_NEGATIVE_DECLARED_LANEWISE_IDLE_MODEL",
        "input_sha256": uniform.PINS,
        "target": str(target),
        "native_calls": 36,
        "minimum_physical_idles_incidence": sum(degrees)*N,
        "opposite_support_checks": 81,
        "extra_body_moment_lower_per_incidence": gate.show(min_extra_body),
        "max_cross_credit_per_two_incidents": gate.show(delta),
        "net_loss_lower_per_extra_incidence": gate.show(slack_penalty),
        "base_head_capacity": rank_at_K_zero,
        "old_paid_and_productive_match": True,
        "directed_max_margin_K": best_K,
        "directed_max_margin": gate.show(best_bound),
        "directed_K_cases_checked": len(bounds),
        "sample_directed_margins": {K: gate.show(bound) for K,bound in bounds if K in (0, 27, 28, 29, 222)},
        "larger_K_have_nonincreasing_upper": True,
        "ignore_extra_cross_rank_positive_control": gate.show(free_sharing),
        "scope": "Fixed #7001 productive profile and 36 native LOCALs, individually charged rank-seven-per-stage lane-wise masks, separate body-free heads, arbitrary rectangular scalar contexts. All extra body incidence covered.",
    }


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), sort_keys=True, indent=2))
