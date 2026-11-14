#!/usr/bin/env python3
"""Read-only sparse-machine and parity-union-find switch review.

Standard library. No author hardware, verifier, direct arithmetic evaluator,
or canonical compiler is imported; only the frozen emitted graph is consumed.
An optional package directory argument supports portable replay.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys

B, LEFT, END = 2, 3, 4
GRAPH_SHA = "320daab199a5528d1e7c273c719b6787c01629ff6160cb01fb9c959e87c7b1d8"
SOURCE_SHA = "89fe721a2920943dbc58eefe7f855ac1573e653e8af3b029c9c2ef838fdeac40"

def need(condition, message):
    if not condition:
        raise RuntimeError(message)

def load_graph(directory):
    path = directory / "switch.py"
    if path.exists():
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == SOURCE_SHA, "fixed source changed")
        namespace = {"__name__": "reviewed_fixed_constructor"}
        exec(compile(raw, str(path), "exec"), namespace)
        code, labels = namespace["compile_query"]()
    else:
        record = json.loads((directory / "GRAPH.json").read_text())
        code, labels = record["code"], record["labels"]
        code = [tuple(ins) for ins in code]
        code = [(ins[0], ins[1], {int(k): v for k, v in ins[2].items()})
                if ins[0] == "R" else ins for ins in code]
    digest = sha256(json.dumps(code, separators=(",", ":"), sort_keys=True).encode()).hexdigest()
    need(digest == GRAPH_SHA and len(code) == 2096, "fixed graph changed")
    for ins in code:
        op = ins[0]
        need(op in ("R", "W", "M", "J", "H"), "nonliteral instruction")
        if op in ("R", "W", "M"):
            need(0 <= ins[1] < 14, "tape role outside ABI")
        if op == "R":
            need(set(ins[2]) == set(range(5)), "incomplete fixed alphabet")
            need(all(0 <= t < len(code) for t in ins[2].values()), "read target")
        elif op == "W":
            need(ins[1] >= 5 and ins[2] in range(5), "borrowed/nonfixed write")
        elif op == "M":
            need(ins[2] in (-1, 1), "nonunit motion")
        elif op == "J":
            need(0 <= ins[1] < len(code), "jump target")
        else:
            need(ins[1] in ("DONE", "REJECT"), "unknown halt")
    return code, labels

def canonical_network(permutation):
    """Canonical colors from input/output pair constraints, not source DFS."""
    n = len(permutation)
    need(n >= 2 and n & (n - 1) == 0, "dyadic oracle domain")
    need(sorted(permutation) == list(range(n)), "oracle permutation")
    if n == 2:
        return [(0, (permutation[0], permutation[0]))]
    parent, parity = list(range(n)), [0] * n
    def find(x):
        value = 0
        while parent[x] != x:
            value ^= parity[x]
            x = parent[x]
        return x, value
    def constrain(x, y):
        rx, px = find(x)
        ry, py = find(y)
        if rx == ry:
            need(px ^ py == 1, "odd canonical coloring cycle")
        else:
            parent[ry] = rx
            parity[ry] = px ^ py ^ 1
    for x in range(0, n, 2):
        constrain(x, x + 1)
    pairs = [[] for _ in range(n // 2)]
    for x, image in enumerate(permutation):
        pairs[image // 2].append(x)
    for pair in pairs:
        need(len(pair) == 2, "output pair degree")
        constrain(*pair)
    anchors, color = {}, []
    for x in range(n):
        root, value = find(x)
        if root not in anchors:
            anchors[root] = value
        color.append(value ^ anchors[root])
    first = tuple(color[x] ^ (x & 1) for x in range(n))
    last = [0] * n
    children = [[None] * (n // 2) for _ in range(2)]
    for x, image in enumerate(permutation):
        last[image] = color[x] ^ (image & 1)
        need(children[color[x]][x // 2] is None, "child input collision")
        children[color[x]][x // 2] = image // 2
    left, right = [canonical_network(child) for child in children]
    result = [(0, first)]
    for a, b in zip(left, right):
        need(a[0] == b[0], "child axis mismatch")
        result.append((a[0] + 1, tuple((a, b)[x & 1][1][x // 2] for x in range(n))))
    result.append((0, tuple(last)))
    for axis, table in result:
        need(all(table[x] == table[x ^ (1 << axis)] for x in range(n)),
             "oracle control depends on switched bit")
    for start in range(n):
        current = start
        for axis, table in result:
            current ^= table[current] << axis
        need(current == permutation[start], "independent network endpoint")
    return result

def rotation_network(h, s, a):
    n = 1 << h
    return canonical_network([(x + a) % s if x < s else x for x in range(n)])

def word(value, width):
    need(0 <= value < 1 << width, "fixture integer outside width")
    return [(value // (1 << i)) % 2 for i in range(width)]

class FrameViolation(RuntimeError):
    pass

def execute(code, labels, h, s, a, j, x, expected, override=None, missing_guard=False):
    """One sparse map, literal instructions, translated negative owner origins."""
    origins = [-37 - 19 * role for role in range(14)]
    height = word(h, max(1, h.bit_length()))
    bodies = {0: height, 1: word(s, h + 1), 2: word(a, h + 1),
              3: word(j, h + 1), 4: word(x, h + 1)}
    bodies.update(override or {})
    maximum = [len(bodies[t]) for t in range(5)] + [1]
    maximum += [max(h + 2, len(bodies[0]) + 1)] * 8
    memory = {}
    for role in range(14):
        origin = origins[role]
        memory[role, origin - 2] = 41
        memory[role, origin + maximum[role] + 1] = 43
        if role < 6:
            memory[role, origin - 1] = LEFT
    for role, body in bodies.items():
        for offset, symbol in enumerate(body):
            if symbol != B:
                memory[role, origins[role] + offset] = symbol
    if missing_guard:
        del memory[0, origins[0] - 1]
    initial = memory.copy()
    heads = origins.copy()
    low, high = origins.copy(), origins.copy()
    writes = [0] * 14
    guard_writes = [[] for _ in range(14)]
    opcounts, visited = Counter(), set()
    pc = steps = loops = 0
    limit = 1024 * (h + 3) ** 2
    while True:
        need(steps < limit, "explicit step bill exceeded")
        need(0 <= pc < len(code), "program counter escaped fixed graph")
        visited.add(pc)
        if pc == labels["query_loop"]:
            loops += 1
        instruction = code[pc]
        op = instruction[0]
        opcounts[op] += 1
        steps += 1
        pc += 1
        if op in ("R", "W", "M"):
            role = instruction[1]
            if not origins[role] - 1 <= heads[role] <= origins[role] + maximum[role]:
                raise FrameViolation("owner boundary crossed")
        if op == "R":
            symbol = memory.get((role, heads[role]), B)
            if symbol not in instruction[2]:
                raise FrameViolation("opaque exterior read")
            pc = instruction[2][symbol]
        elif op == "W":
            symbol = instruction[2]
            writes[role] += 1
            if heads[role] == origins[role] - 1:
                guard_writes[role].append(symbol)
            key = role, heads[role]
            if symbol == B:
                memory.pop(key, None)
            else:
                memory[key] = symbol
        elif op == "M":
            heads[role] += instruction[2]
            low[role] = min(low[role], heads[role])
            high[role] = max(high[role], heads[role])
            if not origins[role] - 1 <= heads[role] <= origins[role] + maximum[role]:
                raise FrameViolation("unit move crossed owner boundary")
        elif op == "J":
            pc = instruction[1]
        elif op == "H":
            outcome = instruction[1]
            break
        else:
            raise RuntimeError("nonliteral opcode")
    need(heads == origins, "not every physical head returned")
    need(all(count == 0 for count in writes[:5]), "borrowed input was written")
    need(all(not history for history in guard_writes[:6]), "permanent guard modified")
    need(all(history == [LEFT, B] for history in guard_writes[6:]),
         "private guard not installed then erased exactly once")
    intended = initial.copy()
    if expected is None:
        need(outcome == "REJECT" and writes[5] == 0, "malformed/domain input accepted")
    else:
        need(outcome == "DONE" and writes[5] == 1, "valid query failed")
        intended[5, origins[5]] = expected
        need(loops <= h, "child descent exceeds height")
    need(memory == intended, "full sparse owner state differs from specified return")
    history = sum(b - a + 1 for a, b in zip(low, high))
    if expected is not None:
        need(history == 11 * h + 2 * h.bit_length() + 48,
             "exact successful owner history changed")
        need(history < 16 * (h + 4), "linear history cap exceeded")
    return {"steps": steps, "history": history, "loops": loops,
            "outcome": outcome, "visited": visited, "opcounts": dict(opcounts)}

def main():
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    code, labels = load_graph(directory)
    union = set()
    calls = networks = total_steps = max_steps = 0
    def record(run):
        nonlocal total_steps, max_steps
        union.update(run["visited"])
        total_steps += run["steps"]
        max_steps = max(max_steps, run["steps"])
    for h in range(1, 4):
        for s in range(1, (1 << h) + 1):
            for a in range(s):
                oracle = rotation_network(h, s, a)
                networks += 1
                for j, (_, row) in enumerate(oracle):
                    for x, bit in enumerate(row):
                        record(execute(code, labels, h, s, a, j, x, bit))
                        calls += 1
    need((networks, calls) == (49, 1566), "small domain coverage changed")
    key_bits = bytearray()
    for a in range(17):
        row = rotation_network(5, 17, a)[6][1]
        for x, bit in enumerate(row):
            record(execute(code, labels, 5, 17, a, 6, x, bit))
            key_bits.append(bit)
    key_digest = sha256(key_bits).hexdigest()
    need(len(key_bits) == 544 and key_digest ==
         "bc0ab563e6d8fdfa24ee89b50dbe3f9a3a6f23681f491e883c6b5aeef07d4104",
         "required independently colored row fingerprint differs")
    # A half turn preserves each lower input bit, recursively remains a half
    # turn, and swaps only the final axis. No exponential network is built.
    deep = []
    for h in (13, 37, 97):
        run = execute(code, labels, h, 1 << h, 1 << (h - 1), h - 1,
                      (1 << h) - 1, 1)
        record(run)
        need(run["loops"] == h, "half-turn fixture did not reach full depth")
        deep.append({k: v for k, v in run.items() if k not in ("visited", "opcounts")} | {"h": h})
    malformed = [
        ("height_zero", (0, 1, 0, 0, 0), None),
        ("size_zero", (3, 0, 0, 0, 0), None),
        ("size_above_cube", (3, 9, 0, 0, 0), None),
        ("offset_equals_size", (3, 5, 5, 0, 0), None),
        ("row_above_last", (3, 5, 1, 5, 0), None),
        ("wire_above_cube", (3, 5, 1, 0, 8), None),
        ("height_empty", (3, 5, 1, 0, 0), {0: []}),
        ("height_noncanonical", (3, 5, 1, 0, 0), {0: [1, 0]}),
        ("height_end_symbol", (3, 5, 1, 0, 0), {0: [END]}),
        ("row_end_symbol", (3, 5, 1, 0, 0), {3: [END, 0, 0, 0]}),
        ("size_short", (3, 5, 1, 0, 0), {1: [1, 0, 1]}),
        ("offset_long", (3, 5, 1, 0, 0), {2: [1, 0, 0, 0, 0]}),
    ]
    rejected = []
    for name, arguments, override in malformed:
        run = execute(code, labels, *arguments, None, override=override)
        record(run)
        rejected.append({"name": name, "steps": run["steps"], "history": run["history"]})
    # Mutate the *emitted table*, independently of the author's mutation API.
    mutant = list(code)
    changed = []
    for pc in range(labels["interior"], labels["child_reduce"]):
        ins = mutant[pc]
        if ins[0] == "R" and ins[1] == 11:
            branches = dict(ins[2])
            branches[0], branches[1] = branches[1], branches[0]
            mutant[pc] = ("R", 11, branches)
            changed.append(pc)
    need(len(changed) == 4, "child-parity mutation missed fixed branches")
    args = (3, 5, 1, 1, 5)
    expected = rotation_network(*args[:3])[args[3]][1][args[4]]
    need(expected == 1, "independent mutation witness changed")
    wrong = execute(mutant, labels, *args, 0)
    need(wrong["outcome"] == "DONE", "mutant is not a returning semantic failure")
    try:
        execute(code, labels, 3, 5, 1, 1, 5, 1, missing_guard=True)
    except FrameViolation:
        outside = "missing permanent LEFT leaves promised owner window; outside ABI"
    else:
        raise RuntimeError("outside-ABI missing-guard control was silently accepted")
    result = {
        "status": "PASS", "source_sha256": SOURCE_SHA,
        "graph_sha256": GRAPH_SHA, "locations": len(code), "tapes": 14,
        "interpreter": "independent single sparse map with negative translated owner origins",
        "oracle": "independent parity-union-find canonical coloring and full route verification",
        "small_networks": networks, "small_queries": calls,
        "required_h5_s17_j6_queries": len(key_bits), "required_row_sha256": key_digest,
        "full_depth_half_turns": deep, "clean_rejection_controls": rejected,
        "returning_child_parity_mutant": {"arguments": args, "correct": expected,
            "returned": 0, "changed_locations": changed, "steps": wrong["steps"],
            "history": wrong["history"], "heads_and_private_state_restored": True},
        "outside_abi_control": outside,
        "all_locations_static_validation": True,
        "normal_graph_dynamic_locations": len(union),
        "normal_graph_complete_steps": total_steps,
        "largest_normal_run_steps": max_steps,
        "claims": "finite independent replay; universal result rests on separately reviewed proof",
    }
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
