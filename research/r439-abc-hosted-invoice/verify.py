#!/usr/bin/env python3
"""Fresh fixed-word nine-stage hosting replay; no synthesis or outer assembly.

Orchestration follows PR589 tune/verify.sh, using unchanged exporters, native
checkers, parameterizers, emitter and owner auditors. Apache-2.0.
Matthieu Pascal, with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = ROOT / 'research/e8-bit-carrier-skeleton'
PKG = ROOT / 'research/e8-bit-p111-tuned'
WORD = ROOT / 'research/r439-abc-semantic-bridge/inputs/candidate.json.gz'
V510 = PKG / 'vendor/pr510/e8-r480-nine-stage'
VK = V510 / 'vendor/e8-r715-eleven-stage-whole/code'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(rows):
        result = {}
        for key, value in rows:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(work, discover=False):
    pins = read(HERE / 'SOURCES.json')
    inputs = {r['path']: r['sha256'] for r in pins['files'] if r['usage'] == 'input'}
    for name, expected in inputs.items():
        need(sha(ROOT / name) == expected, 'source hash: ' + name)
    need(not work.is_relative_to(ROOT), 'output must be outside checkout')
    work.mkdir(parents=True, exist_ok=False)
    (work / 'logs').mkdir()
    (work / 'bin').mkdir()
    consumed = set()
    commands = []

    def run(name, args):
        args = list(map(str, args))
        print(name, flush=True)
        commands.append(args)
        with (work / 'logs' / (name + '.log')).open('x') as log:
            subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=600)

    def python(name, script, *args):
        reads = work / 'logs' / (name + '.inputs.json')
        run(name, [sys.executable, '-I', '-B', HERE / 'invoke.py', ROOT, reads, script, *args])
        consumed.update(read(reads))

    python('semantic-bridge', ROOT / 'research/r439-abc-semantic-bridge/verify.py')
    python('export', P / 'code/bit/export_records.py', WORD, work / 'records')
    python('stage', P / 'code/bit/regression/stage_cohort.py', work / 'records', work / 'records', work / 'cin', work / 'cout')
    checker = P / 'code/bit/checkers'
    flags = shlex.split(os.environ.get('CXX', 'c++')) + ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
             '-I' + str(P / 'portable-include'), '-I' + str(checker), '-I' + os.environ.get('BOOST_INCLUDE', '/usr/include')]
    for name, source, more in [('legality', 'legality_h.cpp', []),
                               ('columns5', 'columns_k.cpp', ['-DVPORTS=111', '-DRHELP=439', '-DKPAIRS=2']),
                               ('columns9', 'columns_k.cpp', ['-DVPORTS=111', '-DRHELP=439', '-DKPAIRS=4'])]:
        dep = work / 'logs' / (name + '.d')
        run('compile-' + name, flags + more + ['-MMD', '-MF', dep, '-o', work / 'bin' / name, checker / source])
        # Make dependency files escape spaces; shlex decodes their path tokens.
        for token in shlex.split(dep.read_text().replace('\\\n', ' ').split(':', 1)[1]):
            path = Path(token).resolve()
            if path.is_relative_to(ROOT):
                consumed.add(path.relative_to(ROOT).as_posix())
    run('legality', [work / 'bin/legality', work / 'cin', work / 'cout', work / 'cout/legality.json'])
    run('columns5', [work / 'bin/columns5', work / 'cout/COHORT249-RECORDS.bin', work / 'cout/columns.json'])
    run('columns9', [work / 'bin/columns9', work / 'cout/COHORT249-RECORDS.bin', work / 'cout/columns9.json'])
    python('geometry-adapter', PKG / 'vendor/pr545/code/adapt.py', P, WORD, work / 'ad545')
    python('geometry', work / 'ad545/nine_geometry.py', '--source', P, '--out', work / 'v9/nine', '--word', WORD)
    # The inherited geometry certificate includes elapsed time in its hash.
    # Normalize that nonmathematical field before any downstream binding.
    geometry_path = work / 'v9/nine/GEOMETRY.json'
    geometry = read(geometry_path)
    geometry['seconds'] = 0
    geometry_path.write_text(json.dumps(geometry, indent=2) + '\n')
    python('parent-adapter', V510 / 'code/adapt.py', VK, work / 'adapted9')
    python('port-adapter', PKG / 'code/adapt9p.py', VK, V510 / 'code', work / 'adapted9/audit_parent_k.py', work / 'a9p')
    (work / 'v9/records').symlink_to(work / 'records', target_is_directory=True)
    python('parent-template', work / 'a9p/global_k.py', '--word', WORD, '--local-check', work,
           '--out', work / 'v9/nine', '--isometries', P / 'data/eleven/residual-isometries.json')
    python('parent-audit', work / 'a9p/audit_parent_k.py', '--local-check', work, '--out', work / 'v9/nine', '--word', WORD)
    python('hosted-emission', work / 'a9p/emit_k.py', work / 'v9/nine', work, work / 'v9/hosted',
           '--selection', PKG / 'data/selection9-p111.json', '--key', 'bit')
    python('hosted-audit', work / 'a9p/audit_hosted_k.py', work / 'v9', work / 'v9/hosted', work / 'v9/hosted/AUDIT.json')
    python('invoice', HERE / 'invoice.py', ROOT, work, work / 'INVOICE.json')
    consumed -= {p for p in consumed if p.startswith('research/r439-abc-hosted-invoice/')}
    (work / 'CONSUMED.json').write_text(json.dumps(sorted(consumed), indent=2) + '\n')
    (work / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    if not discover:
        need(consumed <= set(inputs), 'undeclared consumed inputs: ' + repr(sorted(consumed - set(inputs))))
    result = collect(work)
    result['binding_controls'] = controls(work)
    (work / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def collect(work):
    """Bind fresh producer/auditor outputs, with no generation or mutation."""
    legality = read(work / 'cout/legality.json')
    columns = [read(work / 'cout' / p) for p in ('columns.json', 'columns9.json')]
    parent = read(work / 'v9/nine/GLOBAL.json')
    pa = read(work / 'v9/nine/AUDIT.json')
    hosted = read(work / 'v9/hosted/AUDIT.json')
    hg = read(work / 'v9/hosted/GLOBAL.json')
    invoice = read(work / 'INVOICE.json')
    for folder, receipt in [('nine', parent), ('hosted', hg)]:
        blob = gzip.decompress((work / 'v9' / folder / 'GLOBAL-TEMPLATE.json.gz').read_bytes())
        need(hashlib.sha256(blob).hexdigest() == receipt['template_sha256'], 'template bytes ' + folder)
    need(pa['status'] == 'PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT'
         and pa['template_sha256'] == parent['template_sha256'], 'parent audit binding')
    need(hg['parent_template_sha256'] == parent['template_sha256']
         and hosted['template_sha256'] == hg['template_sha256'], 'hosted audit binding')
    need(hosted['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT', 'hosted status')
    for key in ('emitted_program_sha256', 'emitted_events', 'profile', 'live', 'physical',
                'hosted_residuals', 'bank_assignments', 'rank_mass', 'deficit', 'maxchild'):
        need(hosted[key] == hg[key], 'hosted receipt mismatch: ' + key)
    for key in ('profile', 'live', 'physical', 'rank_mass', 'deficit', 'maxchild'):
        need(invoice[key] == hosted[key], 'invoice ownership mismatch: ' + key)
    need(invoice['paid_calls'] == sum(hosted['profile'].values()), 'invoice paid calls')
    need(invoice['invoice_terms']['prefix'] == int(parent['global_prefix_bound']), 'invoice prefix binding')
    need(invoice['invoice_terms']['copy_erase'] == parent['copy_erase_episodes'] == 2592, 'invoice copy binding')
    need(invoice['invoice_terms']['scalar_additions'] == 288 * 10652 + parent['bridge_additions'], 'invoice scalar binding')
    need(len(pa['mutations_rejected']) == 17 and len(hosted['mutations_rejected']) == 16, 'audit control coverage')
    need(legality['common_frame_ADDs'] == parent['local_additions'] == 10652, 'changed scalar bill')
    need(legality['copies'] == legality['erasures'] == 9 and legality['rank_mass'] == 5129, 'local copy/rank bill')
    need(hosted['hosted_residuals'] == 126432 and hosted['bank_assignments'] == 0, 'complete hosting')
    need(hosted['emitted_events'] == 288 * legality['records'], 'all local instructions emitted')
    for col, count, controls in zip(columns, (883, 1327), (6, 18)):
        need(col['formal_columns_checked'] == count and col['local_scalar_additions'] == 10652, 'native column binding')
        need(col['payload_prefix_bits'] == 92 and len(col['negative_controls']) == controls
             and all(c['rejected'] is True for c in col['negative_controls']), 'native guard/controls')
    result = dict(schema_version=1, word_sha256=sha(WORD), semantic_bridge_receipt_sha256=sha(ROOT / 'research/r439-abc-semantic-bridge/RESULT.json'),
                  records_sha256=sha(work / 'records/249-records.bin'),
                  native={k: legality[k] for k in ('status', 'records', 'common_frame_ADDs', 'rank_mass', 'paid_histogram', 'copies', 'erasures')},
                  stages=[{k: c[k] for k in ('formal_columns_checked', 'local_scalar_additions', 'bridge_additions', 'signed_lift_prefix', 'payload_prefix_bits', 'payload_prefix_upper', 'negative_controls')} for c in columns],
                  parent={k: parent[k] for k in ('template_sha256', 'source_records_sha256', 'word_sha256', 'local_additions', 'global_prefix_bound', 'global_prefix_bits', 'charged_prefix_bits', 'independent_unbanked_scalar_columns', 'copy_erase_episodes', 'bridge_additions')},
                  parent_controls=pa['mutations_rejected'], hosted=hosted, invoice=invoice,
                  no_selected_change=True, new_kappa=False)
    need(result['parent']['word_sha256'] == result['word_sha256'], 'word-to-template binding')
    need(result['parent']['source_records_sha256'] == result['records_sha256'], 'record-to-template binding')
    return result


def controls(work):
    """Reject mixed or understated receipts at the actual collection boundary."""
    cases = [
        ('wrong-word', 'v9/nine/GLOBAL.json', lambda x: x.__setitem__('word_sha256', '0' * 64), 'word-to-template'),
        ('wrong-records', 'v9/nine/GLOBAL.json', lambda x: x.__setitem__('source_records_sha256', '0' * 64), 'record-to-template'),
        ('invoice-profile', 'INVOICE.json', lambda x: x['profile'].__setitem__('1', x['profile']['1'] - 1), 'invoice ownership'),
        ('invoice-prefix', 'INVOICE.json', lambda x: x['invoice_terms'].__setitem__('prefix', x['invoice_terms']['prefix'] // 2), 'invoice prefix'),
        ('invoice-copy', 'INVOICE.json', lambda x: x['invoice_terms'].__setitem__('copy_erase', x['invoice_terms']['copy_erase'] - 1), 'invoice copy'),
        ('missing-bridge-control', 'cout/columns9.json', lambda x: x['negative_controls'].pop(), 'native guard/controls'),
        ('stale-hosted-template', 'v9/hosted/GLOBAL.json', lambda x: x.__setitem__('parent_template_sha256', '0' * 64), 'hosted audit binding'),
    ]
    rejected = []
    for name, relative, mutate, reason in cases:
        path = work / relative
        original = path.read_bytes()
        altered = read(path)
        mutate(altered)
        try:
            path.write_text(json.dumps(altered) + '\n')
            try:
                collect(work)
            except ValueError as exc:
                need(reason in str(exc), 'unexpected control rejection: ' + str(exc))
                rejected.append(name)
            else:
                raise ValueError('accepted control: ' + name)
        finally:
            path.write_bytes(original)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh directory outside checkout; preserve logs')
    parser.add_argument('--write', action='store_true', help='regenerate the deterministic receipt')
    parser.add_argument('--discover-inputs', action='store_true', help='draft-only dependency inventory')
    args = parser.parse_args()
    need(not args.discover_inputs or read(HERE / 'VERIFY.json')['status'] == 'draft', 'discovery requires draft manifest')
    if args.output:
        result = replay(args.output.resolve(), args.discover_inputs)
    else:
        with tempfile.TemporaryDirectory(prefix='r439-abc-hosted-') as tmp:
            result = replay(Path(tmp) / 'run', args.discover_inputs)
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    elif not args.discover_inputs:
        need(canonical(result) == canonical(read(HERE / 'RESULT.json')), 'deterministic receipt differs')
    print('PASS_R439_ABC_HOSTED_INVOICE ADDs=10652 helpers=126432 banks=0 no_new_kappa')


if __name__ == '__main__':
    main()
