"""Write TASK.json (draw_card extraction + session record) and SOURCES.json (exact pins).

The original_card is extracted programmatically from the pinned task catalogue
(docs/research/agent-task-catalog.json) so it is byte-equal to the catalogue card
object; the chooser's flattened "method" shape is never hand-copied.

usage: python -B research/hpe-post-wrapper-lemma/make_meta.py   (Python 3.12)"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BASE = "d8e0f83f00191df62174b641e9fff055c357f641"
CATALOG = "docs/research/agent-task-catalog.json"
TASK_ID = "formal-interface-lemma"


def git_bytes(expr):
    return subprocess.run(["git", "show", expr], cwd=ROOT, capture_output=True,
                          check=True).stdout


def git_blob(expr):
    out = subprocess.run(["git", "rev-parse", expr], cwd=ROOT, capture_output=True,
                         check=True, text=True).stdout.strip()
    return out


def draw_card(task_id):
    """The full catalogue card object for task_id, verbatim."""
    catalog = json.loads(git_bytes(BASE + ":" + CATALOG))
    cards = [t for track in catalog["tracks"] for t in track["tasks"] if t["id"] == task_id]
    assert len(cards) == 1, "draw_card: expected exactly one card for " + task_id
    return cards[0]


def pin(path):
    data = git_bytes(BASE + ":" + path)
    return {"path": path, "git_blob": git_blob(BASE + ":" + path),
            "sha256": hashlib.sha256(data).hexdigest()}


def main():
    card = draw_card(TASK_ID)
    sources = {
        "schema_version": 1,
        "base_commit": BASE,
        "files": [
            dict(pin("research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"), usage="input"),
            dict(pin("research/hyperplane-end-lean/HyperplaneEnd/Labels.lean"), usage="provenance"),
            dict(pin("research/hyperplane-end-lean/PROOF.md"), usage="provenance"),
            dict(pin(CATALOG), usage="provenance"),
            dict(pin("certificates/selected-result.json"), usage="provenance"),
        ],
    }
    task = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "priority_revision": 6,
        "base_commit": BASE,
        "original_card": card,
        "scope_status": "unchanged",
        "actual_scope": card["question"],
        "scope_change_reason": "",
        "bottleneck_link": "A missing interface proof can reduce the conditional gap even if it does not change kappa: hpe_word_exact's wrapper side carried an unformalized post-wrapper obligation; this closes it for the three certified pairs with exact arithmetic and states the universal lemma.",
        "budget_minutes": 60,
        "stop_rule": "Stop after one formal lemma with exact instance binding and its failure controls; no supplier, kappa or frontier claim, no second lemma, no census.",
        "outcome": "completed",
        "evidence": ("Written post-wrapper uniqueness lemma (phase-sharp) with full hypotheses; exact stdlib instance binding on the three certified Lean pairs pair1-3 of HyperplaneEnd/Exact.lean: positive identity exact for the shipped post wrappers, C8 width guard rejected, per pair 9 mutants classified (3 phase mutants hold at exactly their lambda form i^{-t} and no other; 5 wrong wrappers break all four lambda forms each with an exact (row, column) witness; 1 record-dead quadratic bit is inert and correctly accepted), port controls reproduce the kernel literals lits1-3, --self-test rejects a self-consistent corrupted wrapper literal. Author-checked; no Lean kernel proof of the lemma and no independent human review."),
        "author": "Aaron Wang, with help from opencode",
        "ai_assistance": "Substantial AI assistance (no model named) in the derivation, implementation, exact checks and writing; no independent human review claimed.",
        "open_questions": [
            {"question": "Can factor_iff_post and its lambda-sharp form be kernel-checked in HyperplaneEnd/Labels.lean beside factor_iff_pre?",
             "why_it_matters": "It would discharge the post-side conjunct of hrec with the same trust level as the pre side.",
             "first_step": "Add the theorem mirroring factor_iff_pre (rewrite with wrapped_block and (N), invertibility of C7 tensor id) and extend PrintAxioms coverage.",
             "blocked_by": "No Lean toolchain in this session's environment; frozen predecessor packages are not edited in place."},
            {"question": "Does the post-side binding hold for cold (E = 0) helpers and multi-gate tails?",
             "why_it_matters": "The certified pairs cover three non-cold pairs only; cold ends and multi-gate tails keep (N) and the wrapper hypotheses as assumptions.",
             "first_step": "Bind one cold pair exactly with this package's semantics, or extend research/hpe-wrapper-event-binding to cold recipe pairs on an emitted run.",
             "blocked_by": "No cold (N) literal pairs exist in Lean (only the local 511-hyperplane tool check); emitted HPE runs are not vendored in this repository."},
            {"question": "Should record-level wrapper comparison be relaxed to operator equality on dead quadratic bits?",
             "why_it_matters": "The qv semantics reads Q_i only through bits above i, so byte comparison can reject a correct wrapper record.",
             "first_step": "Document the degeneracy in scripts/verify_hpe_lean_binding.py and add a dead-bit mutation control there.",
             "blocked_by": "Shared-tool changes need maintainer review."},
        ],
        "selection": {
            "original_nonce": "80692bf8777fc3a7d12b201233cd6ae2",
            "original_track": "independent-verification",
            "suggested_cards": ["formal-interface-lemma", "independent-moment"],
            "drawn_card": TASK_ID,
            "drawn_method": "Formalize a missing boundary lemma identified by the selected review.",
            "chooser_scope_key": "636f26dec98e26b296e8",
        },
        "draw": {
            "seed": "80692bf8777fc3a7d12b201233cd6ae2",
            "cards": ["formal-interface-lemma", "independent-moment"],
            "chosen": "formal-interface-lemma (first suggestion; construction reading of its drawn method)",
            "re_draw": None,
            "saturation_handling": ("Census/coverage readings of the card are saturated: find_overlap OR-mode ('post wrapper' 'wrapper uniqueness' 'factor_iff' 'hyperplane end' 'formal interface' 'interface lemma') returned 201 possible matches at 2026-10-16T20:38Z (complete pagination; 291 open PRs, 1786 discussion records), the first 20 rows all local original_card rows of this heavily drawn card (hpe-prewrapper-binding, hpe-wrapper-event-binding, hpe-lean-semantic-binding, hpe-axiom-inventory-audit, cold-hyperplane-semantic-binding and others). The construction reading named by the drawn method is unpriced: Labels.lean proves only factor_iff_pre; no package states the post-side uniqueness or its lambda-sharp form; hpe-prewrapper-binding states the pre-side implication and explicitly defers the arithmetic. Took that construction reading inside the card; no saturation re-draw needed."),
            "pair_collision_check": ("disc-comments --grep over discussions 1317 and 1166 at 2026-10-16T20:30Z (claims enumerated by headers and timestamps): no live CLAIM on this object. Nearest rows: comment 18917564 (2026-10-14T06:43Z, formal-interface-lemma scope key e3ffea67887eeb4c396c) DONE/released as PR 1697; comment 18921325 (2026-10-14T10:07Z, independent-moment scope key c6f2494b197df3bc3591) closed; comment 18941591 (2026-10-15T05:28Z, independent-moment, scope changed) expired 2026-10-15T07:30Z. All different scope keys and expired or released. Own CLAIM posted 2026-10-16T20:40Z: discussion 1317 comment 18982589."),
        },
        "freshness": {
            "canonical_main": BASE,
            "priority_revision": 6,
            "catalog_sha256": hashlib.sha256(git_bytes(BASE + ":" + CATALOG)).hexdigest(),
            "checked_utc": "2026-10-16T20:38Z",
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": "Windows (win32), native CPython, standard library only",
            "arithmetic": "exact integer Gaussian arithmetic; no floating point",
        },
    }
    (PKG / "TASK.json").write_text(json.dumps(task, indent=1, sort_keys=True, ensure_ascii=False) + "\n",
                                   encoding="utf-8", newline="\n")
    (PKG / "SOURCES.json").write_text(json.dumps(sources, indent=1, sort_keys=True) + "\n",
                                      encoding="utf-8", newline="\n")
    card_bytes = json.dumps(card, sort_keys=True, separators=(",", ":"))
    print("TASK.json and SOURCES.json written; original_card is the catalogue object",
          hashlib.sha256(card_bytes.encode()).hexdigest()[:16], "files:", len(sources["files"]))


if __name__ == "__main__":
    main()
