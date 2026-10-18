#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound optimistic rank-seven budget; this does not synthesize a word.

Ross Richardson with substantial OpenAI Codex assistance. Credits and exact
source heads are in SOURCE-PINS.json and sources/CREDITS.md. No predecessor
executable is imported. All decisions are integer arithmetic.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(name):
    raw = (ROOT / "sources" / name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def authenticated_sources():
    pins = json.loads((ROOT / "SOURCE-PINS.json").read_text())
    for name, pin in pins["files"].items():
        raw = (ROOT / "sources" / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source digest: " + name)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == pin["git_blob"], "source Git blob: " + name)
    return pins


def profile(value):
    return Counter({int(r): n for r, n in value.items()})


def mass(value):
    return sum(r * n for r, n in value.items())


def main():
    pins = authenticated_sources()
    words = [read("data/WORD-" + tag + ".json.gz") for tag in ("base", "extra")]
    parents = [read("data/PARENT-" + tag + ".json.gz") for tag in ("base", "extra")]
    helpers = sorted(set(range(224, 704)) - set(words[0]["removed"]))
    helper_index = helpers.index(408)
    widths = []
    for w in words:
        need(sorted(set(range(224, 704)) - set(w["removed"])) == helpers, "ordered helper binding")
        widths.append([len(w["helper_final"].get(str(h), [0] * 9)) -
                       len(w["start_extra"].get(str(h), [])) for h in helpers])
    need(len(helpers) == 408 and widths[0] == widths[1], "same provider inventories")
    widths = widths[0]
    need(widths[helper_index] == 8, "actual helper408 width")
    current_local = profile(words[0]["report"]["local_profile"])
    parent_local = profile(parents[0]["report"]["local_profile"])
    for w, parent in zip(words, parents):
        need(profile(w["report"]["local_profile"]) == current_local, "same paid profiles")
        need(profile(parent["report"]["local_profile"]) == parent_local, "same parent profiles")
    delta = {r: current_local[r] - parent_local[r] for r in set(current_local) | set(parent_local)}
    need({r: n for r, n in delta.items() if n} == {1: 3, 2: -2}, "literal rank-eight local delta")
    ideal_local = parent_local.copy()
    ideal_local[2] -= 1  # Hypothesis only: no new climbs, remove original rank-two end climb.
    need(ideal_local[2] >= 0, "available rank-two climb")

    order = read("allocation/ORDER.json")
    replicas = 74
    calls = 9 * replicas
    need(len(order) == calls and set(map(tuple, order)) ==
         {(s, r) for s in range(9) for r in range(replicas)}, "complete calls")
    template = read("allocation/vendor/TEMPLATE.json.gz")
    need(template["m"] == 73, "supplier dimension")
    caps = {}
    for child in template["idle_children"]:
        c, rank = child["child"], child["rank"]
        need(c not in caps or caps[c] == rank, "consistent capacity")
        caps[c] = rank
    fill = read("allocation/FILL.json.gz")
    need(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"], "fill schema")
    seen = set()
    masks = defaultdict(int)
    shrinks = Counter()
    for t, h, owner, child, port, offset in fill["rows"]:
        need(0 <= t < calls and 0 <= h < len(helpers), "role bounds")
        need((t, h) not in seen, "duplicate role")
        seen.add((t, h))
        need(0 <= owner < replicas and child in caps and 0 <= port < 112, "owner bounds")
        width = widths[h]
        need(0 <= offset and offset + width <= caps[child], "capacity")
        key = (owner, child, port)
        mask = ((1 << width) - 1) << offset
        need(not masks[key] & mask, "overlapping intervals")
        masks[key] |= mask
        if h == helper_index:
            shrinks[key] += 1
    need(len(seen) == calls * len(helpers), "complete role coverage")
    need(sum(shrinks.values()) == calls, "one helper408 per call")

    current_idle, ideal_idle, affected = Counter(), Counter(), Counter()
    for owner in range(replicas):
        for child, cap in caps.items():
            for port in range(112):
                key = (owner, child, port)
                occupied = masks[key]
                used = occupied.bit_count()
                need(occupied == (1 << used) - 1, "compact original prefix")
                r, k = cap - used, shrinks[key]
                need(0 <= used - k <= cap, "hypothetical reduced capacity")
                if r:
                    current_idle[r] += 1
                if r + k:
                    ideal_idle[r + k] += 1
                if k:
                    affected[(r, k)] += 1
    current = current_idle.copy()
    ideal = ideal_idle.copy()
    for r, n in current_local.items():
        current[r] += calls * n
    for r, n in ideal_local.items():
        ideal[r] += calls * n
    need(current == profile(read("allocation/PROFILE.json")), "complete current profile")
    need(mass(current) == mass(ideal) == 65088 * replicas, "complete rank mass")
    need(current_local[8] == ideal_local[8] == 8, "all eight centre children retained")
    stock = 896 * replicas + 408 + 8 + 73 + 2
    need(stock == 66795, "charged private stock")

    controls = []
    def reject(name, predicate):
        try:
            predicate()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control accepted: " + name)
    unpaid_idle = current.copy()
    unpaid_idle[1] -= 3 * calls
    unpaid_idle[2] += calls
    reject("omit_new_idle_ranks", lambda: need(mass(unpaid_idle) == mass(current), "rank mass"))
    reject("omit_extra_zero_buffer", lambda: need(896 * replicas + 408 + 8 + 72 + 2 == stock, "private stock"))
    reject("omit_one_helper408_role", lambda: need(sum(shrinks.values()) - 1 == calls, "role count"))
    reject("reuse_rank8_local_profile", lambda: need(mass(current_local) + sum(widths) ==
           mass(ideal_local) + sum(widths) - 1, "changed local and width balance"))
    result = {
        "status": "PASS_HYPOTHETICAL_RANK7_BUDGET_NO_SUPPLIER",
        "source_commit": pins["source_commit"], "calls": calls,
        "roles": len(seen), "helper408_index": helper_index,
        "current_local": dict(sorted(current_local.items())),
        "ideal_local": dict(sorted(ideal_local.items())),
        "current_full_profile": dict(sorted(current.items())),
        "ideal_full_profile": dict(sorted(ideal.items())),
        "affected_bins_by_old_idle_and_number_of_shrinks": [
            {"old_idle": r, "helper408_roles": k, "bins": n}
            for (r, k), n in sorted(affected.items())],
        "complete_rank_mass": mass(current), "private_buffers": 73,
        "physical_families": stock, "controls": controls,
        "comparison": "Delta(p)=666*(-3+2^p)+sum_b((r_b+k_b)^p-r_b^p)<0 for 0<p<1",
        "proof": "Each nonnegative integer k has concave increment at most k; sum k=666, so Delta<=666*(2^p-2)<0.",
        "limits": "Optimistic rank ledger only. No rank7 word exists within the separately tested boundary model. Added frame climbs, scalar/native/precision/routing/outer costs are not constructed or waived in an admission claim. Existing windows/family legality are inherited, not independently reverified here."
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
