#!/usr/bin/env python3
"""Independent finite adversarial checks for the cleanup-prefix proof contract.

Apache-2.0. Substantial OpenAI Codex assistance (seed76 independent reviewer).
The matrix oracle uses only Python's exact Fraction arithmetic. It imports no
supplier arithmetic, emitted replay, binding tool, or Lean-generated result.
This is finite evidence, not the universal proof or the actual CK binding.
Run from any directory: python -I -B /path/to/this/review.py
"""
import ast
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/complex-k492-owner-repair/code/build_hpe.py"
SOURCE_SHA256 = "ba2001695d8c7547a82260c3b016e01dac686e95a61757ca124eb9879078ea8e"


def need(condition, message):
    # Remains active under python -O, unlike supplier assertions.
    if not condition:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Gate:
    kind: str
    target: int
    source: int | None
    coefficient: Q

    def raw(self):
        q = self.coefficient
        if self.kind == "add":
            return ["add", self.target, self.source, q.numerator, q.denominator, []]
        return ["scale", self.target, q.numerator, q.denominator, []]


def add(t, s, q=1):
    return Gate("add", t, s, Q(q))


def scale(t, q):
    return Gate("scale", t, None, Q(q))


def execute(word, vector):
    """Snapshot-before-write register semantics, including t += q*t."""
    state = list(map(Q, vector))
    for gate in word:
        old = tuple(state)
        t = gate.target
        need(type(t) is int and 0 <= t < len(state), "invalid target")
        if gate.kind == "add":
            s = gate.source
            need(type(s) is int and 0 <= s < len(state), "invalid source")
            state[t] = old[t] + gate.coefficient * old[s]
        elif gate.kind == "scale":
            need(gate.source is None, "scale has a source")
            state[t] = gate.coefficient * old[t]
        else:
            raise ValueError("unknown scalar operation")
    return tuple(state)


@lru_cache(maxsize=None)
def matrix(word, n):
    """Full linear map as exact columns; every register may initially be dirty."""
    return tuple(execute(word, [int(i == j) for i in range(n)]) for j in range(n))


def witness(left, right, n):
    a, b = matrix(tuple(left), n), matrix(tuple(right), n)
    for j in range(n):
        if a[j] != b[j]:
            return {"basis_column": j, "left": list(map(str, a[j])),
                    "right": list(map(str, b[j])),
                    "left_word": [gate.raw() for gate in left],
                    "right_word": [gate.raw() for gate in right]}
    raise RuntimeError("claimed counterexample has identical maps")


def source_functions():
    payload = SOURCE.read_bytes()
    need(hashlib.sha256(payload).hexdigest() == SOURCE_SHA256, "source pin changed")
    tree = ast.parse(payload, filename=str(SOURCE))
    names = {"span", "regs", "commute", "last_frames", "apply"}
    definitions = [node for node in tree.body
                   if isinstance(node, ast.FunctionDef) and node.name in names]
    need({node.name for node in definitions} == names, "source functions missing")
    # Extract unchanged source functions without executing the module's CLI.
    # optimize=0 is essential: this review tests the supplier's assert guards.
    namespace = {"Counter": Counter}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(SOURCE),
                 "exec", optimize=0), namespace)
    return namespace


def touched(gate):
    return {gate.target} if gate.kind == "scale" else {gate.target, gate.source}


def extract(word, indices):
    """Original indices; recipe order first, untouched subsequence second."""
    need(len(set(indices)) == len(indices), "duplicate extraction index")
    need(all(type(i) is int and 0 <= i < len(word) for i in indices),
         "invalid extraction index")
    selected = set(indices)
    return tuple(word[i] for i in indices) + tuple(
        gate for i, gate in enumerate(word) if i not in selected)


