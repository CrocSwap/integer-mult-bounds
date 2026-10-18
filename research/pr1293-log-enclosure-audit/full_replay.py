#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent whole-main replay of PR1293; standard library, no Git/network.

Default: read vendor/pr1293_verify.py and the three pinned repository inputs,
run original and strict repair in temporary files, require and compare the
committed FULL-REPLAY.json. --package supports running this file before installation.
--write-receipt writes an explicitly requested JSON outside the repository.
Timings are printed, not included in the deterministic receipt. No parent audit
implementation is imported. Subject attribution: Navinor, with help from opencode.
"""
import argparse
import ast
from collections import Counter
from contextlib import redirect_stdout
from fractions import Fraction as Q
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import tempfile
import time

SUBJECT_SHA = 'e69fc72f0534a8eb9ea8e6c0f83deb1ae6537d2f6bf8e511bca23026b68a270f'
STRICT_SHA = 'a1e2b9eb92e1e868a1d908fc57036c83d61e0107dce6e6ddae283fef916d7138'
RESULT_SHA = '731f77e404c18e3c1329d1ad084b3e0e3752579ae83fcb4e48a2b749d405c7a1'
INPUTS = {
    'research/community-frontier1094-audit/ASSEMBLY.json':
        '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045',
    'research/community-frontier1094-audit/INDEPENDENT1094.json':
        '301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd',
    'research/e8-bit-p111-tuned/tune/EXPECTED.json':
        'b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4',
}
OLD = b'        else:\n            lo = hi = mid\n            break\n'
MESSAGE = 'ln_exp_bisection unresolved at current Taylor order'
NEW = (b'        else:\n'
       b'            # Overlap is not equality; do not report a completed cross-check.\n'
       b"            raise ValueError('ln_exp_bisection unresolved at current Taylor order')\n")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    """Preserve JSON types: false is not zero, and 48.0 is not 48."""
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load_json(data):
    def unique_keys(pairs):
        keys = [key for key, _ in pairs]
        require(len(keys) == len(set(keys)), 'duplicate JSON key')
        return dict(pairs)
    return json.loads(data, object_pairs_hook=unique_keys)


def check_receipt(actual, expected):
    require(canonical(actual) == canonical(expected),
            'FULL-REPLAY.json differs; review before replacing')


def checked(path, expected):
    data = path.read_bytes()
    require(sha(data) == expected, 'source pin mismatch: ' + str(path))
    return data


class Trace:
    """Observe actual invocation order, branch sequence and exact returns."""
    def __init__(self, source, filename):
        self.filename, self.calls = filename, []
        fn = next(n for n in ast.parse(source).body
                  if isinstance(n, ast.FunctionDef) and n.name == 'ln_exp_bisection')
        loop = next(n for n in fn.body if isinstance(n, ast.For))
        test = next(n for n in loop.body if isinstance(n, ast.If))
        self.iteration_line = loop.body[0].lineno
        self.branches = {test.body[0].lineno: 'L', test.orelse[0].body[0].lineno: 'H',
                         test.orelse[0].orelse[0].lineno: 'A'}

    def __call__(self, frame, event, value):
        if (event != 'call' or frame.f_code.co_filename != self.filename
                or frame.f_code.co_name != 'ln_exp_bisection'):
            return None
        row = {'argument': str(frame.f_locals['frac']), 'iterations': 0, 'branches': ''}
        row['constants'] = [frame.f_globals['CROSS_ORDER'], frame.f_globals['CROSS_BITS']]
        row['stack'] = []
        # Normalize comprehension-only frames: CPython 3.12 inlines them.
        # Every logical subject caller and its source line is still retained.
        parent = frame.f_back
        while parent:
            if (parent.f_code.co_filename == self.filename
                    and parent.f_code.co_name not in ('<dictcomp>', '<listcomp>', '<genexpr>')):
                row['stack'].append([parent.f_code.co_name, parent.f_lineno])
            parent = parent.f_back
        self.calls.append(row)

        def local(f, event, value):
            if event == 'line':
                if f.f_lineno == self.iteration_line:
                    if not row['iterations']:
                        row['initial_bracket'] = [str(f.f_locals[k]) for k in ('lo', 'hi')]
                    row['iterations'] += 1
                if f.f_lineno in self.branches:
                    row['branches'] += self.branches[f.f_lineno]
            elif event == 'exception':
                row['exception'] = [value[0].__name__, str(value[1])]
            elif event == 'return':
                row['returned'] = None if value is None else list(map(str, value))
            return local
        return local

    def run(self, action):
        require(sys.gettrace() is None, 'unexpected existing trace hook')
        sys.settrace(self)
        try:
            return action()
        finally:
            sys.settrace(None)


def replay(source, mode, subject_path):
    filename = '<pr1293:' + mode + '>'
    trace = Trace(source, filename)
    namespace = {'__name__': '__main__', '__file__': str(subject_path)}
    stdout = io.StringIO()
    started = time.perf_counter()
    with redirect_stdout(stdout):
        trace.run(lambda: exec(compile(source, filename, 'exec'), namespace))
    elapsed = time.perf_counter() - started
    require([namespace[k] for k in ('CROSS_ORDER', 'CROSS_BITS', 'EXP_ORDER', 'SQRT_STEPS', 'SQRT_BITS')]
            == [48, 72, 48, 112, 320], 'constants changed')
    result = checked(subject_path.with_name('RESULT.json'), RESULT_SHA)
    require(json.loads(result)['status'] == 'PASS_INDEPENDENT_DE_DIAGNOSTIC', 'subject failed')
    require(len(json.loads(result)['controls']) == 12, 'control count')
    print('%s: %.6fs, RESULT %s' % (mode, elapsed, sha(result)))
    return result, stdout.getvalue(), trace, namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    package = args.package.resolve()
    root = package.parents[1]
    output = args.write_receipt.resolve() if args.write_receipt else None
    if output:
        require(output.suffix == '.json' and not output.is_relative_to(root)
                and not output.is_relative_to(package), 'receipt must be external JSON')
    else:
        expected_receipt = load_json((package / 'FULL-REPLAY.json').read_bytes())
    source = checked(package / 'vendor/pr1293_verify.py', SUBJECT_SHA)
    require(source.count(OLD) == 1, 'repair site not unique')
    strict = source.replace(OLD, NEW, 1)
    require(sha(strict) == STRICT_SHA, 'strict source hash')
    inputs = {path: checked(root / path, pin) for path, pin in INPUTS.items()}
    assembly = json.loads(inputs['research/community-frontier1094-audit/ASSEMBLY.json'])
    expected = json.loads(inputs['research/e8-bit-p111-tuned/tune/EXPECTED.json'])
    c, b = list(map(int, assembly['complex_profile'])), list(map(int, expected['nine']['profile']))
    groups = ((2, [1]), (73, c), (64, b), (73, b), (73, c), (64, b))
    arguments = [str(Q(m, rank)) for m, ranks in groups for rank in ranks]
    require(len(arguments) == 41 and len(set(arguments)) == 19, 'expected census')
    with tempfile.TemporaryDirectory(prefix='pr1293-full-replay-') as temporary:
        work = Path(temporary)
        for path, data in inputs.items():
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        subject = work / 'research/selected-suppliers-de-diagnostic/verify.py'
        subject.parent.mkdir(parents=True)
        subject.write_bytes(source)
        original = replay(source, 'original', subject)
        subject.with_name('RESULT.json').unlink()  # no stale output may pass the second run
        repaired = replay(strict, 'strict', subject)
        require(original[0] == repaired[0], 'RESULT bytes changed')
        require(json.loads(original[0]) == json.loads(repaired[0]), 'RESULT semantics changed')
        require(original[1] == repaired[1], 'stdout changed')
        calls = original[2].calls
        require(calls == repaired[2].calls, 'exact call trace changed')
        require([r['argument'] for r in calls] == arguments, 'whole-main argument sequence')
        require(all(r['iterations'] == 72 and r['constants'] == [48, 72] for r in calls), 'depth/order')
        require(all('exception' not in r and Q(r['returned'][0]) < Q(r['returned'][1]) for r in calls),
                'invalid production return')
        branches = Counter(''.join(r['branches'] for r in calls))
        require(branches == {'L': 1480, 'H': 1472}, 'branch census')
        # Independent finite-sum fixture, strictly inside the order-48 exp interval at 4.
        term = total = Q(1)
        for n in range(1, 49):
            term *= Q(4, n)
            total += term
        fixture = total + term * Q(4, 49) / (1 - Q(4, 50)) / 2
        sanity = {}
        for mode, run, code in (('original', original, source), ('strict', repaired, strict)):
            trace = Trace(code, run[2].filename)
            try:
                returned = trace.run(lambda: run[3]['ln_exp_bisection'](fixture))
                require(mode == 'original' and returned == (Q(4), Q(4)), 'point-collapse sanity')
            except ValueError as exc:
                require(mode == 'strict' and str(exc) == MESSAGE, 'strict exception mismatch')
            require(len(trace.calls) == 1 and trace.calls[0]['branches'] == 'A'
                    and trace.calls[0]['iterations'] == 1, 'ambiguity observation sanity')
            if mode == 'strict':
                require(trace.calls[0].get('exception') == ['ValueError', MESSAGE]
                        and trace.calls[0]['returned'] is None, 'strict branch did not raise')
            sanity[mode] = trace.calls[0]
    checked(package / 'vendor/pr1293_verify.py', SUBJECT_SHA)
    for path, pin in INPUTS.items():
        checked(root / path, pin)
    receipt = {
        'schema_version': 1, 'status': 'PASS_PR1293_FULL_REPLAY',
        'source_commit': '85a361233431befe4b11cf878f7b1b77a244d473',
        'input_commit': 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
        'source_sha256': SUBJECT_SHA, 'strict_source_sha256': STRICT_SHA,
        'inputs_sha256': INPUTS, 'result_sha256': RESULT_SHA, 'result_bytes': len(original[0]),
        'result_bytes_equal': True, 'result_json_equal': True, 'changed_outputs': [],
        'stdout_equal': True, 'stdout': original[1], 'exact_calltrace_equal': True,
        'invocations': len(calls), 'distinct_arguments': len(set(arguments)),
        'iterations': sum(r['iterations'] for r in calls), 'ambiguity_hits': branches['A'],
        'lower_updates': branches['L'], 'upper_updates': branches['H'],
        'argument_counts': dict(sorted(Counter(arguments).items())), 'calltrace': calls,
        'separate_branch_sanity': {'argument': str(fixture), 'runs': sanity},
    }
    if output:
        output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
        print('WROTE', output)
    else:
        check_receipt(receipt, expected_receipt)
        print('MATCH FULL-REPLAY.json')
    print('PASS_PR1293_FULL_REPLAY: 41 calls, 19 arguments, 2952 steps, 0 ambiguities; strict sanity raises')
    print('Environment:', sys.executable, sys.version.splitlines()[0], platform.platform())


if __name__ == '__main__':
    main()
