#!/usr/bin/env python3
"""Build the exact PR513/528 Lean sources on a local Lean 4.21 toolchain.

This is an independent source/kernel replay. It does not claim to reproduce
the author's Linux executable/object hashes or Linux memory measurements.
Original packages and their Linux-specific checkers are left unchanged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lean', type=Path, required=True)
    ap.add_argument('--packages', type=Path, required=True,
                    help='Lake package directory containing mathlib and its dependencies')
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    lean, packages, work = a.lean.resolve(), a.packages.resolve(), a.work.resolve()
    version = subprocess.check_output([str(lean), '--version'], text=True).strip()
    require(re.search(r'\b4\.21\.0\b', version), version)
    bank = ROOT / 'research/lean-sequential-bank-bindings'
    endpoint = ROOT / 'research/lean-complete-bank-endpoint'
    roots = {'package': endpoint, 'pr513': bank,
             'pr509': ROOT / 'research/e8-lemma-g-lean',
             'pr516': ROOT / 'research/e8-lemma-a-lean'}
    external = read(endpoint / 'EXTERNAL_OBJECTS.json')
    mathlib = packages / 'mathlib'
    commit = subprocess.check_output(['git', '-C', str(mathlib), 'rev-parse', 'HEAD'], text=True).strip()
    require(commit == external['mathlib_commit'], 'Mathlib source commit')

    def mathpath(rel):
        prefix = '.lake/packages/'
        return packages / rel[len(prefix):] if rel.startswith(prefix) else mathlib / rel

    paths = [mathpath(p) for p in external['library_paths_relative_to_mathlib']]
    require(all(p.is_dir() for p in paths), 'Missing compiled Mathlib dependency')
    external_receipt = []
    for row in external['modules']:
        root = lean.parent.parent
        source = root / row['source_path'] if row['root'] == 'lean' else mathpath(row['source_path'])
        obj = root / row['object_path'] if row['root'] == 'lean' else mathpath(row['object_path'])
        require(sha(source) == row['source_sha256'], f"External source differs: {row['module']}")
        relative = Path(*row['module'].split('.')).with_suffix('.olean')
        resolved = next((p / relative for p in paths + [root / 'lib/lean'] if (p / relative).is_file()), None)
        require(resolved is not None and resolved.resolve() == obj.resolve(), f"Import shadows object: {row['module']}")
        digest = sha(obj)
        external_receipt.append({'module': row['module'], 'source_sha256': sha(source),
                                 'object_sha256': digest, 'matches_author_object': digest == row['object_sha256']})
    work.mkdir(parents=True, exist_ok=False)
    (work / 'EXTERNAL.json').write_text(json.dumps(external_receipt, indent=2) + '\n')
    result = {'platform': platform.platform(), 'lean_version': version, 'lean_sha256': sha(lean),
              'mathlib_commit': commit, 'external_receipt_sha256': sha(work / 'EXTERNAL.json'),
              'scope': 'Exact source/kernel replay; no Linux runtime-hash or memory reproduction claim.', 'packages': {}}
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    pattern = r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])"
    for number, package in [(513, bank), (528, endpoint)]:
        out = work / str(number)
        out.mkdir()
        rows = read(package / 'MANIFEST.json')['compile_order']
        records = []
        seen = set()
        for row in rows:
            source = (roots[row['origin']] if number == 528 else package) / row['file']
            data = source.read_bytes()
            require(hashlib.sha256(data).hexdigest() == row.get('input_sha256', row['sha256']), row['module'])
            if row.get('source_transform'):
                rule = row['source_transform']
                old, new = rule['from'].encode(), rule['to'].encode()
                require(data.count(old) == rule['count'] == 1 and new not in data, 'Import alias transform')
                data = data.replace(old, new)
            require(hashlib.sha256(data).hexdigest() == row['sha256'] and len(data) == row['bytes'], 'Staged source digest')
            imports = re.findall(r'^import\s+(\S+)\s*$', data.decode(), re.M)
            require(imports == row['imports'], 'Declared imports')
            external_names = {r['module'] for r in external['modules']} | {'Lean'}
            require(set(imports) <= seen | external_names, 'Unbound import')
            for p in paths:
                require(not (p / (row['module'] + '.olean')).exists(), 'External local-module shadow')
            staged = out / (row['module'] + '.lean')
            staged.write_bytes(data)
            obj = staged.with_suffix('.olean')
            env = dict(os.environ, LEAN_PATH=os.pathsep.join(map(str, [out] + (paths if number == 528 else []))), LEAN_EXTRA_PATHS='')
            env.pop('LEAN_SYSROOT', None)
            start = time.monotonic()
            proc = subprocess.run([str(lean), '-s', '65536', '-j', '1', '-o', str(obj), staged.name],
                                  cwd=out, env=env, capture_output=True, text=True, timeout=90)
            log = proc.stdout + proc.stderr
            staged.with_suffix('.log').write_text(log)
            require(proc.returncode == 0 and obj.is_file(), log)
            require('sorryAx' not in log and "declaration uses 'sorry'" not in log, 'Unproved declaration')
            probes = [{'declaration': m[1], 'axioms': [] if m[2] is None else [x.strip() for x in m[2].split(',') if x.strip()]}
                      for m in re.finditer(pattern, log, re.S)]
            declared = re.findall(r'^#print axioms (\S+)\s*$', data.decode(), re.M)
            require([p['declaration'] for p in probes] == declared, 'Incomplete axiom reports')
            require(all(set(p['axioms']) <= allowed for p in probes), 'Unexpected axioms')
            if number == 528:
                require(probes == row['expected_probes'], 'Author axiom report differs')
            require(sha(staged) == row['sha256'], 'Source changed during compilation')
            records.append({'module': row['module'], 'source_sha256': row['sha256'], 'object_sha256': sha(obj),
                            'log_sha256': sha(staged.with_suffix('.log')), 'axioms': probes,
                            'seconds': time.monotonic() - start})
            seen.add(row['module'])
            print('PASS', number, row['module'], len(probes), 'axiom reports', flush=True)
        count = sum(len(r['axioms']) for r in records)
        require(count == (77 if number == 513 else 70), 'Axiom probe count')
        result['packages'][str(number)] = {'modules': records, 'axiom_reports': count}
    result['status'] = 'PASS_EXACT_SOURCES_AND_AXIOMS'
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
