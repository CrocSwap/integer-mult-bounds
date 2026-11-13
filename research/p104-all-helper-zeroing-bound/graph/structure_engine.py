"""Portable exact/modular row-matroid reconstruction; returns a document."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from helper_funding_common import (
    AUTHOR_MATROID_SHA256,
    AUTHOR_ROWS_SHA256,
    WORD_SHA256,
    digest_bytes,
    digest_json,
    read_json,
    require,
    validate_rebuilt_doc,
)

MODULUS = 1_000_003


def _add(dst, src, q):
    for h, v in src.items():
        z = dst.get(h, Q(0)) + q * v
        if z:
            dst[h] = z
        else:
            dst.pop(h, None)


def _exact_basis(rows):
    basis = {}
    basis_events = []
    relations = []
    for event, row in rows:
        v = row.copy()
        expr = {event: Q(1)}
        while v:
            p = min(v)
            old = basis.get(p)
            if old is None:
                scale = 1 / v[p]
                v = {h: x * scale for h, x in v.items() if x * scale}
                expr = {e: x * scale for e, x in expr.items() if x * scale}
                basis[p] = (v, expr)
                basis_events.append(event)
                break
            factor = v[p]
            _add(v, old[0], -factor)
            _add(expr, old[1], -factor)
        if not v:
            require(expr.get(event) == 1, "nonbasis relation pivot coefficient")
            relations.append({e: q for e, q in sorted(expr.items()) if q})
    return basis, basis_events, relations


def _is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def _modular_certificate(rows):
    require(_is_prime(MODULUS), "modular certificate modulus is not prime")
    basis = {}
    pivot_columns = []
    determinant_product = 1
    for event, row in rows:
        v = {}
        for h, q in row.items():
            den = q.denominator % MODULUS
            require(den != 0, "modulus divides a rational denominator")
            value = q.numerator % MODULUS * pow(den, MODULUS - 2, MODULUS) % MODULUS
            if value:
                v[h] = value
        while v:
            p = min(v)
            old = basis.get(p)
            if old is None:
                pivot = v[p]
                inv = pow(pivot, MODULUS - 2, MODULUS)
                v = {h: x * inv % MODULUS for h, x in v.items() if x * inv % MODULUS}
                basis[p] = v
                pivot_columns.append(p)
                determinant_product = determinant_product * pivot % MODULUS
                break
            factor = v[p]
            for h, x in old.items():
                y = (v.get(h, 0) - factor * x) % MODULUS
                if y:
                    v[h] = y
                else:
                    v.pop(h, None)
        else:
            raise ValueError(f"exact basis event {event} collapsed modulo the checked prime")
    return {
        "prime": MODULUS,
        "rank": len(basis),
        "pivot_columns": pivot_columns,
        "determinant_up_to_permutation_mod_prime": determinant_product,
        "nonzero": determinant_product != 0,
    }


def _uf_groups(items, rows):
    parent = {e: e for e in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    first = {}
    for e, row in rows:
        for h in row:
            if h in first:
                union(e, first[h])
            else:
                first[h] = e
    grouped = defaultdict(list)
    for e in items:
        grouped[find(e)].append(e)
    return [sorted(v) for v in grouped.values()]


def _fundamental_relation_groups(items, relations):
    parent = {e: e for e in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for relation in relations:
        support = list(relation)
        for e in support[1:]:
            ra, rb = find(support[0]), find(e)
            if ra != rb:
                parent[rb] = ra
    grouped = defaultdict(list)
    for e in items:
        grouped[find(e)].append(e)
    return [sorted(v) for v in grouped.values()]


def structure(rebuilt_doc, matroid_path):
    """Return a source-bound structure certificate; writes no output files."""
    records_doc, targets = validate_rebuilt_doc(rebuilt_doc)
    matroid_raw = Path(matroid_path).read_bytes()
    matroid_hash = digest_bytes(matroid_raw)
    require(matroid_hash == AUTHOR_MATROID_SHA256, "author MATROID file hash mismatch")
    author = json.loads(matroid_raw)
    require(author.get("source_sha256") == WORD_SHA256, "author MATROID source mismatch")
    require(author.get("rows_sha256") == AUTHOR_ROWS_SHA256, "author MATROID row binding mismatch")

    rows = [(r["event"], {int(h): Q(v) for h, v in r["row"].items()})
            for r in records_doc]
    by_event = dict(rows)
    paid = {r["event"]: r["rank"] for r in records_doc}
    events = list(by_event)
    basis, basis_events, relations = _exact_basis(rows)
    require(len(basis_events) == 463 and len(relations) == 5, "exact global row rank/nullity")
    nonbasis = set(events) - set(basis_events)
    require(len(nonbasis) == 5, "exact number of nonbasis rows")
    for rel in relations:
        zero = {}
        for e, q in rel.items():
            _add(zero, by_event[e], q)
        require(not zero, "exact fundamental relation failed direct summation")
        require(len([e for e in rel if e in nonbasis]) == 1,
                "fundamental relation does not have one nonbasis pivot")
    require({next(e for e in rel if e in nonbasis) for rel in relations} == nonbasis,
            "fundamental relations do not cover all nonbasis rows")

    modular = _modular_certificate([(e, by_event[e]) for e in basis_events])
    require(modular["rank"] == 463 and len(modular["pivot_columns"]) == 463 and modular["nonzero"],
            "nonzero modular maximal-minor certificate")

    support_components = _uf_groups(events, rows)
    support_components.sort(key=lambda c: (-len(c), min(c)))
    giant = set(support_components[0])
    giant_columns = set().union(*(set(by_event[e]) for e in giant))
    require(len(support_components) == 94 and len(giant) == 347 and len(giant_columns) == 669,
            "helper-support component census")
    require(nonbasis <= giant and len(set(basis_events) & giant) == 342,
            "global basis partition across helper-support components")
    require(len(events) - len(giant) == 121, "non-giant support row count")
    require(all(e in set(basis_events) for e in events if e not in giant),
            "non-giant row is dependent")

    matroid_components = _fundamental_relation_groups(events, relations)
    dependent_blocks = [c for c in matroid_components if len(c) > 1]
    dependent_blocks.sort(key=lambda c: (len(c), min(c)))
    dependent_set = set().union(*(set(c) for c in dependent_blocks))
    block_summaries = []
    for block_id, block in enumerate(dependent_blocks):
        rank = sum(e in set(basis_events) for e in block)
        block_summaries.append({"id": block_id, "events": block, "rows": len(block), "rank_Q": rank})
    require(sorted((len(c) for c in dependent_blocks), reverse=True) == [11, 5, 5, 5],
            "fundamental relation component sizes")
    require(sorted(x["rank_Q"] for x in block_summaries) == [4, 4, 4, 9],
            "dependent block ranks")
    coloops = sorted(set(events) - dependent_set)
    require(len(coloops) == 442 and len(giant - dependent_set) == 321,
            "coloop count")
    require(dependent_set <= giant, "dependent row escaped support giant")

    overlaps = []
    all_columns = {e: set(row) for e, row in rows}
    for block in dependent_blocks:
        block_set = set(block)
        block_cols = set().union(*(all_columns[e] for e in block_set))
        external_cols = set().union(*(all_columns[e] for e in events if e not in block_set))
        overlaps.append({"rows": len(block_set), "columns": len(block_cols),
                         "columns_shared_outside_component": len(block_cols & external_cols)})

    # Pointwise rank domination is rechecked from the exact source rows.
    min_ratio = None
    for event, row in rows:
        require(row and 1 <= paid[event] <= 9, "paid rank or support invalid")
        minimum_target = min(targets[h] for h in row)
        require(paid[event] <= minimum_target, "support helper target underprices a MOVE row")
        ratio = Q(minimum_target, paid[event])
        min_ratio = ratio if min_ratio is None else min(min_ratio, ratio)
    require(min_ratio == 1, "unexpected pointwise rank ratio")

    require(author.get("giant_rows") == len(giant) and author.get("rank_Q") == 342 and
            author.get("nullity") == 5, "author MATROID summary disagrees after fresh reconstruction")

    doc = {
        "schema": "helper-funding-structure-v1",
        "source_sha256": WORD_SHA256,
        "rows_sha256": AUTHOR_ROWS_SHA256,
        "records_sha256": rebuilt_doc["records_sha256"],
        "target_ranks_sha256": rebuilt_doc["target_ranks_sha256"],
        "author_matroid_sha256": matroid_hash,
        "global_rows": len(events),
        "global_rank_Q": len(basis_events),
        "basis_events": basis_events,
        "exact_fundamental_relations": [
            {"nonbasis_event": next(e for e in rel if e in nonbasis),
             "coefficients": {str(e): str(q) for e, q in rel.items()}}
            for rel in relations
        ],
        "modular_minor": modular,
        "support_component_count": len(support_components),
        "support_component_row_sizes_desc": sorted((len(c) for c in support_components), reverse=True),
        "giant_rows": len(giant),
        "giant_columns": len(giant_columns),
        "giant_rank_Q": len(set(basis_events) & giant),
        "giant_nullity": len(giant) - len(set(basis_events) & giant),
        "non_giant_rows": len(events) - len(giant),
        "dependent_blocks": block_summaries,
        "coloop_events": coloops,
        "giant_coloops": len(giant - dependent_set),
        "dependent_block_support_overlaps": overlaps,
        "minimum_pointwise_target_to_paid_rank_ratio": str(min_ratio),
    }
    doc["structure_sha256"] = digest_json(doc)
    return doc