def source_scalar_guard(word, indices, commute):
    """Only the scalar hypotheses; entering-helper/frame hypotheses are separate."""
    if len(set(indices)) != len(indices):
        return False
    if any(type(i) is not int or not 0 <= i < len(word) for i in indices):
        return False
    seen = set()
    for i in indices:
        registers = touched(word[i])
        if seen & registers:
            return False
        seen |= registers
        for j in range(i):
            # Disjoint gates are omitted by the actual source's on[r] filter.
            if registers & touched(word[j]) and not commute(word[j].raw(), word[i].raw()):
                return False
    return True


def pair_checks(commute):
    coefficients = tuple(map(Q, (-2, -1, 0, 1, 2))) + (Q(1, 2),)
    gates = tuple(add(t, s, q) for t in range(4) for s in range(4) for q in coefficients)
    gates += tuple(scale(t, q) for t in range(4) for q in coefficients)
    accepted = semantic_only = 0
    for a, b in itertools.product(gates, repeat=2):
        allowed = commute(a.raw(), b.raw())
        need(allowed == commute(b.raw(), a.raw()), "source predicate is not symmetric")
        equal = matrix((a, b), 4) == matrix((b, a), 4)
        if allowed:
            need(equal, "source predicate admitted a noncommuting gate pair")
            accepted += 1
        elif equal:
            semantic_only += 1
    cases = {
        "same_target_distinct_sources": (add(0, 1, 2), add(0, 2, Q(1, 2)), True),
        "same_target_same_source": (add(0, 1, 2), add(0, 1, -1), True),
        "same_source_distinct_targets": (add(0, 2), add(1, 2, -1), True),
        "self_add_disjoint": (add(0, 0), scale(1, 0), True),
        "self_add_annihilation_disjoint": (add(0, 0, -1), add(1, 2), True),
        "scales_disjoint_including_zero": (scale(0, 0), scale(1, -1), True),
        "same_register_scales_rejected_but_commute": (scale(0, 2), scale(0, 3), False),
        "zero_add_dependency_rejected_but_commutes": (add(0, 1, 0), add(1, 2), False),
        "self_add_dependency_rejected": (add(0, 0), add(1, 0), False),
        "scale_target_dependency_rejected": (scale(0, 2), add(0, 1), False),
    }
    boundaries = {}
    for name, (a, b, expected) in cases.items():
        need(commute(a.raw(), b.raw()) == expected, name)
        equal = matrix((a, b), 4) == matrix((b, a), 4)
        boundaries[name] = {"predicate_accepts": expected, "maps_equal": equal}
    return {"registers": 4, "coefficients": list(map(str, coefficients)),
            "ordered_pairs": len(gates)**2, "accepted": accepted,
            "rejected_but_semantically_commuting": semantic_only,
            "boundary_cases": boundaries}


def extraction_checks(commute):
    alphabet = (add(0, 1), add(0, 2, -1), add(1, 2), add(2, 2, -1),
                scale(0, 2), scale(3, 0), add(3, 2, Q(1, 2)), add(1, 0, 0))
    tested = admitted = unsorted = multi = 0
    for length in range(4):
        recipes = tuple(indices for size in range(length + 1)
                        for indices in itertools.permutations(range(length), size))
        for word in itertools.product(alphabet, repeat=length):
            original = matrix(word, 4)
            for indices in recipes:
                tested += 1
                if not source_scalar_guard(word, indices, commute):
                    continue
                need(matrix(extract(word, indices), 4) == original,
                     "admissible extraction changed the full map")
                admitted += 1
                unsorted += tuple(sorted(indices)) != indices
                multi += len(indices) > 1
    need(unsorted > 0 and multi > 0, "recipe-order boundary never exercised")
    return {"alphabet_size": len(alphabet), "word_lengths": [0, 1, 2, 3],
            "word_recipe_pairs": tested, "admitted": admitted,
            "admitted_unsorted": unsorted, "admitted_multiple": multi}


