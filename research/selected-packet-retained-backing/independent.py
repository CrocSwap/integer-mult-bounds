#!/usr/bin/env python3
"""Independent retained-root cut check; deterministic stdout, no output files.

Runs authenticated literal packet_engine.run, Tape, read_prefix, Counter and
copy_bits. Only the layout, event stream and length-preserving action interface
are fixtures. In particular the alias action is an interface control, not a claim
that the selected arithmetic trace has an alias-returning primitive.
"""
from __future__ import annotations

import hashlib
import importlib.abc
import importlib.util
import itertools
import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PIN = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
SNAPSHOT_SHA256 = "a9f623f4971232daccb39091b51294d9cd09fe07af054184edc4f3bd7a51008e"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest_bytes = (HERE / "SNAPSHOTS.json").read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == SNAPSHOT_SHA256,
            "fixed SNAPSHOTS.json raw SHA-256")
    manifest = json.loads(manifest_bytes)
    require(manifest["source_head"] == PIN, "fixed source commit")
    modules = {}
    for entry in manifest["files"]:
        path = HERE / entry["path"]
        data = path.read_bytes()
        require(entry["commit"] == PIN, "entry source commit: " + entry["path"])
        require(hashlib.sha256(data).hexdigest() == entry["sha256"],
                "entry SHA-256: " + entry["path"])
        git_blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(git_blob).hexdigest() == entry["blob"],
                "entry Git blob: " + entry["path"])
        if path.suffix == ".py":
            require(path.stem not in modules, "unique source module: " + path.stem)
            modules[path.stem] = (path, data)
    return len(manifest["files"]), modules


class PinnedImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Compile only authenticated in-memory bytes; bypass .pyc and module cache."""

    def __init__(self, sources):
        self.sources = sources
        self.previous = {}

    def __enter__(self):
        self.previous = {name: sys.modules.pop(name)
                         for name in self.sources if name in sys.modules}
        sys.meta_path.insert(0, self)
        return self

    def __exit__(self, *_):
        sys.meta_path.remove(self)
        for name in self.sources:
            sys.modules.pop(name, None)
        sys.modules.update(self.previous)

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.sources:
            return importlib.util.spec_from_loader(
                fullname, self, origin=str(self.sources[fullname][0]))
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path, data = self.sources[module.__name__]
        module.__file__ = str(path)
        # optimize=0 also preserves any acceptance checks in the source module,
        # independently of how the outer interpreter was invoked.
        exec(compile(data, str(path), "exec", dont_inherit=True, optimize=0),
             module.__dict__)


def main():
    authenticated, modules = authenticate()
    with PinnedImporter(modules):
        run_checks(authenticated)


def run_checks(authenticated):
    import packet_engine
    from cardinal_counts import Count
    from packet import read_prefix as literal_read_prefix
    from records import RECORD_END, Tape
    from words import BLANK, ZERO

    class LayoutFixture:
        def __init__(self, length):
            self.length = length

        def fibre(self):
            return Count.literal(self.length)

    controls = {name: 0 for name in (
        "count_source_current_twice", "discard_cleared_payload_roots",
        "discard_previous_fields", "discard_preflight_first",
        "clear_shrinks_backing", "forget_stale_state_at_new_primitive",
        "always_count_changed_separately", "always_alias_changed_local",
        "omit_left_markers")}
    cases = cuts = initial_cuts = boundary_cuts = 0
    fresh_stale = alias_stale = 0

    for n, fibre, header, source_pad, directory_pad, modes in itertools.product(
            (1, 2, 3), (1, 2, 7), (1, 2, 5), (0, 9), (0, 5),
            itertools.product(("fresh", "alias"), repeat=3)):
        source, directory = Tape(), Tape()
        for _ in range(n * fibre):
            source.append(ZERO)
        source.cells.extend([BLANK] * source_pad)
        source.rewind()
        for _ in range(n):
            for _ in range(header - 1):
                directory.append(ZERO)
            directory.append(RECORD_END)
        directory.cells.extend([BLANK] * directory_pad)
        directory.rewind()
        prefix_count, field_count = Count.literal(n), Count.literal(1)
        # Consumer.apply retains first after frame.close(); first.clear(). This
        # fixture reproduces that exact retained tape, not the numeric callback.
        first = literal_read_prefix(directory, field_count)
        directory.rewind()
        first.clear()
        k, d, q = len(source.cells), len(directory.cells), header + 1
        require(len(first.cells) == q and first.read() == BLANK,
                "cleared preflight prefix retains its full backing")
        seen = 0

        def action_fixture(local, event, _layout, _coefficient, factory):
            if event.mode == "alias":
                return local
            result = factory()
            for _ in range(fibre):
                result.append(local.read())
                local.step(1)
            require(local.read() == BLANK, "complete fresh-result fixture input")
            result.rewind()
            return result

        def read_at_cut(the_directory, the_field_count):
            nonlocal seen, cuts, initial_cuts, boundary_cuts
            nonlocal fresh_stale, alias_stale
            fresh = literal_read_prefix(the_directory, the_field_count)
            # The caller has not yet assigned this fresh return value to fields.
            roots = sys._getframe(1).f_locals
            t, j = divmod(seen, n)
            initial = t == 0 and j == 0
            payload = [roots[name] for name in
                       ("source", "current", "output", "local", "changed")
                       if roots.get(name) is not None]
            fields = [the_directory, first, fresh]
            if "fields" in roots:
                fields.append(roots["fields"])
            all_roots = payload + fields
            arrays = {id(tape.cells): tape.cells for tape in all_roots}
            observed = sum(map(len, arrays.values()))
            payload_arrays = {id(tape.cells): tape.cells for tape in payload}
            field_arrays = {id(tape.cells): tape.cells for tape in fields}
            require(set(payload_arrays).isdisjoint(field_arrays),
                    "payload and field arrays are distinct")
            require(roots["source"] is source, "borrowed source identity")
            require((roots["current"] is source) == (t == 0),
                    "current/source alias occurs exactly in the first primitive")
            require(len(roots["output"].cells) == j * fibre + 1,
                    "partially completed output backing")
            require(len(fresh.cells) == q, "fresh field-prefix backing")
            if initial:
                require("fields" not in roots and "local" not in roots,
                        "initial cut has no stale field or local roots")
                require("changed" not in roots,
                        "initial cut has no stale changed root")
                expected_payload, expected_fields = k + 1, d + 2 * q
                initial_cuts += 1
            else:
                previous_mode = modes[t] if j else modes[t - 1]
                extra_changed = int(previous_mode == "fresh")
                require((roots["changed"] is not roots["local"]) == bool(extra_changed),
                        "last completed action determines stale alias relation")
                for name in ("local", "changed", "fields"):
                    require(roots[name].read() == BLANK, "cleared stale " + name)
                require(len(roots["local"].cells) == fibre + 1,
                        "stale local retained backing")
                require(len(roots["changed"].cells) == fibre + 1,
                        "stale changed retained backing")
                require(len(roots["fields"].cells) == q,
                        "stale field-prefix retained backing")
                expected_payload = (k + (n * fibre + 1 if t else 0)
                                    + j * fibre + 1
                                    + (1 + extra_changed) * (fibre + 1))
                expected_fields = d + 3 * q
                fresh_stale += extra_changed
                alias_stale += 1 - extra_changed
                if t and j == 0:
                    boundary_cuts += 1
            require(sum(map(len, payload_arrays.values())) == expected_payload,
                    "independently derived payload root sum")
            require(sum(map(len, field_arrays.values())) == expected_fields,
                    "independently derived field root sum")
            require(observed == expected_payload + expected_fields,
                    "simultaneous identity-aware root sum")

            def reject(name, estimate, applies=True):
                if applies:
                    require(estimate != observed, "reject accounting defect: " + name)
                    controls[name] += 1

            reject("count_source_current_twice",
                   sum(len(t.cells) for t in (roots["source"], roots["current"]))
                   + observed - sum(len(a) for a in
                       {id(t.cells): t.cells for t in
                        (roots["source"], roots["current"])}.values()), t == 0)
            reject("discard_preflight_first", observed - q)
            reject("omit_left_markers", observed - len(arrays))
            cleared = {id(t.cells): t.cells for t in [first] +
                       ([] if initial else [roots[x] for x in
                                           ("fields", "local", "changed")])}
            reject("clear_shrinks_backing", observed - sum(len(a) - 1
                                                         for a in cleared.values()))
            if not initial:
                stale_payload = {id(roots[x].cells): roots[x].cells
                                 for x in ("local", "changed")}
                reject("discard_cleared_payload_roots",
                       observed - sum(map(len, stale_payload.values())))
                reject("discard_previous_fields", observed - q)
                reject("forget_stale_state_at_new_primitive",
                       observed - q - sum(map(len, stale_payload.values())),
                       t > 0 and j == 0)
                reject("always_count_changed_separately", observed + fibre + 1,
                       previous_mode == "alias")
                reject("always_alias_changed_local", observed - fibre - 1,
                       previous_mode == "fresh")
            cuts += 1
            seen += 1
            return fresh

        saved_action, saved_reader = packet_engine.action, packet_engine.read_prefix
        try:
            packet_engine.action = action_fixture
            packet_engine.read_prefix = read_at_cut
            events = (SimpleNamespace(kind="fixture", mode=mode) for mode in modes)
            result = packet_engine.run(source, events, LayoutFixture(fibre), directory,
                                       prefix_count, field_count, lambda *_: None)
            require(seen == 3 * n, "every expected cut observed")
            require(len(result.cells) == n * fibre + 1, "complete final packet backing")
            require(len(source.cells) == k and source.head == 1,
                    "borrowed source backing and restored head")
        finally:
            packet_engine.action, packet_engine.read_prefix = saved_action, saved_reader
            prefix_count.close()
            field_count.close()
        cases += 1

    require(all(controls.values()), "every defect control has nonempty coverage")
    print(json.dumps({
        "status": "PASS", "source_head": PIN,
        "snapshot_sha256": SNAPSHOT_SHA256,
        "authenticated_files": authenticated,
        "cases": cases, "cuts": cuts,
        "initial_cuts": initial_cuts,
        "later_primitive_first_prefix_cuts": boundary_cuts,
        "fresh_changed_stale_cuts": fresh_stale,
        "alias_changed_stale_cuts": alias_stale,
        "defect_controls": controls,
        "domain": {"N": [1, 2, 3], "F": [1, 2, 7],
                   "header_symbols": [1, 2, 5], "source_padding": [0, 9],
                   "directory_padding": [0, 5], "primitive_count": 3,
                   "action_modes": "all eight fresh/alias words of length three"},
        "scope": "Literal engine and tapes with fixture layout/events/action; retained root lengths only"
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
