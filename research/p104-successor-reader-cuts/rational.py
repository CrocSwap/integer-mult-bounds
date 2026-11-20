# SPDX-License-Identifier: Apache-2.0
"""Independent exact rational reachability, reader-rank and exterior checks."""

from collections import Counter, defaultdict
from functools import cache
from itertools import permutations

from common import Q, canonical, digest, row_rank, sparse_axpy

FUND = (88959, 88960, 90605, 90604)
HOLD = (89198, 91110, 94251)
RELEASE = (98703, 91131)
TERMINALS = (154930, 154935)
OLD_CONE = (89198, 91110, 98703, 91131, 94251)
SIDE_AND_RETARGET = (89187, 88, 94034, 156055)
REDIRECT = (95914, 94019, 88, 90369)


class Tape:
    def __init__(self, word):
        self.frames = word["frames"]
        self.initial = tuple(word["initial"])
        self.final = tuple(word["final"])
        self.schedule = tuple(word["schedule"])
        self.clock = {slot: clock for clock, slot in enumerate(self.schedule)}
        self.moves = {slot: (a, b) for slot, a, b in word["moves"]}
        self.terminals = dict(enumerate(self.final, word["first_output"]))
        self.op = {slot: {i: Q(x) for i, x in components} for slot, components in word["forms"]}
        self.stock = defaultdict(list)
        self.outputs = defaultdict(list)
        self.readers = defaultdict(list)
        self.stock_before = {}
        assert set(self.clock) == set(self.op) == self.moves.keys() | self.terminals.keys()
        assert len(self.clock) == len(self.schedule) and len(self.moves) == len(word["moves"])
        owners = {}
        for i, chart in enumerate(self.initial):
            self.stock[chart].append(~i)
            owners[~i] = chart
        for slot in self.schedule:
            a = self.source(slot)
            self.stock_before[slot] = tuple(self.stock[a])
            for i, coefficient in self.op[slot].items():
                assert coefficient and owners.get(i) == a, (slot, i, a)
                self.readers[i].append(slot)
            self.outputs[a].append(slot)
            if slot in self.moves:
                b = self.moves[slot][1]
                self.stock[b].append(slot)
                owners[slot] = b

    def source(self, slot):
        if slot in self.moves:
            return self.moves[slot][0]
        return self.terminals[slot]

    @cache
    def row(self, slot):
        """Compute a public input row by forward substitution of local operands."""
        if slot < 0:
            return {~slot: Q(1)}
        result = {}
        for i, q in self.op[slot].items():
            sparse_axpy(result, self.row(i), q)
        return result

    def eval(self, inputs, forced=None):
        states = {~i: Q(q) for i, q in inputs.items()}
        for slot in self.schedule:
            if forced and slot in forced:
                states[slot] = forced[slot]
                continue
            states[slot] = sum((q * states[i] for i, q in self.op[slot].items() if i in states), Q(0))
        return states

    @cache
    def frame_span(self, chart):
        elements = {0}
        for basis in self.frames[chart]:
            assert basis not in elements, chart
            elements.update(set(i ^ basis for i in elements))
        return elements

    @cache
    def grade(self, a, b, productive=False):
        u, v = self.frame_span(a), self.frame_span(b)
        assert u < v or (v < u and not productive), (a, b)
        return abs(len(self.frames[a]) - len(self.frames[b]))

    def receipt(self, slot):
        if slot < 0:
            return {"axis": ~slot, "chart": self.initial[~slot]}
        return {"slot": slot, "clock": self.clock[slot],
                "route": self.moves.get(slot), "terminal": self.terminals.get(slot)}


def det(matrix):
    """Leibniz formula on the independent fixed-size minors."""
    size = len(matrix)
    result = Q(0)
    for columns in permutations(range(size)):
        weight = Q(1)
        for i, j in enumerate(columns):
            weight *= matrix[i][j]
        if sum(columns[i] > columns[j] for i in range(size) for j in range(i + 1, size)) % 2:
            weight = -weight
        result += weight
    return result


def minor(row_ids, col_ids, matrix_rows):
    matrix = [[matrix_rows[i].get(j, Q(0)) for j in col_ids] for i in row_ids]
    return {"rows": list(row_ids), "columns": list(col_ids),
            "matrix": [[str(q) for q in row] for row in matrix], "determinant": str(det(matrix))}


