"""Verify the local relations on independent coordinates and check all final columns."""
from collections import Counter
from math import lcm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quotient import HERE, add_scaled, construct_candidate, digest, main_roles, need, parent, read, receipt
from vendor import physical


def pull_back(net, reverse_order, row):
    """Express the requested bank combination as a form on public entrances."""
    active = dict(row)
    for key in reverse_order:
        scale = active.pop(key, 0)
        if scale:
            add_scaled(active, net.forms[key], scale)
    need(all(k < 0 for k in active), "unresolved receiver bank")
    return active


def reverse_columns(net, layout):
    order = net.schedule()[::-1]
    grids = {key: 1 for key in net.forms}
    grids.update({~r: 1 for r in range(layout["public"])})
    for key in order:
        for donor, q in net.forms[key].items():
            grids[donor] = lcm(grids[donor], grids[key] * q.denominator)
    unit = lcm(*grids.values())
    columns = {key: {} for key in grids}
    for r in range(layout["public"]):
        columns[net.first_output + r] = {r: unit}
    count = 0
    for key in order:
        adjoint = columns.pop(key)
        for donor, q in net.forms[key].items():
            result = columns[donor]
            for r, value in adjoint.items():
                product, remainder = divmod(q.numerator * value, q.denominator)
                need(remainder == 0, "reverse sweep grid")
                updated = result.get(r, 0) + product
                if updated:
                    result[r] = updated
                else:
                    result.pop(r, None)
            count += len(adjoint)
    planes = list(zip(layout["hosted"]["X2"], layout["hosted"]["Y2"], strict=True))
    interface = main_roles(layout), set(layout["hosted"]["Dports"]), planes
    expected = physical.expected_rows(layout["public"], layout, interface, unit)
    transposed = {~r: {} for r in range(layout["public"])}
    for r, row in enumerate(expected):
        for col, value in row.items():
            transposed[~col][r] = value
    need(columns == transposed, "public column mismatch")
    return dict(columns=len(columns), coefficient_products=count, grid=unit)


def verify():
    word, source = parent()
    edits = read(HERE / "QUOTIENTS.json")
    records, controls = [], set()
    dims = [len(b) for b in word["frames"]]

    def observe(i, before, entrance, banks):
        order = before.schedule()[::-1]
        ranks = []
        for key, _, relation in banks:
            actual = pull_back(before, order, relation)
            need(actual == entrance, f"wrong local relation at step {i+1}, bank {key}")
            a, b = before.moves[key]
            ranks.append(abs(dims[a] - dims[b]))
        r, side = edits[i]["role"], edits[i]["direction"]
        target = abs(dims[before.final[r]] - dims[before.initial[r]])
        need(all(ranks) and sum(ranks) == target, "paid ranks must sum to the lost target rank")
        if side not in controls:
            wrong = dict(banks[0][2])
            wrong[banks[0][0]] += 1
            need(pull_back(before, order, wrong) != entrance, "altered paid coefficient accepted")
            controls.add(side)
        records.append(dict(step=i+1, role=r, direction=side, lost=target, saved=ranks,
                            entrance_terms=len(entrance), receiver_terms=[len(row) for _, _, row in banks]))

    net, layout, keep = construct_candidate(word, source, observe)
    need(controls == {"forward", "transpose"} and len(keep) + len(records) == word["public"],
         "complete restriction sequence")
    return dict(records=records, directions=dict(Counter(r["direction"] for r in records)),
                relations=sum(len(r["saved"]) for r in records), retained_labels_sha256=digest(keep),
                reverse=reverse_columns(net, layout), altered_coefficient_rejected=sorted(controls))


if __name__ == "__main__":
    result = verify()
    receipt("witness", result)
    print("PASS_HELPER_RELATIONS", result["relations"], result["reverse"]["columns"])
