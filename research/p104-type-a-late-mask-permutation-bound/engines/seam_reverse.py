"""Reverse-covector check of a Type A late-mask reassignment at one seam."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
PINS = {"inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CUT = 1741
ROOTS = (0, 9)
N = 36


def read(name):
    raw = (HERE/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name]
    return loads(raw)


def basis(index):
    return [Q(j == index) for j in range(N)]


def swap(row):
    a, b = ROOTS
    out = row[:]
    out[a], out[b] = out[b], out[a]
    return out


def covector(events, row, q, invert=False):
    # If the event product is O_n ... O_1, a row covector acts on it
    # from n to 1 and on its inverse from 1 to n.
    result = row[:]
    direction = -1 if invert else 1
    for event in events if invert else reversed(events):
        kind = event[0]
        if kind == "B":
            continue
        if kind == "J":
            _, _, (u, v, x, y), _ = event
            result[u] += direction*q*result[v]
            result[y] -= direction*q*result[x]
            continue
        assert kind == "A"
        _, op, dest, *args = event
        if op == "ADD":
            src, a = args
            result[src] += direction*Q(a)*result[dest]
        elif op == "QUERY":
            src, exponent = args
            assert exponent == -1
            result[src] += direction*q*result[dest]
        elif op == "SCALE":
            a, = args
            result[dest] *= Q(a)**direction
        elif op == "SWAP":
            src, = args
            result[dest], result[src] = result[src], result[dest]
        elif op == "IDLE_ONE":
            assert args[0]
        else:
            assert op == "LAMBDA" and args[0] in (1, -1)
    return result


def nonzero(matrix):
    return [[i, j, str(value)] for i, row in enumerate(matrix)
            for j, value in enumerate(row) if value]


def row_mul(row, matrix):
    return [sum(a*b for a, b in zip(row, col, strict=True) if a and b)
            for col in zip(*matrix, strict=True)]


def stop(*_):
    raise TimeoutError("20-second exact seam cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(20)
    c = read("inputs/CALLER.json")
    assert c["types"]["A"]["roles"] == N
    assert c["types"]["A"]["alpha2"] == "-1"
    tape = c["events"]
    assert len(tape) == 4783 and tape[CUT] == ["A", "ADD", 10, 0, "2"]
    pre, post = tape[:CUT], tape[CUT:]
    for events, stages, query_count in ((pre, set(range(1, 9)), 4),
                                         (post, set(range(9, 18)), 0)):
        assert sorted(event[1] for event in events if event[0] == "J") == sorted(stages)
        assert sum(event[:2] == ["A", "QUERY"] for event in events) == query_count
        assert all(set(event[3]) <= stages for event in events if event[:2] == ["A", "IDLE_ONE"])
    targets = c["types"]["A"]["diagonal"]
    assert len(targets) == N and all(d[:2] == [-1, 0] for d in targets)
    masks = [[sum(targets[i][2:10]), sum(targets[i][10:])] for i in ROOTS]
    assert masks == [[8, 9], [0, 1]]

    seam, boundary = {}, {}
    prefix = {}

    for q in (1, -1):
        g = [covector(pre, basis(i), q) for i in range(N)]
        prefix[q] = nonzero(g)

        w = [covector(pre, swap(row), q, invert=True) for row in g]
        for i, (g_row, w_row) in enumerate(zip(g, w, strict=True)):
            assert covector(pre, g_row, q, invert=True) == basis(i)
            assert covector(pre, w_row, q) == swap(g_row)
            assert row_mul(w_row, w) == basis(i)
            after_swap = covector(post, swap(basis(i)), q)
            edited = covector(pre, row_mul(after_swap, w), q)
            assert edited == [q*x for x in basis(i)]
            assert covector(tape, basis(i), q) == edited
        seam[q] = w
        boundary[q] = {
            "displacement_nonzeros": len(nonzero([[x-y for x, y in zip(row, basis(i), strict=True)]
                                                  for i, row in enumerate(w)])),
            "seam_nonzeros": len(nonzero(w)),
        }

    odd = [[a-b for a, b in zip(u, v, strict=True)]
           for u, v in zip(seam[1], seam[-1], strict=True)]
    witness = nonzero(odd)
    # A wrong final readout with no output swap is exposed at unit bodies.
    wrong = covector(pre, row_mul(covector(post, basis(ROOTS[0]), 1), seam[1]), 1)
    assert wrong != basis(ROOTS[0])
    alarm(0)
    print(dumps({
        "benchmark": HEAD, "caller": CALLER, "pins": PINS, "cut": CUT,
        "roots": ROOTS, "central_signs": [1, -1], "basis_columns": N,
        "early_late_body_counts": masks, "old_ranks": [137, 9], "new_ranks": [73, 73],
        "q_even_at_real_pair": not witness, "odd_entries_count": len(witness),
        "first_odd_entries": witness[:12], "boundary": boundary,
        "seam_plus": nonzero(seam[1]), "seam_minus": nonzero(seam[-1]),
        "prefix_plus": prefix[1], "prefix_minus": prefix[-1],

        "runner_cap_seconds": 20, "negative_control": "missing final output swap",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
