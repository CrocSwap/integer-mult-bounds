"""Source-bound balanced dirty-prefix precision audit; standard library only.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


core = load('precision_core', HERE/'core.py')
matrix = load('dense_prefixes', HERE/'matrices.py')
numeric = load('rounded_checks', HERE/'numeric.py')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def sources():
    record = json.loads((HERE/'SOURCES.json').read_text())
    for item in record['files']:
        raw = (HERE/item['vendored_path']).read_bytes()
        core.need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source drift: '+item['vendored_path'])
        git_object = b'blob '+str(len(raw)).encode()+b'\0'+raw
        core.need(hashlib.sha1(git_object).hexdigest() == item['git_blob'], 'source Git object')
    return record


def recurrence_checks(vendor):
    cases, instructions = 0, 0
    digest = hashlib.sha256()
    for n in range(1, 10001):
        scratch, calls, exponent = core.resources(n)
        q = 1 << (n.bit_length()-1)
        core.need(calls == 3*q*n-2*q*q, 'independent exact-count formula')
        core.need(scratch == (n-1).bit_length() and exponent <= 4*n-3, 'all-n resource majorant')
        if n == q:
            core.need(exponent == 3*n-2, 'power-of-two prefix formula')
        digest.update(canonical([n, scratch, calls, exponent]).encode()+b'\n')
        if n <= 64:
            for sign in (-1, 1):
                generated = list(core.word(n, sign))
                actual = matrix.vendor_word(vendor, n, sign)
                core.need(generated == actual and len(actual) == calls, 'pinned dispatcher word mismatch')
                cases += 1
                instructions += len(actual)
    return dict(recurrence_cases=10000, exact_predecessor_words=cases,
                predecessor_instructions=instructions, recurrence_sha256=digest.hexdigest())


def dense_checks():
    rng = random.Random(63)
    results = []
    for n in (1, 2, 3, 5, 8, 15, 16, 31, 63):
        factors = [[[rng.randrange(-2, 3) for _ in range(2)] for _ in range(2)] for _ in range(n)]
        K = max(matrix.norm(f) for f in factors)
        scratch, _, exponent = core.resources(n)
        B = (1+K)**exponent
        for sign in (-1, 1):
            record = matrix.trace(factors, list(core.word(n, sign)), sign, scratch+2, B)
            results.append(dict(factors=n, sign=sign, K=K, prefix_exponent=exponent, **record))
    return results


def budget_checks(inherited, original):
    results = []
    for radix in range(3, 513):
        try:
            inherited.prime_power_data(radix)
        except ValueError:
            continue
        for p in (1, 32, 128, 1024, 1048576):
            for d in (0, 20, 1024):
                row = core.kernel_budget(radix, p, d, inherited)
                core.check_kernel_budget(row, inherited)
                old = original.budget(radix, p, d)
                original.check(old)
                results.append({**row, 'original_working_bits': old['working_bits']})
    return results


def controls(inherited):
    results = []

    def reject(name, action):
        try:
            action()
        except (ValueError, StopIteration) as error:
            results.append(dict(name=name, rejected=str(error)))
        else:
            raise ValueError('negative control accepted: '+name)

    row = core.kernel_budget(64, 128, 20, inherited)
    for name, key, value in [('too_few_bits', 'working_bits', row['working_bits']-1),
                             ('missing_inverse_prefix', 'prefix_exponent', 1),
                             ('missing_restoration_calls', 'leaf_calls', row['n']),
                             ('missing_coefficient_scaling', 'coefficient_target_bits', 128),
                             ('boolean_integer', 'dirty_arrays', True)]:
        bad = dict(row);bad[key] = value
        reject(name, lambda bad=bad: core.check_kernel_budget(bad, inherited))
    reject('no_feedback_control', lambda: core.execution_parameters(2, 3, 1, 10, 0))
    reject('unsupported_radix', lambda: core.kernel_budget(6, 128, 20, inherited))
    factors = [[[1, 1], [0, 1]], [[1, 0], [1, 1]], [[2, 1], [1, 1]]]
    word = list(core.word(3));bound = 4**core.resources(3)[2]
    reject('omitted_restore', lambda: matrix.trace(factors, word[:-1], 1, 4, bound))
    # At an odd factor count, flipping every leaf sign accidentally gives the
    # negative ideal product. The two-factor witness distinguishes the defect.
    wrong_inverse = [(s, t, i, -q) for s, t, i, q in core.word(2)]
    reject('sign_only_inverse', lambda: matrix.trace(factors[:2], wrong_inverse, -1, 3, bound))
    # Final product zero makes the whole word the identity. Its dirty prefix
    # is nevertheless nontrivial; final norm 1 is not a prefix certificate.
    factors = [[[2, 0], [0, 2]], [[0, 0], [0, 0]]]
    correct = matrix.trace(factors, list(core.word(2)), 1, 3, 3**core.resources(2)[2])
    core.need(correct['prefix_maximum'] == 3, 'identity-endpoint prefix witness')
    reject('endpoint_only_prefix_bound', lambda: matrix.trace(factors, list(core.word(2)), 1, 3, 1))
    return results


def verify():
    pin = sources()
    vendor = load('unchanged_pr628', HERE/'vendor/pr628/dirty.py')
    inherited = load('inherited_kernel_budget', HERE/'vendor/pr628/check_budgets.py')
    original = load('original_dirty_budget', HERE/'vendor/pr628/dirty_budgets.py')
    recurrence = recurrence_checks(vendor)
    dense = dense_checks()
    budgets = budget_checks(inherited, original)
    adverse = controls(inherited)
    generic = numeric.generic(core, vendor)
    kernels = numeric.kernels(core, vendor, json.loads((HERE/'vendor/pr628/FACTORS.json').read_text()))
    return dict(base_commit=pin['base_commit'], source_head=pin['source_head'],
                recurrence=recurrence, dense_prefixes=dense, uniform_budgets=budgets,
                negative_controls=adverse, rounded_generic=generic, rounded_kernels=kernels,
                result='Balanced dirty commutator: sufficient O(p+d+r^4) word size, unchanged leaf count and dirty arrays; no new kappa',
                scope='Written all-n prefix/perturbation argument plus finite exact evidence. Inherited preparation, phase access, routing and physical/compiler/analytic obligations remain.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='new receipt path; refuses overwrite')
    args = parser.parse_args()
    if args.write:
        core.need(not args.write.exists(), 'output already exists')
    report = verify()
    if args.write:
        with args.write.open('x') as output:
            json.dump(report, output, indent=2, sort_keys=True)
            output.write('\n')
    else:
        core.need(canonical(report) == canonical(json.loads((HERE/'EXPECTED.json').read_text())), 'certificate mismatch')
    print('PASS_DIRTY_PREFIX_PRECISION budgets='+str(len(report['uniform_budgets']))+
          ' prefix_traces='+str(len(report['dense_prefixes']))+
          ' rounded_generic='+str(len(report['rounded_generic']))+
          ' rounded_kernels='+str(len(report['rounded_kernels']))+
          ' controls='+str(len(report['negative_controls']))+' kappa=unchanged')


if __name__ == '__main__':
    main()
