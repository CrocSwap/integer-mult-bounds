"""Source-bound replay; default compares retained evidence without changing it."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    source = json.loads((HERE / "SOURCES.json").read_text())
    count = 0
    for row in source["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(sha256(path.read_bytes()).hexdigest() == row["sha256"],
                    "source pin: " + row["path"])
            count += 1
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text())
    require(sha256((HERE / predecessor["path"]).read_bytes()).hexdigest() == predecessor["sha256"],
            "PR3246 proof export pin")
    return count


def activate():
    authenticate()
    # -B alone would still read stale pyc files. These direct imports also get
    # an empty cache namespace; the registered runner independently does so.
    temporary = tempfile.TemporaryDirectory(prefix="one-factor-bytecode-")
    sys.pycache_prefix = temporary.name
    sys.path.insert(0, str(ROOT / "research/physical-ordinary-interchange"))
    import source
    source.activate()
    sys.path.insert(0, str(HERE))
    return temporary


def setup():
    import encoded
    from cardinal_counts import Count
    from check_support import no_decode
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from selector import select_guard_stock, close_plan, legacy_profile
    from arithmetic import plan as oracle, check_arithmetic

    def decode(count):
        # Observer only, outside the implementation. Distinguish bool/int in
        # receipts through canonical JSON comparison below.
        tape = count.tape
        cells = tape.cells if hasattr(tape, "cells") else tape.physical.cells
        from words import RIGHT
        digits = list(cells[1:])
        end = digits.index(RIGHT)
        require(all(x in (0, 1) for x in digits[:end]), "canonical observer digits")
        return sum(x << i for i, x in enumerate(digits[:end]))

    pool = ScratchPool(64)
    rows = []
    profiles = [encoded.Profile(dimension=2, child_rank=1, row_factor=1,
                                numerator=0, denominator=1),
                encoded.Profile(dimension=3, child_rank=2, row_factor=3,
                                numerator=1, denominator=3)]
    for profile_id, profile in enumerate(profiles):
        for radix in (2, 3):
            for compatibility in (1, 2, 5, 9475):
                for e in (1, 2, 4, 24, 32, 127):
                    original = Count.literal(e)
                    before = bytes(original.tape.cells)
                    with no_decode(), sealed_constructors(), pool.install():
                        candidate = select_guard_stock(original, radix, profile, compatibility)
                        observed = {k: v if k == "fits" else decode(v) for k, v in candidate.items()}
                        expected = oracle(e, radix, profile, compatibility)
                        require(observed == expected, "encoded plan equals independent integer oracle")
                        close_plan(candidate)
                        legacy = encoded.select(original, radix, legacy_profile(profile, compatibility))
                        old = {k: v if k == "fits" else decode(v) for k, v in legacy.items()}
                        require(old == oracle(e, radix, profile, compatibility, repeated=True),
                                "legacy plan oracle")
                        close_plan(legacy)
                        require(observed["stock"] <= old["stock"] and
                                observed["borrowed"] <= old["borrowed"], "reserve monotonicity")
                        require(not old["fits"] or observed["fits"], "retain every old fitted width")
                        require(old["stock"] // observed["stock"] ==
                                compatibility ** max(0, expected["depth"] - 1), "exact reserve ratio")
                        pool.empty()
                    require(bytes(original.tape.cells) == before and original.tape.head == 1,
                            "selector preserves borrowed original count")
                    original.close()
                    rows.append(dict(profile=profile_id, q=radix, compatibility=compatibility,
                                     e=e, plan=observed, legacy_borrowed=old["borrowed"]))
    # Executed wrong-policy controls: the untouched live-only selector supplies
    # plausible tapes but fails the new oracle, including strict-fit/body seams.
    profile = profiles[0]
    controls = []
    for e in (24, 32):
        c = Count.literal(e)
        with no_decode(), sealed_constructors(), pool.install():
            wrong = encoded.select(c, 2, profile)
            got = {k: v if k == "fits" else decode(v) for k, v in wrong.items()}
            expected = oracle(e, 2, profile, 2)
            require(got != expected, "missing compatibility factor detected")
            require(got["fits"] != expected["fits"] if e == 24 else
                    got["body"] != expected["body"], "stale fit/body control discriminates")
            close_plan(wrong)
            pool.empty()
        c.close()
        controls.append(dict(e=e, wrong=got, expected=expected))
    import fresh_rows
    import check_nested_model as model
    from directory import Context
    from words import Arena, Ring
    arena = Arena(3)
    modulus = arena.input(2)
    ring = Ring(modulus)
    context = Context(ring, model.Catalogue().codes)
    guards = []
    for initial, accepted_levels, accepted in ((72, 2, True), (144, 2, True),
                                              (36, 1, False), (73, 0, False),
                                              (12, 1, False)):
        current = Count.literal(initial)
        levels = 0
        message = None
        try:
            for _ in range(2):
                following = fresh_rows.quotient(current, context, 1)
                current.close()
                current = following
                check = Count(current)
                try:
                    require(check.divide_small(2) == 0, "actual Q=2 guard")
                finally:
                    check.close()
                levels += 1
        except ValueError as error:
            message = str(error)
        finally:
            current.close()
        require(levels == accepted_levels and (message is None) == accepted,
                "literal guard chain control")
        guards.append(dict(rows=initial, accepted_levels=levels, accepted=accepted, error=message))
    context.close()
    ring.close()
    arena.free(modulus)
    return dict(selections=rows, mutation_controls=controls, arithmetic=check_arithmetic(),
                literal_guard_controls=guards, peak_setup_roles=pool.peak)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("setup", "nested", "wrapper"), required=True)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    with activate():
        if args.suite == "setup":
            result = setup()
        elif args.suite == "nested":
            import nested
            result = nested.run()
        else:
            import wrapper
            result = wrapper.run()
    serial = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    if args.emit_to:
        with args.emit_to.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())[args.suite]
        require(serial == json.dumps(expected, sort_keys=True, separators=(",", ":")),
                "complete typed receipt: " + args.suite)
    print("PASS_ORDINARY_ONE_FACTOR_" + args.suite.upper(), sha256(serial.encode()).hexdigest())


if __name__ == "__main__":
    main()