def check_chart282(tape, old):
    assert len(tape.initial) == len(tape.terminals) == 1289 and len(tape.moves) == 5707
    assert tape.stock[282] == [90369, *FUND] and tape.outputs[282] == list(OLD_CONE)
    assert all(tape.grade(*tape.moves[i]) == 1 for i in FUND)
    assert all(tape.stock_before[i] == (90369, *FUND) for i in OLD_CONE)
    assert tape.readers[90369] == [91110, 98703, 94251]
    assert tape.readers[88959] == [91110, 98703, 91131, 94251]
    assert tape.readers[88960] == list(OLD_CONE)
    assert tape.readers[95914] == [88] and tape.readers[94019] == [94034, 156055]

    columns = (88959, 88960, 90369, 90605, 90604)
    critical = columns + OLD_CONE
    rows = {i: tape.row(i) for i in critical}
    axes = (11, 21, 62, 129, 142)
    a = minor(columns, axes, rows)
    d = minor(OLD_CONE, axes, rows)
    quotient = minor(OLD_CONE[:3], columns[:3], tape.op)
    local = minor(OLD_CONE, columns, tape.op)
    assert a["determinant"] == d["determinant"] == "-615/37888"
    assert quotient["determinant"] == local["determinant"] == "1"
    assert (a, d, quotient) == (old["old_arrival_public_minor"], old["demand_public_minor"],
                                old["quotient_minor"])

    def rank(ids):
        return row_rank(tape.row(i) for i in ids)

    ranks = [rank(FUND[2:] + OLD_CONE[:n]) for n in range(6)]
    one_recode = [rank((FUND[0], *FUND[2:]) + OLD_CONE[:n]) for n in range(6)]
    single_release = {}
    for release in [(RELEASE[0],), (RELEASE[1],), RELEASE]:
        single_release[",".join(map(str, release))] = rank(FUND[2:] + tuple(
            i for i in OLD_CONE if i not in release)) - ranks[0]
    assert ranks == old["rank_trace"] == [2, 3, 4, 5, 5, 5]
    assert one_recode == old["s10_one_scalar_control_rank_trace"] == [3, 4, 5, 5, 5, 5]
    assert single_release == old["required_directions_if_non_288_rows_released"]
    for i, item in zip(OLD_CONE, old["protected_readers"], strict=True):
        assert (i, tape.clock[i], tape.moves[i], tape.readers[i]) == (
            item["slot"], item["clock"], tuple(item["route"]), item["downstream_readers"])
        assert tape.op[i] == {int(j): Q(q) for j, q in item["literal_terms"].items()}
    fingerprints = {i: digest(canonical([[j, str(q)] for j, q in sorted(rows[i].items())]))
                    for i in critical}
    for item in old["protected_readers"] + old["original_arrivals"]:
        assert fingerprints[item["slot"]] == item["public_row_sha256"]
    return {
        "arrivals": [tape.receipt(i) for i in tape.stock[282]],
        "readers": [tape.receipt(i) | {"downstream": tape.readers[i]} for i in OLD_CONE],
        "rank_trace": ranks, "one_recode_control": one_recode, "release_controls": single_release,
        "arrival_minor": a, "reader_minor": d, "first_three_quotient_minor": quotient,
        "local_coordinate_matrix": local,
    }


