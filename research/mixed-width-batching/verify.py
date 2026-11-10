"""Bounded, read-only corroboration of mixed-width chronological batching."""

import hashlib
import itertools
import json
import platform
import sys
from dataclasses import replace
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batching import Batch, least_replication, partition, residue_minima


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check_table(table):
    """Check feasible representatives and all shortest-path inequalities."""
    widths, divisor, modulus = table.widths, table.divisor, table.modulus
    need(divisor == gcd(*widths), "wrong menu gcd")
    coins = tuple(w // divisor for w in widths)
    need(modulus == min(coins), "wrong residue modulus")
    need(len(table.minima) == len(table.witnesses) == modulus, "missing residue")
    need(table.minima[0] == 0, "wrong zero-residue minimum")
    for residue, (value, counts) in enumerate(zip(table.minima, table.witnesses)):
        need(type(value) is int and value >= 0, "invalid minimum")
        need(value % modulus == residue, "wrong minimum residue")
        need(len(counts) == len(coins), "wrong witness length")
        need(all(type(c) is int and c >= 0 for c in counts), "invalid count")
        need(sum(c * w for c, w in zip(counts, coins)) == value, "bad witness")
        for coin in coins:
            need(table.minima[(residue + coin) % modulus] <= value + coin,
                 "shorter residue path exists")
    need(table.conductor == max(table.minima) - modulus + 1, "wrong conductor")


def reachable(widths, cap):
    """Separate total-size DP, with no gcd or residue-table algorithm."""
    need(0 <= cap <= 640, "oracle capacity")
    flags = [False] * (cap + 1)
    flags[0] = True
    for total in range(1, cap + 1):
        flags[total] = any(total >= w and flags[total - w] for w in widths)
    return tuple(flags)


def check_partition(widths, total, counts):
    need(counts is not None and len(counts) == len(widths), "missing partition")
    need(all(type(c) is int and c >= 0 for c in counts), "bad invocation count")
    need(sum(w * c for w, c in zip(widths, counts)) == total, "wrong job count")


def check_system(batches, oracles):
    actual = least_replication(batches)
    upper = lcm(*(batch.widths[0] for batch in batches))
    expected = None
    for replication in range(1, upper + 1):
        if all(oracles[b.widths][replication * b.multiplicity] for b in batches):
            expected = replication
            break
    need(expected is not None, "direct single-width bound failed")
    need(actual.replication == expected, "least replication disagrees with size DP")
    need(actual.replication % actual.divisibility_step == 0, "gcd step failed")
    need(actual.replication <= actual.divisibility_step * actual.scan_bound,
         "conductor search bound failed")
    for batch, counts in zip(batches, actual.partitions):
        check_partition(batch.widths, actual.replication * batch.multiplicity, counts)


def exhaustive_checks():
    menus = tuple(menu for size in range(1, 4)
                  for menu in itertools.combinations(range(1, 11), size))
    observations = 0
    for menu in menus:
        table = residue_minima(menu)
        check_table(table)
        oracle = reachable(menu, 256)
        for total, feasible in enumerate(oracle):
            counts = partition(table, total)
            need((counts is not None) == feasible, "membership disagrees with DP")
            if feasible:
                check_partition(menu, total, counts)
            observations += 1
    oracles = {menu: reachable(menu, 640) for menu in menus}
    systems = 0
    for menu in menus:
        for multiplicity in range(1, 9):
            check_system((Batch(menu, multiplicity),), oracles)
            systems += 1
    small = tuple(Batch(menu, q) for menu in menus if max(menu) <= 5
                  and min(menu) >= 2 for q in range(1, 5))
    for batches in itertools.product(small, repeat=2):
        check_system(batches, oracles)
        systems += 1
    tiny = tuple(Batch(menu, q) for menu in menus if max(menu) <= 3
                 and len(menu) <= 2 for q in range(1, 3))
    for batches in itertools.product(tiny, repeat=3):
        check_system(batches, oracles)
        systems += 1
    return {"menus": len(menus), "membership_observations": observations,
            "exact_systems": systems, "two_cut_choices": len(small),
            "three_cut_choices": len(tiny)}


def execute_batches(batches, schedule, inputs):
    """Literal compatible direct-sum jobs, each preserving its dirty coordinate."""
    output, cursor, invocations = list(inputs), 0, 0
    for batch, counts in zip(batches, schedule.partitions):
        end = cursor + schedule.replication * batch.multiplicity
        for width, count in zip(batch.widths, counts):
            for _ in range(count):
                for position in range(cursor, cursor + width):
                    x, y, dirty = output[position]
                    output[position] = (x + y, y, dirty)
                cursor += width
                invocations += 1
        need(cursor == end, "batch returned at the wrong cut")
    need(cursor == len(output), "unfinished independent input")
    return tuple(output), invocations


def strict_family_checks():
    bank_count = 0
    for n in range(2, 25):
        batches = (Batch((n, n + 1), n), Batch((n, n + 1), n + 1))
        mixed = least_replication(batches)
        pure = [least_replication(tuple(Batch((w,), b.multiplicity) for b in batches))
                for w in (n, n + 1)]
        need(mixed.replication == 1, "mixed family failed")
        need(tuple(s.replication for s in pure) == (n, n + 1), "single-width floor")
        for schedule in (mixed, pure[0]):
            used = batches if schedule is mixed else tuple(Batch((n,), b.multiplicity)
                                                         for b in batches)
            count = schedule.replication * (2 * n + 1)
            inputs = tuple((j - 7, 2 * j + 1, 11 - j) for j in range(count))
            output, _ = execute_batches(used, schedule, inputs)
            expected = tuple((x + y, y, d) for x, y, d in inputs)
            need(output == expected, "literal complete dirty endpoint failed")
            bill = sum(Fraction(7, 3) * w * c for b, cs in zip(used, schedule.partitions)
                       for w, c in zip(b.widths, cs))
            need(bill / (5 * schedule.replication) == Fraction(7 * (2 * n + 1), 15),
                 "normalized complete linear bill changed")
            bank_count += count
    mixed_batch = least_replication((Batch((4, 7), 11),))
    need(mixed_batch.replication == 1 and mixed_batch.partitions == ((1, 1),),
         "within-cut mixed invocation witness failed")
    return {"strict_family_parameters": 23, "literal_banks": bank_count,
            "within_cut_partition": list(mixed_batch.partitions[0])}


def rejection_checks():
    invalid = [lambda: Batch((), 1), lambda: Batch([2, 3], 1),
               lambda: Batch((2, 2), 1), lambda: Batch((3, 2), 1),
               lambda: Batch((0,), 1), lambda: Batch((65,), 1),
               lambda: Batch((True,), 1), lambda: Batch((2,), 0),
               lambda: Batch((2,), 4097), lambda: Batch((2,), True),
               lambda: Batch(tuple(range(1, 10)), 1),
               lambda: least_replication(()), lambda: least_replication((1,)),
               lambda: least_replication((Batch((1,), 1),) * 9),
               lambda: partition(residue_minima((2, 3)), -1),
               lambda: partition(residue_minima((2, 3)), 2**80)]
    for operation in invalid:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError("invalid boundary was accepted")
    table = residue_minima((4, 7))
    longer = ((1, 3),) + table.witnesses[2:]
    corrupt = [replace(table, divisor=2), replace(table, modulus=2),
               replace(table, minima=(0, 21, 14)),
               replace(table, minima=(0, 25, 14, 7),
                       witnesses=(table.witnesses[0],) + longer),
               replace(table, witnesses=((1, 0),) + table.witnesses[1:]),
               replace(table, conductor=0)]
    for candidate in corrupt:
        try:
            check_table(candidate)
        except ValueError:
            continue
        raise ValueError("bad shortest-path certificate was accepted")
    need(least_replication((Batch((4, 7), 1),)).replication == 4,
         "gcd-only relaxation unexpectedly passed")
    need(least_replication((Batch((2,), 1), Batch((2,), 1))).replication == 2,
         "pooling two different chronological cuts unexpectedly passed")
    return {"invalid_boundaries": len(invalid), "certificate_mutations": len(corrupt),
            "gcd_and_pooling_controls": 2}


def boundary_checks():
    primes = (29, 31, 37, 41, 43, 47, 53, 59)
    fixtures = [(Batch((64,), 4096),), (Batch(primes, 4096),) * 8,
                tuple(Batch((p,), 1) for p in primes),
                (Batch((63, 64), 1),), (Batch((1,), 1),)]
    for batches in fixtures:
        schedule = least_replication(batches)
        for batch, table, counts in zip(batches, schedule.tables, schedule.partitions):
            check_table(table)
            check_partition(batch.widths, schedule.replication * batch.multiplicity,
                            counts)
    table = residue_minima((63, 64))
    need(table.conductor == 3906, "two-generator conductor control")
    need(partition(table, 3905) is None and partition(table, 3906) is not None,
         "conductor boundary failed")
    return {"capacity_fixtures": len(fixtures), "conductor_63_64": table.conductor}


def main():
    result = {"exhaustive": exhaustive_checks(), "strict_gain": strict_family_checks(),
              "controls": rejection_checks(), "bounds": boundary_checks()}
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "batching.py", "verify.py")
    hashes = {}
    for name in files:
        path = Path(__file__).resolve().parent / name
        need(path.stat().st_size <= 262144, "package hash input capacity")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"result": result, "sha256": hashes,
                      "python": platform.python_version()}, sort_keys=True))
    print("PASS_MIXED_WIDTH_BATCHING")


if __name__ == "__main__":
    main()
