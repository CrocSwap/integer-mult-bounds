"""Reverse per-owner exact contact and nested-chart audit of R80."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import alarm
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PRICE = "price/PRICE.json"
WORD = "inputs/7334-WORD.json.gz"
PINS = {
    PRICE: "76926ec9ff997159d281e0363326edb2e1aff8c530b041f361565030588e02cf",
    WORD: "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
WORD_CONTENT = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def verify_bytes(root, name):
    raw = (root / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError(f"changed dependency {name}")
    return raw


def exact_basis_spans(frames):
    @cache
    def span(chart):
        assert 0 <= chart < len(frames)
        s = {0}
        for mask in frames[chart]:
            assert type(mask) is int and 0 < mask < 512 and mask not in s
            s |= {v ^ mask for v in s}
        return frozenset(s)
    return span


def incidences(word, deadline):
    lower = word["public"]
    upper = lower + word["owned_fields"]
    by_owner = defaultdict(list)
    tape = word["program"]
    for clock in range(len(tape) - 1, -1, -1):
        if clock % 256 == 0 and monotonic() >= deadline:
            return by_owner, [0, clock]
        event = tape[clock]
        opcode, destination = event[:2]
        assert 0 <= destination < upper
        if opcode == "MOVE":
            assert event[4] == (destination >= lower)
        elif opcode in ("INIT", "CLEAR"):
            assert destination >= lower
        if destination >= lower:
            by_owner[destination].append((clock, "destination" if opcode in ("ADD", "COPY") else opcode))
        if opcode in ("ADD", "COPY"):
            source = event[2]
            assert 0 <= source < upper and source != destination
            if source >= lower:
                by_owner[source].append((clock, "source"))
    return by_owner, None


def reconstruct(word, by_owner, span):
    tape = word["program"]
    lifetimes = []
    for owner, rows in sorted(by_owner.items()):
        chart = clear = None
        contacts = []
        for clock, access in rows:
            event = tape[clock]
            opcode = event[0]
            if opcode == "CLEAR":
                assert clear is None
                chart, clear = event[2], clock
                span(chart)
            elif opcode == "INIT":
                assert clear is not None and event[2] == chart
                lifetimes.append((owner, clock, clear, tuple(reversed(contacts))))
                chart = clear = None
                contacts = []
            else:
                assert clear is not None
                if opcode == "MOVE":
                    begin, end = event[2:4]
                    assert end == chart
                    assert span(begin) < span(end) or span(end) < span(begin)
                    chart = begin
                else:
                    assert opcode in ("ADD", "COPY", "SCALE") and event[-1] == chart
                    Fraction(event[-2])
                contacts.append((clock, access))
        assert clear is None
    return sorted(lifetimes, key=lambda row: row[1])


def evaluate(word, deadline, cap, quotes=None):
    by_owner, unvisited_interval = incidences(word, deadline)
    if unvisited_interval is not None:
        return {
            "complete": False,
            "unvisited_literal_interval": unvisited_interval,
            "unvisited_geometry": None,
        }
    tape = word["program"]
    span = exact_basis_spans(word["frames"])
    dimensions = [len(basis) for basis in word["frames"]]
    hist = Counter()
    next_hist = Counter()
    owned_moves, pairs = [], []
    lives = reconstruct(word, by_owner, span)
    for owner, birth, clear, contacts in lives:
        positions = []
        for offset, (clock, access) in enumerate(contacts):
            if access != "MOVE":
                continue
            a, b = tape[clock][2:4]
            rank = abs(dimensions[b] - dimensions[a])
            hist[rank] += 1
            next_clock, next_access = contacts[offset + 1] if offset + 1 < len(contacts) else (clear, "CLEAR")
            next_op = tape[next_clock][0]
            next_hist[next_op] += 1
            owned_moves.append({
                "owner": owner, "birth": birth, "clear": clear, "clock": clock,
                "charts": [a, b], "rank": rank,
                "next_contact": [next_clock, next_op, next_access],
            })
            positions.append(offset)

        for left, right in zip(positions, positions[1:]):
            first, second = contacts[left][0], contacts[right][0]
            a, b = tape[first][2:4]
            mid, c = tape[second][2:4]
            assert mid == b
            a_dim, b_dim, c_dim = (dimensions[z] for z in (a, b, c))
            opposite = (b_dim - a_dim) * (c_dim - b_dim) < 0
            intervening = [
                [clock, tape[clock][0], access] for clock, access in contacts[left + 1:right]
            ]
            barriers = [contact for contact in intervening if contact[1] != "SCALE"]
            scales = [[clock, str(Fraction(tape[clock][2]))]
                      for clock, opcode, _ in intervening if opcode == "SCALE"]
            pair = {
                "key": [first, second, owner], "lifetime": [birth, clear],
                "charts": [a, b, c], "ranks": [a_dim, b_dim, c_dim],
                "paid_ranks": [abs(b_dim - a_dim), abs(c_dim - b_dim)],
                "opposite_direction": opposite,
                "intervening": intervening, "barriers": barriers, "scales": scales,
                "status": "same_direction" if not opposite else "binary_contact" if barriers else "geometry_pending",
            }
            pairs.append(pair)

    pairs.sort(key=lambda case: (case["key"][1], case["key"][2]))
    tested = 0
    geometry_pending = []
    for pair in pairs:
        if pair["status"] != "geometry_pending":
            continue
        if tested == cap or monotonic() >= deadline:
            geometry_pending.append(pair["key"])
            continue
        tested += 1
        a, _, c = pair["charts"]
        if a == c or span(a) < span(c) or span(c) < span(a):
            pair["status"] = "scale_survivor" if pair["scales"] else "contact_free_survivor_diagnostic"
            rank_key = ",".join(map(str, sorted(pair["paid_ranks"])))
            if quotes is not None:
                pair["quote"] = quotes[rank_key]
        else:
            pair["status"] = "outer_charts_not_strictly_nested"

    return {
        "complete": not geometry_pending, "literal_events": len(tape), "lifetimes": len(lives),
        "owned_paid": len(owned_moves), "owned_paid_by_rank": dict(sorted(hist.items())),
        "next_owned_contact_counts": dict(sorted(next_hist.items())),
        "moves": sorted(owned_moves, key=lambda row: row["clock"]),
        "pairs": pairs, "neighbor_pairs": len(pairs),
        "strict_opposite": sum(pair["opposite_direction"] for pair in pairs),
        "geometry_tested": tested, "unvisited_literal_interval": None,
        "unvisited_geometry": geometry_pending,
        "status_counts": dict(sorted(Counter(pair["status"] for pair in pairs).items())),
        "survivor_keys": [pair["key"] for pair in pairs if pair["status"] == "scale_survivor"],
        "contact_free_diagnostic_keys": [
            pair["key"] for pair in pairs if pair["status"] == "contact_free_survivor_diagnostic"
        ],
    }


def controls():
    def case(last, contacts, second_chart=3):
        tape = [
            ["INIT", 1, 1], ["MOVE", 1, 1, second_chart, True],
            *contacts, ["MOVE", 1, second_chart, last, True], ["CLEAR", 1, last],
        ]
        return evaluate({"public": 1, "owned_fields": 1, "frames": [[], [1], [1, 2], [1, 2, 4], [2]],
                         "program": tape}, monotonic() + 2, 4)

    scale = [["SCALE", 1, "-7/2", 3]]
    nested = case(2, scale)
    assert nested["survivor_keys"] == [[1, 3, 1]]
    assert nested["pairs"][0]["scales"] == [[2, "-7/2"]]
    assert case(1, [])["contact_free_diagnostic_keys"] == [[1, 2, 1]]
    assert case(4, scale)["status_counts"] == {"outer_charts_not_strictly_nested": 1}
    assert case(2, [["ADD", 0, 1, "1", 3]])["pairs"][0]["barriers"] == [[2, "ADD", "source"]]
    assert case(2, [["COPY", 1, 0, "1", 3]])["pairs"][0]["barriers"] == [[2, "COPY", "destination"]]
    reused = evaluate({
        "public": 1, "owned_fields": 1, "frames": [[], [1]],
        "program": [["INIT", 1, 0], ["MOVE", 1, 0, 1, True], ["CLEAR", 1, 1],
                    ["INIT", 1, 1], ["MOVE", 1, 1, 0, True], ["CLEAR", 1, 0]],
    }, monotonic() + 2, 4)
    assert reused["neighbor_pairs"] == 0
    return ["nonzero_signed_scale", "exact_return_diagnostic", "incomparable_outer_charts",
            "source_add_barrier", "destination_copy_barrier", "owner_reuse_barrier"]


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    root = parser.parse_args().root
    alarm(20)
    deadline = monotonic() + 18
    price = loads(verify_bytes(root, PRICE), object_pairs_hook=unique)
    assert price["head"] == HEAD and price["word_sha256"] == PINS[WORD]
    assert price["first_case_cap"] == 4 and price["runner_seconds_cap"] == 20
    word = loads(decompress(verify_bytes(root, WORD)), object_pairs_hook=unique)
    canonical = dumps(word, sort_keys=True, separators=(",", ":")).encode()
    assert sha256(canonical).hexdigest() == WORD_CONTENT
    tests = controls()
    result = evaluate(word, deadline, price["first_case_cap"], price["quotes"])
    if result["complete"]:
        assert result["owned_paid"] == 47 and result["lifetimes"] == 73
        assert {str(r): n for r, n in result["owned_paid_by_rank"].items()} == price["legacy_paid_owned_rank_stock"]
    result |= {
        "head": HEAD, "word_sha256": PINS[WORD], "price_sha256": PINS[PRICE],
        "input_sha256": PINS, "controls": tests, "case_cap": 4, "hard_seconds": 20,
        "scope": "Reverse per-owner owned MOVE neighbor census. Same lifetime. Strict opposite directions. SCALE-only or contact-free diagnostic. Exact chart-span containment. No build.",
    }
    print(dumps(result, indent=2, sort_keys=True))
    alarm(0)


if __name__ == "__main__":
    main()
