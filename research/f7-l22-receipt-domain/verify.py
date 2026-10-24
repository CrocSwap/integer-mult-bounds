#!/usr/bin/env python3
"""Source-bound domain/receipt adapter; never imports or executes census engines.

Prepared with OpenAI Astra assistance. Predecessors: Nick Petalas (#4221,
#3708), the #3818 union census, and the attributed PR943 word-model lineage.
Apache-2.0. Runtime evidence is emitted only when this command is executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DEEP = "research/f7-l22-deep-shard-census/"
DOMAIN = "research/f7-l22-split-domain/"
PRIOR = "research/f7-l22-union-census/"
ENGINE = PRIOR + "engine/union_census.c"
INPUTS = (
    DEEP + "verify.py",
    DEEP + "README.md",
    DEEP + "RESULT.json",
    DEEP + "SOURCES.json",
    DEEP + "deep_census.py",
    DOMAIN + "verify.py",
    DOMAIN + "README.md",
    DOMAIN + "RESULT.json",
    PRIOR + "RESULT.json",
    ENGINE,
)


class Rejected(ValueError):
    """A failed acceptance obligation, also active under python -O."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def expect_rejected(label, action, reason):
    try:
        action()
    except Rejected as error:
        require(reason in str(error), f"{label}: wrong rejection: {error}")
        return label
    raise Rejected(f"control survived: {label}")


def controls(prior, deep, domain, trusted_status, engine_hash, keys):
    """Mutate actual loaded receipts, not invented one-row success fixtures."""
    rejected = []

    def exercise(label, change, reason):
        p, d, requested = deepcopy(prior), deepcopy(deep), set(domain)
        change(p, d, requested)
        rejected.append(
            expect_rejected(
                label,
                lambda: bind_receipts(
                    p, d, requested, trusted_status, engine_hash, keys
                ),
                reason,
            )
        )

    # Positive acceptance is mandatory; an always-rejecting adapter fails here.
    bind_receipts(prior, deep, domain, trusted_status, engine_hash, keys)
    p, d = deepcopy(prior), deepcopy(deep)
    p["probes"].reverse()
    d["splits"].reverse()
    bind_receipts(p, d, domain, trusted_status, engine_hash, keys)

    for split in sorted(domain):
        target = (
            "deep"
            if any(tuple(r["split"]) == split for r in deep["splits"])
            else "prior"
        )

        def omit(p, d, requested, split=split, target=target):
            rows = d["splits"] if target == "deep" else p["probes"]
            rows[:] = [r for r in rows if tuple(r["split"]) != split]

        exercise(f"omit-{split}", omit, "coverage")

    exercise(
        "duplicate-deep",
        lambda p, d, q: d["splits"].append(deepcopy(d["splits"][0])),
        "duplicate split",
    )
    exercise(
        "duplicate-prior",
        lambda p, d, q: p["probes"].append(deepcopy(p["probes"][0])),
        "duplicate split",
    )
    exercise(
        "deep-incomplete",
        lambda p, d, q: d["splits"][0].update(complete=False),
        "deep completion",
    )
    exercise(
        "truthy-completion",
        lambda p, d, q: d["splits"][0].update(complete=1),
        "deep completion",
    )
    exercise(
        "prior-false-incomplete",
        lambda p, d, q: p["probes"][0].update(complete=False),
        "recorded completion",
    )

    def false_complete(p, d, requested):
        row = next(r for r in p["probes"] if r["complete"] is False)
        row.update(complete=True, finite_split_exclusion=True, capped_shards=[])

    exercise("prior-false-complete", false_complete, "recorded completion")
    exercise(
        "deep-positive-hit",
        lambda p, d, q: d["splits"][0].update(hits=1, hit_words=["01021323"]),
        "hits",
    )
    exercise(
        "prior-positive-hit", lambda p, d, q: p["probes"][0].update(hits=1), "hits"
    )
    exercise(
        "hidden-hit-word",
        lambda p, d, q: d["splits"][0].update(hit_words=["01021323"]),
        "hits",
    )
    exercise(
        "unexpected-split",
        lambda p, d, q: d["splits"][0].update(split=[9, 8]),
        "unexpected split",
    )
    exercise(
        "narrowed-domain-only", lambda p, d, q: q.discard((11, 6)), "derived domain"
    )

    def narrow_both(p, d, requested):
        requested.difference_update({(11, 6), (10, 7)})
        d["splits"][:] = [r for r in d["splits"] if sum(r["split"]) != 17]

    exercise("narrowed-domain-and-receipts", narrow_both, "derived domain")
    exercise(
        "missing-shard",
        lambda p, d, q: d["splits"][0]["per_shard_nodes"].pop(keys[0]),
        "shard keys",
    )
    exercise(
        "wrong-total",
        lambda p, d, q: d["splits"][0].update(nodes=d["splits"][0]["nodes"] + 1),
        "node total",
    )
    exercise(
        "negative-node",
        lambda p, d, q: d["splits"][0]["per_shard_nodes"].update({keys[0]: -1}),
        "node count",
    )
    exercise("wrong-engine", lambda p, d, q: d.update(engine_sha256="0" * 64), "engine")
    rejected.append(
        expect_rejected("omitted-cover", lambda: check_cover(keys[:-1]), "partition")
    )
    rejected.append(
        expect_rejected(
            "overlapping-cover", lambda: check_cover(keys + ["0123456"]), "partition"
        )
    )
    rejected.append(
        expect_rejected(
            "duplicate-json-key",
            lambda: load_json('{"split": [11,6], "split": [10,7]}'),
            "duplicate JSON key",
        )
    )
    return rejected


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(text):
    return json.loads(text, object_pairs_hook=unique_object)


