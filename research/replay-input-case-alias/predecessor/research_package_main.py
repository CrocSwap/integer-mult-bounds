#!/usr/bin/env python3
"""Validate and replay explicitly registered research packages, never every verify.py.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from contextlib import closing
from itertools import chain
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


class _UnsupportedNulBatch(Exception):
    """Git rejected the initial NUL-mode request before yielding any source."""


def _git_blob_batch(root, specs, nul):
    argv = ["git", "cat-file", "--batch"] + (["-z"] if nul else [])
    # Usage diagnostics from the unsupported-option probe are expected. Avoid
    # a second pipe that could block while we consume the framed stdout reply.
    with subprocess.Popen(argv, cwd=root, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
        try:
            for index, spec in enumerate(specs):
                require("\0" not in spec, "invalid Git object request")
                request = spec
                if not nul and ("\n" in spec or "\r" in spec):
                    # Resolve one literal argument, never split a path into requests.
                    request = git(root, "rev-parse", "--verify", "--end-of-options", spec).decode("ascii").strip()
                    require(re.fullmatch(r"[0-9a-f]{40,64}", request), "invalid Git object ID")
                try:
                    process.stdin.write(request.encode("utf-8") + (b"\0" if nul else b"\n"))
                    process.stdin.flush()
                except BrokenPipeError:
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
            # Option rejection can close stdin before our first write/flush.
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
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
    match = re.fullmatch(r"head:([0-9a-f]{40}):(.+)", pin) if isinstance(pin, str) else None
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
    names = [item.split("==")[0] for item in requirements]
    require(len(names) == len(set(names)), "declare only one version per dependency")
    # Validation already treats an omitted list as empty; execution must receive
    # that same default without rewriting the contributor's manifest on disk.
    manifest["requirements"] = requirements
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
    undeclared = sorted({r["path"] for r in sources["files"] if r["usage"] == "input"} - set(inputs))
    require(not undeclared,
            "SOURCES.json input pins must be declared in VERIFY.json inputs; undeclared: " + ", ".join(undeclared))
    if check_pins:
        catalog_name = "docs/research/agent-task-catalog.json"
        require(catalog_name in {r["path"] for r in sources["files"]}, "pin the originating task catalogue")
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
        if task["original_card"] != cards[0]:
            raise ValueError("original card in TASK.json must equal the pinned catalogue card object exactly; "
                             "copy it verbatim from " + catalog_name + " at base_commit " + sources["base_commit"]
                             + ": " + card_differences(task["original_card"], cards[0]))
    return task, manifest


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
            [sys.executable, "-I", "-S", "-c", _WINDOWS_GATE, name, json.dumps(argv)],
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
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    if os.name == "nt":
        code = run_windows_command(argv, cwd, timeout, env)
        require(code == 0, f"verification command exited {code}")
        return
    # Own a group for POSIX cleanup of this command and its descendants.
    process = subprocess.Popen(argv, cwd=cwd, env=env, start_new_session=True)
    try:
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ValueError("verification timed out") from None
        require(code == 0, f"verification command exited {code}")
    finally:
        if hasattr(os, "killpg"):
            # The leader may have exited while descendants still hold the group.
            # Signal it on success, failure and interruption, not only timeout.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass  # A completely finished group needs no cleanup.
        elif process.poll() is None:
            # Windows taskkill can address the tree only while its leader exists.
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
        process.wait()


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


def plan(root, changed):
    changed = set(changed)
    replay_changed = bool(changed.intersection({
        "scripts/research_package.py", ".github/workflows/research-packages.yml",
        ".github/workflows/research-package-batch.yml"}))
    packages = []
    # glob suppresses scan errors, which can publish an incomplete replay matrix.
    # Inventory immediate children explicitly; only an absent opt-in is harmless.
    with os.scandir(root / "research") as entries:
        paths = sorted(Path(entry.path) / "VERIFY.json" for entry in entries)
    for path in paths:
        try:
            path.lstat()
        except (FileNotFoundError, NotADirectoryError):
            continue
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
    ap.add_argument("--install-deps", action="store_true", help="explicit opt-in to install manifest's allowed pinned dependencies")
    ap.add_argument("--changed-since", help="plan affected opt-in packages relative to this Git commit")
    ap.add_argument("--github-output", type=Path)
    ap.add_argument("--matrix-batch-size", type=int,
                    help="group planned packages for bounded reusable-workflow matrices (1..256)")
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
            matrix = json.dumps(replay_matrix(packages, args.matrix_batch_size))
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
