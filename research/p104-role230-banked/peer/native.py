"""Check exact rational signals, all endpoints, and the common integer grid."""
from fractions import Fraction
from math import lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import add_scaled, coefficients, fold, main_roles, need, pivot, read, source_word


def grid(net, order):
    denominators = {~r: 1 for r in range(len(net.initial))}
    common = 1
    for node in order:
        bound = 1
        for donor, factor in net.forms[node].items():
            bound = lcm(bound, denominators[donor] * factor.denominator)
        denominators[node] = bound
        common = lcm(common, bound)
    return common


def evaluate(net, requested=None):
    order = net.schedule()
    if requested is not None:
        active = set(requested)
        for k in reversed(order):
            if k in active:
                active.update(net.forms[k])
        order = [k for k in order if k in active]
    unit = grid(net, order)
    values = {~r: {r: unit} for r in range(len(net.initial))}
    mass = {~r: unit for r in range(len(net.initial))}
    peak = unit
    work = 0
    for k in order:
        row = {}
        bound = 0
        for donor, factor in sorted(net.forms[k].items()):
            a, b = factor.numerator, factor.denominator
            bound += abs(a) * mass[donor] // b
            for i, value in values[donor].items():
                quotient, remainder = divmod(a * value, b)
                need(remainder == 0, "native term left the grid")
                new = row.get(i, 0) + quotient
                if new:
                    row[i] = new
                else:
                    row.pop(i, None)
            work += len(values[donor])
        peak = max(peak, bound)
        values[k] = row
        mass[k] = sum(map(abs, row.values()))
    return unit, values, peak, work


def expected(word, unit):
    n = word["public"]
    out = [{r: unit} for r in range(n)]
    hosted = word["hosted"]
    a_ports = set(hosted["Dports"])
    for j, x in enumerate(word["live"]):
        y = x + 112
        if j in a_ports:
            out[y][x] = unit
        else:
            need(unit % 2 == 0, "butterfly half")
            out[x][y] = -unit
            out[y] = {x: unit // 2, y: unit // 2}
    for x, y in zip(hosted["X2"], hosted["Y2"], strict=True):
        out[x][y] = -unit
    return out


def check_endpoints(net, word):
    unit, rows, peak, terms = evaluate(net)
    targets = expected(word, unit)
    need([rows[net.first_output + r] for r in range(len(targets))] == targets, "native output matrix")
    power = (unit & -unit).bit_length() - 1
    numerator_bits = max(abs(c.numerator).bit_length() for row in net.forms.values() for c in row.values())
    denominator_bits = max(c.denominator.bit_length() for row in net.forms.values() for c in row.values())
    return dict(grid=str(unit), odd=unit >> power, dyadic_height=power, peak_scaled_mass=str(Fraction(peak, 1 << power)),
                checked_products=terms, terms=sum(map(len, net.forms.values())), slots=len(net.moves),
                coefficient_bits=max(numerator_bits, denominator_bits), public=len(targets), mains=len(main_roles(word)))


def verify_pivot(net, edit):
    combo = coefficients(edit["combination"])
    source = coefficients(edit["sender"])
    side = coefficients(edit["receiver"])
    _, values, _, _ = evaluate(net, combo.keys() | source.keys() | side.keys())
    target = {}
    for m, a in combo.items():
        add_scaled(target, values[m], a)
    for m, a in side.items():
        add_scaled(target, values[m], a)
    got = {}
    for m, a in source.items():
        add_scaled(got, values[m], a)
    need(target == got, "saved signal identity")


def check_pivots():
    word = source_word()
    net = fold(word)
    edits = read(HERE / "PIVOTS.json")
    checked = 0
    for i, edit in enumerate(edits):
        if edit["direction"] == "transpose":
            net = net.transpose()
        verify_pivot(net, edit)
        if i == 0:
            donor, weight = edit["sender"][0]
            corrupted = dict(edit, sender=[[donor, str(-Fraction(weight))], *edit["sender"][1:]])
            try:
                verify_pivot(net, corrupted)
            except ValueError as exc:
                need(str(exc) == "saved signal identity", "sender sign control reason")
            else:
                raise ValueError("incorrect sender sign accepted")
        checked += 1
        net = pivot(net, edit)
        if edit["direction"] == "transpose":
            net = net.transpose()
    return checked


if __name__ == "__main__":
    checked = check_pivots()
    need(checked == read(HERE / "RESULT.json")["pivot_checks"], "pivot coverage")
    print("PASS_EXACT_PIVOTS", checked)