def counterexamples():
    a, b = add(0, 1), add(1, 2)
    s, t = scale(0, 2), add(0, 1)
    u, v = add(0, 0), add(1, 0)
    original = (a, scale(3, 2), b)
    return {
        "read_write_dependency": witness((a, b), (b, a), 4),
        "scale_add_same_target": witness((s, t), (t, s), 4),
        "self_add_read_dependency": witness((u, v), (v, u), 4),
        "checking_only_adjacent_predecessor_is_unsound": witness(original, extract(original, (2,)), 4),
        "duplicate_index_repeats_operation": witness((a,), (a, a), 4),
        "selected_pairs_cannot_be_exempted_from_prefix_check": witness((a, b), extract((a, b), (1, 0)), 4),
    }


def mock_word(cleanup):
    # Six registers: one data, one target, four entering helpers.
    return {"report": {"v": 1, "R": 4, "local_profile": {"8": 5, "9": 1}},
            "ports": [1], "start_extra": {str(h): [1] for h in range(2, 6)},
            "A": [], "B": [], "cleanup": [g.raw() for g in cleanup]}


def source_apply_checks(functions):
    apply = functions["apply"]
    word = (scale(4, 2), add(2, 0), scale(5, -1), add(3, 1, Q(1, 2)))
    changes = [{"helper": 3, "cleanup_index": 3, "frame": [1]},
               {"helper": 2, "cleanup_index": 1, "frame": [1]}]
    output = apply(mock_word(word), copy.deepcopy(changes))
    indices = tuple(entry[0] for entry in output["early_cleanup"])
    need(indices == (3, 1), "source sorted or otherwise changed recipe order")
    need(matrix(word, 6) == matrix(extract(word, indices), 6), "source extraction mismatch")
    invalid = {
        "duplicate_change": (mock_word(word), [changes[0], changes[0]]),
        "shared_source_between_changes": (mock_word((add(2, 0), add(3, 0))),
            [{"helper": 2, "cleanup_index": 0, "frame": [1]},
             {"helper": 3, "cleanup_index": 1, "frame": [1]}]),
        "helper_touched_twice": (mock_word((add(2, 0), scale(2, 2))),
            [{"helper": 2, "cleanup_index": 0, "frame": [1]}]),
        "self_add_helper_counted_twice": (mock_word((add(2, 2),)),
            [{"helper": 2, "cleanup_index": 0, "frame": [1]}]),
        "noncommuting_prefix": (mock_word((add(0, 1), add(2, 0))),
            [{"helper": 2, "cleanup_index": 1, "frame": [1]}]),
        "negative_original_index": (mock_word(word),
            [{"helper": 3, "cleanup_index": -1, "frame": [1]}]),
        "wrong_frame_join": (mock_word(word),
            [{"helper": 3, "cleanup_index": 3, "frame": []}]),
    }
    rejected = {}
    for name, (w, recipe) in invalid.items():
        try:
            apply(w, copy.deepcopy(recipe))
        except AssertionError as error:
            rejected[name] = str(error)
        else:
            raise RuntimeError("source accepted invalid recipe: " + name)
    return {"accepted_original_indices_in_recipe_order": list(indices),
            "negative_controls_rejected": rejected,
            "note": "Synthetic scalar/source boundary fixtures, not the selected CK witness."}


def sparse_map(word, n):
    """Independent full-map row propagation, avoiding a dense CK matrix."""
    rows = [{i: Q(1)} for i in range(n)]
    for gate in word:
        t, q = gate.target, gate.coefficient
        old = dict(rows[t])
        if gate.kind == "scale":
            rows[t] = {j: q*x for j, x in old.items() if q*x}
        else:
            source = dict(rows[gate.source])
            for j, x in source.items():
                old[j] = old.get(j, Q(0)) + q*x
            rows[t] = {j: x for j, x in old.items() if x}
    return rows


