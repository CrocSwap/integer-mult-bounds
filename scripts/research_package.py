#!/usr/bin/env python3
"""Validate and replay explicitly registered research packages, never every verify.py.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import errno
from contextlib import closing, contextmanager
from itertools import chain
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
GIT_BLOB_RESPONSE_TIMEOUT = 90


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


def symlink_free_relative_path(root, name):
    """Reject symlink/junction components without requiring a deleted input to exist.

    Git reports changes under the target's path, not a symlink alias declared
    by its consumer. Inspect existing components below the repository root;
    the checkout must remain stable during planning, validation and replay.
    """
    parts = canonical_relative_path(name).parts
    current = root
    for part in parts:
        current = current / part
        try:
            info = current.lstat()
        except (FileNotFoundError, NotADirectoryError):
            break
        require(not stat.S_ISLNK(info.st_mode), "symlink in repository-relative path: " + name)
        # Windows junctions have directory mode, not S_IFLNK. Inspect the same
        # lstat result so even a dangling junction is rejected before traversal.
        require(getattr(info, "st_reparse_tag", 0) != getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", None),
                "junction in repository-relative path: " + name)
    return root / name


def relative_file(root, name):
    result = symlink_free_relative_path(root, name)
    require(result.resolve().is_relative_to(root.resolve()) and result.is_file(),
            "missing or external file: " + name)
    return result


# Adapted from the package-local policy in
# research/t74-2530-source-partner-audit/audit_common.py (Apache-2.0).
# Keep repository configuration and linked-worktree .git discovery intact;
# inherited shell overrides must not choose a different repository or index.
_GIT_REDIRECT_VARS = frozenset((
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT",
))
_GIT_CONFIG_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")


def git_source_env():
    """Use cwd's repository and stored objects, without changing the parent.

    Git can ignore cwd when inherited selection variables point elsewhere.
    Config-injection variables can also redirect worktree/index operations.
    This policy is only for Git metadata/source subprocesses, not verifiers.
    """
    env = {name: value for name, value in os.environ.items()
           if name not in _GIT_REDIRECT_VARS and not name.startswith(_GIT_CONFIG_PREFIXES)}
    # Replacement refs can report an original ID while returning other bytes.
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    return env


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, env=git_source_env(),
                          capture_output=True, check=True).stdout


def tracked_input_paths(root):
    """Use HEAD spelling, never case folding, filesystem resolution or the index.

    Staged/untracked files are not replay inputs until committed. NUL framing
    preserves Git filenames containing whitespace, including CR and LF.
    """
    raw = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", "HEAD"], cwd=root, env=git_source_env(),
        capture_output=True, check=True, timeout=30).stdout
    return frozenset(name.decode("utf-8") for name in raw.split(b"\0") if name)


def require_tracked_input(name, paths):
    canonical_relative_path(name)
    require(name in paths, "use an exact Git-tracked input path from HEAD: " + name)


def git_source_rows(root, base, names):
    """Read one pinned object at a time through one Git process; no persistent cache.

    Each request is consumed before the next is sent. This avoids pipe deadlocks
    and retains the old one-blob memory bound, even for large source archives.
    Newline paths and non-blob objects retain the legacy Git-show semantics.
    The caller must close this generator if source validation fails mid-stream.
    """
    with subprocess.Popen(["git", "cat-file", "--batch"], cwd=root, env=git_source_env(),
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


class _UnsupportedNulBatch(Exception):
    """Git rejected the initial NUL-mode request before yielding any source."""


def _closed_stdin_error(error):
    # Windows can report EINVAL instead of EPIPE when a child closes stdin.
    # This classifies the pipe error only; the retry still requires exit 129.
    return (isinstance(error, BrokenPipeError)
            or (os.name == "nt" and error.errno == errno.EINVAL))


def _stop_git_blob_process(process):
    """Stop this reader's owned POSIX group even after its leader exits."""
    try:
        if os.name == "posix":
            # Reap an exited leader first: signaling a group containing only
            # its unreaped zombie can report EPERM on macOS. A surviving
            # descendant keeps the group alive after the leader is reaped.
            process.poll()
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass


@contextmanager
def _git_blob_response_deadline(stop):
    """Bound one response, excluding time spent by its consumer.

    On POSIX the reader owns a session: ordinary descendants retaining a pipe
    are stopped with the leader. Escaped sessions and separate git() calls are
    outside this contract; non-POSIX retains the direct-child deadline.
    """
    expired = threading.Event()

    def terminate():
        expired.set()
        stop()

    timer = threading.Timer(GIT_BLOB_RESPONSE_TIMEOUT, terminate)
    timer.start()
    try:
        yield
    finally:
        timer.cancel()
        timer.join()
        if expired.is_set():
            raise subprocess.TimeoutExpired("git cat-file blob response", GIT_BLOB_RESPONSE_TIMEOUT)


