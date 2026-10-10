#!/usr/bin/env python3
"""Offline, allowlisted Lean source checking and resumable isolated compilation.

No downloads, scientific regeneration or existing-object adoption. --check-only
validates inputs; only --build invokes Lean. The installed pinned standard library
is a stated toolchain trust boundary, not a theorem of this checker.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import resource
import subprocess
import sys
import time

POLICY = "maintainer-darwin-uncapped-subset-v1"
ALLOWED_AXIOMS = {"propext", "Quot.sound", "Classical.choice"}
NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
AUDIT = re.compile(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)\s*$", re.M)


class CheckError(RuntimeError):
    pass


def need(condition, message):
    if not condition:
        raise CheckError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return digest(path.read_bytes())


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def relative_file(root, name):
    p = PurePosixPath(name)
    need(not p.is_absolute() and ".." not in p.parts and "\\" not in name,
         f"Unsafe source path: {name}")
    full = (root / p).resolve()
    need(full.is_relative_to(root.resolve()), f"Source escapes root: {name}")
    need(full.is_file(), f"Missing accepted source: {name}")
    return full


def uncomment(text):
    """Strip nested Lean comments, preserving lines and quoted strings."""
    out, i, depth, quoted = [], 0, 0, False
    tokens = re.compile(r'/\-|\-/|--|"')
    while i < len(text):
        if not depth and not quoted:
            token = tokens.search(text, i)
            if token is None:
                out.append(text[i:]); break
            out.append(text[i:token.start()]); i = token.start()
        pair = text[i:i + 2]
        if depth:
            if pair == "/-": depth += 1; i += 2
            elif pair == "-/": depth -= 1; i += 2
            else:
                out.append("\n" if text[i] == "\n" else " "); i += 1
        elif quoted:
            out.append(text[i])
            if text[i] == "\\" and i + 1 < len(text):
                i += 1; out.append(text[i])
            elif text[i] == '"': quoted = False
            i += 1
        elif pair == "/-": depth = 1; out.append(" "); i += 2
        elif pair == "--":
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
        else:
            out.append(text[i]); quoted = text[i] == '"'; i += 1
    need(depth == 0 and not quoted, "Unterminated comment or string")
    return "".join(out)


def source_commands(text):
    code = uncomment(text)
    imports, prints = [], []
    for line in code.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            imports.extend(stripped.split()[1:])
        if stripped.startswith("#print axioms "):
            prints.append(stripped[len("#print axioms "):].strip())
    need(all(NAME.fullmatch(x) for x in imports + prints), "Unsupported import/audit syntax")
    return imports, prints


def load_plan(map_path, source_root):
    raw = map_path.read_bytes()
    plan = json.loads(raw)
    records = plan["modules"]
    need(isinstance(records, list) and records, "Empty accepted module map")
    for item in plan.get("scientific_inputs", []):
        pinned = relative_file(source_root, item["path"])
        need(file_hash(pinned) == item["sha256"], f"Changed scientific input: {item['path']}")
    by_name, by_path = {}, set()
    for m in records:
        name = m["module"]
        need(bool(NAME.fullmatch(name)), f"Invalid module name: {name}")
        need(name not in by_name and m["source"] not in by_path, f"Duplicate module/source: {name}")
        source = relative_file(source_root, m["source"])
        data = source.read_bytes()
        need(digest(data) == m["source_sha256"], f"Changed accepted source: {name}")
        imports, prints = source_commands(data.decode("utf-8"))
        need(imports == m["imports"], f"Import map differs: {name}")
        need(prints == m["expected_axiom_commands"], f"Axiom command map differs: {name}")
        need(len(prints) == m["declarations"] and len(set(prints)) == len(prints),
             f"Incomplete/duplicate declaration map: {name}")
        cap = m.get("timeout_seconds", 60)
        need(type(cap) is int and 0 < cap <= 300, f"Invalid recorded timeout: {name}")
        by_name[name] = dict(m, resolved_source=source)
        by_path.add(m["source"])
    external = set(plan["external_imports"])
    need(all(x in {"Lean", "Init"} or x.startswith(("Lean.", "Init.")) for x in external),
         "Non-core external imports require a separate explicit dependency contract")
    dependencies = {}
    for name, m in by_name.items():
        need(set(m["imports"]) <= set(by_name) | external, f"Missing accepted dependency: {name}")
        dependencies[name] = [x for x in m["imports"] if x in by_name]
    order, done = [], set()
    while len(done) != len(by_name):
        ready = sorted(n for n in by_name.keys() - done if set(dependencies[n]) <= done)
        need(ready, "Cyclic accepted imports")
        order.extend(ready); done.update(ready)
    need(len(by_name) == plan["accepted_module_count"], "Module count differs")
    need(sum(m["declarations"] for m in records) == plan["accepted_declarations"], "Declaration count differs")
    return plan, by_name, dependencies, order, digest(raw)


def selected_order(requested, dependencies, order):
    if not requested: return order
    wanted, todo = set(), list(requested)
    while todo:
        name = todo.pop()
        need(name in dependencies, f"Unknown requested module: {name}")
        if name not in wanted:
            wanted.add(name); todo.extend(dependencies[name])
    return [x for x in order if x in wanted]


def audit_output(output, expected):
    rows = AUDIT.findall(output)
    names = [name for name, _ in rows]
    need(len(names) == len(set(names)), "Duplicate axiom audit output")
    need(set(names) == set(expected) and len(names) == len(expected), "Missing or unexpected axiom audits")
    axioms = {a.strip() for _, text in rows for a in text.split(",") if a.strip()}
    need(axioms <= ALLOWED_AXIOMS, f"Disallowed transitive axioms: {sorted(axioms - ALLOWED_AXIOMS)}")
    return dict(declarations=len(rows), axiom_free=sum(not x for _, x in rows), axioms=sorted(axioms))


@contextlib.contextmanager
def compiler_slot(directory, wait_limit=600):
    if directory is None:
        yield None
        return
    need(directory.is_dir(), "Shared compiler slot directory is missing")
    handles = [open(directory / f"compile-slot-{i}.lock", "a+") for i in range(2)]
    slot, start = None, time.monotonic()
    try:
        while slot is None:
            for i, h in enumerate(handles):
                try:
                    fcntl.flock(h, fcntl.LOCK_EX | fcntl.LOCK_NB); slot = i; break
                except BlockingIOError: pass
            need(slot is not None or time.monotonic() - start < wait_limit, "Compiler slots remained busy")
            if slot is None: time.sleep(0.25)
        yield slot
    finally:
        if slot is not None: fcntl.flock(handles[slot], fcntl.LOCK_UN)
        for h in handles: h.close()


def toolchain_identity(lean):
    need(lean.is_file(), "Pinned compiler is missing")
    p = subprocess.run([str(lean), "--version"], capture_output=True, text=True, timeout=10)
    need(p.returncode == 0 and "version 4.21.0," in p.stdout and "commit 6741444a63ee" in p.stdout,
         "Wrong Lean version/commit")
    return dict(version=p.stdout.strip(), executable_sha256=file_hash(lean),
                standard_library_trust="Installed official Lean4.21.0 standard library; not rebuilt by this driver")


def resume_valid(receipt, key, obj, log, expected):
    try:
        if receipt.get("status") != "PASS" or receipt.get("build_key") != key: return False
        if file_hash(obj) != receipt["object_sha256"] or file_hash(log) != receipt["log_sha256"]: return False
        audit_output(log.read_text(), expected)
        return True
    except (OSError, KeyError, CheckError): return False


def compile_one(m, output, dependencies, compiler, lean, map_hash, timeout, slot_dir, resume):
    name = m["module"]
    object_path = output / "objects" / (name.replace(".", "/") + ".olean")
    source_path = output / "sources" / (name.replace(".", "/") + ".lean")
    log_path = output / "logs" / (name + ".log")
    receipt_path = output / "receipts" / (name + ".json")
    for p in [object_path, source_path, log_path, receipt_path]: p.parent.mkdir(parents=True, exist_ok=True)
    key = dict(policy=POLICY, compiler=compiler, source_sha256=m["source_sha256"],
               expected_axiom_commands=m["expected_axiom_commands"], imports=m["imports"],
               dependencies=dependencies, timeout_seconds=timeout, address_space_bytes=None,
               lean_jobs=1, lean_stack_kib=65536, allowed_axioms=sorted(ALLOWED_AXIOMS))
    if resume and receipt_path.exists():
        old = json.loads(receipt_path.read_text())
        if resume_valid(old, key, object_path, log_path, m["expected_axiom_commands"]):
            return old, True
    data = m["resolved_source"].read_bytes()
    need(digest(data) == m["source_sha256"], f"Source changed during build: {name}")
    source_path.write_bytes(data)
    temporary = object_path.with_suffix(".olean.tmp")
    env = os.environ.copy()
    for variable in ["LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT"]: env.pop(variable, None)
    env["LEAN_PATH"] = str(output / "objects")
    command = [str(lean), "-s", "65536", "-j", "1", "-o", str(temporary), str(source_path)]
    started = time.monotonic()
    base = dict(module=name, build_key=key, map_sha256_when_built=map_hash, status="FAILED", compiler_exit=None)
    with compiler_slot(slot_dir) as slot:
        base["compiler_slot"] = slot
        compile_started = time.monotonic()
        try:
            result = subprocess.run(command, cwd=output / "sources", env=env, capture_output=True, text=True,
                                    timeout=timeout)
            text = result.stdout + result.stderr
            base["compiler_exit"] = result.returncode
        except subprocess.TimeoutExpired as exc:
            def decode(x): return x.decode(errors="replace") if isinstance(x, bytes) else x or ""
            text = decode(exc.stdout) + decode(exc.stderr) + f"\nTIMEOUT after {timeout} seconds\n"
            log_path.write_text(text); base.update(status="TIMEOUT", log_sha256=file_hash(log_path))
            atomic_json(receipt_path, base)
            raise CheckError(f"Compilation timed out: {name}") from exc
    log_path.write_text(text)
    base.update(elapsed_seconds=time.monotonic() - compile_started, total_including_queue_seconds=time.monotonic() - started,
                log_sha256=file_hash(log_path))
    try:
        need(result.returncode == 0, f"Lean compilation failed: {name}; see {log_path}")
        audit = audit_output(text, m["expected_axiom_commands"])
        need(temporary.is_file(), f"Compiler emitted no object: {name}")
        temporary.replace(object_path)
        base.update(status="PASS", object_sha256=file_hash(object_path), audit=audit)
        atomic_json(receipt_path, base)
    except CheckError:
        atomic_json(receipt_path, base)
        if temporary.exists(): temporary.unlink()
        raise
    return base, False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check-only", action="store_true")
    modes.add_argument("--build", action="store_true")
    parser.add_argument("--module", action="append", default=[])
    parser.add_argument("--lean", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--slot-dir", type=Path)
    parser.add_argument("--timeout-cap", type=int, default=300, help="Can lower, never raise the recorded per-module cap")
    args = parser.parse_args(argv)
    need(0 < args.timeout_cap <= 300, "Timeout cap must be between1 and300 seconds")
    plan, modules, dependencies, order, map_hash = load_plan(args.map, args.source_root)
    selected = selected_order(args.module, dependencies, order)
    summary = dict(status="INPUTS_CHECKED_ONLY", kernel_compiled=False, map_sha256=map_hash,
                   accepted_modules=len(modules), selected_modules=len(selected), source_commit=plan.get("target_commit"),
                   selected_declarations=sum(modules[n]["declarations"] for n in selected))
    if args.check_only:
        print(json.dumps(summary, indent=2)); return 0
    need(args.lean is not None and args.output is not None, "Build requires --lean and --output")
    output = args.output.resolve(); root = args.source_root.resolve()
    need(output != root and not root.is_relative_to(output), "Output must be isolated from source-root")
    need(not any(m["resolved_source"].is_relative_to(output) for m in modules.values()), "Output contains an accepted source")
    output.mkdir(parents=True, exist_ok=True)
    lock = open(output / "build.lock", "a+")
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc: raise CheckError("Another build uses this output directory") from exc
    compiler = toolchain_identity(args.lean.resolve())
    done, rebuilt, reused = {}, [], []
    try:
        for name in selected:
            dep_hashes = {n: done[n]["object_sha256"] for n in dependencies[name]}
            timeout = min(args.timeout_cap, modules[name].get("timeout_seconds", 60))
            receipt, was_reused = compile_one(modules[name], output, dep_hashes, compiler, args.lean.resolve(),
                                             map_hash, timeout, args.slot_dir, args.resume)
            done[name] = receipt
            (reused if was_reused else rebuilt).append(name)
            print(json.dumps(dict(module=name, status="REUSED_AUDITED" if was_reused else "COMPILED_AUDITED")), flush=True)
        summary.update(status="FULL_ACCEPTED_SET_COMPILED" if len(selected) == len(modules) else "SELECTED_MODULES_COMPILED",
                       kernel_compiled=True, full_accepted_set=len(selected) == len(modules), rebuilt=rebuilt, reused=reused,
                       compiler=compiler, receipts={n:digest(json.dumps(v,sort_keys=True).encode()) for n,v in done.items()})
        atomic_json(output / "SUMMARY.json", summary)
        print(json.dumps(summary, indent=2)); return 0
    except BaseException:
        atomic_json(output / "SUMMARY.json", dict(summary, status="INCOMPLETE_BUILD", completed_modules=list(done)))
        raise
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()


if __name__ == "__main__":
    try: sys.exit(main())
    except (CheckError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); sys.exit(1)
