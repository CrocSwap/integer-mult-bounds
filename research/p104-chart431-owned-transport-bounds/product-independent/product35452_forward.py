"""Exact forward separator for replacing the #7481 chart243 operand return."""
import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path
from signal import alarm
from time import perf_counter

ARCHIVE = "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
SOURCE, RETURN, CUT = 34379, 35448, 35452
BANK = (8, 26, 95, 368, 369, 371, 373, 378, 743, 771, 780, 798, 865, 1130,
        1131, 1133, 1135, 1140, 1389, 1390, 1513, 1539)


def forward(word, probe, omitted=None):
    active = dict(enumerate(word["initial"]))
    values, observed = probe.copy(), {}
    cuts = {SOURCE: (1137, 431), RETURN: (1545, 600)}
    copies = 0
    for clock, (op, dest, *args) in enumerate(word["program"][:CUT]):
        if clock in cuts:
            role, chart = cuts[clock]
            assert active[role] == chart
            observed[role] = values.get(role, 0)
        if clock == omitted:
            assert op == "ADD"
            continue
        if op == "MOVE":
            assert active[dest] == args[0] and args[2] == (dest >= word["public"])
            active[dest] = args[1]
            continue
        if op == "INIT":
            assert dest not in active and dest not in values
            active[dest] = args[0]
            continue
        if op == "CLEAR":
            assert active.pop(dest) == args[0]
            values.pop(dest, None)
            continue
        value = values.get(dest, 0)
        if op == "SCALE":
            assert active[dest] == args[1]
            value *= F(args[0])
        else:
            assert op in ("ADD", "COPY")
            src, coefficient, chart = args
            assert active[dest] == active[src] == chart
            if op == "COPY":
                assert value == 0
                copies += 1
            if src in values:
                value += F(coefficient) * values[src]
        if value:
            values[dest] = value
        else:
            values.pop(dest, None)
    assert tuple(sorted(role for role, chart in active.items() if chart == 243)) == BANK
    assert active[1544] == active[1545] == active[1535] == 431
    return values, observed, copies


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path)
    parser.add_argument("--probe", required=True, type=Path)
    args = parser.parse_args()
    start = perf_counter()
    alarm(30)
    archive = args.word.read_bytes()
    assert sha256(archive).hexdigest() == ARCHIVE
    payload = gzip.decompress(archive)
    assert sha256(payload).hexdigest() == NATIVE
    word = json.loads(payload)
    p = word["program"]
    assert p[SOURCE - 2:SOURCE + 1] == [
        ["ADD", 1135, 1137, "-1", 431], ["INIT", 1535, 431], ["ADD", 1535, 1137, "4", 431],
    ]
    assert p[RETURN:CUT + 2] == [
        ["MOVE", 1545, 600, 431, True], ["ADD", 1535, 1545, "1", 431],
        ["SCALE", 1535, "1/4", 431], ["ADD", 1544, 1535, "1", 431],
        ["MOVE", 1544, 431, 243, True], ["ADD", 1539, 1544, "1", 243],
    ]
    assert p[35350:35354] == [
        ["MOVE", 1135, 431, 243, False], ["ADD", 798, 1135, "-1", 243],
        ["ADD", 1135, 798, "1", 243], ["ADD", 798, 1135, "-1", 243],
    ] and p[35355] == ["SCALE", 798, "-1", 243]
    assert not set(BANK) & {1535, 1544, 1545}
    probe = {int(role): F(value) for role, value in json.loads(args.probe.read_text()).items()}
    assert probe and all(0 <= role < word["public"] for role in probe)
    values, old, copies = forward(word, probe)
    u, product = old[1137], old[1545]
    bank = {role: values.get(role, 0) for role in BANK}
    assert u and not any(bank.values())
    old_return = values.get(1544, 0)
    assert old_return == u + F(product, 4)
    mutant, old_mutant, mutant_copies = forward(word, probe, omitted=SOURCE)
    assert old_mutant == old and copies == mutant_copies
    assert all(mutant.get(role, 0) == 0 for role in BANK)
    assert mutant.get(1544, 0) == F(product, 4)
    print(json.dumps({
        "status": "PASS_EXACT_FULL_CHART243_OPERAND_SEPARATOR",
        "native_sha256": NATIVE, "case_count": 1, "runner_cap_seconds": 30,
        "source_before": SOURCE, "return_cut_before": CUT, "probe": probe, "bank": bank,
        "old_source_1137": u, "old_product_1545": product, "old_return_1544": old_return,
        "copy_guards_checked_on_probe": copies,
        "control_drop_ADD34379": {"old_source_1137": old_mutant[1137],
                                  "return_1544": mutant.get(1544, 0)},
        "seconds": perf_counter() - start,
    }, sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()