def neighbor_review(tape, old):
    assert tape.moves[95914] == (278, 288)
    assert tape.moves[94019] == (3, 304)
    assert tape.moves[90369] == (3, 282)
    assert tape.moves[88] == (288, 127)
    # Use only the surviving schedule and the endpoint delta. Treat four paid
    # ingresses as unconstrained variables. No literal donor formula is needed.
    routes = tape.moves.copy()
    routes.pop(95914)
    routes.update({94019: (3, 278), 90369: (3, 304), 88: (278, 127)})
    available = defaultdict(list)
    for axis, label in enumerate(tape.initial):
        available[label].append(~axis)
    depend = {}
    changed = defaultdict(bool)
    potential = set()
    touched = set()
    fixed_values = set()
    targets = (*HOLD, *TERMINALS)
    for i in tape.schedule:
        if i == 95914:
            continue
        owner = routes[i][0] if i in routes else tape.terminals[i]
        stock = tuple(available[owner])
        if changed[owner] or i in targets:
            variable = set()
            constants = set()
            history = set()
            for key in stock:
                if key in FUND:
                    variable.add(key)
                elif key in potential:
                    v, f, c = depend[key]
                    variable.update(v)
                    constants.update(f)
                    history.update(c, (key,))
                else:
                    constants.add(key)
            depend[i] = variable, constants, history
        if i in FUND or (i not in HOLD and changed[owner]):
            potential.add(i)
            if i in routes:
                changed[routes[i][1]] = True
                touched.add(routes[i][1])
        if i in routes:
            available[routes[i][1]].append(i)
    assert set(RELEASE + TERMINALS) <= potential and set(HOLD).isdisjoint(potential)
    assert not touched.intersection({3, 273, 276, 278, 288, 304})
    assert not any(routes[i][1] == 282 for i in potential & routes.keys() if i not in FUND)
    for context in old["witness_cones"]:
        i = context["demand"]
        variable, constants, history = depend[i]
        parse = lambda event: event["slot"] if "slot" in event else ~event["input_axis"]
        assert variable == set(context["funded_channels"])
        assert constants == set(map(parse, context["fixed_stock"]))
        assert history == set(map(parse, context["internal_mutable_sends"]))
        fixed_values.update(constants)
    assert len(potential & routes.keys()) == old["causally_mutable_paid_count"]
    assert len(potential & tape.terminals.keys()) == old["causally_mutable_terminals_count"]
    assert len(touched) == old["chronologically_reached_charts"]
    assert len(fixed_values) == 74 and set(REDIRECT).isdisjoint(fixed_values)
    assert set(targets).isdisjoint(fixed_values)
    assert set.union(*(depend[i][0] for i in targets)) == set(FUND)

    fixed_values = sorted(fixed_values, key=lambda i: (~i if i < 0 else len(tape.initial) + tape.clock[i]))
    rank = lambda ids: row_rank(tape.row(i) for i in ids)
    rank_trace = [rank(fixed_values + list(targets[:n])) for n in range(6)]
    assert rank_trace == old["rank_trace"] == [62, 63, 64, 65, 66, 67]
    controls = {str(i): rank(fixed_values + [j for j in targets if j != i]) - rank_trace[0]
                for i in TERMINALS}
    assert controls == old["controls"]["quotient_ranks_when_either_exterior_terminal_is_released"]

    receiver_checks = {}
    for release, original in zip(RELEASE, old["receiver_audit"], strict=True):
        bank = tape.moves[release][1]
        direct = tape.readers[release]
        assert direct == tape.outputs[bank] == [k["slot"] for k in original["original_direct_consumers"]]
        stock = tape.stock_before[direct[0]]
        assert all(tape.stock_before[i] == stock for i in direct)
        fixed = [i for i in stock if i != release]
        assert (rank(fixed), rank(fixed + direct)) == (3, 4)
        mono = tape.eval({}, {release: Q(1)})
        impulse = [str(mono[i]) for i in TERMINALS]
        assert impulse == old["incumbent_terminal_responses_to_released_wire_impulses"][str(release)]
        receiver_checks[release] = {
            "receiver": bank, "stock": [tape.receipt(i) for i in fixed],
            "consumers": [tape.receipt(i) | {"coefficient": str(tape.op[i][release])} for i in direct],
            "terminal_impulse": impulse,
        }

    # Verify the retarget controls as identities of all public inputs.
    assert not set(FUND[:2]).intersection(tape.op[89187])
    old_88 = dict(tape.row(95914))
    sparse_axpy(old_88, tape.row(~1288), Q(-845660160))
    assert old_88 == tape.row(88)
    assert not set(REDIRECT).intersection(tape.op[95914])
    assert all(operand in tape.stock_before[90369] for operand in tape.op[94019])
    assert tape.clock[90369] < min(tape.clock[i] for i in tape.readers[94019])
    assert tape.clock[94019] < tape.clock[88]
    assert all(operand in tape.stock_before[88] or
               (operand in tape.moves and tape.moves[operand][1] == 278 and tape.clock[operand] < tape.clock[88])
               for operand in tape.op[95914])
    protections = set(targets[:3]) | set(SIDE_AND_RETARGET) | set(fixed_values)
    # The virtual four-slot control changes 88959 by half the old 90369.
    # Its linear response can be computed on the old literal tape because the
    # three retargeted rows and 90369's removed reads are accounted for directly.
    unit_a = tape.eval({}, {88959: Q(1)})
    unit_observer = tape.eval({}, {90369: Q(1)})
    for i in protections:
        if i not in (*SIDE_AND_RETARGET,):
            assert unit_a.get(i, 0) / 2 == unit_observer.get(i, 0), i

    # Explicitly rebuild both retarget controls. The shadow is a genuine
    # same-route grade-three copy of the old 90369.
    shadow = max(tape.schedule) + 1

    def control(with_shadow):
        schedule = []
        moves = routes.copy()
        operations = {i: terms.copy() for i, terms in tape.op.items() if i != 95914}
        operations[94019] = {~1288: Q(1)}
        operations[90369] = tape.op[94019].copy()
        operations[88] = tape.op[95914] | {94019: Q(-845660160)}
        for i in tape.readers[94019]:
            operations[i][90369] = operations[i].pop(94019)
        for i in tape.readers[90369]:
            value = operations[i].pop(90369)
            if with_shadow:
                operations[i][shadow] = value
        if with_shadow:
            moves[shadow] = tape.moves[90369]
            operations[shadow] = tape.op[90369].copy()
        for i in tape.schedule:
            if i != 95914:
                schedule.append(i)
            if i == 90369 and with_shadow:
                schedule.append(shadow)
        return Tape({"frames": tape.frames, "initial": tape.initial, "final": tape.final,
                     "schedule": schedule, "first_output": min(tape.terminals),
                     "moves": [(i, a, b) for i, (a, b) in moves.items()],
                     "forms": [(i, terms.items()) for i, terms in operations.items()]})

    four, five = control(False), control(True)
    aliases = {shadow: 90369, 90369: 94019}
    for i in tape.schedule:
        if i not in REDIRECT:
            assert {aliases.get(j, j): q for j, q in five.op[i].items()} == tape.op[i], i
    assert five.row(shadow) == tape.row(90369)
    assert five.row(90369) == tape.row(94019)
    assert five.row(88) == tape.row(88)
    response = four.eval({}, {88959: Q(1)})
    for i in protections:
        repaired = dict(four.row(i))
        sparse_axpy(repaired, tape.row(90369), response.get(i, Q(0)) / 2)
        assert repaired == tape.row(i) == five.row(i), i
    pulse_receipts = []
    for witness in old["controls"]["five_independently_evaluated_public_input_pulses"]:
        index = witness["demand_index"]
        inputs = {i: Q(q) for i, q in witness["input_axis_values"]}
        values = tape.eval(inputs)
        assert all(values.get(i, 0) == 0 for i in fixed_values)
        identity = [int(i == index) for i in range(5)]
        assert [values[i] for i in targets] == identity
        four_values = four.eval(inputs, {88959: values[88959] + values[90369] / 2})
        five_values = five.eval(inputs)
        fixed_four = [str(four_values[i]) for i in targets]
        assert fixed_four == witness["four_channel_values"]
        assert all(values.get(i, 0) == four_values.get(i, 0) for i in protections)
        assert all(values[i] == five_values[i] for i in tape.schedule if i not in REDIRECT)
        assert values[88] == five_values[88]
        pulse_receipts.append({"input_axes": witness["input_axis_values"], "responses": identity,
                               "all_fixed_stock_zero": True, "four_channel_values": fixed_four,
                               "five_channel_public_mismatches": 0})
    assert len(pulse_receipts) == 5 and [w["responses"].index(1) for w in pulse_receipts] == list(range(5))
    return {
        "fixed_stock": [tape.receipt(i) for i in fixed_values],
        "rank_trace": rank_trace, "targets": [tape.receipt(i) for i in targets],
        "available_funded_ingresses": list(FUND), "receiver_checks": receiver_checks,
        "terminal_omission_quotient_rank": controls, "touched_charts": len(touched),
        "fixed_donor_and_retarget_charts": [3, 273, 276, 278, 288, 304],
        "public_pulses": pulse_receipts,
        "fifth_channel": {"slot": shadow, "grade": five.grade(*five.moves[shadow]),
                          "public_rows_preserved": len(tape.terminals), "other_paid_rows_preserved": 5704},
        "four_channel_held_and_fixed_rows_preserved": len(protections),
    }


def census(tape, layout):
    assert layout["public"] == len(tape.initial) and tape.frames == layout["frames"]
    h = layout["hosted"]
    mains = set(layout["live"]) | {r + 112 for r in layout["live"]} | set(h["X2"]) | set(h["Y2"])
    assert len(mains) == 400
    paid = Counter(tape.grade(a, b) for a, b in tape.moves.values())
    targets = Counter(tape.grade(a, b, True) for i, (a, b) in
                      enumerate(zip(tape.initial, tape.final, strict=True)) if i not in mains)
    return paid, targets