def _git_blob_batch(root, specs, nul):
    argv = ["git", "cat-file", "--batch"] + (["-z"] if nul else [])
    # Usage diagnostics from the unsupported-option probe are expected. Avoid
    # a second pipe that could block while we consume the framed stdout reply.
    with subprocess.Popen(argv, cwd=root, env=git_source_env(), stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          start_new_session=(os.name == "posix")) as process:
        stopped = False

        def stop():
            nonlocal stopped
            if not stopped:
                _stop_git_blob_process(process)
                stopped = True

        try:
            for index, spec in enumerate(specs):
                require("\0" not in spec, "invalid Git object request")
                request = spec
                if not nul and ("\n" in spec or "\r" in spec):
                    # Resolve one literal argument, never split a path into requests.
                    request = git(root, "rev-parse", "--verify", "--end-of-options", spec).decode("ascii").strip()
                    require(re.fullmatch(r"[0-9a-f]{40,64}", request), "invalid Git object ID")
                with _git_blob_response_deadline(stop):
                    try:
                        process.stdin.write(request.encode("utf-8") + (b"\0" if nul else b"\n"))
                        process.stdin.flush()
                    except OSError as exc:
                        if not _closed_stdin_error(exc):
                            raise
                        header = b""
                    else:
                        header = process.stdout.readline()
                    if nul and index == 0 and not header and process.wait(timeout=90) == 129:
                        raise _UnsupportedNulBatch(spec)
                    fields = header.rstrip(b"\n").split(b" ")
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
            # Terminate ordinary descendants before closing buffered pipes. This
            # also covers successful leader exit and an early generator close.
            if os.name == "posix":
                stop()
            # Option rejection can close stdin before our first write/flush.
            try:
                process.stdin.close()
            except OSError as exc:
                if not _closed_stdin_error(exc):
                    raise
            process.stdout.close()
            if process.poll() is None:
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def git_blobs(root, specs):
    """Stream exact blobs, retaining the one-process NUL protocol on newer Git.

    Git without -z rejects it with usage status 129. Retry only before any
    response, replaying the consumed first request through the line protocol.
    The fallback resolves CR/LF paths to object IDs before requesting content.
    The caller must close this iterator if validation stops before exhaustion.
    """
    specs = iter(specs)
    sentinel = object()
    first = next(specs, sentinel)
    if first is sentinel:
        return
    with closing(_git_blob_batch(root, chain((first,), specs), nul=True)) as rows:
        try:
            yield from rows
        except _UnsupportedNulBatch as exc:
            with closing(_git_blob_batch(root, chain((exc.args[0],), specs), nul=False)) as legacy:
                yield from legacy


def meaningful(value):
    return isinstance(value, str) and bool(value.strip()) and not re.search(r"\bTODO\b", value, re.I)


def brief(value):
    text = json.dumps(value, ensure_ascii=True, sort_keys=True)
    return text if len(text) <= 120 else text[:117] + "..."


def require_key(mapping, key, where, shape=None):
    """Name the missing key and its expected shape instead of a bare KeyError."""
    require(isinstance(mapping, dict),
            where + " must be a JSON object; found " + type(mapping).__name__ + ": " + brief(mapping))
    require(key in mapping, where + "." + key + " is missing"
            + ("; expected " + shape if shape else ""))
    return mapping[key]


def require_text(mapping, key, where, shape="a non-empty string without TODO"):
    """Name the key and distinguish missing, wrong-shaped and weak values."""
    require(isinstance(mapping, dict),
            where + " must be a JSON object; found " + type(mapping).__name__ + ": " + brief(mapping))
    require(key in mapping, where + "." + key + " is missing; expected " + shape)
    value = mapping[key]
    require(isinstance(value, str) and meaningful(value),
            where + "." + key + " must be " + shape + "; found " + type(value).__name__ + ": " + brief(value))


def card_differences(own, pinned):
    """Name every key by which a TASK.json original_card differs from its pin."""
    if not isinstance(own, dict):
        return "TASK.json original_card is " + type(own).__name__ + ", expected a JSON object"
    details = []
    missing = [key for key in pinned if key not in own]
    extra = [key for key in own if key not in pinned]
    if missing:
        details.append("missing keys: " + ", ".join(missing))
    if extra:
        details.append("unexpected keys: " + ", ".join(extra))
    for key in (key for key in pinned if key in own and own[key] != pinned[key]):
        details.append(key + " differs (TASK.json: " + brief(own[key]) + "; pinned: " + brief(pinned[key]) + ")")
    return "; ".join(details) or "cards compare unequal without a key difference"


