"""Rebuild two helper splits and check the resulting rational program."""
from fractions import Fraction
from graphlib import TopologicalSorter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from replay import add
from verify_bidirectional import canonical, check, check_circuit, read, reconstruct, verify_step


def split(word, event):
    first = word["first_output"]
    initial, final = word["initial"].copy(), word["final"].copy()
    role, chart = event["role"], event["chart"]
    fresh = len(initial)
    check((initial[role], final[role]) == (3, 127), "old helper endpoints")

    def load_row(entries):
        return {i: Fraction(q) for i, q in entries}

    rows = {k: load_row(entries) for k, entries in word["forms"]}
    s, w = load_row(event["covector"]), load_row(event["direction"])
    pairing = sum(s.get(i, 0) * v for i, v in w.items())
    check(pairing and w.get(role), "nonzero helper pivots")
    substitute = {~i: -v / pairing for i, v in s.items() if i != role}
    substitute[~role] = 1 / pairing

    def change_source(row):
        coefficient = sum(row.get(~i, 0) * v for i, v in w.items())
        row.pop(~role, None)
        if coefficient:
            add(row, substitute, coefficient)

    for row in rows.values():
        change_source(row)
    observed = load_row(event["read"])
    change_source(observed)
    difference = {~fresh: 1 / pairing}
    add(difference, observed, -1 / pairing)
    for k, coefficient in load_row(event["inject"]).items():
        add(rows[k], difference, coefficient)

    recovered = {}
    for i, v in s.items():
        add(recovered, rows[first + i], v)
    old_return = rows[first + role]
    for i, v in w.items():
        if i != role:
            add(rows[first + i], old_return, -v / w[role])
    rows[first + role] = observed
    rows[first + fresh] = recovered
    initial.append(chart)
    final.append(final[role])
    final[role] = chart
    deps = {k: tuple(j for j in sorted(row) if j >= 0) for k, row in sorted(rows.items())}
    return dict(word, initial=initial, final=final, schedule=list(TopologicalSorter(deps).static_order()),
                forms=[[k, [[j, str(q)] for j, q in sorted(row.items())]] for k, row in sorted(rows.items())])


def rebuild(check_parents=False):
    parent = read("WORD.json.gz")
    for name in ("BIDIRECTIONAL", "BIDIRECTIONAL-QUOTIENT"):
        if check_parents:
            parent = verify_step(parent, name)
        else:
            parent, _ = reconstruct(parent, read(name + ".json.gz"))
    journal, receipt = read("HELPER-SPLITS.json"), read("HELPER-SPLITS-RECEIPT.json")
    check(canonical(parent) == journal["parent"] == read("BIDIRECTIONAL-QUOTIENT-RECEIPT.json")["new_word"],
          "split parent")
    events = journal["splits"]
    check(len(events) == receipt["splits"], "split count")
    word = parent
    for event in events:
        word = split(word, event)
    check(canonical(word) == journal["word"] == receipt["new_word"], "split word")
    check(word["moves"] == parent["moves"] and len(word["moves"]) == receipt["moves"], "shared paid transfers")
    layout = read("LAYOUT.json.gz")
    labels = layout["source_labels"]
    first_label = max(labels) + 1
    layout = dict(layout, public=len(word["initial"]),
                  source_labels=[*labels, *range(first_label, first_label + len(events))])
    check(canonical(layout) == journal["layout"], "new public labels")
    return word, layout


def main():
    word, layout = rebuild(check_parents=True)
    receipt = read("HELPER-SPLITS-RECEIPT.json")
    check_circuit(word, receipt, layout)
    verify_step(word, "BANK-FACTORS", layout)


if __name__ == "__main__":
    main()
