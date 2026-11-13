"""Portable exact subset funding engine; no file output and no greedy basis search."""
from __future__ import annotations

from fractions import Fraction as Q
from pathlib import Path
import json

from helper_funding_common import (
    AUTHOR_MATROID_SHA256,
    AUTHOR_POWER_SHA256,
    AUTHOR_ROWS_SHA256,
    EXPECTED_STRUCTURE_DOC_SHA256,
    WORD_SHA256,
    digest_bytes,
    read_json,
    require,
    validate_rebuilt_doc,
    validate_structure_doc,
)


def _add(dst, src, q):
    for k, v in src.items():
        z = dst.get(k, Q(0)) + q * v
        if z:
            dst[k] = z
        else:
            dst.pop(k, None)


def _rank_q(rows):
    basis = {}
    for row in rows:
        v = {k: Q(x) for k, x in row.items() if x}
        while v:
            p = min(v)
            old = basis.get(p)
            if old is None:
                scale = 1 / v[p]
                basis[p] = {k: x * scale for k, x in v.items() if x * scale}
                break
            _add(v, old, -v[p])
    return len(basis)


def _prefix_minimum_basis_sum(rows, targets):
    columns = set().union(*(set(row) for row in rows))
    require(columns and columns <= set(targets), "subset target weights missing")
    rank = _rank_q(rows)
    prefix = []
    for k in range(1, 9):
        eligible = {h for h in columns if targets[h] <= k}
        restricted = [{h: value for h, value in row.items() if h in eligible} for row in rows]
        prefix.append(_rank_q(restricted))
    minimum_sum = 9 * rank - sum(prefix)
    require(minimum_sum >= rank, "prefix-rank basis price is invalid")
    return rank, minimum_sum, prefix


def _controls():
    overlap_rows = [{0: Q(1), 1: Q(1)}, {0: Q(1), 1: Q(-1)}]
    overlap_weights = {0: 1, 1: 2}
    local_price_sum = sum(_prefix_minimum_basis_sum([r], overlap_weights)[1]
                          for r in overlap_rows)
    global_price = _prefix_minimum_basis_sum(overlap_rows, overlap_weights)[1]
    require(set(overlap_rows[0]) & set(overlap_rows[1]), "overlap control lacks shared columns")
    require(_rank_q(overlap_rows) == 2 and local_price_sum == 2 and global_price == 3 and
            global_price >= local_price_sum, "overlapping-column Laplace control failed")

    false_direct_sum_rows = [{0: Q(1), 1: Q(1)}, {0: Q(2), 1: Q(2)}]
    false_local_ranks = sum(_rank_q([r]) for r in false_direct_sum_rows)
    false_global_rank = _rank_q(false_direct_sum_rows)
    require(false_local_ranks == 2 and false_global_rank == 1 and
            false_global_rank != false_local_ranks, "false direct-sum control failed")

    underpriced_rows = [{0: Q(1), 1: Q(1)}, {0: Q(1), 1: Q(-1)}]
    underpriced_weights = {0: 1, 1: 1}
    underpriced_basis = _prefix_minimum_basis_sum(underpriced_rows, underpriced_weights)[1]
    underpriced_paid = 4
    underpriced_margin = 6 * underpriced_basis - 11 * underpriced_paid
    require(underpriced_basis == 2 and underpriced_margin < 0,
            "underpriced-target control failed to reject the mutant")
    require(9 * 6**4 < 11**4, "quarter-power integer envelope failed")
    return {
        "overlapping_column_support": {
            "global_basis_sum": global_price,
            "sum_of_local_minima": local_price_sum,
            "laplace_lower_bound_passed": True,
        },
        "false_direct_sum_rejected": {
            "local_rank_sum": false_local_ranks,
            "actual_global_rank": false_global_rank,
            "rejected": True,
        },
        "underpriced_target_rejected": {
            "target_basis_sum": underpriced_basis,
            "paid_rank_sum": underpriced_paid,
            "margin_6B_minus_11P": underpriced_margin,
            "rejected": True,
        },
        "strict_power_envelope": "9*6^4 < 11^4",
    }


