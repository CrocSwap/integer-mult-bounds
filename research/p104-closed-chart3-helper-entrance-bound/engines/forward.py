"""One-pass chronology and closed-component check for chart-3 helper entrances."""
import argparse
import gzip
import hashlib
import json
import signal
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
GZIP_PIN = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
JSON_PIN = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CHART = 3
LIMIT = 10


def timeout(_signal, _frame):
    raise TimeoutError("10-second one-word chronology cap")


def unique(pairs):
    values = dict(pairs)
    if len(values) != len(pairs):
        raise ValueError("duplicate JSON key")
    return values


def involved(event):
    kind, destination, *rest = event
    if kind in ("ADD", "COPY"):
        return (destination, rest[0])
    assert kind in ("SCALE", "MOVE", "INIT", "CLEAR")
    return (destination,)


def capture(events, chart3_helpers):
    first_moves = {}
    early_contacts = defaultdict(list)
    for clock, event in enumerate(events):
        touching = set(involved(event)) & chart3_helpers
        for role in touching:
            if role in first_moves:
                continue
            if event[0] == "MOVE":
                assert role == event[1] and event[2] == CHART
                first_moves[role] = (clock, event)
            else:
                early_contacts[role].append((clock, event))
    return first_moves, early_contacts


def proper(word, helpers, first_moves):
    frames = word["frames"]

    @lru_cache(maxsize=None)
    def span(chart):
        space = {0}
        for x in frames[chart]:
            assert 0 < x < 512 and x not in space
            space.update([x ^ old for old in space])
        return space

    outcomes, candidates = {}, {}
    assert span(CHART) == {0}
    for role in sorted(helpers):
        start, end = word["initial"][role], word["final"][role]
        if start != CHART:
            outcomes[role] = "other_initial_chart"
            continue
        if role not in first_moves:
            outcomes[role] = "no_literal_move"
            continue
        clock, event = first_moves[role]
        middle = event[3]
        depth, height = len(frames[middle]), len(frames[end])
        if event[-1] is not False:
            outcome = "first_move_not_paid_ascent"
        elif depth == 0 or not span(middle) <= span(end):
            outcome = "no_proper_nested_first_ascent"
        elif depth == height:
            outcome = "zero_residual_target"
        else:
            assert 0 < depth < height and span(middle) < span(end)
            outcome = "proper"
            candidates[role] = (clock, middle, depth, height)
        outcomes[role] = outcome
    return outcomes, candidates


def components(word, main, early_contacts, candidates):
    adjacency = {r: set() for r in candidates}
    blocked = defaultdict(list)
    moved = defaultdict(set)
    for role, (_, middle, _, _) in candidates.items():
        for clock, event in early_contacts[role]:
            kind, dest, *rest = event
            reason = None
            if kind == "SCALE" and event[-1] == CHART:
                moved[role].add(clock)
                continue
            if kind != "ADD":
                reason = "non_ADD_SCALE_contact"
            elif event[-1] != CHART:
                reason = "different_old_chart"
            else:
                src = rest[0]
                peer = src if role == dest else dest
                if peer in main:
                    reason = "main_contact"
                elif peer >= word["public"]:
                    reason = "owned_contact"
                elif peer not in candidates:
                    reason = "ineligible_helper_contact"
                elif middle != candidates[peer][1]:
                    reason = "different_first_upper_chart"
                elif clock >= candidates[peer][0]:
                    reason = "peer_past_first_MOVE"
                elif role == peer:
                    moved[role].add(clock)
                    continue
                else:
                    adjacency[role].add(peer)
                    adjacency[peer].add(role)
                    moved[role].add(clock)
                    continue
            blocked[role].append(dict(role=role, clock=clock, event=event, reason=reason))

    groups = []
    unseen = set(candidates)
    while unseen:
        seed = min(unseen)
        group = {seed}
        stack = [seed]
        while stack:
            for peer in adjacency[stack.pop()] - group:
                group.add(peer)
                stack.append(peer)
        unseen -= group
        roles = sorted(group)
        barriers = sorted((b for r in roles for b in blocked[r]), key=lambda b: (b["clock"], b["role"]))
        assert len({candidates[r][1] for r in roles}) == 1
        edits = sorted(set().union(*(moved[r] for r in roles)))
        scale_only_singleton = len(roles) == 1 and edits and all(
            word["program"][clock][0] == "SCALE" for clock in edits
        )
        admitted = not barriers and bool(edits) and (len(roles) > 1 or scale_only_singleton)
        groups.append(dict(
            roles=roles, chart=candidates[seed][1], pre_contact_clocks=edits,
            first_moves=[[r,*candidates[r]] for r in roles],
            blocker_count=len(barriers), first_blocker=barriers[0] if barriers else None,
            gate="unresolved physical candidate" if admitted else
                 ("excluded by boundary contact" if barriers else "empty or non-SCALE singleton outside scope"),
        ))
    assert sum(len(g["roles"]) for g in groups) == len(candidates)
    return groups


def main():
    if not __debug__:
        raise RuntimeError("assertions required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, default=Path(__file__).resolve().parent / "inputs/7334-WORD.json.gz")
    path = parser.parse_args().word
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(LIMIT)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != GZIP_PIN:
        raise ValueError("changed gzip input")
    decoded = gzip.decompress(raw)
    if hashlib.sha256(decoded).hexdigest() != JSON_PIN:
        raise ValueError("changed decoded native word")
    word = json.loads(decoded, object_pairs_hook=unique)
    events = word["program"]
    assert (len(events), len(word["frames"]), word["public"], word["owned_fields"]) == (76466,1096,1501,68)
    live = set(word["live"])
    main = live | {r + 112 for r in live} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    assert len(main) == 400 and main <= set(range(word["public"])) and main != set(range(400))
    helpers = set(range(word["public"])) - main
    assert len(helpers) == 1101
    histogram = Counter(len(word["frames"][word["final"][r]]) - len(word["frames"][word["initial"][r]])
                        for r in helpers)
    assert histogram == {1:18,2:21,3:47,4:225,5:80,6:43,7:19,8:32,9:616}
    chart3 = {r for r in helpers if word["initial"][r] == CHART}

    first_moves, early = capture(events, chart3)
    outcomes, candidates = proper(word, helpers, first_moves)
    groups = components(word, main, early, candidates)
    survivors = [g["roles"] for g in groups if g["gate"] == "unresolved physical candidate"]
    assert len(outcomes) == len(helpers)
    assert len(chart3) == len(helpers) - sum(x == "other_initial_chart" for x in outcomes.values())
    assert all(g["pre_contact_clocks"] for g in groups if g["roles"] in survivors)

    receipt = dict(comparator_head=HEAD, caller_head=CALLER_HEAD,
                   pins={"inputs/7334-WORD.json.gz":GZIP_PIN, "decoded_source":JSON_PIN},
                   events=len(events), time_cap_seconds=LIMIT, public_main=len(main),
                   productive_helpers=len(helpers), initial_chart=CHART, chart3_helpers=len(chart3),
                   chart3_first_MOVE=len(first_moves), outcomes=Counter(outcomes.values()),
                   first_proper_MOVEs=len(candidates), components=groups, support_unresolved=survivors,
                   scope_exhausted=True)
    signal.alarm(0)
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
