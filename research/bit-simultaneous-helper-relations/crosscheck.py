"""Column-nullspace cross-check and complete census on the eight small groups.

This path imports no code from the other verifier. Chronological bank witnesses
are solved in bank coordinates, with one equation per excluded entrance role.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parents[1] / "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def banks_from_sets(word, reverse):
    """Interpret a register as a chart and a set of independent entrance names."""
    entrance = word["final" if reverse else "start"]
    exit_charts = word["start" if reverse else "final"]
    state = {i: (chart, {i}) for i, chart in enumerate(entrance)}
    banks = defaultdict(list)

    def append(chart, clock, signal, rank):
        banks[chart].append((clock, sum(1 << role for role in signal), rank))

    for i, chart in enumerate(entrance):
        append(chart, ~i, {i}, 0)
    dim = {int(c): v["dim"] for c, v in word["frames"].items()}
    program = word["program"]
    for clock, event in enumerate(reversed(program) if reverse else program):
        op, i = event[:2]
        if op in ("INIT", "CLEAR"):
            if (op == "INIT") != reverse:
                check(i not in state, "live owned slot")
                state[i] = event[2], set()
            else:
                chart, _ = state.pop(i)
                check(chart == event[2], "retire chart")
        elif op == "SWAP":
            j = event[2]
            state[i], state[j] = state[j], state[i]
        elif op == "ADD":
            j, chart = event[2:]
            check(state[i][0] == state[j][0] == chart, "contact mismatch")
            dst, src = (j, i) if reverse else (i, j)
            state[dst][1].symmetric_difference_update(state[src][1])
        else:
            check(op == "MOVE", "unknown opcode")
            a, b = event[2:]
            if reverse:
                a, b = b, a
            chart, signal = state[i]
            check(chart == a, "move source")
            state[i] = b, signal
            append(b, clock, signal, abs(dim[a] - dim[b]))
    check(set(state) == set(range(len(entrance))), "surviving fields")
    for i, chart in enumerate(exit_charts):
        expected = {i}
        if reverse and i < 111:
            expected.add(i + 111)
        elif not reverse and 111 <= i < 222:
            expected.add(i - 111)
        check(state[i] == (chart, expected), "literal endpoint")
    return banks, entrance, exit_charts


class Receiver:
    def __init__(self, entries):
        self.entries = entries
        self.columns = defaultdict(int)
        for position, (_, value, _) in enumerate(entries):
            for role in bits(value):
                self.columns[role] |= 1 << position

    def clean(self, allowed):
        """Nullspace of the outside columns; free positions are latest bank tokens."""
        equations = {}
        for role, coefficients in self.columns.items():
            if role in allowed:
                continue
            while coefficients:
                first = (coefficients & -coefficients).bit_length() - 1
                if first not in equations:
                    equations[first] = coefficients
                    break
                coefficients ^= equations[first]
        back_order = sorted(equations, reverse=True)
        flag = {}
        for pos in range(len(self.entries)):
            if pos in equations:
                continue
            support = 1 << pos
            for j in back_order:
                if (support & equations[j]).bit_count() % 2:
                    support |= 1 << j
            check(support.bit_length() - 1 == pos, "chronological nullspace generator")
            value = 0
            for j in bits(support):
                value ^= self.entries[j][1]
            check(value and all(r in allowed for r in bits(value)), "nonzero clean vector")
            flag[pos] = value
        return flag


def span_labels(flag):
    """Every nonzero clean signal and the position of its unique latest bank."""
    values = {0: -1}
    for pos, value in sorted(flag.items()):
        check(value not in values, "linearly dependent birth")
        values.update({u ^ value: pos for u in values})
    del values[0]
    return values


def linear_coordinates(basis):
    """Decode by lowest-bit elimination independently of the ordered bank flag."""
    pivots = {}
    for i, v in enumerate(basis):
        tags = 1 << i
        while v:
            j = (v & -v).bit_length() - 1
            if j not in pivots:
                pivots[j] = v, tags
                break
            old, previous = pivots[j]
            v ^= old
            tags ^= previous
        else:
            raise ValueError("coordinate basis dependence")

    def coordinates(v):
        tags = 0
        while v:
            j = (v & -v).bit_length() - 1
            if j not in pivots:
                raise ValueError("signal outside span")
            old, previous = pivots[j]
            v ^= old
            tags ^= previous
        return tags
    return coordinates


def large_charges(result, roles, receivers, flags, full, mixed, reverse):
    a, d = result["entrance"], result["exit"]
    terminal = receivers[d].entries
    if reverse:
        # All but two terminal representatives are unit vectors. Solve each in
        # the original terminal bank. The last bank identifies its flag layer.
        basis = [1 << r for r in roles if r not in (332, 340)]
        basis += [(1 << 340) ^ (1 << 375), (1 << 332) ^ (1 << 333)]
        represent = linear_coordinates([signal for _, signal, _ in terminal])
        ordered = sorted((represent(v).bit_length() - 1, v) for v in basis)
        check([j for j, _ in ordered] == sorted(flags[d]), "terminal flag layers")
        ranks = [terminal[j][2] for j, _ in ordered]
        swaps = [(365, 156), (401, 237), (380, 200), (409, 329), (296, 251), (376, 162)]
        for left, right in swaps:
            check(set(ranks[right:left + 1]) == {1}, "rank-one terminal permutation")
            ordered[left], ordered[right] = ordered[right], ordered[left]
        basis = [v for _, v in ordered]
    else:
        basis = [1 << r for r in roles]
        ranks = [max(terminal[j][2] for j in flags[d])] * len(roles)
    coords = linear_coordinates(basis)
    profiles = [[r] for r in ranks]
    role_mask = sum(1 << r for r in roles)
    for c, receiver in receivers.items():
        if c in (a, d):
            continue
        values = span_labels(full[c] if c in mixed else flags[c])
        by_lead = {}
        for signal, j in values.items():
            if c in mixed:
                signal &= role_mask
                if not signal:
                    continue
            lead = coords(signal).bit_length() - 1
            by_lead[lead] = max(by_lead.get(lead, 0), receiver.entries[j][2])
        for lead, price in by_lead.items():
            profiles[lead].append(price)
    strings = [",".join(map(str, sorted(p))) for p in profiles]
    digest = sha256("".join(s + "\n" for s in strings).encode("ascii")).hexdigest()
    check(digest == result["ordered_profiles_sha256"], "all large-block coordinate prices in order")
    tariff = {1: 27, 2: 45, 4: 75}
    maximum = max(sum(tariff[r] for r in row) for row in profiles)
    check(maximum == result["max_numerator_over_27"] and maximum < 125, "strict large-block cap")
    histogram = Counter(strings)
    check(dict(histogram) == result["profile_counts"], "independent large-block prices")


def subspaces(n):
    """Yield each subspace once by whether it meets the new affine half."""
    spaces = [(0,)]
    for i in range(n):
        new = []
        for previous in spaces:
            remaining = set(range(1 << i))
            while remaining:
                first = min(remaining)
                coset = tuple(first ^ x for x in previous)
                remaining.difference_update(coset)
                new.append(previous + tuple((1 << i) | x for x in coset))
        spaces.extend(new)
    return spaces


def small_census(group, roles, receivers, flags):
    a, d = group["entrance"], group["exit"]
    rank = group["target_rank"]
    possible = defaultdict(int)
    by_rank = defaultdict(int)
    token_number = 0
    convert = linear_coordinates([1 << r for r in roles])
    for c, receiver in receivers.items():
        if c == a:
            continue
        positions = {}
        for signal, j in span_labels(flags[c]).items():
            if j not in positions:
                positions[j] = 1 << token_number
                token_number += 1
                by_rank[receiver.entries[j][2]] |= positions[j]
            possible[convert(signal)] |= positions[j]
    equal = 0
    powers = {1: 27, 2: 45, 4: 75}
    spaces = subspaces(len(roles))
    for space in spaces:
        k = len(space).bit_length() - 1
        removed = 0
        for value in space:
            removed |= possible[value]
        counts = {r: (tokens & removed).bit_count() for r, tokens in by_rank.items()}
        if rank == 6:
            check(counts == {1: k, 4: k}, "exceptional line census")
            continue
        price = sum(powers[r] * count for r, count in counts.items())
        check(price <= k * powers[rank], "actual small-block overcharge")
        if price == k * powers[rank]:
            check(counts.get(rank, 0) == k and sum(counts.values()) == k, "neutral tariff changes with power")
            equal += 1
    if rank != 6:
        check(equal == group["neutral_subspace_count"], "neutral subspace census")
    return len(spaces)


def check_side(word, receipt, reverse):
    banks, start, end = banks_from_sets(word, reverse)
    receivers = {c: Receiver(rows) for c, rows in banks.items()}
    all_roles = set(range(222, len(start)))
    groups = receipt["groups"]
    role_sets = [{r for r in all_roles if (start[r], end[r]) == (g["entrance"], g["exit"])} for g in groups]
    check(set.union(*role_sets) == all_roles and sum(map(len, role_sets)) == 437, "group partition")
    flags = [{c: receiver.clean(group) for c, receiver in receivers.items()} for group in role_sets]
    full = {c: receiver.clean(all_roles) for c, receiver in receivers.items()}
    big = role_sets[0]
    max_defects, mixed_ends = {}, {}
    high = 0
    for c, receiver in receivers.items():
        check(not receiver.clean(set()), "independent source tokens")
        small = receiver.clean(all_roles - big)
        delta = peak = 0
        for j, (_, _, rank) in enumerate(receiver.entries):
            before = delta
            delta += int(j in full[c]) - sum(j in space[c] for space in flags)
            peak = max(peak, delta)
            check(delta >= 0 and int(j in small) == sum(j in s[c] for s in flags[1:]), "block dimension")
            if not rank:
                check(delta == 0, "free decomposition")
            if rank > 1 and j in full[c]:
                check(before == delta == 0, "higher-price prefix")
                high += 1
        if peak:
            max_defects[str(c)] = peak
        if delta:
            mixed_ends[str(c)] = delta
            check(all(receiver.entries[j][2] == 1 for j in full[c]), "mixed unit remainder")
    check((max_defects, mixed_ends, high) ==
          (receipt["mixed_prefix_maximum_by_chart"], receipt["mixed_end_dimension_by_chart"],
           receipt["separated_higher_rank_births"]), "full nullspace certificate")
    check((len(receivers), sum(len(r.entries) for r in receivers.values())) ==
          (receipt["receiver_charts"], receipt["bank_prefixes"]), "all bank coverage")
    possible = Counter(receivers[c].entries[j][2] for c, spans in full.items() for j in spans
                       if receivers[c].entries[j][2] > 0)
    check({str(r): n for r, n in possible.items()} == receipt["paid_omittable_with_all_helpers_zero"],
          "all possible paid omissions")
    large_charges(groups[0], sorted(big), receivers, flags[0], full, set(map(int, mixed_ends)), reverse)
    return sum(small_census(g, sorted(rs), receivers, fs)
               for g, rs, fs in zip(groups[1:], role_sets[1:], flags[1:], strict=True))


if __name__ == "__main__":
    packed = NATIVE.read_bytes()
    check(sha256(packed).hexdigest() == "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
          "native archive digest")
    word = json.loads(gzip.decompress(packed))
    receipt = json.loads((HERE / "RESULT.json").read_bytes())
    total = sum(check_side(word, receipt[side], side == "transpose") for side in ("forward", "transpose"))
    print(f"PASS_BIT_SIMULTANEOUS_DUAL_CHECK small_block_subspaces={total} large_pivot_prices=820")
