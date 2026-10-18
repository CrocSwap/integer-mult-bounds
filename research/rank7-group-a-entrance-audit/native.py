# SPDX-License-Identifier: Apache-2.0
"""Bind emitted mixed-entrance wrappers, then check them with the retained exact kernel.

Recipe generation follows DreamingOfClouds/PR458's bw_adapters.py. It is a
producer, not independent evidence. The separately implemented Gaussian kernel
is Sagar Thakrar's retained verifier; neither predecessor is new here.
"""

import copy
import os
import subprocess
import sys
from common import COMPILER, ENGINE, HELPERS, KERNEL, W, data, decode, digest
from common import encoded, module, reject, require


def bind_program_receipts(programs, checks):
    require(set(programs) == set(checks) == {"forward", "backward"},
            "both emitted orientations")
    for orientation, events in programs.items():
        row = checks[orientation]
        require(row["events"] == len(events) and
                row["sha256"] == digest(encoded(events)[:-1]),
                "event stream digest in pinned receipt")


def generate(blobs, tag, work):
    tools = work / "tools"
    tools.mkdir()
    for name in ("bw_transport.py", "bw_emit.py"):
        (tools / name).write_bytes(blobs[ENGINE + name])
    word = work / "WORD.json.gz"
    word.write_bytes(blobs[f"research/rank7-joint-endframes/data/WORD-{tag}.json.gz"])
    output = work / "local"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONOPTIMIZE", None)
    for script, args in (("bw_transport.py", [word, output]), ("bw_emit.py", [output])):
        run = subprocess.run([sys.executable, "-I", "-B", str(tools / script),
                              *map(str, args)], env=env, capture_output=True,
                             text=True, timeout=120, check=False)
        require(run.returncode == 0, script + ": " + run.stderr[-2000:])
    receipt = data(blobs, "evidence/FULL-NATIVE-RECEIPT.json")["providers"][tag]
    checks = (output / "LOCAL-CHECKS.json").read_bytes()
    require(digest(checks) == receipt["complete_native_files"]["local/LOCAL-CHECKS.json"],
            "emitted program receipt")
    canonical = decode((output / "CANONICAL-WORD.json.gz").read_bytes(), True)
    programs = decode((output / "LOCAL-PROGRAMS.json.gz").read_bytes(), True)
    bind_program_receipts(programs, decode(checks))
    return canonical, programs, digest(checks)


def adapter_file(compiler, canonical):
    """Reconstruct the original serialized file; its exact source receipt must match."""
    frames = canonical["frames"]
    pairs = {(canonical["start"][r], canonical["final"][r])
             for r in range(224, 632)}
    recipes, warps = {}, {}
    for e, u in sorted(pairs):
        if u == 1 and e == 0:
            continue
        entrance, terminal = frames[e], frames[u]
        op = compiler.canonical_frame(9, tuple(entrance)).adjoint().then(
            compiler.canonical_frame(9, tuple(terminal)))
        rec, _ = compiler.lower_child(op)
        row = dict(frame=e, vectors=entrance, entrance_rank=len(entrance),
                   rank=rec["rank"], left=rec["left"], right=rec["right"])
        key = str(e)
        if u != 1:
            row.update(terminal=u, terminal_vectors=terminal, terminal_rank=len(terminal))
            key = f"{e}:{u}"
        recipes[key] = row
    for w in canonical["warps"]:
        columns = tuple(w["G_columns"])
        matrix = compiler.transpose(columns, 9)
        inverse_columns = compiler.transpose(compiler.inv(matrix, 9), 9)
        q = tuple((1 << i) ^ sum(compiler.parity(a & b) << j
                  for j, b in enumerate(inverse_columns))
                  for i, a in enumerate(inverse_columns))
        op = compiler.perm(9, matrix).then(compiler.diag(9, q))
        _, rec = compiler.monomial(op)
        warps[str(w["op"])] = dict(op=w["op"], from_frame=w["from_frame"],
            to_frame=w["to_frame"], G_columns=w["G_columns"], K=rec)
    return decode(encoded(dict(status="RESIDUAL_ADAPTER_RECIPES", recipes=recipes, warps=warps)))


def conjugate(circuit):
    out = []
    for gate in circuit:
        if gate[0] == "C":
            out.append(("C", gate[1], -gate[2]))
        elif gate[0] == "D":
            out.append(("D", gate[1], [-a % 4 for a in gate[2]]))
        elif gate[0] == "PH":
            out.append(("PH", -gate[1] % 4))
        else:
            require(gate[0] in ("P", "X"), "real monomial primitive")
            out.append(gate)
    return out


