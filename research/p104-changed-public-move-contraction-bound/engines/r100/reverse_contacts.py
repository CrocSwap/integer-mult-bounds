"""Verify the frozen R100 public MOVE windows by reverse indexed incidence."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from itertools import pairwise
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PINS = {
    "inputs/PRICE.json": "7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/7334-CHANGED.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PRIMARY = "075301daf545c8021800c36af19d05517e3c4136dac4e2114cb85204d0b31c64"
EVENT_CAP = 76466
PAIR_CAP = 112
SECONDS = 20


def unique(pairs):
    data = dict(pairs)
    if len(data) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return data


def authenticate(path, pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Changed input {path.name}")
    return raw


def read_input(root, rel):
    data = authenticate(root / rel, PINS[rel])
    if rel.endswith(".gz"):
        data = decompress(data)
        assert sha256(data).hexdigest() == PAYLOAD
    return loads(data, object_pairs_hook=unique)


def participants(event):
    op, dst, *args = event
    if op in ("COPY", "ADD"):
        return ((dst, "destination"), (args[0], "source"))
    return ((dst, "unary"),)


def disposition(rows):
    if not rows:
        return "contact free"
    if all(row["event"][0] == "SCALE" for row in rows):
        return "scales only"
    assert any(row["event"][0] in ("ADD", "COPY") for row in rows)
    return "binary barrier"


def span_index(frames):
    @cache
    def span(label):
        values = [0]
        seen = 1
        for v in frames[label]:
            assert type(v) is int and 0 < v < 512 and not (seen >> v & 1)
            layer = [u ^ v for u in values]
            values.extend(layer)
            seen |= sum(1 << u for u in layer)
        return seen
    return span


def strict_subset(a, b):
    return a != b and a & b == a


@cache
def signed_scalar(literal):
    value = Fraction(literal)
    assert value
    return value


def controls():
    add = ["ADD", 1, 0, "-5", 4]
    copy = ["COPY", 5, 0, "3/2", 4]
    scale = ["SCALE", 0, "-5/2", 4]
    assert participants(add)[1] == participants(copy)[1] == (0, "source")
    assert disposition([{"event": e} for e in (scale, add)]) == "binary barrier"
    assert disposition([{"event": copy}]) == "binary barrier"
    assert signed_scalar(scale[-2]) == Fraction(-5, 2)
    assert disposition([{"event": scale}]) == "scales only"
    assert disposition([]) == "contact free"
    span = span_index([[1], [1, 2], [1, 2, 4], [1, 4]])
    assert strict_subset(span(0), span(1)) and strict_subset(span(1), span(2))
    assert not strict_subset(span(1), span(3))
    return ["source ADD", "source COPY", "signed SCALE", "empty interval", "strict GF2 nesting"]


def reverse_index(word, roles, span, deadline, result):
    n = word["public"]
    owned = word["owned_fields"]
    program = word["program"]
    assert (n, owned, len(program)) == (1501, 68, EVENT_CAP)
    charts = word["final"] + [None] * owned
    incidence = {role: [] for role in sorted(roles)}
    must_be_fresh = set()
    for t in range(EVENT_CAP - 1, -1, -1):
        result["last_unvisited_clock"] = t
        if t % 128 == 0 and monotonic() >= deadline:
            raise TimeoutError("reverse literal cap")
        event = program[t]
        op, d, *args = event
        assert 0 <= d < len(charts) and (d not in must_be_fresh or op == "INIT")
        if op == "MOVE":
            low, high, is_owned = args
            assert charts[d] == high and type(is_owned) is bool and is_owned == (d >= n)
            assert strict_subset(span(low), span(high)) or is_owned and strict_subset(span(high), span(low))
            charts[d] = low
        elif op == "INIT":
            assert d >= n and charts[d] == args[0]
            must_be_fresh.discard(d)
            charts[d] = None
        elif op == "CLEAR":
            assert d >= n and charts[d] is None
            charts[d] = args[0]
        else:
            assert op in ("ADD", "COPY", "SCALE") and charts[d] == args[-1]
            signed_scalar(args[-2])
            if op != "SCALE":
                src = args[0]
                assert 0 <= src < len(charts) and src != d and charts[src] == args[-1]
            if op == "COPY":
                assert d >= n
                must_be_fresh.add(d)
        for role, access in participants(event):
            if role in incidence:
                incidence[role].append((t, access))
        result["events_checked"] += 1
    assert charts == word["initial"] + [None] * owned and not must_be_fresh
    result["last_unvisited_clock"] = None
    return {role: list(reversed(rows)) for role, rows in incidence.items()}


def windows(word, price, span, incidence, deadline, result):
    tape = word["program"]
    profiles = {tuple(row["ranks"]): row for row in price["profiles"]}
    assert len(profiles) == 20
    frames = word["frames"]
    pending = []
    for role, events in incidence.items():
        moves = [i for i, (t, _) in enumerate(events) if tape[t][0] == "MOVE"]
        assert len(moves) <= 9
        result["moves"][role] = len(moves)
        for left, right in pairwise(moves):
            pending.append((role, events[left][0], events[right][0], events[left+1:right]))
    pending.sort(key=lambda case: (case[2], case[0], case[1]))
    result["unvisited_pair_keys"] = [[first, second, role] for role, first, second, _ in pending]
    for i, (role, first, second, inside) in enumerate(pending):
        if i == PAIR_CAP or monotonic() >= deadline:
            raise TimeoutError("pair or cooperative cap")
        op, old_role, a, b, old_flag = tape[first]
        op2, new_role, mid, c, new_flag = tape[second]
        assert op == op2 == "MOVE" and old_role == new_role == role and not old_flag and not new_flag
        assert b == mid and strict_subset(span(a), span(b)) and strict_subset(span(b), span(c))
        p, q = len(frames[b]) - len(frames[a]), len(frames[c]) - len(frames[b])
        assert p > 0 and q > 0 and p + q == len(frames[c]) - len(frames[a])
        contacts = [dict(clock=t, event=tape[t], access=access) for t, access in inside]
        assert all(row["event"][-1] == b for row in contacts)
        quote = profiles[(*sorted((p, q)), p+q)]
        assert Fraction(quote["full_probe"][0]) > 0
        result["pairs"].append(dict(key=[first, second, role], charts=[a,b,c],
            ranks=[p,q,p+q], contacts=contacts, status=disposition(contacts),
            full_probe=quote["full_probe"], net=quote["net"]))
        del result["unvisited_pair_keys"][0]


def audit(root):
    result = dict(events_checked=0, last_unvisited_clock=EVENT_CAP-1,
                  unvisited_pair_keys=None, moves={}, pairs=[])
    reason = None

    def stop(*_):
        raise TimeoutError("Hard 20-second cap")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 2
    try:
        price = read_input(root, "inputs/PRICE.json")
        changed = read_input(root, "inputs/7334-CHANGED.json")
        assert price["head"] == HEAD and price["caller_head"] == CALLER
        assert price["word_sha256"] == PINS["inputs/7334-WORD.json.gz"]
        assert price["word_payload_sha256"] == changed["word_sha256"][1] == PAYLOAD
        assert price["limits"]["event_cap"] == EVENT_CAP and price["limits"]["paid_pairs"] == PAIR_CAP
        assert price["limits"]["runner_seconds"] == SECONDS
        roles = set(changed["roles"])
        assert price["roles"] == changed["roles"] and len(roles) == 14 and max(roles) < 1501
        word = read_input(root, "inputs/7334-WORD.json.gz")
        span = span_index(word["frames"])
        incidence = reverse_index(word, roles, span, deadline, result)
        windows(word, price, span, incidence, deadline, result)
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    cases = result["pairs"]
    return dict(head=HEAD, caller_head=CALLER, pins=PINS, event_cap=EVENT_CAP, pair_cap=PAIR_CAP,
        seconds_cap=SECONDS, controls=controls(), timeout=reason, **result,
        counts=dict(Counter(row["status"] for row in cases)),
        access_counts=dict(Counter(f'{r["event"][0]}:{r["access"]}' for row in cases for r in row["contacts"])),
        candidate_keys=[row["key"] for row in cases if row["status"] != "binary barrier"])


def compare(path, result):
    lead = loads(authenticate(path, PRIMARY), object_pairs_hook=unique)
    assert lead["head"] == result["head"] and lead["pins"]["lead/PRICE.json"] == PINS["inputs/PRICE.json"]
    assert lead["pins"]["inputs/7334-WORD.json.gz"] == PINS["inputs/7334-WORD.json.gz"]
    assert lead["first_unvisited_event"] is result["last_unvisited_clock"] is None
    assert lead["timeout"] is result["timeout"] is None and not result["unvisited_pair_keys"]
    assert lead["counts"] == result["counts"] and lead["candidate_keys"] == result["candidate_keys"]
    assert lead["moves"] == {str(k): v for k, v in result["moves"].items()}
    ncontacts = 0
    for a, b in zip(lead["pairs"], result["pairs"], strict=True):
        fields = ("key", "charts", "ranks", "status", "full_probe", "net")
        assert all(a[k] == b[k] for k in fields)
        assert a["contacts"] == [[r["clock"], r["event"]] for r in b["contacts"]]
        ncontacts += len(b["contacts"])
    return dict(primary_sha256=PRIMARY, head=HEAD, exact_windows=len(lead["pairs"]),
                exact_signed_contact_incidences=ncontacts, access_counts=result["access_counts"],
                dispositions=result["counts"], agrees=True)


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--primary", type=Path)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    if args.controls_only:
        print(dumps(controls()))
        return
    result = audit(args.root)
    print(dumps(compare(args.primary, result) if args.primary else result, indent=2, sort_keys=True))
    if result["timeout"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
