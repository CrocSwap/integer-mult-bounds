#!/usr/bin/env python3
"""Exact frame-transport examples and semantic program rejection controls.

Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
Finite examples corroborate the written quantified proof; they do not replace it.
"""
import copy
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as audit


def mm(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) for col in zip(*b)) for row in a)


def trans(a):
    return tuple(zip(*a))


def plus(a, b, q):
    return tuple(tuple(x + q * y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def scale(a, q):
    return tuple(tuple(q * x for x in row) for row in a)


def transport_examples():
    identity = ((Q(1), Q(0)), (Q(0), Q(1)))
    rotation = ((Q(3, 5), Q(-4, 5)), (Q(4, 5), Q(3, 5)))
    frames = [identity, scale(identity, -1), ((Q(1), Q(0)), (Q(0), Q(-1))),
              ((Q(0), Q(1)), (Q(1), Q(0))), rotation, trans(rotation)]
    for frame in frames:
        audit.need(mm(frame, trans(frame)) == identity, "example frame unitarity")
    cuts = cells = 0
    for a, b, c in product(range(len(frames)), repeat=3):
        labels = [0, b, 0]
        initial = list(labels)
        shadow = [[Q(1), Q(0)], [Q(0), Q(1)], [Q(0), Q(0)]]
        physical = [((Q(1), Q(0), Q(0), Q(0)), (Q(0), Q(1), Q(0), Q(0))),
                    ((Q(0), Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(0), Q(1))),
                    ((Q(0),) * 4,) * 2]
        events = [("relabel", 0, a), ("relabel", 1, a), ("add", 0, 1, Q(3, 2)),
                  ("relabel", 0, c), ("scale", 0, Q(-2)), ("copy", 2, 0),
                  ("relabel", 2, a), ("relabel", 1, c), ("add", 1, 0, Q(-1, 2)),
                  ("clear", 2), ("relabel", 0, b)]
        for event in events:
            kind, target, *rest = event
            if kind == "relabel":
                new = rest[0]
                physical[target] = mm(mm(frames[new], trans(frames[labels[target]])), physical[target])
                labels[target] = new
            elif kind == "add":
                source, q = rest
                audit.need(labels[target] == labels[source], "example common frame")
                physical[target] = plus(physical[target], physical[source], q)
                shadow[target] = [x + q * y for x, y in zip(shadow[target], shadow[source])]
            elif kind == "scale":
                physical[target] = scale(physical[target], rest[0])
                shadow[target] = [rest[0] * x for x in shadow[target]]
            elif kind == "copy":
                source = rest[0]
                labels[target] = labels[source]
                physical[target] = physical[source]
                shadow[target] = list(shadow[source])
            else:
                physical[target] = ((Q(0),) * 4,) * 2
                shadow[target] = [Q(0), Q(0)]
            for r in range(3):
                blocks = [scale(mm(frames[labels[r]], trans(frames[initial[j]])), shadow[r][j])
                          for j in range(2)]
                expected = tuple(blocks[0][i] + blocks[1][i] for i in range(2))
                audit.need(physical[r] == expected, "physical prefix conjugation")
                cells += 8
            cuts += 1
    # All numbers below are exact. These are failures of weakened hypotheses,
    # not alleged admission bugs in the selected construction.
    # copy b=a=1; change b's label by -I; inadmissible a-=b.
    a, b = Q(1), Q(1)
    b = -b
    a -= b
    audit.need(a == 2 and (Q(1) - Q(1)) == 0, "mismatched frame witness")
    # Closed continuation restores a and clears private b: endpoint a=1.
    a += b
    b = -b
    b = Q(0)
    audit.need((a, b) == (1, 0), "closed mismatch endpoint")
    # Exact, well-labelled relabels with a nonunitary T have scalar shadow I.
    # Relabel I -> diag(8,1) -> I has physical peak 8 and endpoint 1.
    x = Q(1)
    x *= 8
    nonunitary_peak = x
    x /= 8
    audit.need(nonunitary_peak == 8 and x == 1, "nonunitary label witness")
    # Both declared labels end at -I, but the first recipe wrongly executes I.
    # Starting after copy b=a: wrong a relabel, exact b relabel, then a-=b.
    a, b = Q(1), Q(-1)
    a -= b
    audit.need(a == 2, "inexact recipe witness")
    # A partially stored unit-norm vector may exceed either endpoint norm.
    # Old=(3/5,4/5), new=(1,0), store the first coordinate first.
    partial_squared = Q(1) + Q(4, 5) ** 2
    audit.need(partial_squared == Q(41, 25) and 1 < partial_squared < 2,
               "split-component norm witness")
    return dict(frame_choices=len(frames), words=6 ** 3, prefix_cuts=cuts,
                exact_matrix_entries=cells, adverse=[
                    "unitary mismatched labels: shadow peak 1, physical peak 2, restored endpoint",
                    "nonunitary exact labels: shadow peak 1, physical peak 8, identity endpoint",
                    "unitary labels with inexact recipe: shadow zero, physical value 2",
                    "partially stored unit vectors: squared norm 41/25 > 1; factor-two square bound needed"])


def rejection_controls():
    word, programs, _, _, _, _ = audit.load()
    events = programs["forward"]
    rejected = {}

    def reject(name, change, expected_message):
        mutant = copy.deepcopy(events)
        change(mutant)
        try:
            audit.audit(word, mutant, "forward", crosscheck=False)
        except audit.AuditError as exc:
            audit.need(expected_message in str(exc), "wrong rejection: " + name + ": " + str(exc))
            rejected[name] = str(exc)
        else:
            raise audit.AuditError("accepted mutation: " + name)

    reject("wrong_common_frame", lambda es: next(e for e in es if e[0] == "scalar" and e[2] != 0)
           .__setitem__(2, 0), "common scalar frame")
    reject("omit_climb", lambda es: es.pop(next(i for i, e in enumerate(es) if e[0] == "climb")),
           "common scalar frame")
    reject("wrong_wrapper_terminal_pair", lambda es: next(e for e in es if e[0] == "residual_adapter"
                                                           and len(e) == 5).__setitem__(4, 1),
           "wrapper terminal pair")
    reject("premature_post_wrapper", lambda es: es.insert(es.index(["phase", "A"]) + 1,
           es.pop(next(i for i, e in enumerate(es) if e[0] == "residual_adapter" and e[1] == "post"))),
           "post wrapper placement")
    reject("coefficient_source_alias", lambda es: next(e for e in es if e[0] == "scalar"
           and e[1][0] == "add")[1].__setitem__(1, next(e for e in es if e[0] == "scalar"
           and e[1][0] == "add")[1][2]), "coefficient source alias")
    reject("non_dyadic_scale", lambda es: next(e for e in es if e[0] == "scalar"
           and e[1][0] == "scale")[1].__setitem__(3, 3), "dyadic coefficient")
    reject("wrong_power_two_scale_endpoint", lambda es: next(e for e in es if e[0] == "scalar"
           and e[1][0] == "scale")[1].__setitem__(2, -2), "scalar endpoint")
    saved = json.loads((audit.PACKAGE / "EXPECTED.json").read_text())
    forward = saved["orientations"]["forward"]
    value = audit.literal_witness(events, forward["peak_witness"], 704)
    audit.need(Q(value["primitive_peak"]) > Q(forward["register_peak"]), "scratch-work adverse witness")
    rejected["register_only_precision_bound"] = "131088 > 131072 at coefficient preparation"
    return rejected


def main():
    receipt = dict(transport=transport_examples(), program_controls=rejection_controls())
    expected = json.loads((audit.PACKAGE / "CONTROLS.json").read_text())
    audit.need(receipt == expected, "control receipt mismatch")
    print("PASS_SIGNED_PREFIX_CONTROLS", "unitary_words=216 cuts=2376 program_controls=8",
          "receipt_sha256=" + audit.digest(audit.canonical(receipt)))


if __name__ == "__main__":
    main()
