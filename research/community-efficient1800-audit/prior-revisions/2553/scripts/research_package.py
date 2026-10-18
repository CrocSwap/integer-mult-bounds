#!/usr/bin/env python3
"""Validate and replay explicitly registered research packages, never every verify.py.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from contextlib import closing
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical_relative_path(name):
    # Git's changed paths use one repository-relative POSIX spelling. Accepting
    # aliases here would let a declared input evade the planner's exact match.
    require(isinstance(name, str), "canonical relative path must be a string")
    path = PurePosixPath(name)
    require(bool(path.parts) and not path.is_absolute() and ".." not in path.parts
            and "\\" not in name and path.as_posix() == name,
            "use a canonical repository-relative POSIX path: " + name)
    return path


def relative_file(root, name):
    canonical_relative_path(name)
    result = root / name
    require(result.resolve().is_relative_to(root.resolve()) and result.is_file()
            and not result.is_symlink(), "missing or external file: " + name)
    return result


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def git_source_rows(root, base, names):
    """Read one pinned object at a time through one Git process; no persistent cache.

    Each request is consumed before the next is sent. This avoids pipe deadlocks
    and retains the old one-blob memory bound, even for large source archives.
    Newline paths and non-blob objects retain the legacy Git-show semantics.
    The caller must close this generator if source validation fails mid-stream.
    """
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        try:
            for name in names:
                expression = base + ":" + name
                if "\n" in expression or "\r" in expression:
                    yield git(root, "rev-parse", expression).decode().strip(), git(root, "show", expression)
                    continue
                process.stdin.write(expression.encode("utf-8") + b"\n")
                process.stdin.flush()
                header = process.stdout.readline().rstrip(b"\n").split(b" ")
                require(len(header) == 3 and re.fullmatch(rb"[0-9a-f]{40,64}", header[0])
                        and header[2].isdigit(), "missing or invalid Git source: " + name)
                size = int(header[2])
                payload = process.stdout.read(size)
                require(len(payload) == size and process.stdout.read(1) == b"\n",
                        "truncated Git source: " + name)
                if header[1] != b"blob":
                    payload = git(root, "show", expression)
                yield header[0].decode("ascii"), payload
            process.stdin.close()
            code = process.wait(timeout=90)
            require(code == 0, "Git source reader failed: " + process.stderr.read().decode("utf-8", errors="replace"))
        finally:
            if not process.stdin.closed:
                process.stdin.close()
            if process.poll() is None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def git_blobs(root, specs):
    """Read exact blobs in one Git process, without retaining a cross-call cache.

    NUL-delimited requests preserve spaces/newlines in paths. Each reply's size
    frames the binary content, so embedded newlines and NUL bytes are harmless.
    The caller must close this iterator if validation stops before exhaustion.
    """
    with subprocess.Popen(["git", "cat-file", "--batch", "-z"], cwd=root,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE) as process:
        try:
            for spec in specs:
                require("\0" not in spec, "invalid Git object request")
                process.stdin.write(spec.encode("utf-8") + b"\0")
                process.stdin.flush()
                fields = process.stdout.readline().rstrip(b"\n").split(b" ")
                require(len(fields) == 3 and re.fullmatch(rb"[0-9a-f]{40,64}", fields[0])
                        and fields[1] == b"blob" and fields[2].isdigit(),
                        "missing or non-blob Git source: " + spec)
                size = int(fields[2])
                pinned = process.stdout.read(size)
                require(len(pinned) == size and process.stdout.read(1) == b"\n",
                        "incomplete Git blob response: " + spec)
                yield fields[0].decode("ascii"), pinned
            process.stdin.close()
            require(process.wait(timeout=90) == 0, "Git source reader failed")
        finally:
            # On an early pin/drift failure, EOF releases Git's request loop;
            # closing stdout also releases a producer with an unread reply.
            process.stdin.close()
            process.stdout.close()
            if process.poll() is None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def meaningful(value):
    return isinstance(value, str) and bool(value.strip()) and not re.search(r"\bTODO\b", value, re.I)


def validate(root, package, check_pins=True):
    parts = PurePosixPath(package).parts
    require(len(parts) == 2 and parts[0] == "research" and re.fullmatch(r"[a-z0-9][a-z0-9-]*", parts[1]),
            "package must be research/<slug>")
    data = {}
    for name in ("TASK.json", "SOURCES.json", "VERIFY.json"):
        data[name] = json.loads(relative_file(root, package + "/" + name).read_text(encoding="utf-8"))
        require(data[name].get("schema_version") == 1, "unsupported schema: " + name)
    task, sources, manifest = (data[n] for n in ("TASK.json", "SOURCES.json", "VERIFY.json"))
    require(task["scope_status"] in ("unchanged", "refined", "changed"), "declare scope_status")
    for field in ("actual_scope", "bottleneck_link", "stop_rule", "evidence", "author", "ai_assistance"):
        require(meaningful(task.get(field)), "complete TASK field: " + field)
    if task["scope_status"] == "unchanged":
        require(task["actual_scope"] == task["original_card"]["question"],
                "different wording/scope requires refined or changed plus a reason")
    else:
        require(meaningful(task.get("scope_change_reason")), "explain the scope refinement/change")
    require(task["outcome"] in ("partial", "completed", "blocked", "negative-result"), "declare outcome")
    questions = task.get("open_questions")
    require(isinstance(questions, list), "open_questions must be a list")
    if not questions:
        require(meaningful(task.get("no_open_questions_reason")), "explain an empty next-question list")
    for question in questions:
        for field in ("question", "why_it_matters", "first_step", "blocked_by"):
            require(meaningful(question.get(field)), "complete next-question field: " + field)
    readme = relative_file(root, package + "/README.md").read_text(encoding="utf-8")
    require("## Open next questions" in readme, "README needs Open next questions")
    require(manifest.get("status") == "ready", "VERIFY.json is a draft; complete it before requesting replay")
    require(manifest.get("python") == "3.12", "generic replay currently uses Python 3.12")
    requirements = manifest.get("requirements", [])
    require(isinstance(requirements, list) and len(requirements) == len(set(requirements)), "invalid requirements")
    for item in requirements:
        require(re.fullmatch(r"(?:numpy|sympy|scipy)==[0-9]+(?:\.[0-9]+){1,2}", item),
                "generic CI supports exact numpy/sympy/scipy pins; use a dedicated workflow for other environments")
    commands = manifest.get("commands")
    require(isinstance(commands, list) and 1 <= len(commands) <= 8, "declare 1..8 explicit verification commands")
    total = 0
    for command in commands:
        argv = command.get("argv")
        require(isinstance(argv, list) and len(argv) >= 2 and all(isinstance(a, str) for a in argv), "invalid argv")
        require(argv[0] == "{python}", "commands must explicitly use {python}; no implicit shell")
        require(meaningful(command.get("checks")), "describe command coverage")
        seconds = command.get("timeout_seconds")
        require(type(seconds) is int and 1 <= seconds <= 600, "command timeout must be 1..600 seconds")
        total += seconds
    require(total <= 1200, "generic replay has a 1200-second total budget; use a dedicated job for larger checks")
    inputs = manifest.get("inputs")
    require(isinstance(inputs, list), "declare input paths for CI invalidation")
    for name in inputs:
        relative_file(root, name)
    require(sources.get("files"), "empty source inventory")
    require(re.fullmatch(r"[0-9a-f]{40,64}", sources["base_commit"]), "pin an exact base commit")
    require(task["base_commit"] == sources["base_commit"], "TASK and SOURCES base mismatch")
    require(all(r.get("usage") in ("input", "provenance") for r in sources["files"]), "declare source usage")
    require({r["path"] for r in sources["files"] if r["usage"] == "input"} <= set(inputs),
            "all live pinned inputs must be declared CI inputs")
    if check_pins:
        catalog_name = "docs/research/agent-task-catalog.json"
        require(catalog_name in {r["path"] for r in sources["files"]}, "pin the originating task catalogue")
        names = [r["path"] for r in sources["files"]]
        for name in names:
            p = PurePosixPath(name)
            require(not p.is_absolute() and ".." not in p.parts, "invalid source path")
        specs = [sources["base_commit"] + ":" + name for name in names]
        with closing(git_blobs(root, specs)) as objects:
            for index, (obj, pinned) in enumerate(objects):
                row = sources["files"][index]
                name = row["path"]
                require(obj == row["git_blob"], "source blob provenance mismatch: " + name)
                require(hashlib.sha256(pinned).hexdigest() == row["sha256"], "source SHA256 provenance mismatch: " + name)
                if row["usage"] == "input":
                    require(pinned == relative_file(root, name).read_bytes(), "working source drift: " + name)
                if name == catalog_name:
                    catalog = json.loads(pinned)
        cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == task["task_id"]]
        require(len(cards) == 1 and task["original_card"] == cards[0], "original card does not match pinned catalogue")
    return task, manifest


def run_command(argv, cwd, timeout):
    # Assertion checks must not disappear because of the caller's environment.
    # Keep explicit manifest options (including deliberate -O controls) intact.
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    # A timeout ends the whole local process group, including child solvers.
    process = subprocess.Popen(argv, cwd=cwd, env=env, start_new_session=True)
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        if hasattr(os, "killpg"):
            os.killpg(process.pid, signal.SIGKILL)
        else:  # Windows has no process groups to signal; end the whole child tree instead.
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
        process.wait()
        raise ValueError("verification timed out")
    require(code == 0, f"verification command exited {code}")


def isolated_python_argv(argv, cache_directory):
    """Place our cache option after interpreter flags, before the entry point.

    -B prevents writes, not reads of existing .pyc files. A fresh namespace
    keeps preexisting source-adjacent and externally configured caches out of
    this registered interpreter. It is not inherited by child interpreters.
    """
    require(argv and argv[0] == sys.executable, "cache isolation requires the registered Python interpreter")
    index = 1
    options = [argv[0]]
    while index < len(argv):
        option = argv[index]
        if option in ("-", "--") or not option.startswith("-"):
            break
        if option == "--check-hash-based-pycs":
            require(index + 1 < len(argv), "missing Python hash-cache option argument")
            options.extend(argv[index:index + 2])
            index += 2
            continue
        if option.startswith("--"):
            options.append(option)
            index += 1
            continue
        # Python permits combined short flags, attached -c/-m payloads, and
        # attached or separate -W/-X arguments. Stop scanning an option once
        # its argument begins: letters inside that argument are not flags.
        entry = False
        consumed = 1
        replace_cache = False
        for offset, flag in enumerate(option[1:], start=1):
            if flag in "cm":
                entry = True
                break
            if flag in "WX":
                if offset == len(option) - 1:
                    require(index + 1 < len(argv), "missing Python interpreter option argument")
                    consumed = 2
                value = argv[index + 1] if consumed == 2 else option[offset + 1:]
                if flag == "X" and value.split("=", 1)[0] == "pycache_prefix":
                    replace_cache = True
                    if offset > 1:
                        options.append(option[:offset])
                break
        if entry:
            break
        if not replace_cache:
            options.extend(argv[index:index + consumed])
        index += consumed
    # CPython's effective prefix can use the first duplicate -X value even
    # when sys._xoptions shows the last. Remove only earlier cache-prefix
    # settings; script arguments remain untouched, even when spelled -X.
    return [*options, "-X", "pycache_prefix=" + str(cache_directory), *argv[index:]]


def run_python_replay(argv, cwd, timeout):
    with tempfile.TemporaryDirectory(prefix="research-replay-pycache-") as cache:
        run_command(isolated_python_argv(argv, cache), cwd, timeout)


def run_package(root, package, install=False):
    task, manifest = validate(root, package)
    require(sys.version_info[:2] == (3, 12), "run replay with Python 3.12 (metadata check is version-independent)")
    if install and manifest["requirements"]:
        run_command([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", *manifest["requirements"]], root, 300)
    for requirement in manifest["requirements"]:
        name, version = requirement.split("==")
        require(importlib.metadata.version(name) == version, "dependency version mismatch: " + requirement)
    for command in manifest["commands"]:
        argv = [sys.executable if item == "{python}" else item.replace("{package}", package) for item in command["argv"]]
        print("CHECK " + command["checks"], flush=True)
        run_python_replay(argv, root, command["timeout_seconds"])
    print("PASS_REGISTERED_RESEARCH_PACKAGE " + package + " outcome=" + task["outcome"])


def plan(root, changed):
    changed = set(changed)
    replay_changed = bool(changed.intersection({
        "scripts/research_package.py", ".github/workflows/research-packages.yml"}))
    packages = []
    for path in sorted((root / "research").glob("*/VERIFY.json")):
        package = path.parent.relative_to(root).as_posix()
        manifest = json.loads(path.read_text(encoding="utf-8"))
        # Parse only for selection; validate fully in the isolated replay job.
        inputs = manifest.get("inputs", [])
        require(isinstance(inputs, list), "declare input paths for CI invalidation")
        for name in inputs:
            # Do not require existence: a deleted input must still trigger replay.
            canonical_relative_path(name)
        if (changed.intersection(inputs) or any(p.startswith(package + "/") for p in changed)
                or replay_changed):
            packages.append(package)
    return packages


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--install-deps", action="store_true", help="explicit opt-in to install manifest's allowed pinned dependencies")
    ap.add_argument("--changed-since", help="plan affected opt-in packages relative to this Git commit")
    ap.add_argument("--github-output", type=Path)
    args = ap.parse_args()
    try:
        if args.changed_since:
            if set(args.changed_since) == {"0"}:
                changed = git(ROOT, "ls-files", "-z").decode().split("\0")
            else:
                base = git(ROOT, "rev-parse", "--verify", args.changed_since + "^{commit}").decode().strip()
                # A rename must invalidate both the removed input and its new path.
                changed = git(ROOT, "diff", "--no-renames", "--name-only", "-z", base, "HEAD").decode().split("\0")
            packages = plan(ROOT, changed)
            matrix = json.dumps({"include": [{"package": p} for p in packages]})
            print(matrix)
            if args.github_output:
                with args.github_output.open("a", encoding="utf-8") as out:
                    out.write(f"matrix={matrix}\ncount={len(packages)}\n")
        elif args.package:
            if args.check_only:
                validate(ROOT, args.package)
                print("PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)")
            else:
                run_package(ROOT, args.package, args.install_deps)
        else:
            ap.error("use --package or --changed-since")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, importlib.metadata.PackageNotFoundError) as exc:
        ap.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
