"""Apply the two helper changes without materializing rational copies of untouched rows.

The signed row update, tests and owner convention follow verify_split_helpers.
Each output still uses every term of the original program.
"""

from functools import cache
from fractions import Fraction
from graphlib import TopologicalSorter


def split(word, event):
    from replay import add
    from verify_bidirectional import check

    rational = cache(Fraction)

    def read_row(entries):
        return {i: rational(q) for i, q in entries}

    first = word["first_output"]
    initial, final = word["initial"].copy(), word["final"].copy()
    role, chart = event["role"], event["chart"]
    fresh = len(initial)
    check((initial[role], final[role]) == (3, 127), "old helper endpoints")
    original = dict(word["forms"])
    edited = {}

    def row(k):
        if k not in edited:
            edited[k] = read_row(original[k])
        return edited[k]

    covector, direction = read_row(event["covector"]), read_row(event["direction"])
    pairing = sum(covector.get(i, 0) * w for i, w in direction.items())
    check(pairing and direction.get(role), "nonzero helper pivots")
    substitute = {~i: -s / pairing for i, s in covector.items() if i != role}
    substitute[~role] = 1 / pairing

    def change_source(values):
        coefficient = sum(values.get(~i, 0) * w for i, w in direction.items())
        values.pop(~role, None)
        if coefficient:
            add(values, substitute, coefficient)

    touched = {~i for i in direction}
    touched.add(~role)
    for k, entries in original.items():
        if any(j in touched for j, _ in entries):
            change_source(row(k))
    observed = read_row(event["read"])
    change_source(observed)
    difference = {~fresh: 1 / pairing}
    add(difference, observed, -1 / pairing)
    for k, a in read_row(event["inject"]).items():
        add(row(k), difference, a)
    recovered = {}
    for i, v in covector.items():
        add(recovered, row(first + i), v)
    old_return = row(first + role)
    for i, v in direction.items():
        if i != role:
            add(row(first + i), old_return, -v / direction[role])
    edited[first + role] = observed
    edited[first + fresh] = recovered

    for k, values in edited.items():
        original[k] = [[j, str(q)] for j, q in sorted(values.items())]
    forms = [[k, values] for k, values in sorted(original.items())]
    deps = {k: tuple(j for j, _ in values if j >= 0) for k, values in forms}
    initial.append(chart)
    final.append(final[role])
    final[role] = chart
    return dict(
        word,
        initial=initial,
        final=final,
        forms=forms,
        schedule=list(TopologicalSorter(deps).static_order()),
    )


def rebuild():
    from verify_bidirectional import canonical, check, read, reconstruct

    word = read("WORD.json.gz")
    for name in ("BIDIRECTIONAL", "BIDIRECTIONAL-QUOTIENT"):
        word, _ = reconstruct(word, read(name + ".json.gz"))
    journal = read("HELPER-SPLITS.json")
    receipt = read("HELPER-SPLITS-RECEIPT.json")
    check(
        canonical(word)
        == journal["parent"]
        == read("BIDIRECTIONAL-QUOTIENT-RECEIPT.json")["new_word"],
        "split parent",
    )
    check(len(journal["splits"]) == receipt["splits"], "split count")
    parent_moves = word["moves"]
    for event in journal["splits"]:
        word = split(word, event)
    check(canonical(word) == journal["word"] == receipt["new_word"], "split word")
    check(
        word["moves"] == parent_moves and len(parent_moves) == receipt["moves"],
        "shared paid transfers",
    )
    layout = read("LAYOUT.json.gz")
    labels = layout["source_labels"]
    first_label = max(labels) + 1
    layout = dict(
        layout,
        public=len(word["initial"]),
        source_labels=[
            *labels,
            *range(first_label, first_label + len(journal["splits"])),
        ],
    )
    check(canonical(layout) == journal["layout"], "new public labels")
    return word, layout
