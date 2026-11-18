#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact grids and occupied bank schedule for the chart-595 successor.

The signed caller, guarded selector and physical source model are reused from
#7682, with credit to the sources in NOTICE and PHYSICAL.md.
"""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import importlib.util
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
PEER = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
SOURCE_WORD = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_REPLAY = "ced48867f07ca0143604aa98cfd74fa7453696b9d3221f7c230d73e9ab9ba81f"
STAGES = 16
CALLER_ODD = 2025
AMBIENT_CAP = 153
PROTECTED_HELPERS = (325, 1087)
OLD_NATIVE_STOCK = 15290
EARLY_ROLE = 281
EARLY_LAST_DONOR = 95743
LATER_DEPARTURES = {93859, 96158, 96162, 96302, 96335, 97328, 97329, 98085, 98090, 102698}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def encoded(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def load_gzip(path, pin, *, canonical=True):
    packed = path.read_bytes()
    raw = gzip.decompress(packed)
    require(sha256(raw).hexdigest() == pin, f"wrong decoded hash for {path.name}")
    data = json.loads(raw)
    require(not canonical or encoded(data) == raw, f"noncanonical data for {path.name}")
    return data, sha256(packed).hexdigest()


def chart_span(basis):
    span = {0}
    for axis in basis:
        require(type(axis) is int and 0 < axis < 512 and axis not in span,
                "invalid independent ordered chart basis")
        span |= {axis ^ vector for vector in span}
    return span


def exact_coefficient(text):
    value = Fraction(text)
    require(value and str(value) == text, "noncanonical or zero scalar incidence")
    return value


def exact_div(value, denominator):
    result, remainder = divmod(value, denominator)
    require(remainder == 0, "nonintegral scalar pre-product")
    return result


def grid_parts(grid):
    height = (grid & -grid).bit_length() - 1
    return grid >> height, height


def ceiling_bits(value):
    return (-(-value.numerator // value.denominator)).bit_length()


def public_interface(graph, layout):
    n = len(graph["initial"])
    require(len(graph["final"]) == n and len(layout["live"]) == len(layout["ports"]) == 104,
            "complete public and port denominators")
    hosted = layout["hosted"]
    hosted_ports = set(hosted["Dports"])
    second_planes = list(zip(hosted["X2"], hosted["Y2"], strict=True))
    require(len(hosted_ports) == len(second_planes) == 96, "actual 96 hosted ports")
    live = layout["live"]
    mains = set(live) | {role + 112 for role in live} | set(hosted["X2"]) | set(hosted["Y2"])
    require(len(mains) == 400 and mains <= set(range(n)), "400 distinct real main slots")
    for port, (x, q) in enumerate(zip(live, layout["ports"], strict=True)):
        y = x + 112
        initial, final = graph["initial"], graph["final"]
        frames = graph["frames"]
        require(frames[initial[x]] == [q] and frames[initial[y]] == []
                and frames[final[x]] == [1 << j for j in range(9)]
                and len(frames[final[y]]) == 8
                and all((v & q).bit_count() % 2 == 0 for v in frames[final[y]]),
                f"main binding at port {port}")
    for position, pair in zip(hosted["Dports"], second_planes, strict=True):
        original = (live[position], live[position] + 112)
        require(all(graph[boundary][a] == graph[boundary][b]
                    for boundary in ("initial", "final") for a, b in zip(original, pair)),
                "separate hosted main partners in the same charts")
    require(all(r not in mains and (graph["initial"][r], graph["final"][r]) == (3, 237)
                for r in PROTECTED_HELPERS), "fixed rank-four same-owner helper boundaries")
    return mains, hosted_ports, second_planes


def expected_rows(n, layout, interface, unit):
    mains, hosted, second = interface
    rows = [{r: unit} for r in range(n)]
    for port, x in enumerate(layout["live"]):
        y = x + 112
        if port in hosted:
            rows[y][x] = unit
        else:
            rows[x][y] = -unit
            rows[y] = {x: exact_div(unit, 2), y: exact_div(unit, 2)}
    for x, y in second:
        rows[x][y] = -unit
    require(all(r in mains or row == {r: unit} for r, row in enumerate(rows)),
            "independent arbitrary helper definition")
    return rows


def graph_inputs(graph):
    n = len(graph["initial"])
    first = graph["first_output"]
    require(n in (1501, 1502) and first == 150522, "stable paid and public namespace")
    moves = {key: (a, b) for key, a, b in graph["moves"]}
    rows = {key: [(donor, exact_coefficient(coef)) for donor, coef in terms]
            for key, terms in graph["forms"]}
    terminal_keys = set(range(first, first + n))
    order = graph["schedule"]
    require(len(moves) == len(graph["moves"]) == 6142 and all(0 <= key < first for key in moves),
            "exact positive paid slots")
    require(len(rows) == len(graph["forms"]) == len(moves) + n
            and set(rows) == moves.keys() | terminal_keys and moves.keys().isdisjoint(terminal_keys)
            and len(order) == len(rows) and set(order) == rows.keys(),
            "exact held-bank schedule denominator")
    require(all([donor for donor, _ in row] == sorted({donor for donor, _ in row})
                for row in rows.values()), "unique donor keys in literal scalar order")
    return moves, rows


def graph_bounds(graph, moves, rows, mains):
    frames = graph["frames"]
    spans = list(map(chart_span, frames))
    starts, ends = graph["initial"], graph["final"]
    first = graph["first_output"]
    n = len(starts)
    require(all(type(chart) is int and 0 <= chart < len(spans) for chart in (*starts, *ends)),
            "valid public charts")

    def rank(a, b, helper=False):
        require(0 <= a < len(spans) and 0 <= b < len(spans), "valid paid chart IDs")
        require(spans[a] < spans[b] or (not helper and spans[b] < spans[a]),
                "strictly nested positive paid or helper charts")
        return abs(len(frames[b]) - len(frames[a]))

    paid = Counter(rank(a, b) for a, b in moves.values())
    productive = Counter(rank(starts[r], ends[r], helper=True) for r in range(n) if r not in mains)
    available = {~r: (chart, 1, Fraction(1)) for r, chart in enumerate(starts)}
    grid, peak_mass, peak_node = 1, Fraction(1), None
    for key in graph["schedule"]:
        a = moves[key][0] if key in moves else ends[key - first]
        row_grid, mass = 1, Fraction()
        for donor, q in rows[key]:
            require(donor in available and available[donor][0] == a,
                    f"donor unavailable or in wrong chart at row {key}")
            _, divisor, weight = available[donor]
            row_grid = lcm(row_grid, divisor * q.denominator)
            mass += abs(q) * weight
        grid = lcm(grid, row_grid)
        if mass > peak_mass:
            peak_mass, peak_node = mass, key
        if key in moves:
            available[key] = (moves[key][1], row_grid, mass)
    odd, height = grid_parts(grid)
    return {
        "public": n, "slots": len(moves), "terms": sum(map(len, rows.values())),
        "path_grid": grid, "path_grid_odd": odd, "path_grid_height": height,
        "positive_path_mass_bound_unscaled": str(peak_mass),
        "positive_path_mass_peak_node": peak_node,
        "paid_native_ranks": dict(paid), "positive_helper_ranks": dict(productive),
    }


def exact_basis_grid(graph, moves, rows, grid, expected):
    """Check every separate rational product, prefix and installed basis row."""
    values = {~r: {r: grid} for r in range(len(graph["initial"]))}
    product_gcd = snapshot_gcd = grid
    old_factor_lost = None
    n_checks = nontrivial = seven_checks = 0
    scale_without_seven = grid
    while scale_without_seven % 7 == 0:
        scale_without_seven //= 7
    seven_factor = grid // scale_without_seven
    peak_absolute = grid
    for key in graph["schedule"]:
        row, row_bound = {}, 0
        for donor, q in rows[key]:
            a, b = q.numerator, q.denominator
            n_checks += len(values[donor])
            nontrivial += len(values[donor]) if b != 1 else 0
            seven_checks += len(values[donor]) if b % 7 == 0 else 0
            for column, value in values[donor].items():
                product = exact_div(a * value, b)
                product_gcd = gcd(product_gcd, product)
                if old_factor_lost is None and product % seven_factor:
                    require(value % seven_factor == 0, "first under-scaled donor already off grid")
                    reduced_numerator = a * (value // seven_factor)
                    require(reduced_numerator % b, "removed seven must cause a literal DIV fault")
                    old_factor_lost = {
                        "row": key, "donor": donor, "entrance_column": column,
                        "coefficient": str(q), "removed_factor": seven_factor,
                        "numerator_without_seven": reduced_numerator, "denominator": b,
                        "positive_remainder": reduced_numerator % b,
                    }
                row_bound += abs(product)
                result = row.get(column, 0) + product
                if result:
                    row[column] = result
                else:
                    row.pop(column, None)
        peak_absolute = max(peak_absolute, row_bound)
        for value in row.values():
            snapshot_gcd = gcd(snapshot_gcd, value)
        if key in moves:
            values[key] = row
        else:
            require(row == expected[key - graph["first_output"]], f"wrong normalized endpoint {key}")
    return {
        "coefficient_products": n_checks, "checked_nontrivial_divisions": nontrivial,
        "checked_seven_divisions": seven_checks, "exact_all_public_rows": len(expected),
        "minimum_product_grid": grid // product_gcd, "minimum_snapshot_grid": grid // snapshot_gcd,
        "maximum_exact_row_prefix_mass_scaled": str(Fraction(peak_absolute, 1 << grid_parts(grid)[1])),
        "loss_of_seven_control": old_factor_lost,
    }


class HeldBank:
    """Finite tagged bank model with an isolated selector and copy staging."""

    def __init__(self, homes):
        self.homes = homes
        self.blank = object()
        self.left_guard = object()
        self.right_guard = object()
        self.dummy = object()
        self.left = self.left_guard
        self.right = self.right_guard
        self.slots = [self.dummy] + [("arbitrary old payload", -slot) for slot in range(1, homes + 1)]
        self.head = 0
        self.operations = Counter()
        self.trace = sha256()
        # Each stream is a separately guarded backing area. Selection uses
        # only the bank head, so a staged donor never lives in that head.
        self.streams = {name: self.blank for name in ("accumulator", "donor", "product", "quotient")}

    def access(self, slot, operation, replacement=None, expected=None):
        require(self.head == 0 and 1 <= slot <= self.homes, "bad guarded bank selection")
        self.head = slot
        old = self.slots[slot]
        if expected is not None:
            require(old is expected, "send before previous owner returned and cleared")
        if replacement is not None:
            self.slots[slot] = replacement
        self.head = 0
        self.operations[operation] += 1
        owner = replacement[0] if isinstance(replacement, tuple) else None
        self.trace.update(encoded([operation, slot, owner]))
        return old

    def close(self):
        require(self.head == 0 and self.slots[0] is self.dummy
                and self.left is self.left_guard and self.right is self.right_guard
                and all(slot is self.blank for slot in self.slots[1:])
                and all(stream is self.blank for stream in self.streams.values()),
                "packed bank and four stream retirement")


def held_schedule(graph, moves, rows, grid, expected, control=False):
    n, k, first = len(graph["initial"]), len(moves), graph["first_output"]
    entrance = {~r: r + 1 for r in range(n)}
    returned = {key: n + i + 1 for i, key in enumerate(sorted(moves))}
    terminal = {first + r: n + k + r + 1 for r in range(n)}
    sender = 2*n + k + 1
    scratch = range(sender + 1, sender + 5)
    allocated = set(entrance.values()) | set(returned.values()) | set(terminal.values()) | {sender} | set(scratch)
    require(allocated == set(range(1, 2*n + k + 6)), "injective bank home plan")
    bank = HeldBank(len(allocated))
    blank = bank.blank
    odd = grid_parts(grid)[0]
    binary_grid = grid // odd
    public = [
        (("public", r), chart, (binary_grid * ((r * 719 + 29) % 101 - 50),
                                binary_grid * ((r * 379 + 67) % 127 - 63)))
        for r, chart in enumerate(graph["initial"])
    ]
    original_public = public.copy()
    for slot in sorted(allocated):
        bank.access(slot, "initialize_complete_dirty_home", blank)
    for r, (_, chart, value) in enumerate(public):
        scaled = tuple(x * odd for x in value)
        bank.access(entrance[~r], "write_entrance", (("entry", r), chart, scaled), blank)
    known = dict(entrance)
    installed = set()
    outstanding = None
    attempted_early_reuse = False
    early = first + EARLY_ROLE if n == 1502 else None
    early_installed = None
    prefix_position = None

    def install(role, *, sealed=False):
        require(role not in installed, "same public owner installed twice")
        tag, chart, values = bank.access(terminal[first + role], "read_terminal_for_same_owner_install")
        predicted = tuple(exact_div(
            sum(q * original_public[i][2][axis] for i, q in expected[role].items()), grid)
            for axis in (0, 1))
        expected_tag = ("sealed terminal", role) if sealed else ("terminal", role)
        unscaled = tuple(exact_div(value, odd) for value in values)
        require(tag == expected_tag and chart == graph["final"][role] and unscaled == predicted,
                "wrong shape/chart, value or same-owner terminal install")
        public[role] = (("public", role), chart, unscaled)
        installed.add(role)
        bank.trace.update(encoded(["public_install_and_unscale", role, chart]))

    for position, key in enumerate(graph["schedule"]):
        if key == EARLY_LAST_DONOR:
            prefix_position = position
        if early is not None and key in LATER_DEPARTURES:
            require(early_installed is not None and EARLY_ROLE in installed
                    and public[EARLY_ROLE][:2] == (("public", EARLY_ROLE), 595),
                    "split suffix ran before the short return was installed on its public owner")
        paid = key in moves
        source, destination = moves[key] if paid else (graph["final"][key - first], None)
        require(bank.streams["accumulator"] is blank, "running accumulator already occupied")
        bank.streams["accumulator"] = (0, 0)
        for donor, q in rows[key]:
            require(early_installed is None or donor != ~EARLY_ROLE,
                    "old 281 entrance read after its public return")
            require(early is None or early_installed is not None or donor != ~(n - 1),
                    "fresh split owner read before the short public return")
            require(donor in known, "read before donor RETURN")
            saved = bank.access(known[donor], "read_immutable_donor")
            require(isinstance(saved, tuple) and len(saved) == 3, "donor retired before read")
            tag, chart, value = saved
            require(tag == (("entry", ~donor) if donor < 0 else ("returned", donor))
                    and chart == source, "wrong owner or chart at guarded GET")
            require(all(bank.streams[name] is blank for name in ("donor", "product", "quotient")),
                    "term workspace was live before GET")
            bank.streams["donor"] = value
            bank.streams["product"] = tuple(q.numerator * x for x in value)
            bank.streams["quotient"] = tuple(exact_div(x, q.denominator) for x in bank.streams["product"])
            bank.streams["accumulator"] = tuple(a + b for a, b in zip(
                bank.streams["accumulator"], bank.streams["quotient"], strict=True))
            for name in ("donor", "product", "quotient"):
                bank.streams[name] = blank
        value = bank.streams["accumulator"]
        bank.streams["accumulator"] = blank
        if paid:
            require(outstanding is None, "more than one outstanding native sender")
            bank.access(sender, "stage_full_sender", (("sender", key), source, value), blank)
            outstanding = key
            if control and not attempted_early_reuse:
                try:
                    bank.access(sender, "illegal_early_reuse", (("sender", key + 1), source, value), blank)
                except ValueError as failure:
                    require(str(failure) == "send before previous owner returned and cleared",
                            "wrong outstanding-sender control failure")
                    # A failing real move cannot continue. The control uses a
                    # separate attempted selected write, then restores its head.
                    bank.head = 0
                else:
                    raise ValueError("aliased outstanding sender accepted")
                attempted_early_reuse = True
            held_tag, held_chart, held_value = bank.access(sender, "read_parked_sender")
            require(outstanding == key and held_tag == ("sender", key) and held_chart == source,
                    "parked sender must survive until shape and complete return")
            # The MOVE is identity in normalized coordinates. Its full native
            # Gaussian operation and two adapters are checked separately.
            bank.access(returned[key], "write_complete_return",
                        (("returned", key), destination, held_value), blank)
            bank.access(sender, "clear_full_sender_after_return", blank)
            outstanding = None
            known[key] = returned[key]
        else:
            role = key - first
            bank.access(terminal[key], "write_terminal", (("terminal", role), source, value), blank)
            if key == early:
                require(prefix_position is not None and prefix_position < position and source == 595,
                        "short return must seal at the witnessed prefix cut")
                old = bank.access(terminal[key], "seal_complete_short_return",
                                  (("sealed terminal", role), source, value))
                require(old == (("terminal", role), source, value), "sealing must preserve full typed payload")
                install(role, sealed=True)
                bank.access(terminal[key], "clear_sealed_short_return_after_install", blank)
                old_entry = known.pop(~role)
                bank.access(old_entry, "retire_complete_home", blank)
                early_installed = position

    wanted_early = {EARLY_ROLE} if early is not None else set()
    require(outstanding is None and installed == wanted_early and len(known) == n+k-len(wanted_early)
            and all(public[r] == original_public[r] for r in range(n) if r not in wanted_early),
            "one lawful early public return and other public inputs intact through the native schedule")
    for r in range(n):
        if r not in installed:
            install(r)
    require(installed == set(range(n)) and all(
        record[:2] == (("public", role), graph["final"][role]) for role, record in enumerate(public)),
        "every public owner fully installed exactly once")
    retired_early = {entrance[~EARLY_ROLE]} if early is not None else set()
    for slot in sorted(allocated - retired_early):
        bank.access(slot, "retire_complete_home", blank)
    bank.close()
    wanted = {
        "initialize_complete_dirty_home": len(allocated), "write_entrance": n,
        "read_immutable_donor": sum(map(len, rows.values())),
        "stage_full_sender": k, "read_parked_sender": k,
        "write_complete_return": k, "clear_full_sender_after_return": k,
        "write_terminal": n, "read_terminal_for_same_owner_install": n,
        "retire_complete_home": len(allocated),
    }
    if early is not None:
        wanted["seal_complete_short_return"] = 1
        wanted["clear_sealed_short_return_after_install"] = 1
    require(bank.operations == wanted, "complete independent selected replay counts")
    return {
        "numerical_homes": len(allocated), "guarded_dummy_slots": 1,
        "max_outstanding_native_senders": 1, "declared_senders": 1,
        "immutable_entry_banks": n, "immutable_paid_return_banks": k,
        "deferred_terminal_banks": n, "native_scalar_scratch_homes": 4,
        "additional_independent_guarded_streams": len(bank.streams),
        "trace_sha256": bank.trace.hexdigest(), "selected_logical_operations": dict(bank.operations),
        "two_component_fixture_outputs": len(installed), "exact_odd_unscale_outputs": len(installed),
        "retired_and_guards_restored": True, "live_sender_alias_control_rejected": attempted_early_reuse,
        "short_return_sealed_schedule_position": early_installed,
        "short_return_sealed_at_public_role": EARLY_ROLE if early_installed is not None else None,
        "short_return_public_install_schedule_position": early_installed,
        "short_return_original_entrance_retired_at_install": len(retired_early) == 1,
        "nonretired_public_inputs_preserved_until_final_installs": True,
    }


def scalar_service(value, coefficient, signed_width):
    """Finite signed carry, quotient, exact remainder and padded installation."""
    a, b = abs(coefficient.numerator), coefficient.denominator
    magnitude = abs(value)
    require(magnitude.bit_length() < signed_width, "input width")
    padding = signed_width + 26
    carry, bits = 0, []
    for j in range(padding):
        carry += a * ((magnitude >> j) & 1)
        bits.append(carry & 1)
        carry >>= 1
    require(carry == 0, "padded product overflow")
    quotient = remainder = 0
    for bit in reversed(bits):
        trial = 2 * remainder + bit
        next_bit = int(trial >= b)
        remainder = trial - next_bit * b
        quotient = (quotient << 1) | next_bit
    require(remainder == 0, "physical remainder")
    require(quotient.bit_length() < signed_width, "installed scalar overflow")
    return -quotient if (value < 0) != (coefficient.numerator < 0) else quotient


def scalar_cases(graph_rows, caller, scales):
    factors = {factor for rows in graph_rows for row in rows.values() for _, factor in row}
    factors.update(Fraction(event[-1]) for event in caller["events"]
                   if event[0] != "J" and event[1] in ("ADD", "SCALE"))
    factors.update((Fraction(-1), Fraction(1), Fraction(-1, 2), Fraction(1, 2)))
    for scale in scales:
        factors.update((Fraction(scale), Fraction(1, scale), Fraction(-1, scale)))
    bits = max(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) for q in factors)
    require(bits <= 24, "all literal scalar and division conversions fit W+26")
    cases = 0
    for coefficient in sorted(factors):
        for k in (0, -127, -1, 1, 19, (1 << 68) + 1):
            value = k * coefficient.denominator
            signed_width = max(3, abs(value).bit_length()+2, abs(k * coefficient.numerator).bit_length()+2)
            require(scalar_service(value, coefficient, signed_width) == k * coefficient.numerator,
                    "fixed scalar sign/carry/remainder or installation")
            cases += 1
    for coefficient in (Fraction(1, 2), Fraction(-1, 7)):
        try:
            scalar_service(1, coefficient, 3)
        except ValueError as failure:
            require(str(failure) == "physical remainder", "wrong inexact scalar rejection")
        else:
            raise ValueError("nonintegral scalar installed")
    return {"distinct_scalar_and_conversion_factors": len(factors), "signed_bit_transducer_cases": cases,
            "coefficient_bits": bits, "rejected_one_tick_denominators": [2, 7],
            "retained_max_bits": 24, "component_padding": 26}


def caller_envelope(caller):
    """Majorize raw caller products with no cancellation or operator commutation."""
    roles = [(0, Fraction(1)) for _ in range(caller["roles"])]
    max_height, max_mass = 0, Fraction(1)
    pre_height, pre_mass = 0, Fraction(1)
    visits = Counter()

    def observe(*values):
        nonlocal max_height, max_mass
        for height, mass in values:
            max_height = max(max_height, height)
            max_mass = max(max_mass, mass)

    def scale(value, factor):
        height, mass = value
        return height + grid_parts(factor.denominator)[1], abs(factor) * mass

    def add(first, second):
        return max(first[0], second[0]), first[1] + second[1]

    stages = []
    for event in caller["events"]:
        if event[0] == "J":
            _, stage, (x, y, u, v), (a, b, alpha, beta) = event
            require((Fraction(alpha), Fraction(beta)) == (-1, Fraction(1, 2)),
                    "exact signed joint envelope coefficients")
            stages.append(stage)
            pre_height = max(pre_height, *(roles[j][0] for j in (x, y, u, v, a, b)))
            pre_mass = max(pre_mass, *(roles[j][1] for j in (x, y, u, v, a, b)))
            roles[y], roles[u] = add(roles[y], roles[x]), add(roles[u], roles[v])
            old_a, old_b = roles[a], roles[b]
            roles[a] = add(old_a, old_b)
            roles[b] = add(scale(old_a, Fraction(1, 2)), scale(old_b, Fraction(1, 2)))
            observe(roles[y], roles[u], roles[a], roles[b])
            continue
        kind, op, role, *args = event
        visits[op] += len(caller["types"][kind]["ports"])
        if op == "ADD":
            term = scale(roles[args[0]], Fraction(args[-1]))
            roles[role] = add(roles[role], term)
            observe(term)
        elif op == "SCALE":
            roles[role] = scale(roles[role], Fraction(args[-1]))
        elif op == "SWAP":
            donor = args[0]
            roles[role], roles[donor] = roles[donor], roles[role]
        elif op == "QUERY":
            roles[role] = add(roles[role], roles[args[0]])
        elif op == "LAMBDA":
            height, mass = roles[role]
            # (1 ± i)/2 and (1 ∓ i)/2 each have Gaussian l1 norm one.
            roles[role] = height + 1, 2 * mass
        else:
            require(op in {"IDLE_ONE", "IDLE_ODD"}, "unknown signed caller operation")
        observe(roles[role])
    require(stages == list(range(1, STAGES+1)), "complete exact 16-stage raw schedule")
    return {
        "records": len(caller["events"]), "stages": len(stages), "uses": dict(visits),
        "binary_height_at_all_completed_cuts_and_products": max_height,
        "binary_height_at_native_entrances": pre_height,
        "scaled_mass_at_all_cuts_and_products": str(CALLER_ODD * max_mass),
        "scaled_mass_at_native_entrances": str(CALLER_ODD * pre_mass),
        "normalized_bound_uses_no_cancellation_or_commutation": True,
    }


def replay_caller(caller, layout):
    path = HERE / "engines/caller/caller16.py"
    require(sha256(path.read_bytes()).hexdigest() == CALLER_REPLAY, "wrong signed caller engine")
    spec = importlib.util.spec_from_file_location("physical_signed_caller16", path)
    require(spec is not None and spec.loader is not None, "signed caller engine must be loadable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.signed_caller(caller, layout, CALLER_ODD, 9)
    require(result["calls"] == STAGES and result["roles"] == 68 and result["root_owners"] == 3536
            and result["exact_preproduct_divisions"] == 153295
            and Fraction(result["peak_scaled_mass"]) == Fraction(495734175, 2),
            "exact inherited caller odd scale and literal divide replay")
    roots_q = sum(len(specification["ports"]) * sum(row[0] < 0 for row in specification["diagonal"])
                  for specification in caller["types"].values())
    require(roots_q == 3536, "charge all root negative-q ordinary translations")
    envelope = caller_envelope(caller)
    require(envelope["uses"] == result["uses"], "independent weighted caller operation count")
    return result, envelope, roots_q


def ordinary_budget(native, signed, roots_q, scalar_bits):
    n, k, terms, homes = (native[key] for key in ("public", "slots", "terms", "numerical_homes"))
    conversions = 2 * (signed["root_owners"] + STAGES * n)
    short_clear_and_seal = int(n == 1502)
    # The predecessor charges all four independent streams at row/term
    # boundaries. Add a full reset/reinitialization allowance for each
    # reused source, beyond original fixed numeric-home initialization.
    resets = 2*homes + 8*(terms+k+n) + 4*n + 2*k + short_clear_and_seal
    transfers = 2*terms + 2*(k+n) + 6*k + 4*n + 2*short_clear_and_seal
    selector_l = 14*homes + 9
    selector_constant = 63*homes - 7*homes.bit_count() + 27*homes.bit_length() + 59
    selections = [resets*selector_l + transfers*(selector_l+128),
                  resets*selector_constant + transfers*(selector_constant+320)]
    selected = native["selected_logical_operations"]
    require(resets >= selected["initialize_complete_dirty_home"] + selected["retire_complete_home"]
            + selected["clear_full_sender_after_return"] + short_clear_and_seal,
            "full occupied resets and sender reuse charged")
    require(transfers >= 2 * (sum(selected.values()) - selected["initialize_complete_dirty_home"]
                              - selected["retire_complete_home"] - selected["clear_full_sender_after_return"]
                              - short_clear_and_seal), "complete staged copy visits charged")
    p = STAGES * k + sum(signed["fixed_caller_paid"].values())
    t = STAGES * sum(native["positive_helper_ranks"].values()) + sum(signed["fixed_root_targets"].values())
    uses = signed["uses"]
    maps = 2*(p+t+STAGES*400) + 2*(uses["IDLE_ONE"]+uses["IDLE_ODD"])
    maps += 3*uses["QUERY"] + uses["LAMBDA"] + uses["IDLE_ODD"] + roots_q
    scalar_count = 32 * (STAGES*(terms+4*(k+n)+2*n+homes+2*k+short_clear_and_seal)
                         + sum(uses.values()) + conversions)
    require(homes <= OLD_NATIVE_STOCK and native["additional_independent_guarded_streams"] == 4,
            "retained numerical home ceiling and extra independent streams")
    return {
        "native_numeric_homes": homes, "native_numeric_homes_plus_dummy": homes+1,
        "raw_numeric_homes": STAGES*homes, "raw_numeric_homes_plus_dummy": STAGES*(homes+1),
        "separate_guarded_streams_per_native": 4, "separate_guarded_streams_raw": STAGES*4,
        "odd_conversions": conversions, "reset_services_per_native": resets,
        "typed_selected_transfers_per_native": transfers,
        "selector_steps_per_selected_service_L_and_constant": [selector_l, selector_constant],
        "selected_total_steps_per_native_L_and_constant": selections,
        "scalar_services": scalar_count, "scalar_step_rate": 2**max(20, scalar_bits+8),
        "ordinary_map_slots": maps, "ordinary_elementary_record_upper": maps*4*(AMBIENT_CAP+1)**2,
        "raw_paid_positions": p, "raw_productive_targets": t, "root_negative_q_translations": roots_q,
        "compiled_ordinary_work": "Positive full-view resets, selects, copies, guide and layout setup/return, exact scalar/odd shifts, matchers, fixed descriptors, root normalization and all native/caller/child adapters.",
        "compiled_stock": "Disjoint occurrence-tagged bank tuple, dummy, guide, four guarded streams, complete public owners, matching child views, compiler and BIT workspace, and every parked ancestor.",
        "layout": {
            "padded_payload": "L'=N_c(2(W+26)+3)",
            "per_stage_selector_and_stream_tracks": 11,
            "aggregate_owned_tuple_M": "sum_stage[(homes+6)(L'+2)+ell(N_c)+ell(W+26)+max(ell(N_c),ell(W+26),ell(homes))+max(N_c,homes)+max(W+26,ell(homes))+10]",
            "shadow_cells_upper": "M+352",
            "complete_view_step_bound": "34*(256(M+352)+128) plus fixed-degree descriptor work",
        },
    }


def root_envelope(native, caller):
    max_binary = max(caller["binary_height_at_all_completed_cuts_and_products"],
                     *(caller["binary_height_at_native_entrances"] + side["path_grid_height"]
                       for side in native.values()))
    max_mass = max(Fraction(caller["scaled_mass_at_all_cuts_and_products"]),
                   *(Fraction(caller["scaled_mass_at_native_entrances"]) * side["path_grid_odd"]
                     * Fraction(side["positive_path_mass_bound_unscaled"])
                     for side in native.values()))
    mass_bits = ceiling_bits(max_mass)
    c = 2 * max(max_binary, mass_bits)
    return {
        "caller_odd": CALLER_ODD,
        "native_odd": {side: audit["path_grid_odd"] for side, audit in native.items()},
        "native_binary": {side: audit["path_grid_height"] for side, audit in native.items()},
        "context_mass_bound": str(max_mass), "context_mass_bits": mass_bits,
        "context_binary_bits": max_binary, "context_c": c,
        "H_guard": "bit_length(context_c*1920*153**1920*(H+1)**2) < H for each actual compiler bound H",
        "exact_grid": "2^(-p-D)",
        "signed_width": "W=p+h+2D+3",
        "temporary_width": "W+26",
    }


def qualify(parent, candidate, caller, layout):
    require(layout["source_word_sha256"] == SOURCE_WORD and layout["public"] == 1501,
            "exact 104-port header bound to predecessor source")
    require(parent["frames"] == candidate["frames"] and parent["moves"] == candidate["moves"],
            "only scalar forms and productive boundary may differ")
    require(candidate["initial"] == parent["initial"] + [595]
            and parent["final"][EARLY_ROLE] == 127 and candidate["final"][EARLY_ROLE] == 595
            and candidate["final"][:EARLY_ROLE] == parent["final"][:EARLY_ROLE]
            and candidate["final"][EARLY_ROLE+1:] == parent["final"][EARLY_ROLE+1:] + [127],
            "only retained shortened role and new distinct role change final charts")
    require(parent["initial"][EARLY_ROLE] == 3, "nominal shortened role starts in identity chart")
    signed, caller_bound, roots_q = replay_caller(caller, layout)
    native, all_rows = {}, []
    for side, graph in (("peer", parent), ("candidate", candidate)):
        interface = public_interface(graph, layout)
        moves, rows = graph_inputs(graph)
        all_rows.append(rows)
        audit = graph_bounds(graph, moves, rows, interface[0])
        grid = audit["path_grid"]
        expected = expected_rows(audit["public"], layout, interface, grid)
        native[side] = {
            **audit,
            **exact_basis_grid(graph, moves, rows, grid, expected),
            **held_schedule(graph, moves, rows, grid, expected, control=side == "candidate"),
        }
    peer, child = native["peer"], native["candidate"]
    require(peer["path_grid"] == 2025 << 18 and peer["terms"] == 169349
            and peer["coefficient_products"] == 8535132, "exact #7682 native positive grid anchor")
    require(child["loss_of_seven_control"] is not None and child["live_sender_alias_control_rejected"],
            "new odd factor and outstanding sender controls must reject")
    require(peer["paid_native_ranks"] == child["paid_native_ranks"]
            and Counter(child["positive_helper_ranks"]) - Counter(peer["positive_helper_ranks"]) == {1: 1, 8: 1}
            and Counter(peer["positive_helper_ranks"]) - Counter(child["positive_helper_ranks"]) == {9: 1},
            "one split productive field, all original paid ranks")
    require((peer["numerical_homes"], child["numerical_homes"]) == (9149, 9151),
            "same serial sender realization on both exact graphs")
    root = root_envelope(native, caller_bound)
    scalars = scalar_cases(all_rows, caller, (CALLER_ODD, *root["native_odd"].values()))
    ordinary = {side: ordinary_budget(audit, signed, roots_q, scalars["coefficient_bits"])
                for side, audit in native.items()}
    return {
        "status": "PASS_CHART595_BANK_PHYSICAL",
        "scope": "Exact normalized products and guarded occupied bank schedules, finite scalar services and conservative all-width instances of the selected five interfaces.",
        "native": native, "ordinary": ordinary, "scalar_services": scalars,
        "caller_exact": signed, "caller_hereditary_envelope": caller_bound, "common_exact_root": root,
        "both_graphs_respect_historical_numeric_homes_and_streams": True,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=HERE / "data/PARENT-GRAPH.json.gz")
    parser.add_argument("--candidate", type=Path, default=HERE / "data/CANDIDATE-GRAPH.json.gz")
    parser.add_argument("--caller", type=Path, default=HERE / "data/CALLER.json.gz")
    parser.add_argument("--caller-layout", type=Path, default=HERE / "data/CALLER-LAYOUT.json")
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    expected = {"peer": PEER, "candidate": args.candidate_sha256}
    peer, peer_gzip = load_gzip(args.parent, PEER)
    child, child_gzip = load_gzip(args.candidate, args.candidate_sha256)
    caller, caller_gzip = load_gzip(args.caller, CALLER, canonical=False)
    layout_raw = args.caller_layout.read_bytes()
    result = qualify(peer, child, caller, json.loads(layout_raw))
    result.update({
        "graphs": expected, "caller_sha256": CALLER,
        "transport_sha256": {"peer": peer_gzip, "candidate": child_gzip, "caller": caller_gzip},
        "caller_layout_sha256": sha256(layout_raw).hexdigest(),
    })
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(result["status"])


if __name__ == "__main__":
    main()
