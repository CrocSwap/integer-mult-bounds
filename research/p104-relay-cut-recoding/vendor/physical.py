#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact grids and occupied bank schedules for the cf6a banked relay.

Adapt the guarded bank and exact-root accounting of #7697, based on #7682.
The graph folds the supplied #7700 tape and contracts its role-1256 relay.
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
PEER = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
CANDIDATE = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
SOURCE_WORD = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
SOURCE_HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
SOURCE_CERTS = "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_REPLAY = "ced48867f07ca0143604aa98cfd74fa7453696b9d3221f7c230d73e9ab9ba81f"
STAGES = 16
CALLER_ODD = 2025
COMPILER_H = 14571800000000000000
AMBIENT_CAP = 153
PROTECTED_HELPERS = (325, 1087)
OLD_NATIVE_STOCK = 15290
REMOVED, SURVIVOR = 95828, 104442
RELAY_ROLE = 1256
RELAY_CHARTS = (476, 878, 127)
PAYLOAD_AXES = 4


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
    require(layout["public"] == n == len(graph["final"]) == 1501
            and len(layout["live"]) == len(layout["ports"]) == 104,
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
    require(n == 1501 and first == 154768, "stable paid and public namespace")
    moves = {key: (a, b) for key, a, b in graph["moves"]}
    rows = {key: [(donor, exact_coefficient(coef)) for donor, coef in terms]
            for key, terms in graph["forms"]}
    terminal_keys = set(range(first, first + n))
    order = graph["schedule"]
    require(len(moves) == len(graph["moves"]) and all(0 <= key < first for key in moves),
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
    odd_factors = {}
    for prime in (3, 5):
        reduced = grid
        while reduced % prime == 0:
            reduced //= prime
        require(reduced < grid, f"missing expected odd prime {prime}")
        odd_factors[prime] = grid // reduced
    off_grid_controls = {}
    n_checks = nontrivial = 0
    divisors = Counter()
    peak_absolute = grid
    for key in graph["schedule"]:
        row, row_bound = {}, 0
        for donor, q in rows[key]:
            a, b = q.numerator, q.denominator
            n_checks += len(values[donor])
            nontrivial += len(values[donor]) if b != 1 else 0
            if b != 1:
                divisors[b] += len(values[donor])
            for column, value in values[donor].items():
                product = exact_div(a * value, b)
                product_gcd = gcd(product_gcd, product)
                if len(off_grid_controls) < len(odd_factors):
                    for prime, factor in odd_factors.items():
                        if prime not in off_grid_controls and product % factor:
                            require(value % factor == 0, "first under-scaled donor already off grid")
                            reduced_numerator = a * (value // factor)
                            require(reduced_numerator % b, "removed odd factor must cause a literal DIV fault")
                            off_grid_controls[prime] = {
                                "row": key, "donor": donor, "entrance_column": column,
                                "coefficient": str(q), "removed_factor": factor,
                                "numerator_without_factor": reduced_numerator, "denominator": b,
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
        "checked_nontrivial_divisions_by_denominator": dict(divisors),
        "exact_all_public_rows": len(expected),
        "minimum_product_grid": grid // product_gcd, "minimum_snapshot_grid": grid // snapshot_gcd,
        "maximum_exact_row_prefix_mass_scaled": str(Fraction(peak_absolute, 1 << grid_parts(grid)[1])),
        "missing_odd_factor_controls": off_grid_controls,
    }


class HeldBank:
    """Finite extent fixture with typed payloads and separately guarded streams."""

    def __init__(self, homes):
        self.homes = homes
        self.blank = (None, None, (0,) * PAYLOAD_AXES)
        self.left_guard = object()
        self.right_guard = object()
        self.dummy = object()
        self.left = self.left_guard
        self.right = self.right_guard
        self.slots = [self.dummy] + [
            (("dirty", slot), -1, tuple((-1)**axis * (slot + axis) for axis in range(PAYLOAD_AXES)))
            for slot in range(1, homes + 1)
        ]
        self.head = 0
        self.operations = Counter()
        self.overwritten_cells = Counter()
        self.trace = sha256()
        # GET restores the selector head. Its complete donor and the running
        # accumulator have independent backing throughout the term.
        self.streams = {name: None for name in ("accumulator", "donor", "product", "quotient")}
        self.stream_resets = 0

    def access(self, slot, operation, replacement=None, *, require_blank=False, clear=False):
        require(self.head == 0 and 1 <= slot <= self.homes, "bad guarded bank selection")
        self.head = slot
        try:
            old = self.slots[slot]
            require(not require_blank or old == self.blank,
                    "send or install before previous full owner extent cleared")
            if clear:
                require(replacement is None and len(old[2]) == PAYLOAD_AXES, "wrong reset extent")
                # Scan every addressed payload cell without inspecting its
                # value or treating a normalized zero as a reset.
                cleared = tuple(0 for _ in old[2])
                self.slots[slot] = (None, None, cleared)
                self.overwritten_cells[operation] += len(cleared)
            if replacement is not None:
                require(len(replacement[2]) == PAYLOAD_AXES, "wrong staged copy extent")
                tag, chart, payload = replacement
                self.slots[slot] = (tag, chart, tuple(cell for cell in payload))
            self.operations[operation] += 1
            self.trace.update(encoded([operation, slot, old[0], replacement[0] if replacement else None]))
            return old
        finally:
            self.head = 0

    def reset_stream(self, name):
        live = self.streams[name]
        if live is not None:
            require(len(live) == PAYLOAD_AXES, "wrong stream reset extent")
        self.streams[name] = None
        self.stream_resets += 1

    def close(self):
        require(self.head == 0 and self.slots[0] is self.dummy
                and self.left is self.left_guard and self.right is self.right_guard
                and all(slot == self.blank for slot in self.slots[1:])
                and all(stream is None for stream in self.streams.values()),
                "packed bank and four stream retirement")


def rejected_write(bank, slot, record, control_operation):
    try:
        bank.access(slot, control_operation, record, require_blank=True)
    except ValueError as failure:
        require(str(failure) == "send or install before previous full owner extent cleared"
                and bank.head == 0, "wrong dirty or outstanding-sender control failure")
    else:
        raise ValueError("dirty or held payload accepted as blank")


def partial_clear_control():
    bank = HeldBank(2)
    old_unselected = bank.slots[2]
    # A missing final address remains dirty even though the tag, chart, and
    # all earlier positions have been cleared.
    bank.slots[1] = (None, None, (0,) * (PAYLOAD_AXES - 1) + (17,))
    record = (("fresh", 0), 3, (1,) * PAYLOAD_AXES)
    rejected_write(bank, 1, record, "partial_clear_fault")
    residue = bank.access(1, "clear_every_address", clear=True)
    require(residue[2][-1] == 17 and bank.slots[1] == bank.blank and bank.slots[2] == old_unselected,
            "complete overwrite must remove the residual and preserve neighbors")
    bank.access(1, "accepted_after_full_clear", record, require_blank=True)
    return {"dirty_unaddressed_last_cell_rejected": True, "neighbor_unchanged": True}


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
    odd = grid_parts(grid)[0]
    binary_grid = grid // odd
    public = [
        (("public", r), chart, tuple(
            binary_grid * ((r * (719 - 41*axis) + 29 + 37*axis) % 127 - 63)
            for axis in range(PAYLOAD_AXES)
        ))
        for r, chart in enumerate(graph["initial"])
    ]
    original_public = public.copy()
    for slot in sorted(allocated):
        old = bank.access(slot, "initialize_complete_dirty_home", clear=True)
        require(all(old[2]), "every initial fixture address must be dirty")
    for r, (_, chart, value) in enumerate(public):
        scaled = tuple(x * odd for x in value)
        bank.access(entrance[~r], "write_entrance", (("entry", r), chart, scaled), require_blank=True)
    known = dict(entrance)
    installed = set()
    outstanding = None
    attempted_early_reuse = False

    for key in graph["schedule"]:
        paid = key in moves
        source, destination = moves[key] if paid else (graph["final"][key - first], None)
        require(bank.streams["accumulator"] is None, "running accumulator already occupied")
        bank.streams["accumulator"] = (0,) * PAYLOAD_AXES
        for donor, q in rows[key]:
            require(donor in known, "read before donor RETURN")
            tag, chart, value = bank.access(known[donor], "read_immutable_donor")
            require(tag == (("entry", ~donor) if donor < 0 else ("returned", donor))
                    and chart == source, "wrong owner or chart at guarded GET")
            require(all(bank.streams[name] is None for name in ("donor", "product", "quotient")),
                    "term workspace was live before GET")
            bank.streams["donor"] = tuple(cell for cell in value)
            bank.streams["product"] = tuple(q.numerator * x for x in bank.streams["donor"])
            bank.streams["quotient"] = tuple(exact_div(x, q.denominator) for x in bank.streams["product"])
            bank.streams["accumulator"] = tuple(a + b for a, b in zip(
                bank.streams["accumulator"], bank.streams["quotient"], strict=True))
            for name in ("donor", "product", "quotient"):
                bank.reset_stream(name)
        value = bank.streams["accumulator"]
        if paid:
            require(outstanding is None and key not in known, "invalid new native sender")
            bank.access(sender, "initialize_empty_sender_before_departure", require_blank=True, clear=True)
            record = (("sender", key), source, value)
            bank.access(sender, "stage_full_sender", record, require_blank=True)
            outstanding = key
            if control and key == SURVIVOR:
                rejected_write(bank, sender, (("sender", key + 1), source, value), "early_sender_fault")
                require(bank.slots[sender] == record and key not in known and bank.slots[returned[key]] == bank.blank,
                        "fault disturbed the parked sender or exposed an incomplete return")
                attempted_early_reuse = True
            held_tag, held_chart, held_value = bank.access(sender, "read_parked_sender")
            require(outstanding == key and held_tag == ("sender", key) and held_chart == source,
                    "parked sender must survive until shape and complete return")
            # Native checks supply both complete adapters and the paid
            # Gaussian child. Their normalized composite preserves this value.
            returned_record = (("returned", key), destination, held_value)
            bank.access(returned[key], "write_complete_return", returned_record, require_blank=True)
            bank.access(sender, "clear_full_sender_after_return", clear=True)
            require(bank.head == 0, "sender head not restored after full retirement")
            outstanding = None
            known[key] = returned[key]
        else:
            role = key - first
            bank.access(terminal[key], "write_terminal", (("terminal", role), source, value), require_blank=True)
        bank.reset_stream("accumulator")

    require(outstanding is None and len(known) == n+k and public == original_public,
            "all full public entrances must remain intact throughout the native schedule")
    for role in range(n):
        tag, chart, values = bank.access(terminal[first + role], "read_terminal_for_same_owner_install")
        predicted = tuple(exact_div(
            sum(q * original_public[i][2][axis] for i, q in expected[role].items()), grid)
            for axis in range(PAYLOAD_AXES))
        unscaled = tuple(exact_div(value, odd) for value in values)
        require(tag == ("terminal", role) and chart == graph["final"][role] and unscaled == predicted,
                "wrong extent, chart, value or same-owner terminal install")
        public[role] = (("public", role), chart, unscaled)
        installed.add(role)
        bank.trace.update(encoded(["public_install_and_unscale", role, chart]))
    require(installed == set(range(n)) and all(
        record[:2] == (("public", role), graph["final"][role]) for role, record in enumerate(public)),
        "every public owner fully installed exactly once")
    for slot in sorted(allocated):
        bank.access(slot, "retire_complete_home", clear=True)
    bank.close()
    terms = sum(map(len, rows.values()))
    wanted = {
        "initialize_complete_dirty_home": len(allocated), "write_entrance": n,
        "read_immutable_donor": terms, "initialize_empty_sender_before_departure": k,
        "stage_full_sender": k, "read_parked_sender": k, "write_complete_return": k,
        "clear_full_sender_after_return": k, "write_terminal": n,
        "read_terminal_for_same_owner_install": n, "retire_complete_home": len(allocated),
    }
    resets = {
        op: count * PAYLOAD_AXES for op, count in wanted.items()
        if op in {"initialize_complete_dirty_home", "initialize_empty_sender_before_departure",
                  "clear_full_sender_after_return", "retire_complete_home"}
    }
    require(bank.operations == wanted and bank.overwritten_cells == resets
            and bank.stream_resets == 3*terms+k+n, "complete independent selected replay counts")
    return {
        "numerical_homes": len(allocated), "guarded_dummy_slots": 1, "separate_guide_tracks": 1,
        "max_outstanding_native_senders": 1, "declared_senders": 1,
        "immutable_entry_banks": n, "immutable_paid_return_banks": k,
        "deferred_terminal_banks": n, "native_scalar_scratch_homes": 4,
        "additional_independent_guarded_streams": len(bank.streams),
        "trace_sha256": bank.trace.hexdigest(), "selected_logical_operations": dict(bank.operations),
        "fixture_addressed_cells_per_home": PAYLOAD_AXES,
        "fixture_addressed_cells_overwritten": dict(bank.overwritten_cells),
        "tracked_stream_reset_visits": bank.stream_resets,
        "same_owner_complete_fixture_outputs": len(installed), "exact_odd_unscale_outputs": len(installed),
        "retired_and_guards_restored": True, "live_sender_alias_control_rejected": attempted_early_reuse,
        "all_public_inputs_preserved_until_final_installs": True,
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
    rejected_denominators = (2, 3, 5, 7)
    for denominator in rejected_denominators:
        try:
            scalar_service(1, Fraction(-1, denominator), 3)
        except ValueError as failure:
            require(str(failure) == "physical remainder", "wrong inexact scalar rejection")
        else:
            raise ValueError("nonintegral scalar installed")
    return {"distinct_scalar_and_conversion_factors": len(factors), "signed_bit_transducer_cases": cases,
            "coefficient_bits": bits, "rejected_one_tick_denominators": rejected_denominators,
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
    reset_counts = {
        "dirty_home_initializations_and_retirements": 2 * homes,
        "term_and_row_stream_initializations_and_retirements": 8 * (terms + k + n),
        "owner_scale_unscale_stream_initializations_and_retirements": 4 * n,
        "sender_reinitializations_and_retirements": 2 * k,
    }
    transfer_counts = {
        "complete_scalar_donor_staging_legs": 2 * terms,
        "complete_sender_and_terminal_staging_legs": 2 * (k + n),
        "paid_parked_sender_return_and_adapter_legs": 6 * k,
        "immutable_entrance_and_public_terminal_install_legs": 4 * n,
    }
    resets, transfers = sum(reset_counts.values()), sum(transfer_counts.values())
    selector_l = 14*homes + 9
    selector_constant = 63*homes - 7*homes.bit_count() + 27*homes.bit_length() + 59
    # Allow the separate full overwrite scan for every reset, in addition
    # to the selector/reset bound, including the stream resets.
    selections = [resets*(selector_l+2) + transfers*(selector_l+128),
                  resets*(selector_constant+3) + transfers*(selector_constant+320)]
    selected = native["selected_logical_operations"]
    checked_home_resets = sum(selected[op] for op in native["fixture_addressed_cells_overwritten"])
    checked_copy_visits = sum(selected.values()) - checked_home_resets
    require(checked_home_resets == 2*(homes+k)
            and resets >= checked_home_resets + native["tracked_stream_reset_visits"],
            "full occupied resets, sender reuse and independent stream resets charged")
    require(checked_copy_visits == terms+3*(k+n) and transfers == 2*checked_copy_visits + 2*k,
            "all staged copy visits plus complete paid adapter legs charged")
    p = STAGES * k + sum(signed["fixed_caller_paid"].values())
    t = STAGES * sum(native["positive_helper_ranks"].values()) + sum(signed["fixed_root_targets"].values())
    uses = signed["uses"]
    maps = 2*(p+t+STAGES*400) + 2*(uses["IDLE_ONE"]+uses["IDLE_ODD"])
    maps += 3*uses["QUERY"] + uses["LAMBDA"] + uses["IDLE_ODD"] + roots_q
    scalar_counts = {
        "literal_native_products_and_accumulations": STAGES * terms,
        "width_padded_native_row_lifecycles": STAGES * 4 * (k + n),
        "public_boundary_installations_and_scale_preparations": STAGES * 2 * n,
        "private_home_flags_and_cleanup": STAGES * homes,
        "serial_sender_initialization_and_retirement": STAGES * 2 * k,
        "weighted_signed_caller_operation_slots": sum(uses.values()),
        "complete_array_odd_conversions": conversions,
    }
    scalar_count = 32 * sum(scalar_counts.values())
    require(homes <= OLD_NATIVE_STOCK and native["additional_independent_guarded_streams"] == 4,
            "retained numerical home ceiling and extra independent streams")
    return {
        "native_numeric_homes": homes, "native_numeric_homes_plus_dummy": homes+1,
        "raw_numeric_homes": STAGES*homes, "raw_numeric_homes_plus_dummy": STAGES*(homes+1),
        "separate_guarded_guide_tracks_per_native": 1, "separate_guarded_guide_tracks_raw": STAGES,
        "separate_guarded_streams_per_native": 4, "separate_guarded_streams_raw": STAGES*4,
        "odd_conversions": conversions, "reset_services_per_native": resets,
        "typed_selected_transfers_per_native": transfers,
        "reset_services_by_kind_per_native": reset_counts,
        "typed_transfer_legs_by_kind_per_native": transfer_counts,
        "reset_services_all_native_stages": STAGES * resets,
        "typed_selected_transfer_legs_all_native_stages": STAGES * transfers,
        "selector_steps_per_selected_service_L_and_constant": [selector_l, selector_constant],
        "additional_full_overwrite_steps_per_reset_L_and_constant": [2, 3],
        "selected_total_steps_per_native_L_and_constant": selections,
        "selected_total_steps_raw_L_and_constant": [STAGES * part for part in selections],
        "scalar_services": scalar_count, "scalar_step_rate": 2**max(20, scalar_bits+8),
        "raw_scalar_incidence_allowance_before_factor_32": scalar_counts,
        "ordinary_map_slots": maps, "ordinary_elementary_record_upper": maps*4*(AMBIENT_CAP+1)**2,
        "raw_paid_positions": p, "raw_productive_targets": t, "root_negative_q_translations": roots_q,
        "native_paid_wrappers": STAGES * k,
        "native_productive_wrappers": STAGES * sum(native["positive_helper_ranks"].values()),
        "ordinary_main_pair_slots": STAGES * 400,
        "compiled_ordinary_work": "Full-view resets, selects, copies, guide and layout setup and return, exact scalar and odd conversions, matchers, fixed descriptors, root normalization, and all native, caller and child adapters.",
        "compiled_stock": "Disjoint occurrence-tagged bank tuples, dummy origins, guides and four guarded streams per stage; complete public owners, matching child views, compiler and BIT workspace, and every parked ancestor.",
        "layout": {
            "padded_payload": "L'=N_c(2(W+26)+3)",
            "per_stage_selector_and_stream_tracks": 11,
            "guide_setup_and_retirement": "q(N_c)+q(W')+22N_cW'+36N_c+7W'+36+7L'+10; q(x)=24x-7popcount(x)+15ell(x)+12; W'=W+26",
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


def relay_edit(parent, candidate, word):
    require(all(parent[field] == candidate[field] == word[field]
                for field in ("frames", "initial", "final")),
            "same complete raw chart atlas and public owner shapes")
    require(parent["first_output"] == candidate["first_output"] == len(word["program"]),
            "stable raw clocks and complete public output namespace")
    enter, middle, leave = RELAY_CHARTS
    require(word["program"][REMOVED] == ["MOVE", RELAY_ROLE, enter, middle, False]
            and word["program"][SURVIVOR] == ["MOVE", RELAY_ROLE, middle, leave, False],
            "literal nonproductive source relay on owner 1256")
    parent_moves, parent_rows = graph_inputs(parent)
    child_moves, child_rows = graph_inputs(candidate)
    raw_moves = {clock: (event[2], event[3]) for clock, event in enumerate(word["program"])
                 if event[0] == "MOVE"}
    require(parent_moves == raw_moves and len(raw_moves) == 6144 and len(child_moves) == 6143,
            "exact source and contracted paid denominators")
    require(child_moves == {key: (enter, leave) if key == SURVIVOR else edge
                            for key, edge in parent_moves.items() if key != REMOVED},
            "only one direct paid edge replaces the two source children")
    require(parent_rows[SURVIVOR] == [(REMOVED, Fraction(1))]
            and [key for key, terms in parent_rows.items() if any(donor == REMOVED for donor, _ in terms)]
            == [SURVIVOR],
            "pure single-consumer relay")
    require(child_rows == {key: parent_rows[REMOVED] if key == SURVIVOR else terms
                           for key, terms in parent_rows.items() if key != REMOVED},
            "retained paid sender uses exactly four substituted source terms")
    edited = {REMOVED, SURVIVOR}
    require([key for key in candidate["schedule"] if key not in edited]
            == [key for key in parent["schedule"] if key not in edited],
            "relative schedule order of all rows outside the relay")
    positions = (parent["schedule"].index(REMOVED), parent["schedule"].index(SURVIVOR),
                 candidate["schedule"].index(SURVIVOR))
    require(positions == (3308, 4114, 3310), "exact old and new zero-based relay schedule positions")
    a, b, c = (chart_span(word["frames"][chart]) for chart in RELAY_CHARTS)
    require(a < b < c and (len(a), len(b), len(c)) == (8, 64, 512),
            "strict consecutive ranks 3+3, direct rank 6")
    return {"role": RELAY_ROLE, "removed_paid_key": REMOVED, "surviving_paid_key": SURVIVOR,
            "ordered_charts": list(RELAY_CHARTS), "old_ranks": [3, 3], "new_rank": 6,
            "new_sender_donors": [[donor, str(coef)] for donor, coef in child_rows[SURVIVOR]],
            "schedule_positions_zero_based": {"parent_removed": positions[0], "parent_survivor": positions[1],
                                              "candidate_survivor": positions[2]},
            "relative_order_unchanged_rows": len(candidate["schedule"]) - 1,
            "row_later_relay_consumers": 1, "new_recursive_charges_outside_replacement": 0}


def check_raw_clear_inventory(word, certs):
    indices = {str(clock) for clock, event in enumerate(word["program"]) if event[0] == "CLEAR"}
    certificates = certs["clear_event_index"]
    count = sum(len(terms) for terms in certificates.values())
    require(certs["candidate_canonical_sha256"] == SOURCE_WORD and set(certificates) == indices
            and len(indices) == 235 and count == 1135, "source raw CLEAR certificate inventory")
    return {"raw_clear_clocks": len(indices), "normalized_source_terms": count,
            "bank_execution_source": "complete addressed retirement in the new banked schedule",
            "raw_clear_role": "source-word chronological normalized proof; graph replay checks its own ownership"}


def check_depth_guard(root, h):
    require(h > 0, "positive compiler H")
    k_star = 1920 * 153**1920 * (h + 1)**2
    bits = (root["context_c"] * k_star).bit_length()
    require(bits < h, "common exact-root depth guard")
    return {"compiler_H": h, "argument_bit_length": bits, "strict_guard_passed": True}


def qualify(parent, candidate, word, certs, caller, h):
    relay = relay_edit(parent, candidate, word)
    clear_inventory = check_raw_clear_inventory(word, certs)
    signed, caller_bound, roots_q = replay_caller(caller, word)
    native, all_rows = {}, []
    for side, graph in (("parent", parent), ("candidate", candidate)):
        interface = public_interface(graph, word)
        moves, rows = graph_inputs(graph)
        all_rows.append(rows)
        audit = graph_bounds(graph, moves, rows, interface[0])
        grid = audit["path_grid"]
        expected = expected_rows(audit["public"], word, interface, grid)
        native[side] = {
            **audit,
            **exact_basis_grid(graph, moves, rows, grid, expected),
            **held_schedule(graph, moves, rows, grid, expected, control=side == "candidate"),
        }
    parent_audit, child = native["parent"], native["candidate"]
    require(parent_audit["path_grid"] == 2025 << 20 and parent_audit["terms"] == 172415
            and parent_audit["coefficient_products"] == 9044218, "independent G3 folded native anchor")
    require(set(child["missing_odd_factor_controls"]) == {3, 5} and child["live_sender_alias_control_rejected"],
            "actual under-scaled literal divisions and outstanding sender controls must reject")
    old_paid = Counter(parent_audit["paid_native_ranks"])
    new_paid = Counter(child["paid_native_ranks"])
    require(new_paid - old_paid == {6: 1} and old_paid - new_paid == {3: 2}
            and child["positive_helper_ranks"] == parent_audit["positive_helper_ranks"],
            "exact paid replacement, unchanged productive ranks")
    require(sum(rank * count for rank, count in new_paid.items())
            == sum(rank * count for rank, count in old_paid.items()), "paid rank mass conservation")
    require((parent_audit["numerical_homes"], child["numerical_homes"]) == (9151, 9150),
            "complete serial sender realization on both exact graphs")
    root = root_envelope(native, caller_bound)
    scalars = scalar_cases(all_rows, caller, (CALLER_ODD, *root["native_odd"].values()))
    ordinary = {side: ordinary_budget(audit, signed, roots_q, scalars["coefficient_bits"])
                for side, audit in native.items()}
    return {
        "status": "PASS_CF6A_RELAY_BANK_PHYSICAL",
        "scope": "Complete folded normalized products, all public endpoints, charged guarded bank schedules, finite scalar services and common exact root under the retained physical and recursive interfaces.",
        "relay": relay, "raw_clear_source_inventory": clear_inventory,
        "native": native, "ordinary": ordinary, "scalar_services": scalars,
        "physical_controls": partial_clear_control(),
        "caller_exact": signed, "caller_hereditary_envelope": caller_bound, "common_exact_root": root,
        "bit_guard": check_depth_guard(root, h),
        "both_graphs_respect_historical_numeric_homes_and_streams": True,
        "inherited_private_home_cap_per_stage": OLD_NATIVE_STOCK,
        "raw_stage_count": STAGES,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--parent", type=Path, default=HERE / "data/PARENT-GRAPH.json.gz")
    parser.add_argument("--candidate", type=Path, default=HERE / "data/CANDIDATE-GRAPH.json.gz")
    parser.add_argument("--word", type=Path, default=HERE / "data/WORD.json.gz")
    parser.add_argument("--certs", type=Path, default=HERE / "data/CERTS.json")
    parser.add_argument("--caller", type=Path, default=HERE / "data/CALLER.json.gz")
    parser.add_argument("--candidate-sha256", default=CANDIDATE)
    parser.add_argument("--compiler-H", type=int, default=COMPILER_H)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    require(args.candidate_sha256 == CANDIDATE, "wrong frozen candidate pin")
    parent, parent_gzip = load_gzip(args.parent, PEER)
    child, child_gzip = load_gzip(args.candidate, CANDIDATE)
    word, word_gzip = load_gzip(args.word, SOURCE_WORD)
    caller, caller_gzip = load_gzip(args.caller, CALLER, canonical=False)
    certs_raw = args.certs.read_bytes()
    require(sha256(certs_raw).hexdigest() == SOURCE_CERTS, "wrong literal raw CLEAR certificate binding")
    result = qualify(parent, child, word, json.loads(certs_raw), caller, args.compiler_H)
    result.update({
        "graphs": {"parent": PEER, "candidate": CANDIDATE}, "caller_sha256": CALLER,
        "source_head": SOURCE_HEAD, "source_word_sha256": SOURCE_WORD, "source_certs_sha256": SOURCE_CERTS,
        "transport_sha256": {"parent": parent_gzip, "candidate": child_gzip, "word": word_gzip,
                             "caller": caller_gzip},
    })
    if args.out is None:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        with args.out.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write("\n")
        print(result["status"])


if __name__ == "__main__":
    main()
