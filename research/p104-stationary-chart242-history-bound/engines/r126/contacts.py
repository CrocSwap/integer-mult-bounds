"""Forward exact public-span generator census for the chart-242 tail."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "9a3ce52bda81c4046dc2751dddcf490360500dec976c692f84eb6814cbe85402",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


def checked(path):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return data


def unique(items):
    doc = dict(items)
    if len(doc) != len(items):
        raise ValueError("duplicate JSON key")
    return doc


def classify(event, n, chart):
    op, r, *args = event
    if op == "MOVE":
        before, after, _ = args
        if before == chart:
            return ("owned exit" if r >= n else "public exit"), None
        if after == chart:
            return ("owned entrance", None) if r >= n else ("public entrance", r)
        return None, None
    if args[-1] != chart:
        return None, None
    if op in ("ADD", "COPY") and r >= n and args[0] < n:
        return "public source to owned destination", args[0]
    return op, None


def controls():
    assert classify(["ADD", 12, 2, "1", 242], 10, 242) == ("public source to owned destination", 2)
    assert classify(["COPY", 12, 2, "-1", 242], 10, 242)[1] == 2
    assert classify(["ADD", 2, 12, "1", 242], 10, 242)[1] is None
    assert classify(["MOVE", 2, 1, 242, False], 10, 242)[1] == 2
    assert classify(["MOVE", 2, 242, 1, False], 10, 242)[1] is None
    return ["public source to owned ADD and COPY", "owned source to public ADD", "ingress versus exit"]


def stop(*_):
    raise TimeoutError("20-second hard cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    deadline = monotonic() + 18
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    touches, gens, seen, terminal, reason = [], [], 0, None, None
    copy_destinations = 0
    try:
        data = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(data).hexdigest() == PAYLOAD
        word = loads(data, object_pairs_hook=unique)
        n = word["public"]
        chart, start = price["retirement"]["chart"], price["maximal_cut"]
        assert chart == 242 and start == 45472
        tape = word["program"]
        assert len(tape) == 76466
        active = word["initial"] + [None] * word["owned_fields"]
        for t, event in enumerate(tape):
            if t % 128 == 0 and monotonic() >= deadline:
                raise TimeoutError("literal event walk cap")
            if t == start:
                assert [i for i, c in enumerate(active) if c == chart] == price["maximal_bank"]
            op, r, *args = event
            if op == "MOVE":
                before, after, owned = args
                assert active[r] == before and owned == (r >= n)
                active[r] = after
            elif op == "INIT":
                assert active[r] is None and r >= n
                active[r] = args[0]
            elif op == "CLEAR":
                assert active[r] == args[0] and r >= n
                active[r] = None
            else:
                assert op in ("ADD", "COPY", "SCALE") and active[r] == args[-1]
                if op in ("ADD", "COPY"):
                    assert active[args[0]] == args[-1] and args[0] != r
                if op == "COPY":
                    assert r >= n
                    copy_destinations += 1
            if t >= start:
                category, generator = classify(event, n, chart)
                if category:
                    touches.append([t, event, category])
                if generator is not None:
                    gens.append([t + 1, generator])
            seen += 1
        assert active == word["final"] + [None] * word["owned_fields"]
        terminal = [r for r, c in enumerate(active) if c == chart]
    except TimeoutError as error:
        reason = str(error)
    finally:
        alarm(0)
    print(dumps({
        "head": price["head"], "caller": price["caller"], "pins": PINS, "controls": controls(),
        "events": seen, "maximal_cut": price["maximal_cut"], "maximal_bank": price["maximal_bank"],
        "chart_contacts": touches, "counts": Counter(row[2] for row in touches),
        "new_generator_keys": gens, "copy_owned_destinations": copy_destinations,
        "final_bank": terminal, "closed_without_new_columns": not reason and not gens,
        "unresolved_tail_from": seen if reason else None, "timeout": reason,
    }, sort_keys=True, indent=2))
    return 124 if reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