def check_recipe(kernel, rec, entrance, terminal):
    width = len(terminal) - len(entrance)
    require(type(rec["rank"]) is int and rec["rank"] == width, "entrance-relative width")
    require(kernel.well_formed(rec["left"]) and
            (rec["right"] is None or kernel.well_formed(rec["right"])),
            "serialized monomials")
    left = kernel.monomial(rec["left"])
    right = [] if rec["right"] is None else kernel.monomial(rec["right"])
    reference = kernel.adjoint(kernel.canonical_frame(entrance)) + kernel.canonical_frame(terminal)
    candidate = right + kernel.fourier(width) + left
    wrapped = kernel.adjoint(right) + reference + kernel.adjoint(left)
    require(kernel.same_operator(candidate, reference), "phase-exact all-column residual")
    require(kernel.same_operator(wrapped, kernel.fourier(width)), "wrapped coordinate factor")
    require(kernel.same_operator(conjugate(wrapped), kernel.fourier(width, -1)),
            "inverse-transpose coordinate factor")
    return {"rank": width, "columns": 512, "orientations": 2,
            "spectator_axes": 9 - width, "recipe": rec}


def source_events(word, helper):
    """Reconstruct all direct scalar clocks and climbs from the original word."""
    private = 704 + helper
    touched = {helper, private}
    for section in ("precondition", "compensation", "cut"):
        require(all(not (touched & set(g[1:3] if g[0] == "add" else g[1:2]))
                    for g in word[section]), "no uncovered direct source section")
    require(all(not (touched & {c["source"], c["target"]})
                for c in word["initial_corrections"]), "no uncovered direct correction")
    require(all(w[1] != helper for w in word["warps"]), "no direct lender warp")
    scalars, climbs = [], []
    current = word["start_extra"].get(str(helper), [])
    for section, phase in (("A", "A"), ("B", "B"), ("restore", "cleanup_tail"),
                           ("cleanup", "full_frame_cleanup")):
        clock = 0
        for gate in word[section]:
            regs = gate[1:3] if gate[0] == "add" else gate[1:2]
            if touched & set(regs):
                require(gate[0] in ("add", "scale"), "no direct source warp")
                if helper in regs and current != gate[-1]:
                    climbs.append([phase, clock, current, gate[-1], len(gate[-1]) - len(current)])
                    current = gate[-1]
                scalars.append([phase, clock, gate[:-1], gate[-1]])
            clock += gate[0] != "warp"
    require(current == W, "source reaches the terminal frame")
    return scalars, climbs


def scalar_original(operation, kept, backward):
    require(operation[0] in ("add", "scale", "copy", "clear"), "known emitted scalar")
    count = 2 if operation[0] in ("add", "copy") else 1
    regs = []
    for kind, r in operation[1:1 + count]:
        require(kind in ("L", "Z", "C"), "register namespace")
        regs.append(-1 if kind == "C" else kept[r] + (704 if kind == "Z" else 0))
    row = [operation[0], *regs, *operation[1 + count:]]
    if backward and row[0] == "add":
        row[1], row[2], row[3] = row[2], row[1], -row[3]
    elif backward and row[0] == "scale":
        row[2], row[3] = row[3], row[2]
    return row, regs


def emitted_binding(word, canonical, stream, helper, backward=False):
    """A separate boundary check: entrance pair, climbs, cleanup lifetime and wrappers."""
    kept = [r for r in range(704) if r not in word["removed"]]
    require(canonical["helper_origin"] == kept[224:], "original-to-compact binding")
    r = kept.index(helper)
    e, u = canonical["start"][r], canonical["final"][r]
    entrance = word["start_extra"].get(str(helper), [])
    require(canonical["frames"][e] == entrance and canonical["frames"][u] == W,
            "literal entrance/terminal pair")
    wrappers, buffers, climbs, private_uses, scalars, climb_clocks = [], [], [], [], [], []
    scalar_indices = []
    phase, clock = None, 0
    for i, event in enumerate(stream):
        if event[0] == "phase":
            phase, clock = event[1], 0
        elif event[0] == "residual_adapter" and event[2] == r:
            require(event[3:] == [e, u], "emitted wrapper pair")
            wrappers.append([i, event[1]])
        elif event[0] == "zero_buffer" and event[2] == r:
            buffers.append([i, event[1]])
        elif event[0] == "climb" and event[2] == r:
            old, new = (canonical["frames"][f] for f in event[3:5])
            require(event[5] == len(new) - len(old) > 0, "emitted climb rank")
            climbs.append({"index": i, "old": old, "new": new, "rank": event[5]})
            climb_clocks.append([phase, clock, old, new, event[5]])
        elif event[0] == "scalar":
            row, regs = scalar_original(event[1], kept, backward)
            if helper in regs or helper + 704 in regs:
                scalars.append([phase, clock, row, canonical["frames"][event[2]]])
                scalar_indices.append(i)
            if ["Z", r] in event[1][1:3]:
                private_uses.append(i)
            clock += 1
        elif event[0] == "warp":
            require(event[1] not in (["L", r], ["Z", r]), "no unaccounted direct warp")
        elif event[0] == "adapter":
            require(event[2] != r, "ordinary adapter cannot replace residual wrapper")
    expected_scalars, expected_climbs = source_events(word, helper)
    require(scalars == expected_scalars and climb_clocks == expected_climbs,
            "source-to-emission direct scalar/climb clocks")
    require([x[1] for x in wrappers] == ["pre", "post"], "two residual wrappers")
    require([x[1] for x in buffers] == ["alloc", "free"], "private lifetime")
    require(private_uses and wrappers[0][0] < buffers[0][0] < min(private_uses)
            <= max(private_uses) < buffers[1][0] < wrappers[1][0], "cleanup before post-wrapper")
    require(r in canonical["zero_buffers"], "private buffer counted")
    current = entrance
    for climb in climbs:
        require(climb["old"] == current, "complete direct climb chain")
        current = climb["new"]
    require(current == W and sum(c["rank"] for c in climbs) == len(W) - len(entrance),
            "complete entrance-relative path")
    return {"compact_helper": r, "recipe_key": f"{e}:{u}", "entrance": entrance,
            "terminal": W, "wrappers": wrappers, "buffers": buffers,
            "private_uses": private_uses, "climbs": climbs,
            "direct_scalar_count": len(scalars), "direct_scalar_indices": scalar_indices,
            "direct_scalar_sha256": digest(encoded(scalars))}


