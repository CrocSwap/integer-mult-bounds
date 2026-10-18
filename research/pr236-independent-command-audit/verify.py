#!/usr/bin/env python3
"""Reconcile PR236's submitted sources with retained historical audit evidence.

This reads pinned Git objects and archives. It neither imports the submitted
driver nor invokes Lean, and cannot validate absent compiler/object binaries.
Prepared for WeberChen8128 with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile

BASE = 'f567884aeb8851b6e794af1184119a3bfbe1e631'
SOURCE = 'f825b6fdfd763f189db3aa1c02fdd5d604c85a01'
TARGET = 'd1d6c070f5a8c684727ee7ec35d930f9ebfa9758'
PACKAGE = 'research/lean-paired-cube-d1d6/'
EVIDENCE = 'research/community-round9-audit/'
ALLOWED = ['Classical.choice', 'Quot.sound', 'propext']
POLICY = 'maintainer-darwin-uncapped-subset-v1'
AUDIT = re.compile(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)")


class ReconciliationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReconciliationError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def receipt_hash(value):
    # The historical summary uses this precise, non-indented serialization.
    return sha(json.dumps(value, sort_keys=True).encode())


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def decode(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def blob(root, commit, path):
    return git(root, 'show', commit + ':' + path)


def tree(root, commit, prefix=''):
    result = {}
    for row in git(root, 'ls-tree', '-r', '-z', commit, '--', prefix or '.').split(b'\0'):
        if row:
            meta, path = row.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            require(kind == 'blob' and mode in {'100644', '100755'}, 'Non-file Git entry')
            result[path.decode()] = oid
    return result


def archive(raw):
    """Read regular members without extracting paths; reject ambiguous archives."""
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as stream:
        for member in stream:
            path = PurePosixPath(member.name)
            require(member.isfile() and not path.is_absolute()
                    and '..' not in path.parts and str(path) == member.name
                    and '\\' not in member.name, 'Unsafe archive member')
            require(member.name not in result, 'Duplicate archive member')
            result[member.name] = stream.extractfile(member).read()
    return result


def audit_log(raw, expected):
    """Recount recorded Lean reports; this is not a new kernel axiom audit."""
    found = {}
    lines = iter(raw.decode().splitlines())
    for line in lines:
        if line.startswith("'") and 'depends on axioms: [' in line and ']' not in line:
            while ']' not in line:
                continuation = next(lines, None)
                require(continuation is not None, 'Unterminated axiom report')
                line += '\n' + continuation
        match = AUDIT.fullmatch(line.strip())
        if match is None:
            # Historical logs also contain multiline compiler/linter warnings.
            require('depends on axioms:' not in line
                    and 'does not depend on any axioms' not in line,
                    'Malformed axiom report')
            continue
        name, values = match.groups()
        require(name not in found, 'Duplicate axiom report')
        axioms = {v.strip() for v in values.split(',')} if values else set()
        require(axioms <= set(ALLOWED), 'Disallowed recorded axiom')
        found[name] = axioms
    require(len(expected) == len(set(expected)) and set(found) == set(expected),
            'Axiom declaration coverage')
    return dict(declarations=len(found), axiom_free=sum(not x for x in found.values()),
                axioms=sorted(set().union(*found.values()) if found else set()))


def source_commands(raw):
    """Independently scan the submitted corpus's line-oriented Lean commands.

    Mask strings and nested/line comments before recognizing commands. This is
    deliberately not a general Lean parser: only literal single-line import
    and #print axioms commands in the pinned corpus are supported.
    """
    text = raw.decode('utf-8')
    marker = re.compile(r'/\-|--|"')
    block = re.compile(r'/\-|\-/')
    string = re.compile(r'\\[\s\S]|"')
    pieces = []
    position = 0
    while match := marker.search(text, position):
        start = match.start()
        pieces.append(text[position:start])
        if match.group() == '--':
            end = text.find('\n', match.end())
            end = len(text) if end < 0 else end
        elif match.group() == '/-':
            depth, end = 1, match.end()
            while depth:
                closing = block.search(text, end)
                require(closing is not None, 'Unterminated source comment')
                depth += 1 if closing.group() == '/-' else -1
                end = closing.end()
        else:
            end = match.end()
            while True:
                closing = string.search(text, end)
                require(closing is not None, 'Unterminated source string')
                end = closing.end()
                if closing.group() == '"':
                    break
        pieces.append(re.sub(r'[^\n]', ' ', text[start:end]))
        position = end
    pieces.append(text[position:])
    masked = ''.join(pieces)
    name = r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*'
    imports, prints = [], []
    for line in masked.splitlines():
        stripped = line.strip()
        if re.match(r'import\b', stripped):
            require(re.fullmatch(r'import[ \t]+' + name + r'(?:[ \t]+' + name + r')*', stripped),
                    'Unsupported import command syntax')
            imports.extend(stripped.split()[1:])
        elif re.match(r'#print\s+axioms\b', stripped):
            require(re.fullmatch(r'#print[ \t]+axioms[ \t]+' + name, stripped),
                    'Unsupported axiom command syntax')
            prints.append(stripped.split()[-1])
    return imports, prints


def source_inventory(plan, sources):
    modules = plan['modules']
    names = [m['module'] for m in modules]
    paths = [m['source'] for m in modules]
    scientific = plan['scientific_inputs']
    expected = paths + [m['path'] for m in scientific]
    require(len(names) == len(set(names)) == plan['accepted_module_count'],
            'Module identity coverage')
    require(len(expected) == len(set(expected)) and set(sources) == set(expected),
            'Exact source archive inventory')
    for m in modules:
        require(sha(sources[m['source']]) == m['source_sha256'],
                'Accepted source digest: ' + m['module'])
        imports, prints = source_commands(sources[m['source']])
        require(imports == m['imports'], 'Source import commands: ' + m['module'])
        require(prints == m['expected_axiom_commands'], 'Source axiom commands: ' + m['module'])
        require(len(m['expected_axiom_commands']) == m['declarations'],
                'Mapped declaration count')
    for item in scientific:
        require(sha(sources[item['path']]) == item['sha256'], 'Scientific input digest')
    require(sum(m['declarations'] for m in modules) == plan['accepted_declarations'],
            'Total declaration count')
    external = set(plan['external_imports'])
    require(all(n in {'Init', 'Lean'} or n.startswith(('Init.', 'Lean.')) for n in external),
            'Unexpected external module')
    by_name = {m['module']: m for m in modules}
    order = plan['ordered_modules']
    require(len(order) == len(set(order)) and set(order) == set(names), 'Module order coverage')
    visited = set()
    name_set = set(names)
    edges = 0
    for name in order:
        imports = by_name[name]['imports']
        require(set(imports) <= visited | external, 'Dependency order/closure: ' + name)
        edges += len(set(imports) & name_set)
        visited.add(name)
    return by_name, edges


def reconcile(map_bytes, sources, evidence):
    """Check every source/receipt/log/dependency edge, beyond container hashes."""
    plan = decode(map_bytes)
    map_hash = sha(map_bytes)
    require(plan['target_commit'] == TARGET, 'Scientific target commit')
    require(plan['axiom_policy'] == ALLOWED, 'Mapped axiom policy')
    modules, edges = source_inventory(plan, sources)
    require(evidence['INPUT_MAP.json'] == map_bytes, 'Submitted/retained map equality')
    expected_members = {'INPUT_MAP.json', 'SUMMARY.json', 'darwin-driver.py'}
    expected_members.update('receipts/' + n + '.json' for n in modules)
    expected_members.update('logs/' + n + '.log' for n in modules)
    require(set(evidence) == expected_members, 'Exact historical evidence inventory')
    summary = decode(evidence['SUMMARY.json'])
    require(summary['status'] == 'FULL_ACCEPTED_SET_COMPILED'
            and summary['full_accepted_set'] is True and summary['kernel_compiled'] is True,
            'Historical full-build claim')
    require(summary['map_sha256'] == map_hash and summary['source_commit'] == TARGET,
            'Summary source binding')
    require(summary['accepted_modules'] == summary['selected_modules'] == len(modules)
            and summary['selected_declarations'] == plan['accepted_declarations'],
            'Summary count coverage')
    visited = summary['rebuilt'] + summary['reused']
    require(len(visited) == len(set(visited)) and set(visited) == set(modules)
            and set(summary['receipts']) == set(modules), 'Historical build partition')
    done = {}
    total = Counter()
    observed = set()
    bindings = []
    for name in plan['ordered_modules']:
        m = modules[name]
        r = decode(evidence['receipts/' + name + '.json'])
        log = evidence['logs/' + name + '.log']
        require(r['module'] == name and r['status'] == 'PASS'
                and type(r['compiler_exit']) is int and r['compiler_exit'] == 0,
                'Historical receipt status: ' + name)
        require(r['map_sha256_when_built'] == map_hash, 'Receipt map binding')
        require(re.fullmatch('[0-9a-f]{64}', r['object_sha256']) is not None,
                'Recorded object digest format')
        expected_key = dict(policy=POLICY, compiler=summary['compiler'],
                            source_sha256=m['source_sha256'], imports=m['imports'],
                            expected_axiom_commands=m['expected_axiom_commands'],
                            dependencies={d: done[d]['object_sha256'] for d in m['imports'] if d in modules},
                            timeout_seconds=m.get('timeout_seconds', 60), address_space_bytes=None,
                            lean_jobs=1, lean_stack_kib=65536, allowed_axioms=ALLOWED)
        require(typed_equal(r['build_key'], expected_key), 'Receipt source/dependency/policy binding: ' + name)
        require(r['log_sha256'] == sha(log), 'Receipt log digest')
        audit = audit_log(log, m['expected_axiom_commands'])
        require(typed_equal(r['audit'], audit), 'Receipt axiom recount')
        require(summary['receipts'][name] == receipt_hash(r), 'Summary receipt digest')
        total.update({k: audit[k] for k in ['declarations', 'axiom_free']})
        observed.update(audit['axioms'])
        bindings.append([name, m['source_sha256'], r['object_sha256'], r['log_sha256']])
        done[name] = r
    require(total['declarations'] == plan['accepted_declarations'], 'Audited declaration total')
    return dict(accepted_modules=len(modules), scientific_inputs=len(plan['scientific_inputs']),
                independently_scanned_source_modules=len(modules),
                modules_without_audit_commands=sum(not m['expected_axiom_commands'] for m in modules.values()),
                accepted_source_bytes=sum(len(v) for v in sources.values()),
                internal_dependency_edges=edges, audited_declarations=total['declarations'],
                axiom_free_declarations=total['axiom_free'], observed_axioms=sorted(observed),
                source_receipt_log_bindings_sha256=sha(encode(sorted(bindings))),
                historical_rebuilt_modules=len(summary['rebuilt']), historical_reused_modules=summary['reused'],
                compiler_record=summary['compiler'], present_compiled_objects=0,
                present_compiler_binaries=0, fresh_kernel_compilation=False,
                object_and_compiler_hashes_independently_revalidated=False)


def adapted_driver(original):
    replacements = [
        (b'POLICY = "offline-lean-check-v1"', b'POLICY = "maintainer-darwin-uncapped-subset-v1"'),
        (b'address_space_bytes=4 * 1024**3,', b'address_space_bytes=None,'),
        (b'timeout=timeout, preexec_fn=lambda: resource.setrlimit(\n'
         b'                                        resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3)))',
         b'timeout=timeout)'),
    ]
    for old, new in replacements:
        require(original.count(old) == 1, 'Unique documented Darwin adapter site')
        original = original.replace(old, new)
    return original


def run(root):
    package_tree = tree(root, SOURCE, PACKAGE)
    require(len(package_tree) == 14, 'Submitted package file coverage')
    package = {p.removeprefix(PACKAGE): blob(root, SOURCE, p) for p in package_tree}
    checksum_rows = [line.split('  ', 1) for line in package['SHA256SUMS'].decode().splitlines()]
    require(len(checksum_rows) == 13 and len({p for _, p in checksum_rows}) == 13
            and {p for _, p in checksum_rows} == set(package) - {'SHA256SUMS'},
            'Submitted checksum inventory')
    require(all(sha(package[p]) == h for h, p in checksum_rows), 'Submitted checksum mismatch')
    evidence_raw = blob(root, BASE, EVIDENCE + 'pr236-kernel-evidence.tar.gz')
    manifest = decode(blob(root, BASE, EVIDENCE + 'pr236-evidence-manifest.json'))
    require(sha(evidence_raw) == manifest['archive_sha256'], 'Historical archive digest')
    evidence = archive(evidence_raw)
    require({p: sha(v) for p, v in evidence.items()} == manifest['member_sha256'],
            'Historical archive member manifest')
    sources = archive(package['scientific_sources.tar.gz'])
    readback = decode(package['ARCHIVE_READBACK.json'])
    require(sha(package['scientific_sources.tar.gz']) == readback['archive_sha256']
            and sha(package['INPUT_MAP.json']) == readback['public_map_sha256']
            and len(sources) == readback['members']
            and len(package['scientific_sources.tar.gz']) == readback['bytes'],
            'Submitted archive readback pins')
    report = reconcile(package['INPUT_MAP.json'], sources, evidence)
    require(report['accepted_modules'] == 3606 and report['audited_declarations'] == 14320
            and report['axiom_free_declarations'] == 2816 and report['scientific_inputs'] == 8,
            'Pinned actual audit counts')
    require(report['accepted_source_bytes'] == readback['uncompressed_file_bytes']
            and readback['lean_modules'] == report['accepted_modules']
            and readback['theorems'] == report['audited_declarations']
            and readback['scientific_inputs'] == report['scientific_inputs'],
            'Submitted readback coverage')
    plan = decode(package['INPUT_MAP.json'])
    scientific = []
    for item in plan['scientific_inputs']:
        path = item['path'].removeprefix('scientific/')
        original = blob(root, TARGET, path)
        require(original == sources[item['path']], 'Scientific bytes differ from target Git commit')
        scientific.append(dict(path=path, sha256=sha(original)))
    theorem_names = []
    for path in package:
        if path.startswith('key_theorems/'):
            name = PurePosixPath(path).name
            require(package[path] == sources['src/' + name], 'Readable theorem differs from accepted source')
            theorem_names.append(name)
    require(len(theorem_names) == 6, 'Readable theorem inventory')
    require(adapted_driver(package['offline_check.py']) == evidence['darwin-driver.py'],
            'Unexpected Darwin driver changes')
    final = decode(blob(root, BASE, EVIDENCE + 'pr236-final-integrity.json'))
    require(final['summary_sha256'] == sha(evidence['SUMMARY.json'])
            and final['driver_sha256'] == sha(evidence['darwin-driver.py'])
            and final['map_sha256'] == sha(package['INPUT_MAP.json'])
            and final['compiler'] == report['compiler_record'], 'Final integrity record binding')
    for field in ['accepted_modules', 'audited_declarations', 'axiom_free_declarations', 'observed_axioms']:
        require(final[field] == report[field], 'Final integrity total differs: ' + field)
    base_index = defaultdict(list)
    for path, oid in tree(root, BASE).items():
        base_index[oid].append(path)
    inventory = []
    for path, data in sorted(package.items()):
        oid = package_tree[PACKAGE + path]
        inventory.append(dict(path=path, git_blob=oid, sha256=sha(data),
                              base_tracked_exact_matches=base_index[oid],
                              retained_evidence_exact_members=[p for p, v in evidence.items() if v == data],
                              recoverable_by_reversing_documented_adapter=path == 'offline_check.py'))
    return dict(status='PASS_PR236_INDEPENDENT_SOURCE_COMMAND_AND_LOG_AUDIT',
                base_commit=BASE, source_pr=236, source_head=SOURCE, scientific_target=TARGET,
                assignment_seed=95,
                submitted_package_files=inventory, scientific_inputs_at_target=scientific,
                readable_theorems=sorted(theorem_names), reconciliation=report,
                source_archive_sha256=sha(package['scientific_sources.tar.gz']),
                retained_evidence_archive_sha256=sha(evidence_raw),
                scope='Source/archive/map/recorded receipt consistency only; no new Lean compilation, '
                      'no independent object/compiler binary verification, no current-frontier instantiation, '
                      'no all-size theorem and no recommendation to close PR236.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Fetch missing pinned commits from upstream (read-only)')
    parser.add_argument('--write', type=Path, help='Write the deterministic report to this path')
    parser.add_argument('--check', type=Path, help='Require equality to an existing report')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    for commit in [BASE, SOURCE, TARGET]:
        found = subprocess.run(['git', '-C', str(root), 'cat-file', '-e', commit + '^{commit}'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not found:
            require(args.fetch, 'Missing pinned Git commit; rerun with --fetch: ' + commit)
            subprocess.run(['git', '-C', str(root), 'fetch', '--no-tags',
                            'https://github.com/CrocSwap/integer-mult-bounds.git', commit], check=True)
    report = run(root)
    if args.check:
        require(typed_equal(decode(args.check.read_text()), report), 'Report differs')
    if args.write:
        args.write.write_bytes(encode(report))
    r = report['reconciliation']
    print(report['status'])
    print(f"{r['accepted_modules']} sources/receipts/logs; {r['audited_declarations']} recorded declarations; "
          f"{r['axiom_free_declarations']} recorded axiom-free declarations; 8 scientific input Git matches")
    print('No compiler or .olean bytes present; no fresh kernel compilation.')


if __name__ == '__main__':
    main()
