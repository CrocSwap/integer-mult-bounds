#!/usr/bin/env python3
"""Find and price one five-dimensional P112 port cover."""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location("five_plane_core", PACKAGE / "core.py")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-cap", type=int, default=10_000)
    parser.add_argument("--out", type=Path, default=PACKAGE / "CANDIDATE.json")
    args = parser.parse_args()
    core.need(args.attempt_cap > 0, "positive attempt cap")
    labels, _ = core.load_sources()
    cover = core.find_cover(labels, args.attempt_cap)
    core.need(cover is not None, "no exact cover within the stated randomized-greedy cap")
    candidate = core.make_candidate(cover, labels)
    task = json.loads((PACKAGE / "TASK.json").read_text())
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    result = {
        "schema_version": 1,
        "seed": core.SEED,
        "task_id": task["task_id"],
        "priority_revision": task["priority_revision"],
        "base_commit": task["base_commit"],
        "selected_record_sha256": next(x["sha256"] for x in sources["files"]
                                         if x["path"] == "certificates/selected-result.json"),
        "catalogue_sha256": next(x["sha256"] for x in sources["files"]
                                  if x["path"] == "docs/research/agent-task-catalog.json"),
        "candidate": candidate,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FOUND_FIVE_PLANE_P112",
          f"attempt={cover['attempt']}", f"steps={cover['greedy_steps']}",
          f"frames={cover['five_frame_count']}", f"terms={candidate['term_count']}",
          f"copy_charge={candidate['copy_charge']}",
          f"copy_hist={candidate['copy_rank_histogram']}",
          f"a_hi={candidate['moment_screen_u5']['ceiling_upper_decimal']:.12f}")

if __name__ == "__main__":
    main()
