"""Independent exact census of PR889's signed star queries (Apache-2.0).

The only imported subject routine is its instruction emitter. No predecessor
state interpreter, word census, price function, or expected receipt is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def remaining_lower_bound(t, pairs):
    # Each nonzero dirt coefficient needs at least |a| unit queries. If a=0
    # but b!=1, at least two opposite queries are needed to change the signal
    # and return the dirt coefficient to zero. B restoration is separate.
    return abs(t) + sum(abs(a) if a else (0 if b == 1 else 2)
                        for a, b in pairs)


def transitions(state):
    t, pairs = state
    yield (t + 1, pairs), 1
    yield (t - 1, pairs), 1
    for (a, b), multiplicity in Counter(pairs).items():
        rest = list(pairs)
        rest.remove((a, b))
        for sign in (-1, 1):
            changed = tuple(sorted(rest + [(a + sign, b + sign * t)]))
            yield (t, changed), multiplicity


def census(k):
    """Count labelled signed words through 2k+2 via exact orbit multiplicities."""
    limit = 2 * k + 2
    goal = (0, ((0, 1),) * k)
    layer = {(0, ((0, 0),) * k): 1}
    counts = [0]
    sizes = [1]
    for depth in range(1, limit + 1):
        following = Counter()
        for state, ways in layer.items():
            for target, multiplicity in transitions(state):
                if remaining_lower_bound(*target) <= limit - depth:
                    following[target] += ways * multiplicity
        layer = following
        counts.append(layer.get(goal, 0))
        sizes.append(len(layer))
    require(not any(counts[:-1]), f"shorter valid word at k={k}")
    expected = 2 * (k + 1) * factorial(k) ** 2
    require(counts[-1] == expected, f"minimum-word census at k={k}")
    return dict(outputs=k, maximum_length=limit, alphabet_size=2*(k+1),
                raw_words_through_horizon=sum((2*(k+1))**n for n in range(limit+1)),
                accepted_by_length=counts,
                retained_states_by_length=sizes, minimum_word_count=expected)


def labelled_census(k):
    """Unquotiented and unpruned cross-check; only used for k=1,2."""
    limit = 2 * k + 2
    layer = {(0, (0,) * k, (0,) * k): 1}
    counts = [0]
    for _ in range(limit):
        following = Counter()
        for (t, a, b), ways in layer.items():
            following[t + 1, a, b] += ways
            following[t - 1, a, b] += ways
            for i in range(k):
                for sign in (-1, 1):
                    aa, bb = list(a), list(b)
                    aa[i] += sign
                    bb[i] += sign * t
                    following[t, tuple(aa), tuple(bb)] += ways
        layer = following
        counts.append(layer.get((0, (0,) * k, (1,) * k), 0))
    return counts


def source_emitter():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    require(manifest["commit"] == "e2021d1c9e06948528cbc0a8fd7079b671da981d",
            "unexpected subject commit")
    require(sorted(record["path"] for record in manifest["files"]) ==
            ["vendor/pr889/NOTICE.md", "vendor/pr889/README.md", "vendor/pr889/batch.py"],
            "incomplete or duplicate source inventory")
    for record in manifest["files"]:
        data = (ROOT / record["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record["sha256"],
                "source SHA256: " + record["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == record["git_blob"],
                "source Git blob: " + record["path"])
    spec = importlib.util.spec_from_file_location("subject_batch", ROOT / "vendor/pr889/batch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compile_batch


def polynomial_replay(word, roles):
    """Free associative algebra over Z, retaining every initial dirty input.

    A monomial (r, fs) means the initial contents of role r with factors fs
    applied from left to right. Distinct fs never commute or cancel by chance.
    """
    values = [{(r, ()): 1} for r in range(roles)]
    for f, source, target, sign in word:
        require(type(f) is int and f >= 0, "bad factor")
        require(type(source) is int and type(target) is int and
                0 <= source < roles and 0 <= target < roles and source != target,
                "aliased or invalid ports")
        require(type(sign) is int and sign in (-1, 1), "bad sign")
        for (r, factors), coefficient in list(values[source].items()):
            key = r, factors + (f,)
            value = values[target].get(key, 0) + sign * coefficient
            if value:
                values[target][key] = value
            else:
                values[target].pop(key, None)
    return values


def check_word(word, roles, common, branches):
    actual = polynomial_replay(word, roles)
    expected = [{(r, ()): 1} for r in range(roles)]
    for i, branch in enumerate(branches, 1):
        expected[i][0, tuple(common + branch)] = 1
    require(actual == expected, "free-polynomial endpoint mismatch")


def check_star_word(word, k, connector):
    """Admit only the claimed one-connector star alphabet, then check its state."""
    t, a, b = 0, [0] * k, [0] * k
    for f, x, y, sign in word:
        require(sign in (-1, 1), "nonunit star sign")
        if (f, x, y) == (0, 0, connector):
            t += sign
        else:
            require(1 <= f <= k and (x, y) == (connector, f),
                    "outside star-query alphabet")
            a[f-1] += sign
            b[f-1] += sign*t
    require(t == 0 and a == [0]*k and b == [1]*k, "star endpoint mismatch")


def emitter_checks(compile_batch):
    records = []
    for k in range(1, 6):
        for common_length in range(1, 5):
            common = list(range(common_length))
            branches = []
            next_factor = common_length
            for i in range(k):
                # Seed 79 diversifies asymmetric branch lengths (1..3).
                length = 1 + (79 + i) % 3
                branches.append(list(range(next_factor, next_factor + length)))
                next_factor += length
            for mode in ("batch", "separate", "grouped"):
                word, dirt = compile_batch(common, branches, mode)
                roles = k + 1 + dirt
                check_word(word, roles, common, branches)
                reverse = [(f, x, y, -s) for f, x, y, s in reversed(word)]
                identity = [{(r, ()): 1} for r in range(roles)]
                require(polynomial_replay(word + reverse, roles) == identity,
                        "literal inverse mismatch")
                encoded = json.dumps(word, separators=(",", ":")).encode()
                records.append(dict(outputs=k, common_factors=common_length,
                                    branch_factors=list(map(len, branches)), mode=mode,
                                    leaf_calls=len(word), dirty_roles=dirt,
                                    word_sha256=hashlib.sha256(encoded).hexdigest()))
        common, branches = [0], [[i] for i in range(1, k + 1)]
        word, dirt = compile_batch(common, branches)
        require(dirt == 1, "emitter uses extra connector storage")
        require(len(word) == 2 * k + 2, "emitter misses query minimum")
        check_star_word(word, k, k + 1)
        check_word(word, k + 1 + dirt, common, branches)
    return records


def mutation_controls(compile_batch):
    common, branches = [0], [[1], [2]]
    word, dirt = compile_batch(common, branches)
    roles = 3 + dirt
    mutants = {}
    mutants["omit_B_restoration"] = word[:3] + word[4:]
    wrong = list(word)
    f, x, y, s = wrong[1]
    wrong[1] = (f, x, y, -s)
    mutants["wrong_output_sign"] = wrong
    wrong = list(word)
    f, x, y, s = wrong[3]
    wrong[3] = (79, x, y, s)
    mutants["change_common_factor_on_return"] = wrong
    mutants["omit_output_dirty_cancellation"] = word[:-1]
    wrong = list(word)
    f, x, y, s = wrong[1]
    wrong[1] = (f, x, x, s)
    mutants["aliased_source_target"] = wrong
    results = []
    for name, mutant in mutants.items():
        try:
            check_word(mutant, roles, common, branches)
        except ValueError:
            results.append(name)
        else:
            raise ValueError("accepted mutation: " + name)
    # Reversed application order would agree for commuting scalar fixtures.
    actual = polynomial_replay(word, roles)
    require(actual[1].get((0, (1, 0)), 0) != 1,
            "factor-order control was invisible")
    results.append("commuted_factor_product")
    return results


def certificate():
    compiler = source_emitter()
    rows = [census(k) for k in range(1, 6)]
    for k in (1, 2):
        require(labelled_census(k) == rows[k - 1]["accepted_by_length"],
                "labelled/unpruned census mismatch")
    return dict(schema="dirty-fanout-star-census-v1", assignment_seed=79,
                subject_head="e2021d1c9e06948528cbc0a8fd7079b671da981d",
                source_manifest_sha256=hashlib.sha256((ROOT / "SOURCES.json").read_bytes()).hexdigest(),
                census=rows, unquotiented_unpruned_crosschecks=[1, 2],
                source_star_minimum_cases=5,
                emitter_cases=emitter_checks(compiler),
                rejected_controls=mutation_controls(compiler),
                scope="Exact finite star-query census and free-algebra emitter endpoints; no new kappa")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = parser.parse_args()
    result = certificate()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    path = ROOT / "CERTIFICATE.json"
    if args.write:
        path.write_text(encoded)
    else:
        require(path.read_text() == encoded, "certificate mismatch")
    print("PASS_STAR_CENSUS k=1..5 minima=4,6,8,10,12 counts=4,24,288,5760,172800 "
          "emitter_cases=60 star_cases=5 controls=6 no_new_kappa")


if __name__ == "__main__":
    main()
