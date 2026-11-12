"""Reverse literal chart and operand-contact census for paid-donor hoists."""
from collections import Counter
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "R137-LEAD.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "R137-INDEPENDENT.json": "25928be557cbdd12d6df7f50982fc5a90d257eeee4cd33a27d5c7eff81e6d753",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PREDECESSOR = "8f4b87165e158c4329999ad857b775b4361b4063"
SECONDS = 25


def read(name):
    raw = (ROOT / "inputs" / name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return raw


def unique(items):
    data = dict(items)
    assert len(data) == len(items), "duplicate key"
    return data


def decode(raw):
    return loads(raw, object_pairs_hook=unique)


def stop(*_):
    raise TimeoutError("25-second reverse geometry cap")


def donors_at(tape, future, state, chart, owner):
    result = []
    for r, live in enumerate(state):
        if r == owner or live is None or future[r] is None:
            continue
        i = future[r]
        e = tape[i]
        if e[:2] == ["MOVE", r] and e[2:4] == [live, chart]:
            result.append([r, i, live, chart, e[4]])
    return result


def control():
    tape = [["MOVE", 2, 0, 7, False], ["ADD", 0, 2, "1", 0],
            ["MOVE", 0, 0, 7, False], ["MOVE", 1, 1, 7, False],
            ["MOVE", 3, 1, 8, False], ["MOVE", 4, 1, 7, True]]
    assert donors_at(tape, [1, 3, 0, 4, 5], [0, 1, 0, 1, None], 7, 2) == [[1, 3, 1, 7, False]]
    return "different live source chart allowed; preceding donor read, self, wrong target ID and inactive donor reject"


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(SECONDS)
    raw = decompress(read("7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    word = decode(raw)
    n, m, tape, frames = (word[k] for k in ("public", "owned_fields", "program", "frames"))
    assert (n, m, len(tape), len(frames)) == (1501, 68, 76466, 1096)
    prior, independent = (decode(read(f)) for f in ("R137-LEAD.json", "R137-INDEPENDENT.json"))
    assert all(x["head"] == HEAD and x["caller"] == CALLER for x in (prior, independent))
    assert prior["counts"] == {"outside donor span": 47} and not prior["unvisited"]
    old = {r["move_clock"]: r for r in prior["records"]}
    independent_old = {r["move_clock"]: r for r in independent["cases"]}
    assert len(old) == len(independent_old) == 47
    assert old.keys() == independent_old.keys() and not independent["unresolved"]
    state = word["final"] + [None] * m
    future = [None] * len(state)
    records, old_keys = [], set()

    @cache
    def span(chart):
        values = {0}
        for bit in frames[chart]:
            assert bit not in values
            values.update({v ^ bit for v in values})
        return values

    for i in range(len(tape) - 1, -1, -1):
        op, r, *args = tape[i]
        assert 0 <= r < n + m
        if op == "MOVE":
            low, high, is_owned = args
            assert state[r] == high and is_owned == (r >= n)
            rise = span(low) < span(high)
            assert rise or (is_owned and span(high) < span(low))
            state[r] = low
            if is_owned:
                assert i in old
                p, q = old[i], independent_old[i]
                target_bank = [d for d, c in enumerate(state) if c == high and d != r]
                expected = sorted(set(p["bank_roles"]) | set(q["extra_live_donors"]))
                assert target_bank == expected and q["donor_count"] == len(expected)
                assert (r, low, high, future[r]) == (p["role"], p["chart_from"], p["chart_to"], i + 1)
                assert p["first_clock"] == i + 1 and p["first_event"] == tape[i + 1]
                assert abs(len(frames[high]) - len(frames[low])) == p["rank"] == q["paid_rank"]
                old_keys.add(i)
                if rise:
                    candidates = donors_at(tape, future, state, high, r)
                    records.append({"clock": i, "owner": r, "from_chart": low, "to_chart": high,
                                    "owner_rank": p["rank"], "next_owner_contact": future[r],
                                    "unchanged_target_bank": target_bank, "candidates": candidates})
        elif op == "CLEAR":
            assert r >= n and state[r] is None
            state[r] = args[0]
        elif op == "INIT":
            assert r >= n and state[r] == args[0]
            state[r] = None
        else:
            assert op in ("ADD", "COPY", "SCALE") and state[r] == args[-1]
            if op != "SCALE":
                source = args[0]
                assert source != r and state[source] == args[-1]
                future[source] = i
        future[r] = i

    assert state == word["initial"] + [None] * m
    assert old_keys == old.keys() and len(records) == 23
    controls = [control(), "full reverse chart lifetime closes at exact initial state",
                "all 47 independent prior first-contact bank memberships reproduce"]
    records.reverse()
    alarm(0)
    print(dumps({
        "head": HEAD, "caller": CALLER, "prior_head": PREDECESSOR, "pins": PINS,
        "owned_rises": len(records), "old_bank_keys": len(old_keys), "events": len(tape),
        "sites_with_donors": sum(bool(r["candidates"]) for r in records),
        "donor_pairs": sum(len(r["candidates"]) for r in records),
        "donor_pairs_by_owner_rank": Counter({k: sum(len(r["candidates"]) for r in records if r["owner_rank"] == k)
                                               for k in sorted({r["owner_rank"] for r in records})}),
        "cap_seconds": SECONDS, "controls": controls, "records": records,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
