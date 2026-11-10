#!/usr/bin/env python3
"""The new G20 input does not make a same-frame paid query free.

Replays the pinned PR5679 word and its predecessor. No constructor import.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""
import gzip
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPLIT = ROOT / "research" / "g20-helper-split"
NEW = 684
FIELD = 27


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_word(path):
    with gzip.open(path, "rb") as handle:
        word = json.loads(handle.read())
    need(isinstance(word.get("records"), list), "word records")
    return word


def expected_rows(word):
    owned = set(word["owned"])
    width = len(word["start"])
    return [
        0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0)
        for i in range(width)
    ]


def replay(word, records=None):
    """Forward F2 replay. Returns paid counts and final rows, or raises."""
    records = word["records"] if records is None else records
    width = len(word["start"])
    owned = set(word["owned"])
    rows = [1 << i for i in range(width)]
    state = word["start"][:]
    paid = Counter()
    for event in records:
        op, dest = event[:2]
        if op == "ADD":
            source, frame = event[2], event[3]
            need(state[dest] == state[source] == frame, "common frame")
            rows[dest] ^= rows[source]
        elif op == "ERASE":
            need(dest in owned, "owned erase")
            rows[dest] = 0
            state[dest] = event[2]
        elif op == "INIT":
            need(dest in owned and rows[dest] == 0, "zero init")
            state[dest] = event[2]
        elif op in ("Q", "ZERO_Q"):
            need(state[dest] == event[2], "query frame")
            if op == "ZERO_Q":
                need(rows[dest] == 0, "free move of a nonzero row")
            else:
                paid[event[4]] += 1
            state[dest] = event[3]
        else:
            raise ValueError("unknown event")
    need(state == word["final"], "final frames")
    return paid, rows


def rref(ids, vecs, width):
    columns = list(vecs)
    combo = [1 << i for i in range(len(vecs))]
    used = [False] * len(vecs)
    pivots = []
    for bit in range(width - 1, -1, -1):
        chosen = next((i for i in range(len(vecs)) if not used[i] and (columns[i] >> bit) & 1), None)
        if chosen is None:
            continue
        used[chosen] = True
        pivots.append((bit, chosen))
        for i in range(len(vecs)):
            if i != chosen and (columns[i] >> bit) & 1:
                columns[i] ^= columns[chosen]
                combo[i] ^= combo[chosen]
    return columns, combo, used, pivots


def solve(target, ids, vecs, width):
    columns, combo, used, pivots = rref(ids, vecs, width)
    value = target
    coeff = 0
    for bit, chosen in pivots:
        if (value >> bit) & 1:
            value ^= columns[chosen]
            coeff ^= combo[chosen]
    if value:
        return None
    support = tuple(ids[i] for i in range(len(ids)) if (coeff >> i) & 1)
    kernel = []
    for i, free in enumerate(used):
        if free:
            continue
        need(columns[i] == 0, "free column")
        kernel.append(tuple(ids[j] for j in range(len(ids)) if (combo[i] >> j) & 1))
    return support, tuple(kernel)


def identities_using(word, needle):
    """Paid queries whose bank span has a solution containing needle."""
    width = len(word["start"])
    rows = [1 << i for i in range(width)]
    state = word["start"][:]
    found = []
    for index, event in enumerate(word["records"]):
        op, dest = event[:2]
        if op == "Q" and dest != needle and state[dest] == state[needle] and rows[dest]:
            bank = [i for i in range(width) if state[i] == state[dest] and i != dest]
            if needle in bank:
                solved = solve(rows[dest], bank, [rows[i] for i in bank], width)
                if solved is not None:
                    support, kernel = solved
                    uses = needle in support or any(needle in vector for vector in kernel)
                    if uses:
                        alternatives = [support]
                        for vector in kernel:
                            mixed = set(support).symmetric_difference(vector)
                            alternatives.append(tuple(sorted(mixed)))
                        found.append({
                            "index": index,
                            "field": dest,
                            "frame": event[2],
                            "dest": event[3],
                            "rank": event[4],
                            "row": rows[dest],
                            "support": support,
                            "kernel": kernel,
                            "alternatives": alternatives,
                        })
        if op == "ADD":
            rows[dest] ^= rows[event[2]]
        elif op == "ERASE":
            rows[dest] = 0
            state[dest] = event[2]
        elif op == "INIT":
            state[dest] = event[2]
        elif op in ("Q", "ZERO_Q"):
            state[dest] = event[3]
    return found


def next_read(word, field, after):
    width = len(word["start"])
    rows = [1 << i for i in range(width)]
    state = word["start"][:]
    saved = None
    for index, event in enumerate(word["records"]):
        if index == after:
            saved = rows[field]
        if index > after and event[0] == "ADD" and event[2] == field:
            others = [i for i in range(width) if i != field and state[i] == state[field]]
            return index, event, state[field], others, saved, rows
        if event[0] == "ADD":
            rows[event[1]] ^= rows[event[2]]
        elif event[0] == "ERASE":
            rows[event[1]] = 0
            state[event[1]] = event[2]
        elif event[0] == "INIT":
            state[event[1]] = event[2]
        elif event[0] in ("Q", "ZERO_Q"):
            state[event[1]] = event[3]
    raise ValueError("no later read")


def window_can_restore(word, field, after, before, original):
    width = len(word["start"])
    rows = [1 << i for i in range(width)]
    state = word["start"][:]
    best = 0
    for index, event in enumerate(word["records"]):
        if after < index <= before:
            others = [i for i in range(width) if i != field and state[i] == state[field]]
            best = max(best, len(others))
            if solve(original, others, [rows[i] for i in others], width) is not None:
                return True, best
        if event[0] == "ADD":
            rows[event[1]] ^= rows[event[2]]
        elif event[0] == "ERASE":
            rows[event[1]] = 0
            state[event[1]] = event[2]
        elif event[0] == "INIT":
            state[event[1]] = event[2]
        elif event[0] in ("Q", "ZERO_Q"):
            state[event[1]] = event[3]
    return False, best


def cancel(word, query_index, witnesses):
    records = []
    for index, event in enumerate(word["records"]):
        if index == query_index:
            frame = event[2]
            for source in witnesses:
                records.append(["ADD", event[1], source, frame])
            records.append(["ZERO_Q", event[1], event[2], event[3], event[4]])
        else:
            records.append(event)
    return records


def main():
    question = json.loads((SPLIT / "TASK.json").read_text(encoding="utf-8"))["open_questions"][1]
    need(question["question"] == "Can the changed split word enable another paid-query removal?",
         "predecessor question moved")
    emitted = load_word(SPLIT / "WORD.json.gz")
    prior = load_word(SPLIT / "prior" / "WORD.json.gz")
    need(len(emitted["start"]) == 685 and emitted["start"][NEW] == 508 and emitted["final"][NEW] == 0,
         "new input boundary")
    need(len(prior["start"]) == 684, "predecessor has no field 684")

    paid, rows = replay(emitted)
    need(rows == expected_rows(emitted), "emitted endpoint")
    need(sum(paid.values()) == 2846 and paid[2] == 1342, "emitted paid histogram")

    found = identities_using(emitted, NEW)
    need([item["field"] for item in found] == [35, 19, 74, FIELD], "four queries")
    by_field = {item["field"]: item for item in found}
    need(by_field[35]["support"] == (27, 466, 665), "field 35 witness")
    need(by_field[35]["kernel"] == ((19, 27, 465, 466, NEW),), "field 35 kernel")
    need(by_field[19]["support"] == (661,), "field 19 witness")
    need(by_field[19]["kernel"] == ((27, 465, 466, 661, NEW),), "field 19 kernel")
    need(by_field[74]["support"] == (664,), "field 74 witness")
    need(by_field[74]["kernel"] == ((27, 465, 466, 661, NEW),), "field 74 kernel")
    need(by_field[FIELD]["support"] == (465, 466, 661, NEW) and by_field[FIELD]["kernel"] == (),
         "field 27 has one witness and it uses 684")
    need(by_field[FIELD]["row"] == 1 << 27, "field 27 stores its own input")
    # Rows of the unique witness, read from the same replay snapshot.
    snapshot = None
    width = len(emitted["start"])
    rows = [1 << i for i in range(width)]
    state = emitted["start"][:]
    for index, event in enumerate(emitted["records"]):
        if index == by_field[FIELD]["index"]:
            snapshot = {i: rows[i] for i in (FIELD, 465, 466, 661, NEW, 19)}
            break
        if event[0] == "ADD":
            rows[event[1]] ^= rows[event[2]]
        elif event[0] == "ERASE":
            rows[event[1]] = 0
            state[event[1]] = event[2]
        elif event[0] == "INIT":
            state[event[1]] = event[2]
        elif event[0] in ("Q", "ZERO_Q"):
            state[event[1]] = event[3]
    need(snapshot[465] == 1 << 465, "row 465")
    need(snapshot[466] == (1 << 27) ^ (1 << 465) ^ (1 << NEW), "row 466")
    need(snapshot[661] == 1 << 19, "row 661")
    need(snapshot[NEW] == (1 << 19) ^ (1 << NEW), "row 684")
    need(snapshot[465] ^ snapshot[466] ^ snapshot[661] ^ snapshot[NEW] == snapshot[FIELD], "sum")

    for field, query in by_field.items():
        use, event, frame, others, saved, _ = next_read(emitted, field, query["index"])
        need(event[0] == "ADD" and event[2] == field, "next use is a read")
        need(others and saved == query["row"], "value still present in the original word")
        can, width_seen = window_can_restore(emitted, field, query["index"], use, query["row"])
        need(not can and width_seen == 1, "destination window has no restoring field")
        for witness in query["alternatives"]:
            need(not set(witness) & set(others), "witness is not the consumer")

    mutated = cancel(emitted, by_field[FIELD]["index"], by_field[FIELD]["support"])
    mutated_paid, mutated_rows = replay(emitted, mutated)
    mismatches = [i for i in range(width) if mutated_rows[i] != expected_rows(emitted)[i]]
    need(len(mismatches) == 109 and mismatches[0] == FIELD, "cancellation misses the endpoint")
    need(mutated_rows[FIELD] == 0, "cancelled field stays zero")
    need(sum(mutated_paid.values()) == 2845 and mutated_paid[2] == 1341, "one rank-2 query removed")
    short = cancel(emitted, by_field[FIELD]["index"], (465, 466, 661))
    try:
        replay(emitted, short)
    except ValueError as exc:
        need("nonzero" in str(exc), "omitting 684 must leave a paid row")
    else:
        raise ValueError("omitting 684 was accepted")

    # The predecessor query of field 27 from frame 508 is a single twin, not 684.
    prior_paid, prior_rows = replay(prior)
    need(prior_rows == expected_rows(prior), "predecessor endpoint")
    prior_queries = [
        index for index, event in enumerate(prior["records"])
        if event[:4] == ["Q", FIELD, 508, 156]
    ]
    need(prior_queries == [14888], "predecessor query index")
    width = len(prior["start"])
    rows = [1 << i for i in range(width)]
    state = prior["start"][:]
    solved = None
    for index, event in enumerate(prior["records"]):
        if index == 14888:
            bank = [i for i in range(width) if state[i] == 508 and i != FIELD]
            solved = solve(rows[FIELD], bank, [rows[i] for i in bank], width)
            break
        if event[0] == "ADD":
            rows[event[1]] ^= rows[event[2]]
        elif event[0] == "ERASE":
            rows[event[1]] = 0
            state[event[1]] = event[2]
        elif event[0] == "INIT":
            state[event[1]] = event[2]
        elif event[0] in ("Q", "ZERO_Q"):
            state[event[1]] = event[3]
    need(solved == ((466,), ()), "predecessor witness is field 466 alone")
    use, _, _, others, _, _ = next_read(prior, FIELD, 14888)
    can, seen = window_can_restore(prior, FIELD, 14888, use, 1 << 27)
    need(use == 15096 and others == [200] and not can and seen == 1, "predecessor window")
    need(sum(prior_paid.values()) == sum(paid.values()), "split retains the paid count")
    print(
        "PASS_G20_SPLIT_QUERY_IDENTITY"
        " candidates=4 field27_witness=465,466,661,684"
        " windows=empty paid=2846 cancelled_endpoint_mismatches=109"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
