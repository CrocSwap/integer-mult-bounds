"""Check the signed operators on the remaining chart pairs and all main contacts."""
from collections import Counter
from copy import deepcopy
from functools import cache
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quotient import HERE, construct_candidate, digest, main_roles, need, parent, read, receipt
from binding16 import contact_phase
from upstream_application import boundary

sys.path.insert(0, str(HERE.parents[1] / "research/shared-wire-split-composition/frozen"))
import clifford_exact as producer
import native_verify as checker


def jobs(net, layout):
    mains = main_roles(layout)
    helpers = [(a, b) for r, (a, b) in enumerate(zip(net.initial, net.final, strict=True)) if r not in mains]
    pairs = set(net.moves.values()) | set(helpers)
    spans = {}
    for i in {j for pair in pairs for j in pair}:
        span = {0}
        for v in layout["frames"][i]:
            need(0 < v < 512 and v not in span, "independent frame axes")
            span |= {x ^ v for x in span}
        spans[i] = span
    for a, b in set(helpers):
        need(spans[a] < spans[b], "positive oriented helper")
    for a, b in pairs:
        need(spans[a] < spans[b] or spans[b] < spans[a], "nested paid pair")
    def rank(pair):
        a, b = pair
        return abs(len(layout["frames"][a]) - len(layout["frames"][b]))
    return Counter(map(rank, net.moves.values())), Counter(map(rank, helpers)), pairs


def verify(shard):
    word, source = parent()
    candidate, layout, keep = construct_candidate(word, source)
    _, _, original = jobs(source, word)
    _, _, pairs = jobs(candidate, layout)
    need(pairs <= original and all(source.moves[k] == v for k, v in candidate.moves.items()),
         "the final schedule uses only inherited physical routes")
    basis = layout["frames"]
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
        if not records:
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
    by_q = read(HERE / "data/CALLER-PHASE-BASES.json")["by_q"]
    rejected = False
    for x, q in list(zip(layout["live"], layout["ports"], strict=True))[shard::3]:
        a, b = candidate.initial[x], candidate.final[x + 112]
        need(keep[x + 112] == keep[x] + 112 and not basis[candidate.initial[x + 112]], "first-plane partners")
        first, _ = producer.lower_child(producer.cgate(9, q, 1).adjoint().then(chart(a)))
        last, _ = producer.lower_child(chart(b).adjoint().then(producer.cgate(9, q, -1).then(producer.fourier(9))))
        need(first["rank"] == last["rank"] == 0, "ordinary main adapters")
        checker.equal(checker.recipe(first), (("C", q, -1),) + frame(a), "main entrance phase")
        checker.equal(checker.recipe(last), checker.adjoint(frame(b)) + (("C", q, -1),) + checker.fourier(9),
                      "main exit phase")
        checker.equal(frame(candidate.final[x]), checker.fourier(9), "main Fourier exit")
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
    return dict(shard=shard, total_pairs=len(pairs), checked_pairs=len(records), dense_pair=records[0][:2],
                forward_and_adjoint_columns=1024, ports=ports, contacts=len(contacts),
                recipes_sha256=digest(records), contacts_sha256=digest(contacts))


if __name__ == "__main__":
    shard = int(sys.argv[1])
    need(0 <= shard < 3, "invalid shard")
    result = verify(shard)
    receipt(f"catalogue-{shard}", result)
    print("PASS_HELPER_CHARTS", shard, result["checked_pairs"], result["contacts"])
