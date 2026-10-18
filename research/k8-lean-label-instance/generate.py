# SPDX-License-Identifier: Apache-2.0
"""Generate bounded kernel proof blocks; generated files stay in a temp tree."""
from translate import REGISTERS, lean_event, require, step

BLOCK = 256
PER_MODULE = 8
DEPTH = 10
CAPACITY = 2**DEPTH


def tree(labels):
    """Depth-ten parity tree, matching TreeCheckpoint.get/put."""
    require(len(labels) == CAPACITY, "tree capacity")
    level = [f"(.leaf {label})" for label in labels]
    # Pair indices with the same low bits. Each level removes the high bit;
    # the resulting root chooses the original low bit, then the next bit.
    for _ in range(DEPTH):
        half = len(level) // 2
        level = [f"(.node {level[i]} {level[i + half]})" for i in range(half)]
    require(len(level) == 1, "tree depth")
    return level[0]


def state_literal(labels):
    require(len(labels) == REGISTERS, "label capacity")
    return tree(labels + [0] * (CAPACITY - REGISTERS))


def emit(out, name, start, events):
    require(name in ("Forward", "Backward") and len(events) <= 25000, "generation domain")
    blocks = [events[i:i + BLOCK] for i in range(0, len(events), BLOCK)]
    require(0 < len(blocks) <= 100, "block count")
    state = list(start)
    files, checked, block_names = [], [], []
    for group in range((len(blocks) + PER_MODULE - 1) // PER_MODULE):
        module = f"{name}{group:02}"
        previous = f"{name}{group - 1:02}" if group else "TreeCheckpoint"
        lines = [f"import {previous}", f"namespace K8.{name}",
                 "open LemmaG LemmaG.TreeCheckpoint", "set_option maxRecDepth 10000",
                 "set_option maxHeartbeats 0"]
        first = group * PER_MODULE
        if group == 0:
            lines.append(f"def state0 : State 10 := {state_literal(state)}")
        for index in range(first, min(first + PER_MODULE, len(blocks))):
            block = blocks[index]
            for event in block:
                state = step(state, event)
            lines.append(f"def state{index + 1} : State 10 := {state_literal(state)}")
            lines.append(f"def block{index} : List (Event (Fin (2 ^ 10)) Nat Rat) := [\n" +
                         ",\n".join(lean_event(event) for event in block) + "]")
            lines.append(f"theorem checked{index} : check block{index} state{index} = "
                         f"some state{index + 1} := by decide +kernel")
            checked.append(f"checked{index}")
            block_names.append(f"block{index}")
        lines.append(f"end K8.{name}")
        path = out / (module + ".lean")
        path.write_text("\n".join(lines) + "\n")
        files.append(path)
    root = f"{name}Result"
    lines = [f"import {files[-1].stem}", f"namespace K8.{name}",
             "open LemmaG LemmaG.TreeCheckpoint", "set_option maxRecDepth 10000",
             "set_option maxHeartbeats 0", "def blocks := [" + ", ".join(block_names) + "]",
             "def events := blocks.flatten"]
    chain = f"(Chain.nil state{len(blocks)})"
    for proof in reversed(checked):
        chain = f"(Chain.cons {proof} {chain})"
    lines.append(f"theorem certified : Chain state0 state{len(blocks)} blocks := {chain}")
    lines.append("theorem wellLabelled : Stream.WellLabelled events (view state0) := "
                 "(Chain.sound certified).1")
    lines.append(f"theorem finalLabels : Stream.labRun events (view state0) = "
                 f"view state{len(blocks)} := (Chain.sound certified).2")
    lines += ["#print axioms wellLabelled", "#print axioms finalLabels", f"end K8.{name}"]
    path = out / (root + ".lean")
    path.write_text("\n".join(lines) + "\n")
    files.append(path)
    return files