def source_pin(row, base):
    """Resolve one SOURCES.json row to its exact Git object expression.

    Rows without an explicit pin keep the historical base_commit:<path> form.
    A file vendored from a pull-request head is pinned exactly with
    head:<40-hex sha>:<path>, so its bytes resolve at that commit, not at the
    package base. An explicit but unparseable pin fails closed.
    """
    name = row["path"]
    pin = row.get("pin")
    if pin is None:
        return base + ":" + name
    if pin == "base_commit:" + name:
        return base + ":" + name
    # Git filenames can contain LF; it is part of the exact path, not a delimiter.
    match = re.fullmatch(r"head:([0-9a-f]{40}):(.+)", pin, re.DOTALL) if isinstance(pin, str) else None
    if match is not None and match.group(2) == name:
        return match.group(1) + ":" + name
    raise ValueError("SOURCES.json pin for " + name + " is not a supported pin form: " + brief(pin)
                     + "; accepted pin forms are base_commit:<path> and head:<40-hex sha>:<path>")


def validate(root, package, check_pins=True):
    parts = PurePosixPath(package).parts
    require(len(parts) == 2 and parts[0] == "research" and re.fullmatch(r"[a-z0-9][a-z0-9-]*", parts[1]),
            "package must be research/<slug>")
    data = {}
    for name in ("TASK.json", "SOURCES.json", "VERIFY.json"):
        data[name] = json.loads(relative_file(root, package + "/" + name).read_text(encoding="utf-8"))
        version = require_key(data[name], "schema_version", name)
        require(version == 1, name + ".schema_version must be 1; found " + brief(version))
    task, sources, manifest = (data[n] for n in ("TASK.json", "SOURCES.json", "VERIFY.json"))
    scope_status = require_key(task, "scope_status", "TASK.json", "unchanged, refined or changed")
    require(scope_status in ("unchanged", "refined", "changed"),
            "TASK.json.scope_status must be unchanged, refined or changed; found " + brief(scope_status))
    for field in ("actual_scope", "bottleneck_link", "stop_rule", "evidence", "author", "ai_assistance"):
        require_text(task, field, "TASK.json")
    if scope_status == "unchanged":
        question = require_key(require_key(task, "original_card", "TASK.json",
                                           "the pinned catalogue card object"),
                               "question", "TASK.json.original_card")
        require(task["actual_scope"] == question,
                "different wording/scope requires refined or changed plus a reason"
                + " (TASK.json.actual_scope " + brief(task["actual_scope"])
                + " differs from TASK.json.original_card.question " + brief(question) + ")")
    else:
        require_text(task, "scope_change_reason", "TASK.json",
                     "a non-empty string without TODO explaining the scope refinement/change")
    outcome = require_key(task, "outcome", "TASK.json",
                          "partial, completed, blocked or negative-result")
    require(outcome in ("partial", "completed", "blocked", "negative-result"),
            "TASK.json.outcome must be partial, completed, blocked or negative-result; found " + brief(outcome))
    questions = task.get("open_questions")
    require(isinstance(questions, list),
            "TASK.json.open_questions must be a list; found " + type(questions).__name__ + ": " + brief(questions))
    if not questions:
        require_text(task, "no_open_questions_reason", "TASK.json",
                     "a non-empty string without TODO explaining an empty next-question list")
    for position, question in enumerate(questions):
        for field in ("question", "why_it_matters", "first_step", "blocked_by"):
            require_text(question, field, "TASK.json.open_questions[" + str(position) + "]")
    readme = relative_file(root, package + "/README.md").read_text(encoding="utf-8")
    require("## Open next questions" in readme, "README.md needs an \"## Open next questions\" section")
    status = require_key(manifest, "status", "VERIFY.json")
    require(status == "ready",
            "VERIFY.json.status must be \"ready\"; complete the draft before requesting replay; found " + brief(status))
    python = require_key(manifest, "python", "VERIFY.json")
    require(python == "3.12",
            "VERIFY.json.python must be \"3.12\" (generic replay currently uses Python 3.12); found " + brief(python))
    requirements = manifest.get("requirements", [])
    require(isinstance(requirements, list),
            "VERIFY.json.requirements must be a list of exact \"name==version\" pins; found "
            + type(requirements).__name__ + ": " + brief(requirements))
    require(len(requirements) == len(set(requirements)), "VERIFY.json.requirements must not repeat a pin")
    for item in requirements:
        require(isinstance(item, str)
                and re.fullmatch(r"(?:numpy|sympy|scipy)==[0-9]+(?:\.[0-9]+){1,2}", item),
                "generic CI supports exact numpy/sympy/scipy pins; use a dedicated workflow for other environments"
                + "; offending entry: " + brief(item))
    names = [item.split("==")[0] for item in requirements]
    require(len(names) == len(set(names)), "declare only one version per dependency")
    # Validation already treats an omitted list as empty; execution must receive
    # that same default without rewriting the contributor's manifest on disk.
    manifest["requirements"] = requirements
    commands = manifest.get("commands")
    require(isinstance(commands, list) and 1 <= len(commands) <= 8,
            "VERIFY.json.commands must be a list of 1..8 explicit verification commands; found "
            + type(commands).__name__ + ": " + brief(commands))
    total = 0
    for position, command in enumerate(commands):
        path = "VERIFY.json.commands[" + str(position) + "]"
        require(isinstance(command, dict),
                path + " must be a JSON object; found " + type(command).__name__ + ": " + brief(command))
        argv = command.get("argv")
        require(isinstance(argv, list) and len(argv) >= 2 and all(isinstance(a, str) for a in argv),
                path + ".argv must be a list of at least 2 strings; found " + brief(argv))
        require(argv[0] == "{python}", path + ".argv must explicitly use {python}; no implicit shell")
        require_text(command, "checks", path, "a non-empty string without TODO describing command coverage")
        seconds = command.get("timeout_seconds")
        require(type(seconds) is int,
                path + ".timeout_seconds must be an integer number of seconds; found "
                + type(seconds).__name__ + ": " + brief(seconds))
        require(1 <= seconds <= 600,
                path + ".timeout_seconds " + str(seconds)
                + (" exceeds the 600 s per-command cap" if seconds > 600
                   else " is below the 1 s per-command minimum"))
        total += seconds
    require(total <= 1200, "declared replay budget " + str(total)
            + " s (sum of timeout_seconds) exceeds the 1200 s total cap"
            + "; use a dedicated job for larger checks")
    inputs = manifest.get("inputs")
    require(isinstance(inputs, list),
            "VERIFY.json.inputs must be a list of canonical repository-relative paths; found "
            + type(inputs).__name__ + ": " + brief(inputs))
    tracked = tracked_input_paths(root)
    for name in inputs:
        symlink_free_relative_path(root, name)
        require_tracked_input(name, tracked)
        relative_file(root, name)
    files = require_key(sources, "files", "SOURCES.json")
    require(files, "SOURCES.json.files is empty; declare the source inventory")
    base = require_key(sources, "base_commit", "SOURCES.json", "a 40-64 hex string pinning an exact base commit")
    require(isinstance(base, str) and re.fullmatch(r"[0-9a-f]{40,64}", base),
            "SOURCES.json.base_commit must be a 40-64 hex string pinning an exact base commit; found " + brief(base))
    task_base = require_key(task, "base_commit", "TASK.json",
                            "a 40-64 hex string equal to SOURCES.json.base_commit")
    require(task_base == base, "TASK.json.base_commit " + brief(task_base)
            + " must equal SOURCES.json.base_commit " + brief(base))
    for row in files:
        require(isinstance(row, dict) and isinstance(row.get("path"), str),
                "SOURCES.json.files rows must be JSON objects with a string path; offending row: " + brief(row))
        require(row.get("usage") in ("input", "provenance"),
                "SOURCES.json.files row " + row["path"] + " must declare usage \"input\" or \"provenance\"; found "
                + brief(row.get("usage")))
    undeclared = sorted({r["path"] for r in sources["files"] if r["usage"] == "input"} - set(inputs))
    require(not undeclared,
            "every SOURCES.json files row with usage \"input\" must also be declared in VERIFY.json inputs"
            + " (they drive CI invalidation); undeclared: " + ", ".join(undeclared))
    if check_pins:
        catalog_name = "docs/research/agent-task-catalog.json"
        require(catalog_name in {r["path"] for r in sources["files"]},
                "SOURCES.json.files must pin the originating task catalogue " + catalog_name
                + " (a provenance row pinned at base_commit)")
        names = [r["path"] for r in sources["files"]]
        for name in names:
            p = PurePosixPath(name)
            require(not p.is_absolute() and ".." not in p.parts, "invalid source path")
        specs = [source_pin(row, sources["base_commit"]) for row in sources["files"]]
        require(all(spec == sources["base_commit"] + ":" + catalog_name
                    for name, spec in zip(names, specs) if name == catalog_name),
                "originating task catalogue must be pinned at base_commit")
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
        require(len(cards) == 1,
                "TASK.json task_id " + brief(task["task_id"]) + " matches " + str(len(cards))
                + " cards in pinned " + catalog_name + " at base_commit " + sources["base_commit"]
                + "; need exactly one")
        original_card = require_key(task, "original_card", "TASK.json",
                                    "the pinned catalogue card object (copy --print-card output verbatim)")
        if original_card != cards[0]:
            raise ValueError("original card in TASK.json must equal the pinned catalogue card object exactly; "
                             "copy it verbatim from " + catalog_name + " at base_commit " + sources["base_commit"]
                             + ": " + card_differences(original_card, cards[0]))
    return task, manifest