def authenticate_inputs():
    sources = load_json((PACKAGE / "SOURCES.json").read_bytes())
    live = [r for r in sources["files"] if r["usage"] == "input"]
    require(
        len(live) == len(INPUTS) and {r["path"] for r in live} == set(INPUTS),
        "live input inventory differs from the adapter contract",
    )
    payloads = {}
    for row in live:
        payload = (ROOT / row["path"]).read_bytes()
        require(
            hashlib.sha256(payload).hexdigest() == row["sha256"],
            "source SHA256 mismatch: " + row["path"],
        )
        header = f"blob {len(payload)}\0".encode("ascii")
        require(
            hashlib.sha1(header + payload).hexdigest() == row["git_blob"],
            "source Git blob mismatch: " + row["path"],
        )
        payloads[row["path"]] = payload
    return payloads


def arithmetic(s, t):
    """Four necessary conditions at n=7, L=22; no set-level imports."""
    budget = s * (s - 1) // 2 + t * (t - 1) // 2 - 63
    need = max(0, (s * t - 64 + 1) // 2)
    upper = budget + budget * budget // 4 if budget >= 0 else budget
    return {
        "split": [s, t],
        "points": s + t,
        "revisits_forced": 22 - s - t,
        "even_budget": budget,
        "identity_need": need,
        "identity_max_upper": upper,
        "odd_pairs": s * t,
    }, (s <= 11 and t <= 11, s * t >= 64, budget >= 0, upper >= need)


def derive_domain():
    # A prefix set has at most L distinct positions. The deliberately wider
    # range exercises the time condition rather than building it into a table.
    rows = []
    for s in range(1, 23):
        for t in range(1, s + 1):
            row, conditions = arithmetic(s, t)
            if all(conditions):
                rows.append(row)
    return sorted(rows, key=lambda r: (-r["points"], -r["split"][0]))


def check_domain(record):
    rows = derive_domain()
    require(
        rows == record["split_domains"]["22"], "pre-import arithmetic rows disagree"
    )
    require(
        [r["split"] for r in rows] == record["length_22_self_contained"],
        "pre-import representatives disagree",
    )
    require(len(rows) == 11, "expected eleven independently derived representatives")
    domain = {tuple(r["split"]) for r in rows}
    require({(11, 6), (10, 7)} <= domain, "17-point import leaked into derivation")
    simple = [r["split"] for r in rows if r["points"] == 22]
    require(
        simple == [[11, 11]] == record["length_22_simple_cycle_admissible"],
        "self-avoidance classification",
    )
    revisits = {str(tuple(r["split"])): r["revisits_forced"] for r in rows}
    require(revisits == record["length_22_revisits_forced"], "revisit classification")
    row, conditions = arithmetic(9, 8)
    require(
        conditions == (True, True, True, False)
        and row["even_budget"] == 1
        and row["identity_need"] == 4,
        "(9,8) must fail only the identity",
    )
    require(not arithmetic(12, 6)[1][0], "time condition is not active")
    require(not arithmetic(8, 8)[1][2], "even-budget condition is not active")
    require(not arithmetic(11, 5)[1][1], "odd-budget condition is not active")
    require(
        arithmetic(11, 11)[0]["identity_need"] == 29,
        "odd excess 57 must round up, not down",
    )
    # Independently optimize over integer a+b<=B, rather than repeating B^2//4.
    for budget in range(48):
        best = max(a * b for a in range(budget + 1) for b in range(budget - a + 1))
        require(best == budget * budget // 4, "integer identity maximization")
    return rows, domain


def growth_words(depth):
    words = [""]
    for _ in range(depth):
        words = [
            word + str(label)
            for word in words
            for label in range(min(7, max(map(int, word), default=-1) + 2))
        ]
    return words


def make_cover():
    extensions = [w for w in growth_words(8) if w.startswith("012345")]
    base = growth_words(6)
    require(len(base) == 203 and len(extensions) == 49, "cover construction")
    return [
        key
        for prefix in base
        for key in (extensions if prefix == "012345" else [prefix])
    ]


def check_cover(keys):
    require(len(keys) == len(set(keys)), "duplicate cover prefix")
    require(all(1 <= len(key) <= 8 for key in keys), "cover partition depths")
    words = growth_words(8)
    require(
        all(any(word.startswith(key) for word in words) for key in keys),
        "cover partition contains invalid prefix",
    )
    for word in words:
        require(
            sum(word.startswith(key) for key in keys) == 1,
            "cover partition missing or overlapping at " + word,
        )


def index_splits(rows):
    require(type(rows) is list, "split rows must be a list")
    indexed = {}
    for row in rows:
        split = row["split"]
        require(
            type(split) is list
            and len(split) == 2
            and all(type(v) is int for v in split),
            "invalid split",
        )
        key = tuple(split)
        require(key not in indexed, f"duplicate split: {key}")
        indexed[key] = row
    return indexed


def nonnegative_integer(value):
    return type(value) is int and value >= 0


def bind_receipts(prior, deep, requested_domain, trusted_status, engine_hash, keys):
    # Re-derive at the acceptance boundary: even a domain+receipt co-mutation
    # cannot turn exact coverage into coverage of a caller-selected subset.
    domain = {tuple(r["split"]) for r in derive_domain()}
    require(requested_domain == domain, "requested domain differs from derived domain")
    p = index_splits(prior["probes"])
    d = index_splits(deep["splits"])
    require(set(p) <= domain and set(d) <= domain, "unexpected split")
    require(set(p) == set(trusted_status), "predecessor coverage changed")
    require(
        prior["shard_depth"] == 4 and prior["shard_prefixes"] == growth_words(4),
        "predecessor shard coverage",
    )
    complete = set()
    for split, row in p.items():
        require(
            type(row["complete"]) is bool and row["complete"] is trusted_status[split],
            f"{split}: recorded completion changed",
        )
        require(
            row["finite_split_exclusion"] is row["complete"],
            f"{split}: inconsistent exclusion flag",
        )
        require(type(row["hits"]) is int and row["hits"] == 0, f"{split}: prior hits")
        require(nonnegative_integer(row["sharded_nodes"]), "prior node count")
        if "shards_recorded" in row:
            require(row["shards_recorded"] == 15, "prior shard coverage")
        if row["complete"]:
            require(
                not row.get("capped_shards", []), "complete prior has capped shards"
            )
            require(
                nonnegative_integer(row["unsharded_nodes"]),
                "prior unsharded node count",
            )
            complete.add(split)
        else:
            capped = row["capped_shards"]
            require(
                capped
                and len(capped) == len(set(capped))
                and set(capped) <= set(prior["shard_prefixes"]),
                "prior capped coverage",
            )
    require(
        deep["engine"] == ENGINE and deep["engine_sha256"] == engine_hash,
        "receipt engine identity",
    )
    require(
        deep["base_depth"] == 6
        and deep["cover_size"] == 251
        and deep["expanded"] == {"012345": 8},
        "deep cover metadata",
    )
    for split, row in d.items():
        require(row["complete"] is True, f"{split}: deep completion")
        require(
            type(row["hits"]) is int and row["hits"] == 0 and row["hit_words"] == [],
            f"{split}: deep hits",
        )
        require(
            row["shards"] == 251 and list(row["per_shard_nodes"]) == keys,
            f"{split}: shard keys differ",
        )
        counts = row["per_shard_nodes"].values()
        require(
            all(nonnegative_integer(n) for n in counts), f"{split}: invalid node count"
        )
        require(
            nonnegative_integer(row["nodes"]) and sum(counts) == row["nodes"],
            f"{split}: node total",
        )
    require(
        set(d) == domain - complete,
        "deep coverage must equal derived domain minus prior complete",
    )
    require(
        not (set(d) & complete) and complete | set(d) == domain,
        "completed receipt coverage is not an exact partition",
    )
    return {
        "prior_complete": sorted(complete),
        "deep_complete": sorted(d),
        "recorded_deep_nodes": sum(row["nodes"] for row in d.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        action="store_true",
        help="print deterministic arithmetic and control details",
    )
    args = parser.parse_args()
    payloads = authenticate_inputs()
    prior = load_json(payloads[PRIOR + "RESULT.json"])
    deep = load_json(payloads[DEEP + "RESULT.json"])
    record = load_json(payloads[DOMAIN + "RESULT.json"])
    old_sources = load_json(payloads[DEEP + "SOURCES.json"])
    engine_pins = [r for r in old_sources["files"] if r["path"] == ENGINE]
    engine_hash = hashlib.sha256(payloads[ENGINE]).hexdigest()
    require(
        len(engine_pins) == 1 and engine_pins[0]["sha256"] == engine_hash,
        "predecessor engine source guarantee",
    )
    rows, domain = check_domain(record)
    keys = make_cover()
    check_cover(keys)
    # These completion states come only from the authenticated original bytes;
    # controls cannot make a capped run complete by changing both of its flags.
    trusted_status = {
        key: row["complete"] for key, row in index_splits(prior["probes"]).items()
    }
    summary = bind_receipts(prior, deep, domain, trusted_status, engine_hash, keys)
    rejected = controls(prior, deep, domain, trusted_status, engine_hash, keys)
    if args.emit:
        print(
            json.dumps(
                {
                    "derived_rows": rows,
                    "binding": summary,
                    "rejected_controls": rejected,
                    "evidence_kind": "authenticated recorded counts; no census replay",
                },
                indent=2,
                sort_keys=True,
            )
        )
    print(
        f"PASS_F7_L22_RECEIPT_DOMAIN domain=11 prior=4 deep=7 controls={len(rejected)} no_census_replay"
    )


if __name__ == "__main__":
    try:
        main()
    except (Rejected, KeyError, TypeError, ValueError, OSError) as error:
        print(f"FAIL_F7_L22_RECEIPT_DOMAIN: {error}", file=sys.stderr)
        sys.exit(1)
