"""Check the paid and productive maps and the main-port boundaries."""
from functools import cache
import argparse
import copy
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from word import catalogue, encoded, need, words
from hashlib import sha256

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/shared-wire-split-composition/frozen"))
import clifford_exact as producer
import native_verify as interpreter


def verify(shard, shards=6):
    need(sys.flags.optimize == 0 and 0 <= shard < shards, "proof configuration")
    source, word = words()
    basis = word["frames"]
    pairs = sorted(catalogue(word))
    fresh = set(pairs) - catalogue(source)

    @cache
    def chart(index):
        return producer.canonical_frame(9, tuple(basis[index]))

    @cache
    def frame(index):
        return interpreter.frame(basis[index], 9)

    full = 0
    negative = False
    records = []
    for a, b in pairs[shard::shards]:
        recipe, _ = producer.lower_child(chart(a).adjoint().then(chart(b)))
        need(recipe["rank"] == abs(len(basis[a]) - len(basis[b])) > 0, "paid or helper rank")
        actual = interpreter.recipe(recipe)
        desired = interpreter.adjoint(frame(a)) + frame(b)
        interpreter.equal(actual, desired, "signed Pauli generators and Gaussian phase")
        if (a, b) in fresh:
            for u, v in ((actual, desired), (interpreter.adjoint(actual), interpreter.adjoint(desired))):
                for j in range(512):
                    need(interpreter.state(u, j) == interpreter.state(v, j), "literal Gaussian column")
            full += 1
        if not negative:
            wrong = copy.deepcopy(recipe)
            wrong["left"]["phase"] = (wrong["left"]["phase"] + 1) % 4
            bad = interpreter.recipe(wrong)
            need(interpreter.tableau(bad) == interpreter.tableau(actual), "phase-only control shape")
            try:
                interpreter.equal(bad, desired, "wrong phase")
            except ValueError:
                negative = True
            need(negative, "phase-only control escaped")
        records.append([a, b, recipe])
    bounds = 0
    if shard == 0:
        for x, q in zip(word["live"], word["ports"], strict=True):
            a, b = word["initial"][x], word["final"][x + 112]
            before, _ = producer.lower_child(producer.cgate(9, q, 1).adjoint().then(chart(a)))
            after, _ = producer.lower_child(chart(b).adjoint().then(producer.cgate(9, q, -1).then(producer.fourier(9))))
            need(before["rank"] == after["rank"] == 0, "main monomial boundary")
            interpreter.equal(interpreter.recipe(before), (("C", q, -1),) + frame(a), "input phase")
            interpreter.equal(interpreter.recipe(after), interpreter.adjoint(frame(b)) + (("C", q, -1),) + interpreter.fourier(9), "output phase")
            interpreter.equal(frame(word["final"][x]), interpreter.fourier(9), "full main endpoint")
            bounds += 1
    return dict(shard=shard, of=shards, catalogue=len(pairs), new=len(fresh), checked=len(records),
                all_columns=full, main_boundaries=bounds, wrong_phase_rejected=negative,
                recipe_sha256=sha256(encoded(records)).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("shard", type=int)
    args = parser.parse_args()
    receipt = verify(args.shard)
    expected = json.loads((HERE / "RESULT.json").read_bytes())["catalogue"][args.shard]
    need(receipt == expected, "catalogue receipt")
    print("PASS_CHART_CATALOGUE", args.shard, receipt["checked"], receipt["all_columns"])