def catalogue_card(root, package, task_id):
    """The exact original_card object a hand-authored TASK.json must copy.

    Reads the catalogue blob pinned at the package base commit, never the
    working tree, because validate() compares original_card against that pin.
    """
    sources = json.loads(relative_file(root, package + "/SOURCES.json").read_text(encoding="utf-8"))
    name = "docs/research/agent-task-catalog.json"
    rows = require_key(sources, "files", "SOURCES.json")
    row = next((r for r in rows if isinstance(r, dict) and r.get("path") == name), None)
    require(row is not None, "SOURCES.json.files must pin the originating task catalogue " + name)
    base = require_key(sources, "base_commit", "SOURCES.json", "a 40-64 hex string pinning an exact base commit")
    spec = source_pin(row, base)
    require(spec == base + ":" + name, "originating task catalogue must be pinned at base_commit")
    catalog = json.loads(git(root, "show", spec))
    cards = [t for tr in catalog["tracks"] for t in tr["tasks"] if t["id"] == task_id]
    require(len(cards) == 1,
            "task_id " + brief(task_id) + " matches " + str(len(cards))
            + " cards in pinned " + name + " at base_commit " + base + "; need exactly one")
    return cards[0]


_WINDOWS_GATE = r"""
import ctypes
from ctypes import wintypes
import json
import subprocess
import sys
api = ctypes.WinDLL('kernel32', use_last_error=True)
api.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
api.OpenEventW.restype = wintypes.HANDLE
api.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
api.WaitForSingleObject.restype = wintypes.DWORD
api.CloseHandle.argtypes = [wintypes.HANDLE]
api.CloseHandle.restype = wintypes.BOOL
event = api.OpenEventW(0x00100000, False, sys.argv[1])
if not event:
    raise ctypes.WinError(ctypes.get_last_error())
try:
    if api.WaitForSingleObject(event, 30000) != 0:
        raise RuntimeError('replay ownership gate was not released')
finally:
    api.CloseHandle(event)
# No verification command or descendant starts until the parent owns this job.
sys.exit(subprocess.call(json.loads(sys.argv[2])))
"""

