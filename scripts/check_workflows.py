#!/usr/bin/env python3
"""Lint every workflow in a worktree or exact Git commit, without running it.

--pre-push consumes Git's four-column pre-push input and validates every
non-deleted local object, including non-checked-out branches and annotated tags.
The validator can live in a separate tooling checkout from the repository tested.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

MANIFEST = Path(__file__).resolve().parents[1] / ".github/actionlint.json"
WORKFLOWS = Path(".github/workflows")


class ValidationError(Exception):
    pass


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValidationError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def push_refs(lines) -> list[str]:
    refs = []
    for line in lines:
        fields = line.split()
        if len(fields) != 4:
            raise ValidationError("malformed pre-push input: expected four fields")
        _, local_oid, _, remote_oid = fields
        if any(not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", oid)
               for oid in (local_oid, remote_oid)):
            raise ValidationError("malformed pre-push object ID")
        if set(local_oid) == {"0"}:  # deletion, no new workflow tree to check
            continue
        if local_oid not in refs:
            refs.append(local_oid)
    return refs


def is_workflow(path: Path) -> bool:
    return path.parent == WORKFLOWS and path.suffix in (".yml", ".yaml")


def is_metadata(path: Path) -> bool:
    return path.name in ("action.yml", "action.yaml")


def snapshot(repo: Path, ref: str | None) -> tuple[str, dict[str, bytes], set[str]]:
    files = {}
    regular_paths = set()
    if ref is None:
        # Git's source list excludes .git, ignored build/dependency trees, and
        # linked-worktree administrative files. Staged and untracked source
        # paths are included; ordinary worktree deletions stay deleted.
        paths = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        for raw_path in set(paths.split(b"\0")):
            if not raw_path:
                continue
            path = Path(raw_path.decode())
            source = repo / path
            if any((repo / Path(*path.parts[:n])).is_symlink()
                   for n in range(1, len(path.parts) + 1)):
                raise ValidationError(f"symlink source paths are unsupported: {path}")
            if not source.exists():
                continue
            regular = source.is_file()
            if regular:
                regular_paths.add(path.as_posix())
            if not (is_workflow(path) or is_metadata(path)):
                continue
            if not regular:
                raise ValidationError(f"workflow/action metadata must be a regular file: {path}")
            files[path.as_posix()] = source.read_bytes()
        label = "working tree (includes uncommitted workflow edits)"
    else:
        oid = git(repo, "rev-parse", "--verify", "--end-of-options",
                  f"{ref}^{{commit}}").decode().strip()
        label = oid
        entries = git(repo, "ls-tree", "-rz", "--full-tree", oid)
        for entry in entries.split(b"\0"):
            if not entry:
                continue
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, blob = metadata.decode().split()
            path = Path(raw_path.decode())
            if path.is_absolute() or ".." in path.parts or ".git" in path.parts:
                raise ValidationError(f"unsafe Git tree path: {path}")
            if mode == "120000":
                raise ValidationError(f"symlink source paths are unsupported: {path}")
            regular = mode in ("100644", "100755") and kind == "blob"
            if regular:
                regular_paths.add(path.as_posix())
            if not (is_workflow(path) or is_metadata(path)):
                continue
            if not regular:
                raise ValidationError(f"workflow/action metadata must be a regular file: {path}")
            files[path.as_posix()] = git(repo, "cat-file", "blob", blob)
    if not any(is_workflow(Path(path)) for path in files):
        raise ValidationError(f"no workflow files found in {label}; refusing an empty pass")
    # Local JS/Docker action metadata may reference resources outside its own
    # directory. Preserve regular-file existence, without reading/executing the
    # resources, only when there is local-action metadata to check.
    resources = regular_paths if any(is_metadata(Path(p)) for p in files) else set()
    return label, files, resources


def actionlint_binary(command: str) -> str:
    binary = shutil.which(command)
    if not binary:
        raise ValidationError("actionlint is missing; run scripts/install_actionlint.py "
                              "--directory /your/tool/directory and add it to PATH")
    binary = str(Path(binary).resolve())
    expected = json.loads(MANIFEST.read_text())["version"]
    version = subprocess.run([binary, "-version"], capture_output=True, text=True)
    if version.returncode or version.stdout.splitlines()[:1] != [expected]:
        raise ValidationError(f"actionlint {expected} required; got {version.stdout.strip()!r}")
    return binary


def lint(binary: str, label: str, files: dict[str, bytes], resources: set[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="workflow-lint-") as tmp:
        root = Path(tmp)
        # Without a project marker, actionlint silently omits local reusable
        # workflow and local-action metadata checks.
        (root / ".git").mkdir()
        # Never import ignore rules, even as empty resource placeholders.
        config_paths = {".github/actionlint.yaml", ".github/actionlint.yml"}
        for name in sorted(resources | files.keys()):
            if name in config_paths:
                continue
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(files.get(name, b""))
        workflows = sorted(name for name in files if is_workflow(Path(name)))
        # Native workflow/context/expression/local-metadata checks stay enabled.
        # External shell/Python linters are excluded to avoid PATH-dependent
        # results. Empty resource placeholders supply existence, not code.
        command = [binary, "-no-color", "-shellcheck=", "-pyflakes=", *workflows]
        print(f"Checking {len(workflows)} workflows at {label}", flush=True)
        result = subprocess.run(command, cwd=root)
    return result.returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--actionlint", default="actionlint")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ref", help="validate exactly this committed tree, not the checkout")
    mode.add_argument("--pre-push", action="store_true")
    args = parser.parse_args(argv)
    try:
        refs = push_refs(sys.stdin) if args.pre_push else [args.ref]
        if not refs:
            print("No non-deleted refs to validate")
            return 0
        binary = actionlint_binary(args.actionlint)
        failed = False
        for ref in refs:
            label, files, resources = snapshot(args.repo, ref)
            failed = bool(lint(binary, label, files, resources)) or failed
        return 1 if failed else 0
    except (ValidationError, OSError, ValueError) as error:
        print(f"Workflow validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
