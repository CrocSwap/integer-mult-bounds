"""Check every native transfer, helper job and main-port adapter."""
from collections import Counter
from functools import cache
from hashlib import sha256
from pathlib import Path
import copy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from recoding import apply, encoded, need, read, receipt, sources
from network import main_roles
from binding16 import contact_phase
from upstream_application import boundary

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/shared-wire-split-composition/frozen"))
import clifford_exact as producer
import native_verify as checker


def span(basis):
    points = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in points, "independent native axes")
        points |= {x ^ v for x in points}
    return sum(1 << x for x in points)


def rank_data(word, net):
    masks = [span(b) for b in word["frames"]]
    dimensions = [len(b) for b in word["frames"]]

    def rank(pair):
        a, b = pair
        need(0 <= a < len(masks) and 0 <= b < len(masks), "frame index")
        intersection = (masks[a] & masks[b]).bit_count()
        need(intersection in (1 << dimensions[a], 1 << dimensions[b]) and dimensions[a] != dimensions[b], "positive nested pair")
        return abs(dimensions[a] - dimensions[b])

    mains = main_roles(word)
    helper_pairs = [(net.initial[r], net.final[r]) for r in range(len(net.initial)) if r not in mains]
    return Counter(map(rank, net.moves.values())), Counter(map(rank, helper_pairs)), set(helper_pairs)


def verify(shard, parts=5):
    word, parent, cuts = sources()
    net = apply(parent, cuts, word["frames"])
    _, _, helpers = rank_data(word, net)
    pairs = sorted(set(net.moves.values()) | helpers)
    rerouted = {pair for node, pair in net.moves.items() if pair != parent.moves[node]}
    basis = word["frames"]

    @cache
    def chart(i):
        return producer.canonical_frame(9, tuple(basis[i]))

    @cache
    def frame(i):
        return checker.frame(basis[i], 9)

    records = []
    exhaustive = []
    assigned = sorted(rerouted)[shard::parts] + sorted(set(pairs) - rerouted)[shard::parts]
    for a, b in assigned:
        recipe, _ = producer.lower_child(chart(a).adjoint().then(chart(b)))
        need(recipe["rank"] == abs(len(basis[a]) - len(basis[b])) > 0, "physical rank")
        actual = checker.recipe(recipe)
        target = checker.adjoint(frame(a)) + frame(b)
        checker.equal(actual, target, "signed Pauli action and Gaussian phase")
        if (a, b) in rerouted:
            for u, v in ((actual, target), (checker.adjoint(actual), checker.adjoint(target))):
                for col in range(512):
                    need(checker.state(u, col) == checker.state(v, col), "literal Gaussian column")
            exhaustive.append([a, b])
        if not records:
            wrong = copy.deepcopy(recipe)
            wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
            bad = checker.recipe(wrong)
            need(checker.tableau(bad) == checker.tableau(actual), "phase-only mutation")
            try:
                checker.equal(bad, target, "altered phase")
            except ValueError:
                pass
            else:
                raise ValueError("incorrect absolute phase accepted")
        records.append([a, b, recipe])
    ports = 0
    by_q = read(HERE / "data/CALLER-PHASE-BASES.json")["by_q"]
    contacts = []
    rejected_shift = False
    for x, q in list(zip(word["live"], word["ports"], strict=True))[shard::parts]:
        a, b = net.initial[x], net.final[x + 112]
        first, _ = producer.lower_child(producer.cgate(9, q, 1).adjoint().then(chart(a)))
        last, _ = producer.lower_child(chart(b).adjoint().then(producer.cgate(9, q, -1).then(producer.fourier(9))))
        need(first["rank"] == last["rank"] == 0 and not basis[net.initial[x + 112]], "main adapters")
        checker.equal(checker.recipe(first), (("C", q, -1),) + frame(a), "main input phase")
        checker.equal(checker.recipe(last), checker.adjoint(frame(b)) + (("C", q, -1),) + checker.fourier(9), "main output phase")
        checker.equal(frame(net.final[x]), checker.fourier(9), "full main endpoint")
        ports += 1
        for stage in range(1, 17):
            shifts, fault = contact_phase(q, by_q[str(q)], stage, 137)
            contacts.append([q, stage, shifts])
            if fault and not rejected_shift:
                transform, (before, after) = fault
                try:
                    boundary(before, after, transform, omit_translation=True)
                except ValueError as exc:
                    need(str(exc) == "forward contact includes its phase", "contact control")
                    rejected_shift = True
                else:
                    raise ValueError("omitted contact phase accepted")
    need(rejected_shift, "nontrivial phase control")
    return dict(slice=shard, total=len(pairs), checked=len(records), columns=exhaustive,
                ports=ports, contacts=len(contacts), contact_sha256=sha256(encoded(contacts)).hexdigest(),
                recipes_sha256=sha256(encoded(records)).hexdigest())


if __name__ == "__main__":
    shard = int(sys.argv[1])
    need(sys.flags.optimize == 0 and 0 <= shard < 5, "catalogue configuration")
    result = verify(shard)
    receipt(f"catalogue-{shard}", result)
    print("PASS_CUT_CATALOGUE", shard, result["checked"], len(result["columns"]), result["contacts"])