def audit(blobs, tag, work):
    compiler = module(blobs[COMPILER], "group_a_source_compiler")
    kernel = module(blobs[KERNEL], "group_a_independent_kernel")
    canonical, programs, checks_sha = generate(blobs, tag, work)
    adapters = adapter_file(compiler, canonical)
    expected = data(blobs, "evidence/FULL-NATIVE-RECEIPT.json")["providers"][tag]
    require(digest(encoded(adapters)) == expected["complete_native_files"]["local/RESIDUAL-ADAPTERS.json"],
            "complete serialized adapter source receipt")
    word = data(blobs, f"data/WORD-{tag}.json.gz")
    bindings, recipes, climb_recipes = {}, {}, {}
    for h in HELPERS:
        bindings[str(h)] = {orientation: emitted_binding(word, canonical, stream, h, orientation == "backward")
                           for orientation, stream in programs.items()}
        row = bindings[str(h)]["forward"]
        key = row["recipe_key"]
        if key not in recipes:
            recipes[key] = check_recipe(kernel, adapters["recipes"][key], row["entrance"], W)
        for climb in row["climbs"]:
            old, new = climb["old"], climb["new"]
            identity = encoded([old, new]).decode().strip()
            if identity not in climb_recipes:
                op = compiler.canonical_frame(9, tuple(old)).adjoint().then(
                    compiler.canonical_frame(9, tuple(new)))
                candidate, _ = compiler.lower_child(op)
                candidate = decode(encoded(candidate))
                climb_recipes[identity] = check_recipe(kernel, candidate, old, new)
    entering = bindings["450"]["forward"]["recipe_key"]
    cold = bindings["331"]["forward"]["recipe_key"]
    rec = adapters["recipes"][entering]
    controls = {}
    controls["omitted_entrance"] = reject(lambda: check_recipe(kernel, rec, [], W), "entrance")
    bad = copy.deepcopy(rec); bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    controls["phase"] = reject(lambda: check_recipe(kernel, bad, [30], W), "phase")
    bad = copy.deepcopy(rec); bad["right"] = adapters["recipes"][cold]["right"]
    controls["cold_wrapper_alias"] = reject(lambda: check_recipe(kernel, bad, [30], W), "cold alias")
    # A same-rank wrong entrance tests operator semantics, rather than metadata alone.
    controls["wrong_entrance_line"] = reject(lambda: check_recipe(kernel, rec, [10], W), "wrong line")
    parent = data(blobs, f"data/PARENT-{tag}.json.gz")
    comparison = {}
    for h in (331, 450):
        entrance = parent["start_extra"].get(str(h), [])
        terminal = parent["helper_final"][str(h)]
        require(len(terminal) == 8, "rank-eight parent terminal")
        op = compiler.canonical_frame(9, tuple(entrance)).adjoint().then(
            compiler.canonical_frame(9, tuple(terminal)))
        candidate, _ = compiler.lower_child(op)
        comparison[str(h)] = {"entrance": entrance, "parent_terminal": terminal,
            "parent": check_recipe(kernel, decode(encoded(candidate)), entrance, terminal),
            "joint_recipe_key": cold if h == 331 else entering}
    require(all(parent["start_extra"][str(h)] == [30] and
                parent["helper_final"][str(h)] == comparison["450"]["parent_terminal"]
                for h in HELPERS[1:]), "four common entering parent pairs")
    return {"local_checks_sha256": checks_sha, "adapter_sha256": digest(encoded(adapters)),
            "bindings": bindings, "residuals": recipes, "climb_recipes": climb_recipes,
            "parent_residual_comparison": comparison, "controls": controls}
