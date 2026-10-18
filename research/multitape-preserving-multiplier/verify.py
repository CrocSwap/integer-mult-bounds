"""Source inventory and independently replayed finite controls. Apache-2.0."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

def need(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()

def inventory(root):
    root = Path(root)
    pins = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and ".lake" not in p.relative_to(root).parts
              and "__pycache__" not in p.relative_to(root).parts
              and p.relative_to(root).as_posix() != "MANIFEST.json"}
    need(actual == set(pins), "exact package source inventory differs")
    for name, expected in pins.items():
        p = root / name
        need(not p.is_symlink() and p.resolve().is_relative_to(root.resolve()), "external source: " + name)
        need(digest(p) == expected, "source hash differs: " + name)
    return pins

def validate_audit(rows, expected_names, expected_modules):
    need(isinstance(rows, list) and rows, "empty declaration audit")
    names = [r.get("name") for r in rows]
    need(len(names) == len(set(names)), "duplicate declaration reports")
    need(set(names) == set(expected_names), "missing or unexpected declaration reports")
    need(all(r.get("module") in expected_modules for r in rows), "foreign defining module")
    need(set(r["module"] for r in rows) == set(expected_modules), "missing defining module coverage")
    for row in rows:
        need(row.get("kind") in {"theorem", "definition", "opaque", "axiom", "other"}, "missing declaration kind")
        need(row["kind"] != "axiom", "package declares its own axiom: " + row["name"])
        need(isinstance(row.get("axioms"), list), "missing axiom list")
        need(set(row["axioms"]) <= ALLOWED_AXIOMS, "unapproved dependency: " + row["name"])
    need(any(r["kind"] == "theorem" for r in rows), "no actual theorem audit")

def step(table, config):
    q, heads, cells = config
    scan = tuple(cells[i].get(heads[i], 0) for i in range(len(heads)))
    choice = table[(q, scan)]
    if choice is None:
        return None
    next_q, actions = choice
    new_cells = [dict(t) for t in cells]
    new_heads = list(heads)
    for i, (symbol, move) in enumerate(actions):
        need(move in (-1, 0, 1), "nonunit head movement")
        new_cells[i][heads[i]] = symbol
        new_heads[i] += move
    return next_q, tuple(new_heads), new_cells

def run(table, config, budget):
    current = deepcopy(config)
    footprints = [set() for _ in current[1]]
    for count in range(budget):
        successor = step(table, current)
        if successor is None:
            return count, current, footprints, True
        for i, head in enumerate(current[1]):
            footprints[i].add(head)
        current = successor
    return budget, current, footprints, step(table, current) is None

def finite_replay():
    # Complete finite tables, not a register machine or an assumed primitive.
    copy = {}
    for q, scan in product(range(2), product(range(4), repeat=3)):
        copy[(q, scan)] = None if q else (1, tuple((scan[0] if i == 1 else scan[i], 0) for i in range(3)))
    copies = 0
    for source, target, spectator, head in product(range(4), range(4), range(4), range(-2, 3)):
        initial = (0, (head, head + 2, head - 2),
                   [{head: source, head + 9: 3}, {head + 2: target, head + 11: 2},
                    {head - 2: spectator, head + 7: 1}])
        count, final, footprint, halted = run(copy, initial, 3)
        need(count == 1 and halted, "literal copy step/true halt")
        need(final[2][1][head + 2] == source, "actual copied symbol")
        need(final[1] == initial[1] and final[2][2] == initial[2][2], "dirty spectator preservation")
        for i in range(3):
            for x in range(head - 12, head + 13):
                if x not in footprint[i]:
                    need(final[2][i].get(x, 0) == initial[2][i].get(x, 0), "actual write footprint")
        copies += 1
    # A one-step stationary handoff is an actual step between the two copies.
    stages = {}
    for q, scan in product(range(4), product(range(4), repeat=3)):
        if q == 0:
            stages[(q, scan)] = (1, tuple((scan[0] if i == 1 else scan[i], 0) for i in range(3)))
        elif q == 1:
            stages[(q, scan)] = (2, tuple((scan[i], 0) for i in range(3)))
        elif q == 2:
            stages[(q, scan)] = (3, tuple((scan[1] if i == 0 else scan[i], 0) for i in range(3)))
        else:
            stages[(q, scan)] = None
    chains = 0
    for symbols in product(range(4), repeat=3):
        initial = (0, (0, 0, 0), [{0: b, 7: 3 - b} for b in symbols])
        count, final, _, halted = run(stages, initial, 4)
        need(count == 3 and halted, "paid sum of stage costs plus one handoff")
        need(final[2][0][0] == symbols[0] and final[2][1][0] == symbols[0], "pipeline semantics")
        need(final[2][2] == initial[2][2], "pipeline dirty spectator")
        chains += 1
    # Write BEFORE moving. Both directions and all symbols, on arbitrary dirty neighbours.
    motions = 0
    for old, new, direction, head in product(range(4), range(4), (-1, 0, 1), range(-3, 4)):
        table = {(0, (old,)): (1, ((new, direction),))}
        initial = (0, (head,), [{head: old, head - 1: 2, head + 1: 3}])
        final = step(table, initial)
        need(final[1][0] == head + direction and final[2][0][head] == new, "write/move order")
        for x in (head - 1, head + 1):
            need(final[2][0][x] == initial[2][0][x], "unscanned neighbour preserved")
        motions += 1
    # Terminal observations belong to the COMPLETED footprint even though a halt is not a step.
    table = {}
    for q, scan in product(range(2), product(range(2), repeat=1)):
        table[(q, scan)] = ((1, ((scan[0], 1),)) if q == 0 else
                            (None if scan[0] == 0 else (1, ((1, 1),))))
    initial = (0, (0,), [{0: 1, 1: 0}])
    dirty = (0, (0,), [{0: 1, 1: 1}])
    _, final, visited, halted = run(table, initial, 1)
    _, dirty_final, _, dirty_halted = run(table, dirty, 1)
    need(visited == [{0}] and halted and not dirty_halted, "terminal scan control")
    need(final[0:2] == dirty_final[0:2], "same executed trace with different halt observation")
    observed = visited[0] | {final[1][0]}
    need(observed == {0, 1}, "completed observation footprint")
    # A foreign tagged symbol must not masquerade as an element of another stack alphabet.
    tags = 0
    for stack in range(3):
        for length in range(5):
            for word in product(range(2), repeat=length):
                encoded = [(stack, a) for a in word]
                decoded = [a for tag, a in encoded if tag == stack]
                need(decoded == list(word), "typed output roundtrip")
                need(not [a for tag, a in encoded if tag == (stack + 1) % 3], "foreign tag exclusion")
                tags += 1
    return {"literal_dirty_copies": copies, "charged_two_stage_pipelines": chains,
            "write_before_move_cases": motions, "terminal_observation_fixture": 1,
            "typed_word_roundtrips": tags}

def audit_controls():
    good = [{"name": "MultitapeToolkit.fixture", "module": "MultitapeToolkit.Model", "kind": "theorem", "axioms": ["propext"]},
            {"name": "_private.MultitapeToolkit.Model.0.helper", "module": "MultitapeToolkit.Model", "kind": "theorem", "axioms": []}]
    expected = [r["name"] for r in good]
    modules = {"MultitapeToolkit.Model"}
    validate_audit(good, expected, modules)
    cases = [([], "zero reports"), (good[:1], "missing report"),
             (good + [good[0]], "duplicate report"),
             (good + [dict(good[0], name="MultitapeToolkit.extra")], "unexpected report"),
             ([dict(good[0], axioms=["sorryAx"]), good[1]], "unproved theorem"),
             ([dict(good[0], axioms=["arbitraryOracle"]), good[1]], "unproved oracle"),
             ([dict(r, kind="definition") for r in good], "no theorem"),
             ([dict(good[0], axioms=None), good[1]], "absent axiom list"),
             ([dict(good[0], kind="axiom", axioms=[]), good[1]], "forged empty own axiom"),
             ([dict(good[0], module="Foreign.Model"), good[1]], "foreign ownership"),
             ([dict(good[0], module="MultitapeToolkit.Trace"), good[1]], "unexpected module")]
    for rows, label in cases:
        try:
            validate_audit(rows, expected, modules)
        except (ValueError, TypeError):
            continue
        raise ValueError("accepted audit corruption: " + label)
    return len(cases)


"""Independent finite paired-copy controls. Apache-2.0; OpenAI Codex assistance.