def _validate_author_power(path):
    raw = Path(path).read_bytes()
    power_hash = digest_bytes(raw)
    require(power_hash == AUTHOR_POWER_SHA256, "author POWER file hash mismatch")
    author = json.loads(raw)
    require(author.get("source_sha256") == WORD_SHA256 and
            author.get("rows_sha256") == AUTHOR_ROWS_SHA256 and
            author.get("matroid_components_sha256") == AUTHOR_MATROID_SHA256,
            "author POWER source binding mismatch")
    require(author.get("power_interval") == ["0", "1/4"] and
            author.get("coefficient_rule") == "6*sum(basis target ranks)>=11*sum(paid ranks)",
            "author POWER certificate scope mismatch")
    return power_hash


def subsets(rebuilt_doc, structure_doc, author_power_path=None):
    """Return subset funding checks in memory; writes no output files."""
    records_doc, target_ints = validate_rebuilt_doc(rebuilt_doc)
    blocks = validate_structure_doc(structure_doc, rebuilt_doc)
    power_hash = _validate_author_power(author_power_path) if author_power_path is not None else None
    rows = {r["event"]: {int(h): Q(v) for h, v in r["row"].items()} for r in records_doc}
    paid = {r["event"]: r["rank"] for r in records_doc}
    summaries = []
    details = []
    independent_total = dependent_total = subset_total = 0
    ratios = []
    for block in blocks:
        ordered = sorted(block["events"])
        block_rank = _rank_q([rows[e] for e in ordered])
        indep_count = dep_count = 0
        for mask in range(1, 1 << len(ordered)):
            selected = [e for j, e in enumerate(ordered) if mask & (1 << j)]
            selected_rows = [rows[e] for e in selected]
            rank = _rank_q(selected_rows)
            subset_total += 1
            if rank == len(selected):
                independent_total += 1
                indep_count += 1
                continue
            dependent_total += 1
            dep_count += 1
            rank2, basis_sum, prefix = _prefix_minimum_basis_sum(selected_rows, target_ints)
            require(rank2 == rank, "dependent subset rank mismatch")
            paid_sum = sum(paid[e] for e in selected)
            margin = 6 * basis_sum - 11 * paid_sum
            require(margin >= 0, f"dependent subset is underfunded: {selected}")
            ratios.append((Q(basis_sum, paid_sum), block["id"], selected, basis_sum, paid_sum))
            details.append({
                "block_id": block["id"],
                "mask": mask,
                "events": selected,
                "rank_Q": rank,
                "paid_rank_sum": paid_sum,
                "prefix_ranks_target_le_1_to_8": prefix,
                "minimum_column_basis_target_rank_sum": basis_sum,
                "margin_6B_minus_11P": margin,
            })
        summaries.append({
            "block_id": block["id"],
            "events": ordered,
            "rows": len(ordered),
            "rank_Q": block_rank,
            "nonempty_subsets": (1 << len(ordered)) - 1,
            "independent_subsets": indep_count,
            "dependent_subsets": dep_count,
        })

    require(subset_total == 2140 and independent_total == 2109 and dependent_total == 31,
            "local subset count mismatch")
    minimum_ratio = min(x[0] for x in ratios)
    require(minimum_ratio == Q(11, 6), "dependent minimum linear-price ratio mismatch")
    witness = next(x for x in ratios if x[0] == minimum_ratio)
    require(witness[3:] == (44, 24), "minimum ratio witness mismatch")
    require(9 * 6**4 < 11**4, "strict envelope arithmetic failed")
    return {
        "schema": "helper-funding-subsets-v1",
        "source_sha256": WORD_SHA256,
        "records_sha256": rebuilt_doc["records_sha256"],
        "target_ranks_sha256": rebuilt_doc["target_ranks_sha256"],
        "structure_sha256": structure_doc["structure_sha256"],
        "author_power_sha256": power_hash,
        "local_nonempty_subsets": subset_total,
        "independent_subsets": independent_total,
        "dependent_subsets": dependent_total,
        "all_dependent_subsets_pass_6B_ge_11P": True,
        "minimum_basis_to_paid_linear_ratio": "11/6",
        "minimum_ratio_witness": {
            "block_id": witness[1],
            "events": witness[2],
            "basis_target_rank_sum": witness[3],
            "paid_rank_sum": witness[4],
        },
        "minimum_integer_margin": min(x["margin_6B_minus_11P"] for x in details),
        "strict_integer_power_envelope": "9*6^4 < 11^4",
        "blocks": summaries,
        "dependent_subset_details": details,
        "controls": _controls(),
        "scope": "Exact unchanged-word main-free helper MOVE funding under the retained original-coordinate interface; preparation and cleanup granted free.",
    }
