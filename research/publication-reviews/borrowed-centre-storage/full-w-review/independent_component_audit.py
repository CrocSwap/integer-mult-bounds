"""Check the frozen component counts, error map, and adapter phases."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path


def need(value, label):
    if not value:
        raise ValueError(label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.annex / "frozen"
    lanes = root / "work/centre-encoding-campaign-20261014/lanes"
    dirty = lanes / "portable-source-codes/dirty-record-hosting-20261015"
    pins = {}

    def read(path):
        data = path.read_bytes()
        pins[str(path.relative_to(root))] = hashlib.sha256(data).hexdigest()
        return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)

    word = read(dirty / "consumer/DIRTY-CONSUMER-WORD.json")
    donors = read(dirty / "TWO-CUT-DONORS.json")
    cert = read(lanes / "paired-package-review/upstream-followthrough-20261015/base/research/joint-query/certificate.json.gz")
    acceptance = read(dirty / "FULL-W-ACCEPTANCE.json")
    selected = sorted(donors["allocations"]["all"]["selected"], key=lambda r: r["role"])
    need([r["role"] for r in selected] == list(range(128)), "All donor roles")
    need(len({r["family"] for r in selected}) == 128, "Distinct donor families")
    need(all(0 <= r["family"] < 14336 for r in selected), "Old productive donors")

    costs = {"add": {F(1): 8, F(2): 10, F(1, 2): 10, F(1, 4): 12}}
    procedure_counts, procedure_bills, coefficients = {}, {}, {}
    for name, events in word["procedures"].items():
        count, bill, coeff = Counter(), 0, Counter()
        for event in events:
            op = event["op"]
            count[op] += 1
            if op in ("add", "scale"):
                c = F(event["c"])
                coeff[op + ":" + str(c)] += 1
                if op == "add":
                    need(abs(c) in costs[op], "Declared ADD tariff")
                    bill += costs[op][abs(c)]
                else:
                    shifts = {F(1): 0, F(2): 1, F(4): 2, F(1, 2): 1, F(1, 4): 2}
                    need(abs(c) in shifts, "Declared SCALE tariff")
                    bill += 2 * (shifts[abs(c)] + (c < 0))
            elif op == "clear":
                need(event["field"] == "C", "Only owned C is cleared")
                bill += 2
        procedure_counts[name] = dict(count)
        procedure_bills[name] = bill
        coefficients[name] = dict(sorted(coeff.items()))
    need(procedure_bills == {"capture": 64, "cleanup": 23780, "repair": 20258}, "Literal scalar bills")

    schedule = word["schedule"]
    anchors = [e["old_event"] for e in schedule if "old_event" in e]
    need(anchors == list(range(482)), "All old event anchors")
    need(len(schedule) == 1506, "Full outer word")
    calls = Counter(e["name"] for e in schedule if e["op"] == "call_procedure")
    need(calls == {"capture": 16, "repair": 16, "cleanup": 16}, "All procedure instances")
    need(all(e["bindings"]["C"] == 14336 for e in schedule if e["op"] == "call_procedure"), "Old owned C0")
    swaps = [e for e in schedule if e["op"] == "physical_pair_swap"]
    need(len(swaps) == 96 and all(e["ports"] == list(range(112)) for e in swaps), "Full-W swaps")
    need(all(e["ordered_scalar_word"] == ["a+=b", "b-=a", "a+=b", "b=-b"] for e in swaps), "Literal scalar swap")
    peak = max(sum(8 for r in donors["rows"] if r["capture_after_event"] <= event <= r["cleanup_after_event"])
               for event in range(482))
    need(peak == 48, "Peak donor leases")

    profiles = [Counter(), Counter(), Counter()]
    phase_checks, final_debts, witnesses = 0, 0, []
    basis = [1 << j for j in range(73)]
    characters = [0] + basis + [basis[j] | basis[k] for j in range(73) for k in range(j)]
    for row in selected:
        for cut, adapter in enumerate(row["adapters"]):
            axes, shift = adapter["axes"], adapter["translation"]
            if axes or shift:
                need(len(axes) in (1, 2), "Nonempty native adapter rank")
                profiles[cut][len(axes)] += 1
            low, high, cross = adapter["phase"]
            witness = None
            for character in characters:
                direct = (sum((character & v).bit_count() % 2 for v in axes)
                          + 2 * ((character & shift).bit_count() % 2)) % 4
                bits = [j for j in range(73) if character >> j & 1]
                packed = sum((low >> j & 1) + 2 * (high >> j & 1) for j in bits)
                packed += 2 * sum(cross >> (j * (j - 1) // 2 + k) & 1 for j in bits for k in bits if k < j)
                need(direct == packed % 4, "Direct and packed adapter phases")
                if direct and witness is None:
                    witness = {"role": row["role"], "family": row["family"], "character": character, "phase": direct}
                phase_checks += 1
            if cut == 2 and (axes or shift):
                need(witness is not None, "Final adapter has a nonzero phase")
                final_debts += 1
                witnesses.append(witness)
    profile = sum(profiles, Counter())
    need(profiles == [Counter({1: 90}), Counter({1: 71}), Counter({1: 39, 2: 7})], "All three adapter profiles")
    need(final_debts == 46, "Final phase debts")
    native_profile = profile + Counter({1: 16 * (procedure_counts["repair"]["line"] + 112)})
    cover_maps = sum(e["op"] == "donor_cover_map" for e in schedule)
    cover_maps += sum(calls[n] * procedure_counts[n].get("map", 0) for n in calls)
    scalar = sum(calls[n] * procedure_bills[n] for n in calls)
    bridges = len(swaps) * 224 * (3 * 8 + 2)
    totals = {"native_profile": dict(sorted(native_profile.items())),
              "native_rank_mass": sum(k * v for k, v in native_profile.items()),
              "native_wrappers": 2 * sum(native_profile.values()),
              "cover_maps": cover_maps, "procedure_scalar_allowance": scalar,
              "full_replacement_bridge_scalar_allowance": bridges,
              "scalar_components_including_full_replacement_bridges": scalar + bridges}
    for key in ("native_rank_mass", "native_wrappers", "cover_maps", "scalar_components_including_full_replacement_bridges"):
        need(totals[key] == acceptance[key], "Accepted component count: " + key)

    a, t = cert["A_ports"], cert["T_ports"]
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in cert["R_rows"]]
    gram = lambda ports, i, j: sum(r[i][p] * r[j][p] for p in ports)
    need(all(gram(t, i, j) == 4 * (i == j) for i in range(8) for j in range(8)), "Actual T minor Gram")
    ex = [[F(0) for _ in a] for _ in range(112)]
    for j, p in enumerate(a):
        ex[p][j] = -1
    for p in t:
        for j, q in enumerate(a):
            ex[p][j] = sum(r[k][p] * r[k][q] for k in range(8)) / 4
    need(all(sum(r[k][p] * ex[p][j] for p in range(112)) == 0 for k in range(8) for j in range(8)), "Actual R0 E_X is zero")
    support = [p for p in range(112) if any(ex[p])]
    need(len(support) == 16, "Both-bank error support is32 fields")
    wrong = [row[:] for row in ex]
    for p in t:
        wrong[p] = [-x for x in wrong[p]]
    need(any(sum(r[k][p] * wrong[p][j] for p in range(112)) for k in range(8) for j in range(8)), "Wrong T sign leaves a query error")
    need(any(ex[p][0] for p in range(112)), "Omitted E correction leaves data dirt")
    result = {"status": "PASS_INDEPENDENT_FULL_W_COMPONENT_AUDIT",
              "method": "Read pinned data without producer imports. Count literal operations. Evaluate adapter phases directly on zero, basis, and basis-pair characters. Check the actual rational error map.",
              "source_pins": pins, "procedure_counts": procedure_counts,
              "procedure_bills": procedure_bills, "coefficients": coefficients,
              "totals": totals, "distinct_donors": 128, "peak_live_donors": peak,
              "adapter_profiles_by_cut": [dict(sorted(p.items())) for p in profiles],
              "direct_adapter_phase_evaluations": phase_checks,
              "nonzero_final_adapter_witnesses": witnesses,
              "error_support_per_bank": support,
              "controls": {"wrong_T_error_sign_rejected": True,
                           "omitted_E_correction_leaves_nonzero_data": True,
                           "omitted_nonempty_A3_leaves_phase_debt_count": final_debts},
              "limits": "This is a static component audit. The four frozen review replays supply the complete schedule, route, and cleanup checks. No raw native kernel, new child hosting, full supplier invoice, or kappa calculation is run."}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
