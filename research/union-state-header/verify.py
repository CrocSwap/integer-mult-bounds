"""Bounded exact corroboration, produced by Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path
import sys

# -I removes the script directory. Resolve just this package's sibling module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from codec import Header, Layout


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def read_small(path):
    check(path.stat().st_size <= 1 << 20, "source file exceeds one MiB")
    return path.read_bytes()


def expect_rejection(operation, *arguments):
    try:
        operation(*arguments)
    except ValueError:
        return 1
    raise AssertionError("invalid input accepted")


def literal_states(side, boundaries):
    """Independent semantic enumeration, without index arithmetic."""
    g = len(boundaries)
    for x in itertools.product(range(side), repeat=g):
        flags = tuple(int(value in e) for value, e in zip(x, boundaries))
        ordinals = tuple(e.index(value) if flag else 0
                         for value, e, flag in zip(x, boundaries, flags))
        for tag in (g,) + tuple(i for i, flag in enumerate(flags) if flag):
            yield Header(x, flags, ordinals, sum(flags), tag)


def check_context(side, boundaries):
    layout = Layout(side, boundaries)
    ranks = set()
    states = retags = unused = 0
    for expected in literal_states(side, boundaries):
        rank = layout.rank(expected.coordinates, expected.tag)
        check(rank not in ranks, "two legal states collide")
        ranks.add(rank)
        encoded = layout.encode(expected.coordinates, expected.tag)
        check(len(encoded) == layout.width, "nonconstant record width")
        check(layout.decode(encoded) == expected, "semantic round trip")
        check(layout.unrank(rank) == expected, "index round trip")
        for round_index in range(expected.count):
            updated = layout.retag(encoded, round_index)
            axis = tuple(i for i, flag in enumerate(expected.flags) if flag)[round_index]
            actual = layout.decode(updated)
            check(actual == Header(expected.coordinates, expected.flags,
                                   expected.ordinals, expected.count, axis),
                  "retag metadata")
            check(layout.line_key(updated, round_index) ==
                  (expected.coordinates[:axis], expected.ordinals[axis]), "line key")
            retags += 1
        states += 1
    check(ranks == set(range(layout.states)), "rank map is not onto")
    check(states == layout.states, "closed state count")
    check(1 << (layout.index_bits - 1) < states <= 1 << layout.index_bits,
          "fixed-width information minimum")
    old = 2 + 2 * layout.g * (side - 1).bit_length() + layout.g + 2 * layout.g.bit_length()
    gain = layout.g * (side - 1).bit_length() + layout.g + layout.g.bit_length()
    check(old - layout.width >= gain, "uniform width improvement")
    for index in range(layout.states, 1 << layout.index_bits):
        unused += expect_rejection(layout.decode, "01" + format(index, f"0{layout.index_bits}b"))
    return states, retags, unused


def exhaustive():
    totals = {"contexts": 0, "states": 0, "retags": 0, "unused_codes_rejected": 0}
    for side, maximum_axes in ((2, 4), (3, 3), (4, 2)):
        subsets = tuple(tuple(i for i in range(side) if mask >> i & 1)
                        for mask in range(1 << side))
        for g in range(1, maximum_axes + 1):
            for boundaries in itertools.product(subsets, repeat=g):
                values = check_context(side, boundaries)
                totals["contexts"] += 1
                for key, value in zip(("states", "retags", "unused_codes_rejected"), values):
                    totals[key] += value
    return totals


def large_and_controls():
    count = 0
    for exponent in (8, 31, 127, 1024, 4096):
        side = 1 << exponent
        for g in (1, 2, 7, 32):
            boundaries = tuple((0, side - 1) if i % 2 else () for i in range(g))
            layout = Layout(side, boundaries)
            for index in (0, layout.sentinel_size - 1, layout.states - 1):
                record = layout.unrank(index)
                check(layout.rank(record.coordinates, record.tag) == index, "large index")
                check(layout.decode(layout.encode(record.coordinates, record.tag)) == record,
                      "large serialization")
                count += 1
    layout = Layout(3, ((1,), ()))
    encoded = layout.encode((1, 2), 0)
    controls = 0
    for args in ((1, ((0,),)), (3, ()), (3, ((1, 1),)), (3, ((2, 1),)),
                 (3, ((3,),)), (3, ((True,),)), (3, ((0,),) * 33),
                 (1 << 4097, ((0,),)), (256, (tuple(range(129)),))):
        controls += expect_rejection(Layout, *args)
    for x, tag in (((1,), 0), ((1, 3), 0), ((0, 2), 0), ((1, 2), 1),
                   ((1, 2), 3), ((True, 2), 0), ((1, 2), True)):
        controls += expect_rejection(layout.encode, x, tag)
    for value in (-1, layout.states, True):
        controls += expect_rejection(layout.unrank, value)
    for value in (encoded[:-1], encoded + "0", "00" + encoded[2:], "x" + encoded[1:]):
        controls += expect_rejection(layout.decode, value)
    for round_index in (-1, 1, True):
        controls += expect_rejection(layout.retag, encoded, round_index)
    controls += expect_rejection(layout.line_key, layout.encode((1, 2)), 0)
    check(layout.rank((1, 2), 0) != layout.rank((1, 2)), "tag collision control")
    check(layout.decode(layout.encode((0, 0))).coordinates == (0, 0), "legal substitution")
    witness = Layout(16, ((0, 15),) * 4)
    check((witness.states, witness.width) == (98304, 19), "strict improvement fixture")
    return {"large_round_trips": count, "domain_controls": controls,
            "witness_states": witness.states, "witness_old_bits": 44,
            "witness_new_bits": witness.width}


def source_hashes(package):
    manifest = json.loads(read_small(package / "SOURCES.json"))
    check(len(manifest["files"]) <= 16, "source manifest capacity")
    root = package.parents[1]
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            digest = hashlib.sha256(read_small(path)).hexdigest()
            check(digest == row["sha256"], "changed source input: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


def main():
    package = Path(__file__).resolve().parent
    inputs = source_hashes(package)
    result = exhaustive()
    result.update(large_and_controls())
    result["inputs_sha256"] = inputs
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "codec.py", "verify.py")
    result["package_sha256"] = {
        name: hashlib.sha256(read_small(package / name)).hexdigest() for name in names}
    print("PASS_UNION_STATE_HEADER")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