def source_binding_checks():
    """Phase 3: completed source artifacts only; never loads Lean/build files."""
    here = Path(__file__).resolve().parent
    pins = json.loads((here/'SOURCES.json').read_bytes())
    spec = json.loads((SOURCE.parents[1]/'data/SPEC.json').read_bytes())
    chain = spec['build']['providers']['ck']
    need(pins['ck_chain'] == chain, "descriptive CK chain differs from pinned SPEC")
    hpe = [s for s in chain['steps'] if s['type'] == 'hyperplane_end']
    need(len(hpe) == 1, "HPE step not unique")
    payload = gzip.decompress((here/'CK-PRE-HPE.json.gz').read_bytes())
    need(hashlib.sha256(payload).hexdigest() == hpe[0]['input_content_sha256'],
         "independent pre-HPE pin")
    word = json.loads(payload)
    recipe_path = SOURCE.parents[1]/hpe[0]['recipe'].removeprefix('pkg:')
    recipe = json.loads(recipe_path.read_bytes())
    fixture = json.loads((here/'CK-FIXTURE.json').read_bytes())
    n = 2*word['report']['v'] + word['report']['R']
    need(n == fixture['register_count'] == 716, "independent register count")
    gates = []
    for event, normalized in zip(word['cleanup'], fixture['cleanup']):
        kind = event[0]
        need(kind in ('add', 'scale'), "unknown raw gate")
        position = 3 if kind == 'add' else 2
        q = Q(event[position], event[position+1])
        gate = add(event[1], event[2], q) if kind == 'add' else scale(event[1], q)
        expected = dict(kind=kind, target=gate.target, num=q.numerator, den=q.denominator)
        if kind == 'add':
            expected['source'] = gate.source
        need(normalized == expected, "independent raw-to-fixture projection")
        gates.append(gate)
    need(len(gates) == len(word['cleanup']) == len(fixture['cleanup']) == 2869,
         "complete cleanup projection")
    indices = tuple(change['cleanup_index'] for change in recipe['changes'])
    need(list(indices) == fixture['selected_indices'] and len(indices) == 34,
         "recipe order/selection binding")
    need(all(indices[k] > indices[k+1] for k in range(len(indices)-1)),
         "expected descending original indices")
    original_functions = source_functions()
    need(source_scalar_guard(gates, indices, original_functions['commute']),
         "original source scalar guards fail")
    shared = [[j, i] for i in indices for j in range(i) if touched(gates[j]) & touched(gates[i])]
    occupied = set().union(*(touched(gates[i]) for i in indices))
    need(sum(indices) == fixture['counts']['full_prefix_pairs'] == 19084,
         "independent full-prefix pair count")
    need(shared == fixture['counts']['shared_register_pairs'] and len(shared) == 8,
         "independent shared prefix pairs")
    need(len(occupied) == fixture['counts']['selected_registers'] == 68,
         "independent selected register count")
    # Execute precisely the pinned constructor's eligibility/frame/profile checks.
    output = original_functions['apply'](copy.deepcopy(word), copy.deepcopy(recipe['changes']))
    out_bytes = json.dumps(output, sort_keys=True, separators=(',', ':')).encode()
    need(hashlib.sha256(out_bytes).hexdigest() == hpe[0]['output_content_sha256'],
         "actual pinned apply output hash")
    need(sparse_map(gates, n) == sparse_map(extract(gates, indices), n),
         "independent entire CK cleanup map differs")

    # Use the completed checker only as a system under test. Its arithmetic is
    # not used to compute the independent full-map equality above.
    checker_path = here/'check_source.py'
    checker_bytes = checker_path.read_bytes()
    checker = {'__file__': str(checker_path), '__name__': 'completed_source_under_review'}
    exec(compile(checker_bytes, str(checker_path), 'exec'), checker)
    checker['load_fixture']()
    original_read = Path.read_bytes

    def virtual_load(path, replacement):
        def read(candidate):
            return replacement if candidate == path else original_read(candidate)
        with patch.object(Path, 'read_bytes', read):
            return checker['load_fixture']()

    mutations = {}
    for name, mutate in (
        ('last_unselected_gate_coefficient', lambda d: d['cleanup'][-1].__setitem__('num', d['cleanup'][-1]['num']+1)),
        ('empty_selection', lambda d: d.__setitem__('selected_indices', [])),
        ('sorted_selection', lambda d: d.__setitem__('selected_indices', sorted(d['selected_indices']))),
        ('extra_gate_field', lambda d: d['cleanup'][0].__setitem__('unexpected', 1)),
        ('equivalent_unnormalized_fraction', lambda d: (d['cleanup'][0].__setitem__('num', 2*d['cleanup'][0]['num']), d['cleanup'][0].__setitem__('den', 2*d['cleanup'][0]['den']))),
    ):
        damaged = copy.deepcopy(fixture)
        mutate(damaged)
        mutations[name] = (here/'CK-FIXTURE.json', json.dumps(damaged).encode(), 'fixture mismatch')
    damaged = copy.deepcopy(word)
    damaged['ports'][0] ^= 1
    mutations['noncleanup_payload_field'] = (here/'CK-PRE-HPE.json.gz', gzip.compress(json.dumps(damaged).encode()), 'pre-HPE payload hash')
    mutations['recipe_source_bytes'] = (recipe_path, recipe_path.read_bytes()+b' ', 'source hash:')
    mutations['producer_source_bytes'] = (SOURCE, SOURCE.read_bytes()+b'\n', 'source hash:')
    rejected = {}
    for name, (path, replacement, reason) in mutations.items():
        try:
            virtual_load(path, replacement)
        except ValueError as error:
            need(reason in str(error), "unexpected rejection path: "+name)
            rejected[name] = str(error)
        else:
            raise RuntimeError("source bridge corruption accepted: "+name)
    recompressed = virtual_load(here/'CK-PRE-HPE.json.gz', gzip.compress(payload, mtime=123))
    need(recompressed == fixture, "gzip recompression changed semantic fixture")
    raw_boundary_rejections = {}
    for name, raw in (
        ('boolean_denominator', ['add', 0, 1, 1, True, []]),
        ('float_coefficient', ['add', 0, 1, 1.0, 1, []]),
        ('boolean_register', ['scale', True, 2, 1, []]),
        ('source_upper_bound', ['add', 0, n, 1, 1, []]),
        ('zero_scale_fixture_domain', ['scale', 0, 0, 1, []]),
    ):
        try:
            checker['normalize'](raw, n)
        except ValueError as error:
            raw_boundary_rejections[name] = str(error)
        else:
            raise RuntimeError("boundary accepted: "+name)
    need(checker['normalize'](['scale', 0, 2, -4, []], n)['num'] == -1,
         "negative denominator normalization")
    return dict(status='PASS_INDEPENDENT_CK_SOURCE_BINDING_REVIEW',
                checker_sha256=hashlib.sha256(checker_bytes).hexdigest(),
                full_map_columns=n, cleanup_gates=len(gates), selected_gates=len(indices),
                full_prefix_pairs=sum(indices), shared_register_pairs=shared,
                selected_registers=len(occupied),
                source_apply_output_sha256=hashlib.sha256(out_bytes).hexdigest(),
                corrupted_artifacts_rejected=rejected,
                schema_boundaries_rejected=raw_boundary_rejections,
                gzip_recompression='accepted with identical decompressed payload',
                scope='Completed source bridge only; Lean and generator/runner artifacts unread.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-binding', action='store_true',
                        help='also review completed CK source artifacts; never load Lean/build files')
    args = parser.parse_args()
    functions = source_functions()
    result = {"status": "PASS_INDEPENDENT_FINITE_CLEANUP_PREFIX_REVIEW",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": SOURCE_SHA256,
              "pair_checks": pair_checks(functions["commute"]),
              "extraction_checks": extraction_checks(functions["commute"]),
              "counterexamples": counterexamples(),
              "source_apply_checks": source_apply_checks(functions),
              "scope": "Exact finite scalar maps and source guard controls; not a universal proof, CK source binding, frame-accounting proof, or multiplication theorem."}
    if args.source_binding:
        result['source_binding'] = source_binding_checks()
        result['scope'] = ('Finite phase-1 scalar tests plus independent CK source-bridge review; '
                           'not a universal proof or validation of Lean/generator/runner artifacts.')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