def run_windows_command(argv, cwd, timeout, env):
    """Own ordinary verification descendants even after their leader exits.

    The gated launcher joins a kill-on-close Job Object before it may spawn
    the requested command. A late taskkill cannot recover an exited leader's
    tree. Job handles are not inherited and breakaway is not enabled.
    """
    import ctypes
    from ctypes import wintypes
    import time
    import uuid

    class BasicLimits(ctypes.Structure):
        _fields_ = [("ProcessTime", ctypes.c_int64), ("JobTime", ctypes.c_int64),
                    ("Flags", wintypes.DWORD), ("MinWorkingSet", ctypes.c_size_t),
                    ("MaxWorkingSet", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("Priority", wintypes.DWORD),
                    ("Scheduling", wintypes.DWORD)]

    class IOCounts(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("ReadOps", "WriteOps", "OtherOps", "ReadBytes", "WriteBytes", "OtherBytes")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [("Basic", BasicLimits), ("IO", IOCounts),
                    ("ProcessMemory", ctypes.c_size_t), ("JobMemory", ctypes.c_size_t),
                    ("PeakProcessMemory", ctypes.c_size_t), ("PeakJobMemory", ctypes.c_size_t)]

    class Accounting(ctypes.Structure):
        _fields_ = [(name, ctypes.c_int64) for name in
                    ("UserTime", "KernelTime", "PeriodUserTime", "PeriodKernelTime")] + [
                    (name, wintypes.DWORD) for name in
                    ("PageFaults", "TotalProcesses", "ActiveProcesses", "TerminatedProcesses")]

    api = ctypes.WinDLL("kernel32", use_last_error=True)

    def native(name, result, *arguments):
        fn = getattr(api, name)
        fn.restype, fn.argtypes = result, arguments
        return fn

    handle, dword, boolean = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL
    create_job = native("CreateJobObjectW", handle, ctypes.c_void_p, wintypes.LPCWSTR)
    set_info = native("SetInformationJobObject", boolean, handle, ctypes.c_int, ctypes.c_void_p, dword)
    assign = native("AssignProcessToJobObject", boolean, handle, handle)
    terminate = native("TerminateJobObject", boolean, handle, wintypes.UINT)
    query = native("QueryInformationJobObject", boolean, handle, ctypes.c_int,
                   ctypes.c_void_p, dword, ctypes.c_void_p)
    create_event = native("CreateEventW", handle, ctypes.c_void_p, boolean, boolean, wintypes.LPCWSTR)
    set_event = native("SetEvent", boolean, handle)
    close = native("CloseHandle", boolean, handle)

    def checked(ok):
        if not ok:
            raise ctypes.WinError(ctypes.get_last_error())
        return ok

    job = checked(create_job(None, None))
    event, process, assigned = None, None, False
    try:
        limits = ExtendedLimits()
        limits.Basic.Flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        checked(set_info(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)))
        name = "Local\\research-replay-" + uuid.uuid4().hex
        event = checked(create_event(None, True, False, name))
        # A name collision must not attach to an already-signaled event.
        if ctypes.get_last_error() == 183:
            raise ValueError("replay ownership gate name already exists")
        process = subprocess.Popen(
            # The gate itself must not run sitecustomize/PYTHONPATH startup
            # code before ownership. The requested command retains env/argv.
            # Windows accepts Unicode argv directly. ASCII JSON escaping can
            # expand an otherwise valid command past its UTF-16 launch limit.
            [sys.executable, "-I", "-S", "-c", _WINDOWS_GATE, name,
             json.dumps(argv, ensure_ascii=False)],
            cwd=cwd, env=env, start_new_session=True)
        checked(assign(job, int(process._handle)))
        assigned = True
        checked(set_event(event))
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ValueError("verification timed out") from None
    finally:
        try:
            if process is not None:
                if assigned:
                    checked(terminate(job, 1))
                    # Termination is asynchronous. Require the job to report
                    # no active processes before releasing its ownership handle.
                    deadline = time.monotonic() + 10
                    while True:
                        state = Accounting()
                        checked(query(job, 1, ctypes.byref(state), ctypes.sizeof(state), None))
                        if not state.ActiveProcesses:
                            break
                        if time.monotonic() >= deadline:
                            raise ValueError("verification process cleanup timed out")
                        time.sleep(0.01)
                elif process.poll() is None:
                    # Assignment failed before the gate opened: no command child
                    # exists, so only this known gated launcher needs stopping.
                    process.kill()
                process.wait(timeout=10)
        finally:
            try:
                if event:
                    checked(close(event))
            finally:
                checked(close(job))

def run_command(argv, cwd, timeout):
    # Assertion checks must not disappear because of the caller's environment.
    # Keep explicit manifest options (including deliberate -O controls) intact.
    # PYTHONPATH precedes the standard library on a child's sys.path, so a stray
    # same-named module could end a verifier with exit code 0 before any check.
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    # Ambient inspection can turn a verifier exception into a successful REPL
    # exit at terminal EOF. Keep explicit -i and the caller's stdin unchanged.
    env.pop("PYTHONINSPECT", None)
    env.pop("PYTHONPATH", None)
    if os.name == "nt":
        code = run_windows_command(argv, cwd, timeout, env)
        require(code == 0, f"verification command exited {code}")
        return
    previous_handler = None
    terminating = False
    waiting = False
    process = None

    def terminate(signum, frame):
        nonlocal terminating
        if not terminating:
            terminating = True
            # Only interrupt the protected wait. Launch/assignment and cleanup
            # defer delivery; repeated signals cannot interrupt group cleanup.
            if waiting:
                raise SystemExit(128 + signum)

    # Own a group for POSIX cleanup of this command and its descendants.
    try:
        if (threading.current_thread() is threading.main_thread()
                and signal.getsignal(signal.SIGTERM) == signal.SIG_DFL):
            previous_handler = signal.SIG_DFL
            signal.signal(signal.SIGTERM, terminate)
        if terminating:
            raise SystemExit(143)
        process = subprocess.Popen(argv, cwd=cwd, env=env, start_new_session=True)
        try:
            try:
                waiting = True
                if terminating:
                    raise SystemExit(143)
                code = process.wait(timeout=timeout)
            finally:
                waiting = False
        except subprocess.TimeoutExpired:
            raise ValueError("verification timed out") from None
        require(code == 0, f"verification command exited {code}")
    finally:
        try:
            if process is not None:
                if hasattr(os, "killpg"):
                    # The leader may have exited while descendants hold its group.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                elif process.poll() is None:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
                process.wait()
        finally:
            if previous_handler is not None:
                signal.signal(signal.SIGTERM, previous_handler)
    if terminating:
        raise SystemExit(143)


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
    # Coverage labels are UTF-8 metadata but a redirected Windows stdout may
    # use cp1252. Escape unrepresentable display characters instead of aborting
    # before replay. This changes only our stream, not child encoding or env.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    for command in manifest["commands"]:
        argv = [sys.executable if item == "{python}" else item.replace("{package}", package) for item in command["argv"]]
        print("CHECK " + command["checks"], flush=True)
        run_python_replay(argv, root, command["timeout_seconds"])
    print("PASS_REGISTERED_RESEARCH_PACKAGE " + package + " outcome=" + task["outcome"])


def planning_manifests(root, tracked):
    """Include deliberate sparse omissions without disguising deletions or drift.

    The fallback follows the chooser's PR3102 contract: one stage-zero regular
    skip-worktree index entry must match the exact HEAD mode and blob. This is
    declaration discovery only, not permission to replay absent package code.
    """
    committed = {name for name in tracked
                 if name.startswith("research/") and name.count("/") == 2
                 and name.endswith("/VERIFY.json")}
    # Explicit scandir retains error detection; only an absent directory is OK.
    try:
        with os.scandir(root / "research") as entries:
            local = {Path(entry.path) / "VERIFY.json" for entry in entries}
    except FileNotFoundError:
        local = set()
    present, missing = {}, set()
    for path in sorted(local | {root / name for name in committed}):
        name = path.relative_to(root).as_posix()
        symlink_free_relative_path(root, name)
        try:
            mode = path.lstat().st_mode
        except (FileNotFoundError, NotADirectoryError):
            if name in committed:
                missing.add(name)
            continue
        require(stat.S_ISREG(mode), "non-regular replay manifest: " + name)
        present[name] = path
    fallback = {}
    if missing:
        indexed, objects = {}, {}
        for record in git(root, "ls-files", "-t", "--stage", "-z", "--", "research").split(b"\0"):
            if not record:
                continue
            header, raw_name = record.split(b"\t", 1)
            name = raw_name.decode("utf-8")
            if name in missing:
                indexed.setdefault(name, []).append(header.split())
        for record in git(root, "ls-tree", "-r", "-z", "HEAD", "--", "research").split(b"\0"):
            if not record:
                continue
            header, raw_name = record.split(b"\t", 1)
            name = raw_name.decode("utf-8")
            if name in missing:
                objects[name] = header.split()
        for name in sorted(missing):
            metadata = objects.get(name, [])
            require(len(metadata) == 3 and metadata[0] in (b"100644", b"100755")
                    and metadata[1] == b"blob"
                    and indexed.get(name) == [[b"S", metadata[0], metadata[2], b"0"]],
                    "missing replay manifest is not an unchanged sparse HEAD input: " + name
                    + "; materialize it or commit its intended deletion")
            # A regular file occupying the package directory is not an omission.
            require(not (root / name).parent.exists() or (root / name).parent.is_dir(),
                    "non-directory replay package: " + name)
        names = sorted(missing)
        with closing(git_blobs(root, [objects[n][2].decode("ascii") for n in names])) as rows:
            for (oid, raw), name in zip(rows, names):
                require(oid.encode("ascii") == objects[name][2], "sparse manifest blob mismatch: " + name)
                fallback[name] = raw
    # Preserve Path's component ordering: package "a" precedes "a-extra".
    for name in sorted(present.keys() | fallback.keys(), key=lambda name: PurePosixPath(name).parts):
        yield root / name, fallback[name] if name in fallback else present[name].read_bytes(), name in fallback


def plan_details(root, changed):
    """One selection pass with exact causes; no replay or acceptance decision."""
    changed = set(changed)
    # A removed input is absent from HEAD, including an old case-only rename
    # spelling on case-insensitive filesystems. Git's exact changed paths remain
    # eligible so its consumer is selected, rather than rejected or skipped.
    head_tracked = tracked_input_paths(root)
    tracked = head_tracked | changed
    replay_changed = sorted(changed.intersection({
        "scripts/research_package.py", ".github/workflows/research-packages.yml",
        ".github/workflows/research-package-batch.yml"}))
    # Group literal Git paths once. Keep removed paths and exact spellings.
    changed_packages = {}
    for name in sorted(changed):
        parts = name.split("/", 2)
        if len(parts) == 3 and parts[0] == "research":
            changed_packages.setdefault("/".join(parts[:2]), []).append(name)
    packages = []
    sparse_count = 0
    for path, raw, sparse in planning_manifests(root, head_tracked):
        sparse_count += sparse
        package = path.parent.relative_to(root).as_posix()
        manifest = json.loads(raw.decode("utf-8"))
        # Parse only for selection; validate fully in the isolated replay job.
        inputs = manifest.get("inputs", [])
        require(isinstance(inputs, list), "declare input paths for CI invalidation")
        for name in inputs:
            # Do not require existence: a deleted input must still trigger replay.
            symlink_free_relative_path(root, name)
            require_tracked_input(name, tracked)
        causes = {
            "declared_inputs": sorted(changed.intersection(inputs)),
            "package_files": changed_packages.get(package, []),
            "shared_controls": replay_changed,
        }
        if any(causes.values()):
            packages.append({"package": package, "causes": causes,
                             "manifest_sha256": hashlib.sha256(raw).hexdigest()})
    if sparse_count:
        print(f"Planning includes {sparse_count} unchanged sparse manifests from HEAD; "
              "materialize packages and inputs before replay.", file=sys.stderr)
    return packages


def plan(root, changed):
    return [row["package"] for row in plan_details(root, changed)]


def write_plan_explanation(path, base, head, changed, details):
    """Publish a complete sidecar before stdout/GitHub matrix publication."""
    matched = {name for row in details for names in row["causes"].values() for name in names}
    report = {
        "schema_version": 1, "base": base, "head": head,
        "mode": "all-tracked" if base is None else "commit-diff",
        "scope": "Selection from working or authenticated sparse HEAD manifests, not replay or mathematical acceptance. "
                 "Manifest hashes bind the declarations read; checkout must remain stable.",
        "changed_paths": sorted(set(changed) - {""}), "selected": details,
        "unmatched_paths": sorted(set(changed) - matched - {""}),
    }
    fd, temporary = tempfile.mkstemp(prefix=".replay-plan-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def replay_matrix(packages, batch_size=None):
    """Retain the flat CLI format, or group complete coverage into bounded matrices."""
    if batch_size is None:
        return {"include": [{"package": p} for p in packages]}
    require(type(batch_size) is int and 1 <= batch_size <= 256,
            "matrix batch size must be 1..256")
    batches = [packages[i:i + batch_size] for i in range(0, len(packages), batch_size)]
    require(len(batches) <= 256,
            "more than 256 matrix batches required; no packages were truncated")
    return {"include": [{"packages": batch} for batch in batches]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--print-card", metavar="TASK_ID",
                    help="print the exact pinned catalogue card object to copy into TASK.json original_card")
    ap.add_argument("--install-deps", action="store_true", help="explicit opt-in to install manifest's allowed pinned dependencies")
    ap.add_argument("--changed-since", help="plan affected opt-in packages relative to this Git commit")
    ap.add_argument("--github-output", type=Path)
    ap.add_argument("--explain-plan", type=Path,
                    help="write exact replay-selection causes to JSON; matrix output stays unchanged")
    ap.add_argument("--matrix-batch-size", type=int,
                    help="group planned packages for bounded reusable-workflow matrices (1..256)")
    args = ap.parse_args()
    if args.explain_plan and (not args.changed_since or args.package or args.print_card):
        ap.error("--explain-plan requires --changed-since without --package or --print-card")
    if args.explain_plan and args.github_output and args.explain_plan.resolve() == args.github_output.resolve():
        ap.error("--explain-plan and --github-output must use different files")
    try:
        if args.print_card:
            require(args.package,
                    "--print-card needs --package research/<slug> to resolve its pinned catalogue")
            sys.stdout.write(json.dumps(catalogue_card(ROOT, args.package, args.print_card), indent=2) + "\n")
        elif args.changed_since:
            if set(args.changed_since) == {"0"}:
                base = None
                changed = git(ROOT, "ls-files", "-z").decode().split("\0")
            else:
                base = git(ROOT, "rev-parse", "--verify", args.changed_since + "^{commit}").decode().strip()
                # A rename must invalidate both the removed input and its new path.
                changed = git(ROOT, "diff", "--no-renames", "--name-only", "-z", base, "HEAD").decode().split("\0")
            details = plan_details(ROOT, changed)
            packages = [row["package"] for row in details]
            matrix = json.dumps(replay_matrix(packages, args.matrix_batch_size))
            if args.explain_plan:
                head = git(ROOT, "rev-parse", "--verify", "HEAD^{commit}").decode().strip()
                write_plan_explanation(args.explain_plan, base, head, changed, details)
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
            ap.error("use --package, --print-card or --changed-since")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, importlib.metadata.PackageNotFoundError) as exc:
        ap.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
