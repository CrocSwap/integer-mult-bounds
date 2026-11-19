"""Check signed pairs and main contacts. Adapted from the catalogue in PR 7756.

See retained/CREDITS.md for the source authors and retained engines.
"""
from copy import deepcopy
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from supplier import HERE, SOURCE, build, digest, need, read
from binding16 import contact_phase
from upstream_application import boundary

sys.path.insert(0, str(HERE.parents[2] / "research/shared-wire-split-composition/frozen"))
import clifford_exact as producer
import native_verify as checker


def verify(shard):
    candidate, layout, net = build()
    hosted = layout["hosted"]
    mains = set(layout["live"]) | {x + 112 for x in layout["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    pairs = set(net.moves.values()) | {(a, b) for r, (a, b) in enumerate(zip(net.initial, net.final, strict=True))
                                       if r not in mains}
    basis, keep = layout["frames"], layout["source_labels"]
    dense_pairs = []

    @cache
    def chart(i):
        return producer.canonical_frame(9, tuple(basis[i]))
    @cache
    def frame(i):
        return checker.frame(basis[i], 9)

    records = []
    for a, b in sorted(pairs)[shard::3]:
        recipe, _ = producer.lower_child(chart(a).adjoint().then(chart(b)))
        need(recipe["rank"] == abs(len(basis[a]) - len(basis[b])) > 0, "physical rank")
        target = checker.adjoint(frame(a)) + frame(b)
        actual = checker.recipe(recipe)
        checker.equal(actual, target, "signed Pauli action and absolute phase")
        if not records or (a, b) in {(3, 288), (767, 127)}:
            dense_pairs.append([a, b])
            for op, ref in ((actual, target), (checker.adjoint(actual), checker.adjoint(target))):
                for column in range(512):
                    need(checker.state(op, column) == checker.state(ref, column), "literal Gaussian column")
            bad = deepcopy(recipe)
            bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
            try:
                checker.equal(checker.recipe(bad), target, "phase fault")
            except ValueError:
                pass
            else:
                raise ValueError("altered global phase accepted")
        records.append([a, b, recipe])
    contacts, ports = [], 0
    by_q = read(SOURCE / "data/CALLER-PHASE-BASES.json")["by_q"]
    rejected = False
    for x, q in list(zip(layout["live"], layout["ports"], strict=True))[shard::3]:
        a, b = candidate["initial"][x], candidate["final"][x + 112]
        need(keep[x + 112] == keep[x] + 112 and not basis[candidate["initial"][x + 112]], "first-plane partners")
        first, _ = producer.lower_child(producer.cgate(9, q, 1).adjoint().then(chart(a)))
        last, _ = producer.lower_child(chart(b).adjoint().then(producer.cgate(9, q, -1).then(producer.fourier(9))))
        need(first["rank"] == last["rank"] == 0, "ordinary main adapters")
        checker.equal(checker.recipe(first), (("C", q, -1),) + frame(a), "main entrance phase")
        checker.equal(checker.recipe(last), checker.adjoint(frame(b)) + (("C", q, -1),) + checker.fourier(9),
                      "main exit phase")
        checker.equal(frame(candidate["final"][x]), checker.fourier(9), "main Fourier exit")
        ports += 1
        for stage in range(1, 17):
            shifts, fault = contact_phase(q, by_q[str(q)], stage, 137)
            contacts.append([q, stage, shifts])
            if fault and not rejected:
                transform, (before, after) = fault
                try:
                    boundary(before, after, transform, omit_translation=True)
                except ValueError as exc:
                    need(str(exc) == "forward contact includes its phase", "wrong contact rejection")
                    rejected = True
    need(rejected, "missing contact phase control")
    return dict(shard=shard, total_pairs=len(pairs), checked_pairs=len(records), dense_pairs=dense_pairs,
                forward_and_adjoint_columns=1024 * len(dense_pairs), ports=ports, contacts=len(contacts),
                recipes_sha256=digest(records), contacts_sha256=digest(contacts))


if __name__ == "__main__":
    need(sys.flags.optimize == 0, "source compiler assertions enabled")
    shard = int(sys.argv[1])
    need(0 <= shard < 3, "invalid shard")
    result = verify(shard)
    need(read(HERE / f"CHARTS-{shard}.json") == result, "complete chart receipt")
    print("PASS_SUPPLIER_CHARTS", shard, result["checked_pairs"], result["contacts"])
