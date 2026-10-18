# SPDX-License-Identifier: Apache-2.0
"""Replay the pinned T37 log inventory and exhaust its single-log omissions.

Prepared for Sagar Thakrar with substantial OpenAI Codex assistance.
This executes the frozen native-stage predicates, not the full final binder.
"""
import argparse
import ast
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
spec = importlib.util.spec_from_file_location('t37_log_audit', PACKAGE / 'audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
require = audit.require


def check_producer_orders():
    def declarations(relative):
        tree = ast.parse((ROOT / relative).read_bytes())
        calls = sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call)
                        and isinstance(n.func, ast.Name) and n.func.id == 'run'
                        and isinstance(n.args[0], ast.Constant)), key=lambda n: n.lineno)
        return tree, tuple(n.args[0].value for n in calls)
    _, top = declarations('research/complex-t37-owners/verify.py')
    _, native = declarations('research/complex-t21-owners/vendor/pr870/construction/barch/reproduce_barch.py')
    tree, discovery = declarations('research/complex-t37-owners/replay.py')
    loops = [n for n in ast.walk(tree) if isinstance(n, ast.For)
             and isinstance(n.target, ast.Tuple)
             and [t.id for t in n.target.elts] == ['name', 'script', 'out']]
    require(len(loops) == 1, 'Strict control declarations changed')
    strict = discovery[:-1] + tuple(x[0] for x in ast.literal_eval(loops[0].iter))
    require(top == ('baseline799-cold',) + audit.TOP and native == audit.NATIVE
            and discovery == audit.INDEXES['discovery/STAGES.json'][1]
            and strict == audit.INDEXES['strict/STAGES.json'][1], 'Producer stage orders differ')


def native_predicates(source):
    """Compile exactly the frozen native index read and its next two assertions."""
    tree = ast.parse(source.read_bytes())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'check')
    offsets = [i for i, n in enumerate(function.body) if isinstance(n, ast.Assign)
               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
               and n.targets[0].id == 'steps']
    require(len(offsets) == 1, 'Native-stage source slice changed')
    body = function.body[offsets[0]:offsets[0] + 3]
    require(len(body) == 3 and all(isinstance(n, ast.Assert) for n in body[1:]),
            'Native-stage assertions changed')
    # Explicit optimization level retains the original predicates under python -O.
    code = compile(ast.Module(body=body, type_ignores=[]), str(source), 'exec', optimize=0)

    def check(work):
        exec(code, {'work': work, 'read': lambda p: json.loads(p.read_bytes())})
    return check, [body[0].lineno, body[-1].end_lineno]


def verify():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    for name, digest in sources['consumed_sha256'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest, 'Source pin differs: ' + name)
    check_producer_orders()
    archive = ROOT / 'research/community-frontier942-audit/t37-replay.tar.gz'
    frozen, lines = native_predicates(ROOT / 'research/complex-t37-owners/final_binding.py')
    rejected = []
    native_omissions_accepted = []
    native_changes_observed = []
    with tempfile.TemporaryDirectory(prefix='t37-log-coverage-') as temporary:
        work = Path(temporary).resolve()
        with tarfile.open(archive) as bundle:
            members = bundle.getmembers()
            names = [m.name for m in members]
            require(len(names) == len(set(names)), 'Duplicate archive member')
            wanted = set(audit.INDEXES) | {n for n in names if n.endswith('.log')}
            for name in sorted(wanted):
                member = bundle.getmember(name)
                target = work / name
                require(member.isfile() and target.resolve().is_relative_to(work),
                        'Invalid archived evidence: ' + name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(bundle.extractfile(member).read())
        baseline = audit.check(work)
        require(set(baseline['logs']) == wanted - set(audit.INDEXES), 'Unaccounted archived log')
        require(len(baseline['logs']) == 34 and baseline['producer_digest_checks'] == 26
                and baseline['presence_only_logs'] == 8, 'Archived coverage changed')
        frozen(work)

        def reject(name, operation):
            try:
                operation()
            except ValueError:
                rejected.append(name)
            else:
                raise RuntimeError('Accepted negative control: ' + name)

        for name, entry in baseline['logs'].items():
            path = work / name
            original = path.read_bytes()
            try:
                path.unlink()
                if not entry['producer_digest_checked']:
                    frozen(work)
                    native_omissions_accepted.append(name)
                reject('omit:' + name, lambda: audit.check(work))
                path.write_bytes(original + b'\nchanged log control\n')
                if entry['producer_digest_checked']:
                    reject('alter:' + name, lambda: audit.check(work))
                else:
                    changed = audit.check(work)
                    require(changed['logs'][name]['sha256'] != entry['sha256'],
                            'Native content change was not observed')
                    native_changes_observed.append(name)
            finally:
                path.write_bytes(original)

        for name in audit.INDEXES:
            path = work / name
            original = path.read_bytes()
            pristine = json.loads(original)
            variants = [('omitted-stage', pristine[:-1]), ('reordered', list(reversed(pristine)))]
            for value in (1, False, 0.0):
                changed = deepcopy(pristine)
                changed[0]['exit_code'] = value
                variants.append(('exit-' + repr(value), changed))
            try:
                for kind, value in variants:
                    path.write_text(json.dumps(value), encoding='utf-8')
                    reject(kind + ':' + name, lambda: audit.check(work))
            finally:
                path.write_bytes(original)
        # The current producer also has a cold-baseline branch. This is a
        # synthetic coverage-positive control, not a cold supplier execution.
        path = work / 'STAGES.json'
        original = path.read_bytes()
        cold = work / 'baseline799-cold.log'
        try:
            cold.write_bytes(b'synthetic coverage control\n')
            stage = dict(name='baseline799-cold', exit_code=0,
                         log_sha256=sha256(cold.read_bytes()).hexdigest())
            path.write_text(json.dumps([stage] + json.loads(original)), encoding='utf-8')
            require(len(audit.check(work)['logs']) == 35, 'Cold stage coverage differs')
        finally:
            path.write_bytes(original)
            cold.unlink()
        require(audit.check(work) == baseline, 'Pristine evidence was not restored')
    identity = lambda value: sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    certificate = {
        'coverage_sha256': identity(baseline),
        'rejected_control_names_sha256': identity(rejected),
        'frozen_native_predicate_lines': lines,
        'native_omissions_accepted_by_frozen_component': native_omissions_accepted,
        'native_content_changes_observed_without_rejection': len(native_changes_observed),
        'synthetic_cold_log_count': 35,
    }
    require(certificate == json.loads((PACKAGE / 'CERTIFICATE.json').read_bytes()),
            'Exact coverage/control certificate differs')
    return {
        'status': 'PASS_T37_LOG_COVERAGE_CONTROLS',
        'coverage': baseline,
        'consumed_sha256': sources['consumed_sha256'],
        'frozen_native_predicate_lines': lines,
        'frozen_native_predicates_accept_omissions': native_omissions_accepted,
        'native_content_changes_observed_without_rejection': native_changes_observed,
        'rejected_controls': rejected,
        'synthetic_cold_log_count': 35,
        'scope': 'Archived log evidence and component-level native predicates only. '
                 'The complete original binder, native supplier, invoices and theorem '
                 'were not replayed. No counterexample to the mathematics is claimed.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    if args.out:
        with args.out.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'], len(result['coverage']['logs']), 'logs;',
          len(result['rejected_controls']), 'rejections;',
          len(result['frozen_native_predicates_accept_omissions']), 'native omissions admitted by frozen slice')


if __name__ == '__main__':
    main()
