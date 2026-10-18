#!/usr/bin/env python3
"""Read-only, reproducible research suggestions; never a reservation service.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CATALOG = Path("docs/research/agent-task-catalog.json")
HANDOFF_URL = "https://github.com/CrocSwap/integer-mult-bounds/discussions/1166"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def check_catalog_files(root, required):
    """Allow deliberate sparse omissions, not deletions or changed index inputs."""
    missing = {}
    for name, error in required:
        path = root / name
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(error)
        if path.is_file():
            continue
        if path.exists() or path.is_symlink() or path.resolve() != root.resolve() / name:
            raise ValueError(error)
        missing[name] = error
    if not missing:
        return []
    omitted = {}
    try:
        def git(*args):
            return subprocess.run(
                ["git", "--literal-pathspecs", *args, "--", *missing], cwd=root,
                check=True, capture_output=True, text=True, encoding="utf-8",
            ).stdout.split("\0")
        for entry in git("ls-files", "-t", "--stage", "-z"):
            if not entry:
                continue
            metadata, name = entry.split("\t", 1)
            flag, mode, blob, stage = metadata.split()
            if flag == "S" and mode in ("100644", "100755") and stage == "0":
                omitted[name] = blob
        committed = {}
        for entry in git("ls-tree", "-r", "-z", "HEAD"):
            if not entry:
                continue
            metadata, name = entry.split("\t", 1)
            mode, kind, blob = metadata.split()
            if kind == "blob" and mode in ("100644", "100755"):
                committed[name] = blob
    except (OSError, subprocess.CalledProcessError):
        omitted = {}
        committed = {}
    for name, error in missing.items():
        if name not in omitted or omitted[name] != committed.get(name):
            raise ValueError(error)
    return sorted(missing)


def validate_catalog(catalog, root):
    if catalog.get("schema_version") != 1:
        raise ValueError("unsupported catalogue schema")
    revision = catalog.get("priority_revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("priority_revision must be a positive integer")
    required = [(catalog["priority_log"], "missing or external priority log")]
    tracks = catalog.get("tracks", [])
    if not tracks:
        raise ValueError("empty catalogue")
    ids = set()
    task_ids = set()
    for track in tracks:
        ident = track["id"]
        if ident in ids or not re.fullmatch(r"[a-z0-9-]+", ident):
            raise ValueError("duplicate or invalid track id")
        ids.add(ident)
        if type(track["weight"]) is not int or track["weight"] <= 0:
            raise ValueError("weights must be positive integers")
        if not track["tasks"]:
            raise ValueError("track has no tasks")
        for task in track["tasks"]:
            if task["id"] in task_ids:
                raise ValueError("duplicate task id")
            task_ids.add(task["id"])
            if not task["question"] or not task["acceptance_gate"] or not task["methods"]:
                raise ValueError("incomplete task card")
            if not task["starting_points"]:
                raise ValueError("task needs a starting point")
            for key in ("first_step", "first_experiment", "bottleneck_link", "allowed_variations", "scope_change_triggers", "overlap_terms"):
                if not task.get(key):
                    raise ValueError("missing actionable task field: " + key)
            checks = task.get("existing_checks", [])
            if not isinstance(checks, list):
                raise ValueError("existing_checks must be a list")
            for check in checks:
                if not isinstance(check, dict):
                    raise ValueError("coverage entry must be an object")
                for key in ("scope", "evidence", "remaining"):
                    if not isinstance(check.get(key), str) or not check[key].strip():
                        raise ValueError("incomplete coverage: " + key)
                if check.get("status") not in ("author-checked", "independently-checked", "reviewed"):
                    raise ValueError("invalid coverage status")
                if not isinstance(check.get("source_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", check["source_commit"]):
                    raise ValueError("coverage needs an exact source commit")
                if not isinstance(check.get("selected_record_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", check["selected_record_sha256"]):
                    raise ValueError("coverage needs its selected-record context")
            step = task["first_step"]
            if not step.get("expected") or not step.get("inspect") or not step.get("command"):
                raise ValueError("incomplete first step")
            script = step["command"][-1]
            required.append((script, "missing first-step script: " + script))
            for name in task["starting_points"]:
                required.append((name, f"missing or external starting point: {name}"))
    if sum(t["weight"] for t in tracks) != 100:
        raise ValueError("track weights must sum to 100")
    return check_catalog_files(root, required)


def scope_key(task_id, method):
    # Base and nonce intentionally do not affect the semantic collision key.
    return digest(canonical({"task": task_id, "method": method}))[:20]


def select(catalog, seed, track_id=None, task_id=None):
    if not re.fullmatch(r"[0-9a-fA-F]{32}", seed):
        raise ValueError("seed must be exactly 32 hexadecimal digits")
    seed = seed.lower()

    def draw(label):
        return int(digest(canonical([seed, label])), 16)

    tracks = catalog["tracks"]
    if task_id:
        owners = [t for t in tracks if any(card["id"] == task_id for card in t["tasks"])]
        if len(owners) != 1 or (track_id and owners[0]["id"] != track_id):
            raise ValueError("unknown task or task/track mismatch")
        track_id = owners[0]["id"]
    if track_id is not None:
        matches = [t for t in tracks if t["id"] == track_id]
        if not matches:
            raise ValueError(f"unknown track: {track_id}")
        track = matches[0]
    else:
        ticket = draw("track") % 100
        for track in tracks:
            ticket -= track["weight"]
            if ticket < 0:
                break

    ordered = sorted([t for t in track["tasks"] if not task_id or t["id"] == task_id],
                     key=lambda t: draw("task:" + t["id"]))
    suggestions = []
    for task in ordered[:3]:
        method = task["methods"][draw("method:" + task["id"]) % len(task["methods"])]
        suggestions.append({
            "task_id": task["id"], "scope_key": scope_key(task["id"], method),
            "handoff_url": HANDOFF_URL,
            "existing_checks": task.get("existing_checks", []),
            "coverage_rule": "These checks have limited scopes. Empty coverage means unknown, not unstudied. Audit a missing implication or explicitly justify independent repetition.",
            "question": task["question"], "method": method,
            "starting_points": task["starting_points"],
            "acceptance_gate": task["acceptance_gate"],
            **{key: task[key] for key in ("first_step", "first_experiment", "bottleneck_link", "allowed_variations", "scope_change_triggers", "overlap_terms")},
            "scope_rule": "If you change the card's premise, record scope_status=changed and explain why. A package metadata check cannot establish mathematical relevance.",
        })
    return {"seed": seed, "track": track["id"], "suggestions": suggestions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", help="32 hex digits; default: fresh OS-random 128-bit nonce")
    parser.add_argument("--track", help="override weighted track selection; see catalogue")
    parser.add_argument("--task", help="show one specific card, without rerolling an existing assignment")
    parser.add_argument("--coordination-cache", type=Path,
                        help="Optional existing find_overlap.py cache; no automatic fetch or reservation")
    args = parser.parse_args()
    try:
        catalog_bytes = (ROOT / CATALOG).read_bytes()
        catalog = json.loads(catalog_bytes)
        omitted = validate_catalog(catalog, ROOT)
        result = select(catalog, args.seed if args.seed is not None else secrets.token_hex(16), args.track, args.task)
        selected_bytes = (ROOT / "certificates/selected-result.json").read_bytes()
        selected = json.loads(selected_bytes)
        try:
            base = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                capture_output=True, text=True, encoding="utf-8",
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            base = None
        coordination = {"handoff_url": HANDOFF_URL,
                        "scope": "Check live handoffs first; no structured snapshot supplied."}
        if args.coordination_cache:
            from research_coordination import board_view
            coordination = board_view(json.loads(args.coordination_cache.read_text(encoding="utf-8")))
        for suggestion in result["suggestions"]:
            suggestion["coverage_context_matches_selected"] = all(
                check["selected_record_sha256"] == digest(selected_bytes)
                for check in suggestion["existing_checks"]) if suggestion["existing_checks"] else None
            suggestion["open_handoffs"] = [row for row in coordination.get("open_handoffs", [])
                                           if row["task"] == suggestion["task_id"]]
            suggestion["advisory_claims"] = [row for row in coordination.get("claims", [])
                                            if row["task"] == suggestion["task_id"]]
        result.update({
            "coordination": coordination,
            "priorities": "docs/research/current-priorities.md",
            "base_commit": base,
            "catalog_assessed_on": catalog.get("assessed_on"),
            "priority_revision": catalog["priority_revision"],
            "priority_log": catalog["priority_log"],
            "catalog_sha256": digest(catalog_bytes),
            "selected_record_sha256": digest(selected_bytes),
            "selected": {k: selected[k] for k in ("kappa", "review", "source_manifest", "reproduce")},
            "status": "SUGGESTIONS_ONLY_NOT_RESERVED",
            "next_step": "First check #1166 for a suitable open handoff. Use these suggestions if none fits, check live overlap and existing coverage, then record a bounded scope. Claims never exclude independent audits.",
        })
        if omitted:
            result["sparse_checkout"] = {
                "omitted_catalogue_paths": omitted,
                "scope": "These absent regular files match HEAD and skip-worktree index entries. Materialize the chosen task's inputs before running it; this validates catalogue references, not replay dependencies.",
            }
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
