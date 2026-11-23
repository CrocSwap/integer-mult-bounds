"""Replay one literal rank-five relay with its native dense physical primitives."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from shutil import disk_usage
import signal
import sys
from tempfile import gettempdir
from types import SimpleNamespace

NODE, DONOR, PAIR = 104493, 94870, (365, 529)
RESERVE = 8 * 1024**3
PINS = {
    "strong_complex.py": "8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d",
    "w5669_shortcut5.json.gz": "6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149",
    "check_strong_physical.py": "c1497710e88267cff463ca0ad47acca4d8e88d48c8c4cf563e6ad35c2836d978",
}
MODULES = {
    "native_verify": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "raw48": "86c30fd4a906830bb6f4b54cdc0be083bd2649bebf68da7383efd7beee223700",
    "compact_columns": "2a9cdf04bbb22fe8e3cc065dd9159916cc13d83a8700477b595faf834be76f50",
    "spool": "b24796e8d220eed9107ecf4e7b1bb28bd3c75f1e3596774bb47a9c6af9a0814d",
    "positive": "a1b5d1725c6230667646d3e50551d566e2faac39bc39a02c703c3da065f4db5c",
}
RECEIPT = "316bb1a57ea8aa87fb2b565a4899c9b0b5a64ff1513c89e14a19d83ecd58e8e1"
OWNER = "external"
PERM = (1, 0, *range(2, 9))


def digest(data):
    return sha256(data).hexdigest()


def checked(path, pin):
    data = path.read_bytes()
    if digest(data) != pin:
        raise ValueError(f"Unexpected authenticated bytes for {path.name}")
    return data


def swap_low_chart_axes(address):
    return address ^ ((((address >> 1) ^ (address >> 2)) & 1) * 6)


def dirty(seed):
    return [((17*j - 11*seed) << 18, (3*j*j + 41*seed - 971) << 18)
            for j in range(2048)]


def lifted(values, circuit, direct, engine, quarter):
    out = [None] * len(values)
    for high in (0, 1):
        for low in (0, 1):
            slots = [low | j << 1 | high << 10 for j in range(512)]
            result = direct(circuit, [values[i] for i in slots], engine, quarter)
            for i, value in zip(slots, result, strict=True):
                out[i] = value
    return out


def compare(actual, expected, label):
    if actual != expected:
        index = next(i for i, (a, b) in enumerate(zip(actual, expected, strict=True)) if a != b)
        raise AssertionError(f"{label} differs at dense address {index}")


def replay(runtime, receipt):
    for name, pin in PINS.items():
        checked(runtime / name, pin)
    record = json.loads(checked(receipt, RECEIPT))
    if (record["node"], record["charts"][::2], record["rank"]) != (NODE, list(PAIR), 5):
        raise ValueError("Round 416 retained a different witness")
    if min(disk_usage(runtime).free, disk_usage(gettempdir()).free) < RESERVE:
        raise RuntimeError("The 8 GiB native reserve is unavailable")

    sys.path.insert(0, str(runtime))
    from upstream import install

    _, _, _, source = install()
    import native_verify as engine
    import compact_columns
    import positive
    import raw48
    import spool
    from check_strong_physical import direct
    from periodic import Job
    from strong_complex import artifacts

    for module in (engine, compact_columns, positive, raw48, spool):
        checked(Path(module.__file__), MODULES[module.__name__])
    atlas = artifacts(source / "research/grade14-native-realization", runtime / "inputs")
    assert atlas.moves[NODE] == PAIR and atlas.forms[NODE] == ((DONOR, 1),)
    rank, right, left = atlas.factors[PAIR]
    r = record["record"]
    assert (rank, right, left) == (5, raw48.monomial(r["right"]), raw48.monomial(r["left"]))
    old, new = (engine.frame(tuple(atlas.graph["frames"][i]), 9) for i in PAIR)
    forward = engine.adjoint(old) + new
    backward = engine.adjoint(new) + old

    # Install the literal node's paid action inside the live graph generator.
    # The synthetic identity helper supplies its predecessor row without
    # materializing the unrelated full raw caller or its numerical calendar.
    identity = (PAIR[0], PAIR[0])
    excerpt = SimpleNamespace(
        graph={"initial": [PAIR[0]], "final": [PAIR[0]],
               "schedule": [DONOR, NODE], "first_output": NODE},
        moves={NODE: PAIR}, forms={DONOR: ((~0, 1),), NODE: atlas.forms[NODE]},
        factors={identity: (9, (), ()), PAIR: (rank, right, left)},
        regs=[], main=set(), layout={"source_labels": [DONOR]}, odd=atlas.odd,
    )
    clock, call_row = next((i, row) for i, row in enumerate(atlas.instructions()) if row[0] == "NATIVE")
    call, color = call_row[1:3]
    columns = compact_columns.Columns(1, 0, 1, 0, 0, 0, 1, spool.cold_swap)
    arena = spool.Arena(11, 32)
    field = arena.field()
    initial = dirty(365)
    field.write(initial)
    fields = {OWNER: field}
    raw = raw48.ComplexRaw(excerpt, fields, columns, low=1, bundle=1, slots=9)
    helpers = {("helper", clock, call, DONOR): Job(OWNER, PERM)}
    tape = raw.graph(clock, call, color, (), helpers, {}, 1)
    tag, job = next(tape)
    assert tag == ("return", clock, call, NODE)
    assert tuple(job.axes) == tuple(range(rank))
    assert set(fields) == {OWNER, job.owner} and fields[job.owner] is not field
    loan = fields[job.owner]
    aligned = [tuple(atlas.odd*v for v in initial[swap_low_chart_axes(i)]) for i in range(2048)]
    before_child = lifted(aligned, engine.monomial(r["right"]), direct, engine, spool.quarter)
    compare(list(loan.values()), before_child, "Published scratch")
    compare(list(field.values()), initial, "Owned field during publication")
    for axis in job.axes:
        positive.one_axis(loan, axis + 1)
    assert next(tape, None) is None
    assert fields == {OWNER: field} and arena.live == 1
    canonical = [initial[swap_low_chart_axes(i)] for i in range(2048)]
    result = lifted(canonical, forward, direct, engine, spool.quarter)
    expected = [result[swap_low_chart_axes(i)] for i in range(2048)]
    compare(list(field.values()), expected, "Signed output after owner return")

    inverse_input = dirty(529)
    field.write(inverse_input)
    raw.chart(field, left, range(9), 1, inverse=True)
    for axis in range(rank):
        positive.one_axis(field, axis + 1)
        columns.row(field, (axis + 1,))
    raw.chart(field, right, range(9), 1, inverse=True)
    inverse_expected = lifted(inverse_input, backward, direct, engine, spool.quarter)
    compare(list(field.values()), inverse_expected, "Independent adjoint output")
    wrong = lifted(inverse_input, engine.adjoint(engine.monomial(r["left"]))
                   + engine.fourier(rank) + engine.adjoint(engine.monomial(r["right"])),
                   direct, engine, spool.quarter)
    assert wrong != inverse_expected
    assert arena.live == 1 and fields.pop(OWNER) is field and not fields
    field.retire()
    arena.close()
    return {
        "scope": "One-column dense physical chart and actual graph scratch lifecycle, with synthetic identity boundary",
        "node": NODE, "charts": PAIR, "literal_donor": DONOR,
        "paid_tag": tag, "paid_rank": rank, "spectator_fibres": 4,
        "forward_values": len(initial), "adjoint_values": len(inverse_input),
        "wrong_fourier_rejected": True, "external_owner_restored": True,
    }


def timeout(_signum, _frame):
    raise TimeoutError("The one-relay installed fixture reached its 90-second cap")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--relay-receipt", type=Path, required=True)
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError("Enable assertions for the exact fixture")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(90)
    try:
        print(json.dumps(replay(args.runtime.resolve(), args.relay_receipt), indent=2))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
