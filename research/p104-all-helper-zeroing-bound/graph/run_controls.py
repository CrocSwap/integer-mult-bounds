"""Read-only portable smoke and adversarial mutation controls."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from helper_funding_common import ValidationError, digest_bytes, require
from rebuild_engine import _rebuild_bytes, rebuild
from structure_engine import structure
from subset_engine import subsets


def _rejects(call, expected):
    try:
        call()
    except ValidationError as exc:
        return str(exc) == expected
    return False


def run():
    here = Path(__file__).resolve().parent
    inputs = here / "inputs"
    word_path = here.parent / "inputs/WORD.json.gz"
    rows_path = inputs / "author-ROWS.json"
    matroid_path = inputs / "author-MATROID-COMPONENTS.json"
    power_path = inputs / "author-POWER-RESULT.json"

    rebuilt = rebuild(word_path, rows_path)
    shaped = structure(rebuilt, matroid_path)
    prices = subsets(rebuilt, shaped, power_path)
    prices_without_author_power = subsets(rebuilt, shaped)
    optional_power_absent_supported = (
        prices_without_author_power["dependent_subsets"] == prices["dependent_subsets"] and
        prices_without_author_power["minimum_basis_to_paid_linear_ratio"] ==
        prices["minimum_basis_to_paid_linear_ratio"] and
        prices_without_author_power["author_power_sha256"] is None
    )
    require(optional_power_absent_supported, "optional author POWER input was not optional")

    # Mutate actual gzip bytes in memory; no file or output is written.
    mutated_word = bytearray(word_path.read_bytes())
    mutated_word[len(mutated_word) // 2] ^= 1
    author_rows_raw = rows_path.read_bytes()
    author_rows_doc = json.loads(author_rows_raw)
    source_mutation_rejected = _rejects(
        lambda: _rebuild_bytes(bytes(mutated_word), author_rows_doc, digest_bytes(author_rows_raw)),
        "native source hash mismatch",
    )

    missing = deepcopy(rebuilt)
    missing["records"].pop()
    missing_rows_rejected = _rejects(
        lambda: structure(missing, matroid_path), "missing or extra MOVE rows")

    duplicate = deepcopy(rebuilt)
    duplicate["records"][-1] = deepcopy(duplicate["records"][0])
    duplicate_rows_rejected = _rejects(
        lambda: structure(duplicate, matroid_path), "duplicate MOVE row event ID")

    forged_weight = deepcopy(rebuilt)
    one_helper = next(h for h, rank in forged_weight["helper_target_ranks"].items() if rank < 9)
    forged_weight["helper_target_ranks"][one_helper] += 1
    forged_weights_rejected = _rejects(
        lambda: structure(forged_weight, matroid_path), "helper target weights are forged or incomplete")

    false_components = deepcopy(shaped)
    false_components["dependent_blocks"][0]["events"].pop()
    false_component_rejected = _rejects(
        lambda: subsets(rebuilt, false_components, power_path),
        "structure component/certificate digest mismatch",
    )

    wrong_power_input_rejected = _rejects(
        lambda: subsets(rebuilt, shaped, matroid_path), "author POWER file hash mismatch")

    results = {
        "status": "PASS_PORTABLE_READ_ONLY_REPLAY_AND_MUTATION_CONTROLS",
        "valid_run": {
            "source_sha256": rebuilt["source_sha256"],
            "rows": len(rebuilt["records"]),
            "global_rank_Q": shaped["global_rank_Q"],
            "dependent_block_sizes": sorted((len(b["events"]) for b in shaped["dependent_blocks"]), reverse=True),
            "subsets": prices["local_nonempty_subsets"],
            "independent_subsets": prices["independent_subsets"],
            "dependent_subsets": prices["dependent_subsets"],
            "minimum_ratio": prices["minimum_basis_to_paid_linear_ratio"],
        },
        "mutation_controls": {
            "mutated_native_word_bytes_rejected": source_mutation_rejected,
            "missing_row_rejected_by_structure": missing_rows_rejected,
            "duplicate_event_row_rejected_by_structure": duplicate_rows_rejected,
            "forged_helper_target_weight_rejected_by_structure": forged_weights_rejected,
            "forged_component_partition_rejected_by_subsets": false_component_rejected,
            "wrong_optional_author_power_file_rejected": wrong_power_input_rejected,
        },
        "optional_author_power_path_absent_supported": optional_power_absent_supported,
        "writes_files": False,
    }
    require(all(results["mutation_controls"].values()), "one or more mutation controls did not reject")
    return results


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