These executable examples supplement the universal Lean theorem. They do not
certify Lean source equivalence, novelty, or the complete multiplication bound.
No third-party dependency, network request, service, model or solver is used.
"""
from itertools import product
import json
import random

SYMBOLS = (None, False, True)
STATES = ("enter", "scan", "rewind")


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def table(mutation=None):
    result = {}
    for state, scanned in product(STATES, product(SYMBOLS, repeat=4)):
        a, b, da, db = scanned
        if state == "enter":
            action = ("scan", scanned, (1, 1, 1, 1))
        elif state == "scan":
            if a is not None and b is not None:
                writes = (a, b, a, b)
                if mutation == "wrong_source":
                    writes = (a, b, b, b)
                if mutation == "missing_second_copy":
                    writes = (a, b, a, db)
                action = ("scan", writes, (1, 1, 1, 1))
            elif a is None and b is None:
                moves = (0, 0, 0, 0) if mutation == "missing_turn_left" else (-1, -1, -1, -1)
                action = ("rewind", scanned, moves)
            else:
                action = None
        elif a is not None and b is not None:
            moves = (1, 1, 1, 1) if mutation == "wrong_rewind" else (-1, -1, -1, -1)
            writes = (a, b, None, db) if mutation == "erase_on_rewind" else scanned
            action = ("rewind", writes, moves)
        elif mutation == "stutter_after_halt":
            action = ("rewind", scanned, (0, 0, 0, 0))
        else:
            action = None
        result[state, scanned] = action
    need(len(result) == 243, "incomplete three-state/four-tape finite table")
    return result


def literal_word(bits):
    return {i + 1: bit for i, bit in enumerate(bits)}


def execute(controller, left, right, spectators=()):
    """Native sparse interpreter; no high-level copy/rewind routine is called."""
    need(len(left) == len(right), "equal-length source contract required")
    source = [literal_word(left), literal_word(right)]
    cells = [dict(source[0]), dict(source[1]), {}, {}]
    heads = [0, 0, 0, 0]
    for position, dirty in spectators:
        heads.append(position)
        cells.append(dict(dirty))
    before = [dict(c) for c in cells]
    state, steps = "enter", 0
    limit = 2 * len(left) + 8
    while True:
        scanned = tuple(cells[i].get(heads[i]) for i in range(4))
        action = controller[state, scanned]
        if action is None:
            break
        need(steps < limit, "execution budget exceeded before genuine halt")
        following, writes, moves = action
        for i in range(4):
            if writes[i] is None:
                cells[i].pop(heads[i], None)
            else:
                cells[i][heads[i]] = writes[i]
            heads[i] += moves[i]
        # Check source integrity at every prefix, not only after restoration.
        need(cells[:2] == before[:2], "source changed during actual prefix")
        need(cells[4:] == before[4:], "dirty spectator changed during prefix")
        state, steps = following, steps + 1
    need(state == "rewind", "wrong terminal control")
    need(steps == 2 * len(left) + 2, "wrong actual transition count")
    need(heads[:4] == [0] * 4, "physical active head not restored")
    need(cells[:2] == source, "full literal source bank changed")
    need(cells[2:4] == source, "full destination bank differs from literal words")
    need(heads[4:] == [h for h, _ in spectators], "spectator head changed")
    need(cells[4:] == before[4:], "spectator cells changed")
    return steps


def verify():
    controller = table()
    exhaustive, transitions = 0, 0
    dirty = ((-7, {-100: True, -7: False, 0: True, 100: False}),
             (13, {-90: False, 13: True, 500: False}))
    for width in range(6):
        for joined in product((False, True), repeat=2 * width):
            transitions += execute(controller, joined[:width], joined[width:], dirty)
            exhaustive += 1
    rng = random.Random(20261015)
    long_cases = 0
    for width in (16, 31, 64, 257, 1024, 4096):
        left = [bool(rng.getrandbits(1)) for _ in range(width)]
        right = [bool(rng.getrandbits(1)) for _ in range(width)]
        transitions += execute(controller, left, right, dirty)
        long_cases += 1
    rejected = []
    for mutation in ("wrong_source", "missing_second_copy", "missing_turn_left",
                     "wrong_rewind", "erase_on_rewind", "stutter_after_halt"):
        try:
            execute(table(mutation), [False], [True], dirty)
        except ValueError:
            rejected.append(mutation)
        else:
            raise ValueError("accepted corrupted copy/rewind table: " + mutation)
    return {"status": "PASS_INDEPENDENT_PAIRED_COPY_CONTROLS", "finite_table_entries": 243,
            "equal_length_pairs_exhaustive_width_0_through_5": exhaustive,
            "seeded_long_cases_max_width_4096": long_cases,
            "checked_actual_transitions": transitions,
            "source_preserved_every_prefix": True,
            "dirty_spectators": len(dirty), "rejected_table_mutations": rejected}


if __name__ == '__main__':
 import sys
 sys.dont_write_bytecode=True
 package_root=Path(__file__).resolve().parent
 pins=inventory(package_root)
 print(json.dumps(dict(status='PASS_SOURCE_AND_PAIRED_COPY_CONTROLS',kernel_check='not_run',source_files=len(pins),manifest_sha256=digest(package_root/'MANIFEST.json'),paired_copy=verify(),audit_report_corruptions_rejected=audit_controls()),sort_keys=True))
