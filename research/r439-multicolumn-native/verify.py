#!/usr/bin/env python3
"""Native audit of PR2440's exact three-window, one-slot stream.

Staging/native receipt checks follow starship-s PR2421 and Gareth Davidson
PR2373; construction and finite source replay are Sagar Thakrar PR2440.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import runpy
import shlex
import signal
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HUB = 'research/e8-bit-carrier-skeleton'
PARENT = 'research/r439-one-slot-multicolumn-interleave'
HEAD = '1b38482a3a749f5815b074326b7ebda177a76f63'
FILES = {HUB + '/' + name for name in (
    'LICENSE', 'NOTICE.md', 'code/bit/export_records.py',
    'code/bit/regression/stage_cohort.py', 'portable-include/bits/stdc++.h',
    'code/bit/checkers/legality_h.cpp', 'code/bit/checkers/columns_k.cpp',
    'code/bit/checkers/json.hpp')} | {
    'research/e8-bit-p111-tuned/code/xcheck_p.py',
    'research/r439-bsection-stars-seed01/candidate.json.gz'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_bytes())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def same(a, b, message):
    need(canonical(a) == canonical(b), message)


def packed(rows):
    return b''.join(struct.pack('<6i', *row) for row in rows)


def execute(argv, *, cwd=None, timeout=180, rejects=None):
    env = {k: v for k, v in os.environ.items() if k != 'PYTHONOPTIMIZE'}
    with subprocess.Popen([str(x) for x in argv], cwd=cwd, env=env,
                          start_new_session=os.name != 'nt',
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        try:
            out, err = proc.communicate(timeout=timeout)
        except BaseException:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.kill()
            proc.wait()
            raise
    diagnostic = err.decode('utf-8', errors='replace')
    if rejects is not None:
        need(proc.returncode != 0 and rejects in diagnostic,
             'wrong native rejection (' + str(proc.returncode) + '): ' + diagnostic + out.decode(errors='replace'))
        # Abort status is platform-specific; retain the exact diagnosed obligation.
        return {'rejected': True, 'diagnostic': rejects}
    need(proc.returncode == 0, 'command failed: ' + repr(argv) + '\n' + diagnostic
         + out.decode('utf-8', errors='replace'))
    return out


def bindings(root):
    """Hash all inputs before staging or executing any predecessor code."""
    source, predecessor = load(HERE / 'SOURCES.json'), load(HERE / 'PREDECESSOR.json')
    need(predecessor['head'] == HEAD and predecessor['pr'] == 2440, 'predecessor identity')
    raw_files = {}
    for pin in source['files']:
        if pin['usage'] != 'input':
            continue
        name = pin['path']
        need(name in FILES and name not in raw_files, 'unexpected or duplicate input')
        raw = (ROOT / name).read_bytes()
        need(sha(raw) == pin['sha256'], 'source SHA256: ' + name)
        need(hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest() == pin['git_blob'],
             'source Git blob: ' + name)
        raw_files[name] = raw
    need(set(raw_files) == FILES, 'complete native inventory')
    names = ('verify.py', 'SOURCES.json', 'RESULT.json', 'WITNESS.json', 'SEARCH.json', 'README.md')
    expected = {PARENT + '/' + name: 'vendor/pr2440/' + name for name in names}
    need(len(predecessor['files']) == len(expected), 'complete predecessor inventory')
    for pin in predecessor['files']:
        name = pin['path']
        need(name in expected and expected.pop(name) == pin['local'], 'predecessor member')
        raw = (HERE / pin['local']).read_bytes()
        need(sha(raw) == pin['sha256'], 'predecessor SHA256: ' + name)
        need(hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest() == pin['git_blob'],
             'predecessor Git blob: ' + name)
        raw_files[name] = raw
    need(not expected, 'missing predecessor member')
    for name, raw in raw_files.items():
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    return {name: sha(raw) for name, raw in sorted(raw_files.items())}


def mutations(rows):
    """Discover actual intervals in RAW6, independently of schedule-builder code."""
    windows, active = [], None
    for i, row in enumerate(rows):
        if row[0] == 2:
            need(active is None and row[2] == 661, 'one-slot COPY lifecycle')
            active = (i, row[1])
        elif row[0] == 3:
            need(active is not None and row[1] == active[1] and row[2] == 661,
                 'ERASE owner binding')
            opening, owner = active
            taps = [j for j in range(opening + 1, i) if rows[j][0] == 1 and rows[j][5] == 3]
            undos = [j for j in range(opening + 1, i) if rows[j][0] == 1 and rows[j][5] == 4]
            windows.append({'copy': opening, 'erase': i, 'owner': owner,
                            'taps': taps, 'undo_count': len(undos)})
            active = None
    need(active is None and len(windows) == 9, 'nine closed windows')
    long = [w for w in windows if w['undo_count']]
    same([w['undo_count'] for w in long], [18, 24, 140], 'three consecutive undo intervals')
    same([len(w['taps']) for w in long], [5, 15, 10], 'three tap counts')
    first, second = long[:2]
    a, b = first['erase'], second['copy']
    overlap = rows[:a] + [rows[b]] + rows[a:b] + rows[b + 1:]
    stale = rows.copy()
    tap = stale.pop(first['taps'][-1])
    stale.insert(b, tap)  # Original b shifts left on deletion; insert after COPY.
    owner = rows.copy()
    index = second['erase']
    owner[index] = (3, first['owner'], *rows[index][2:])
    for changed in (overlap, stale):
        same(sorted(Counter(changed).items()), sorted(Counter(rows).items()), 'record multiset')
    return {'overlapping_handoff': overlap, 'stale_slot_tap': stale,
            'wrong_erase_owner': owner}, windows


def stage(root, name, rows, metadata):
    folder = root / name
    records = folder / 'records'
    records.mkdir(parents=True)
    raw = packed(rows)
    (records / '249-records.bin').write_bytes(raw)
    for file, data in metadata.items():
        (records / file).write_bytes(data)
    execute([sys.executable, '-I', '-B', root / HUB / 'code/bit/regression/stage_cohort.py',
             records, records, folder / 'cin', folder / 'cout'])
    need((folder / 'cout/COHORT249-RECORDS.bin').read_bytes() == raw, 'staged RAW6 equality')
    states, frames = (json.loads(metadata[n]) for n in ('249-states.json', 'frames.json'))
    expected = {'cin/249-states.json': states, 'cin/frames.json': frames,
                'cin/249-DONOR-OWNERSHIP.json': {'donor_keys': []},
                'cout/COHORT249-INITIAL.json': states['initial'],
                'cout/COHORT249-FRAMES.json': {}, 'cout/COHORT249-SELECTION.json': []}
    for file, value in expected.items():
        same(load(folder / file), value, 'staged metadata: ' + file)
    return {'record_sha256': sha(raw), 'records': len(rows),
            'metadata_sha256': {file: sha(canonical(value)) for file, value in expected.items()}}


def replay(root):
    pins = bindings(root)
    parent = root / PARENT / 'verify.py'
    execute([sys.executable, '-I', '-B', parent, '--output', root / 'emitted'], cwd=root)
    expected = load(root / PARENT / 'RESULT.json')
    same(load(root / 'emitted/RESULT.json'), expected, 'complete PR2440 receipt')
    p = runpy.run_path(str(parent))
    data = p['inputs']()
    import gzip
    word = json.loads(gzip.decompress(data[p['WORD']]))
    split, _, _, _, _ = p['split_word'](word)
    fixed, _ = p['export'](split, data, root / 'split-export')
    raw = (root / 'emitted/records.bin').read_bytes()
    candidate = list(struct.iter_unpack('<6i', raw))
    bill = expected['schedules']['candidate']
    need(sha(raw) == bill['record_sha256'], 'exact emitted candidate binding')
    bad, windows = mutations(candidate)
    cases = {'split94': fixed, 'multicolumn84': candidate, **bad}
    metadata = {name: (root / 'split-export/out' / name).read_bytes()
                for name in ('249-states.json', 'frames.json')}
    staging = {name: stage(root, name, rows, metadata) for name, rows in cases.items()}
    return {'status': 'PASS_MULTICOLUMN_SOURCE_BINDING', 'native_executed': False,
            'source_hashes': pins, 'predecessor_head': HEAD,
            'predecessor_receipt_sha256': sha(canonical(expected)), 'windows': windows,
            'schedules': {'split94': expected['schedules']['split94_exported'], 'multicolumn84': bill},
            'staging': staging, 'new_kappa': False}


def native(root, replay_report):
    checker = root / HUB / 'code/bit/checkers'
    build = root / 'build'
    build.mkdir()
    # A quoted multi-argument CXX is supported on POSIX; a literal Windows path
    # with spaces is one executable, not shlex's POSIX backslash syntax.
    value = os.environ.get('CXX', 'g++')
    compiler = [value] if os.name == 'nt' else shlex.split(value)
    flags = ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9']
    includes = ['-I' + str(root / HUB / 'portable-include'), '-I' + str(checker)]
    if os.environ.get('BOOST_INCLUDE'):
        includes += ['-I' + os.environ['BOOST_INCLUDE']]
    suffix = '.exe' if os.name == 'nt' else ''
    binary = lambda name: build / (name + suffix)
    print('Compile unchanged legality and three column engines', flush=True)
    execute(compiler + flags + includes + [checker / 'legality_h.cpp', HERE / 'native_diagnostics.cpp',
                                           '-o', binary('legality')])
    for k in (2, 4, 5):
        execute(compiler + flags + includes + ['-DVPORTS=111', '-DRHELP=439', f'-DKPAIRS={k}',
                checker / 'columns_k.cpp', '-o', binary(f'columns-{k}')])
    failures = {'overlapping_handoff': ('invalid COPY lifecycle', 'boundcopy'),
                'wrong_erase_owner': ('invalid ERASE lifecycle', 'discard original-source binding'),
                'stale_slot_tap': (None, 'local defining-decoder full formal column')}
    results = {}
    for name, binding in replay_report['staging'].items():
        print('Native replay:', name, flush=True)
        folder = root / name
        cin, cout = folder / 'cin', folder / 'cout'
        raw = cout / 'COHORT249-RECORDS.bin'
        need(sha(raw.read_bytes()) == binding['record_sha256'], 'native consumed RAW6')
        badleg, badcol = failures.get(name, (None, None))
        leg = execute([binary('legality'), cin, cout, cout / 'legality.json'], rejects=badleg)
        if badleg is None:
            leg = load(cout / 'legality.json')
            need(leg['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE',
                 'native legality status')
        columns = {}
        for k in (2, 4, 5):
            result = execute([binary(f'columns-{k}'), raw, cout / f'columns-{k}.json'], rejects=badcol)
            if badcol is None:
                result = load(cout / f'columns-{k}.json')
                need(result.pop('local_scalar_stream') == str(raw), 'native stream path')
                result.pop('seconds')
                result['local_scalar_stream_sha256'] = binding['record_sha256']
                bill = replay_report['schedules'][name]
                status = ('PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' if k == 2
                          else 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL')
                need(result['status'] == status, 'column status')
                need(result['formal_columns_checked'] == 222 * k + 439
                     and len(result['stages']) == 2 * k + 1, 'column and stage coverage')
                need(result['bridge_additions'] == 666 * (k - 1)
                     and result['fresh_center_copies'] == 9 * (2 * k + 1)
                     and result['reverse_fresh_center_copies'] == 9 * k, 'bridge/COPY bill')
                key = 'five_stage_additions' if k == 2 else 'stage_additions'
                need(result[key] == (2 * k + 1) * bill['ADDs']
                     and result['local_scalar_additions'] == bill['ADDs'], 'native ADD bill')
                same([int(x['cancellation_free_signed_row_l1_upper']) for x in result['signed_lift_prefix']],
                     [bill['F'], bill['B']], 'native positive envelopes')
                need(result['payload_prefix_bits'] == bill['local_bits'] < 104
                     and int(result['payload_prefix_upper']) == 64 * bill['F'] ** 3 * bill['B'] ** 2,
                     'native exact prefix invoice')
                same(result['negative_controls'], [{'omit_bridge': i, 'rejected': True}
                     for i in range(6 * (k - 1))], 'all omitted-bridge controls')
            columns[str(k)] = result
        if name in replay_report['schedules']:
            bill = replay_report['schedules'][name]
            need(leg['records'] == binding['records'] and leg['common_frame_ADDs'] == bill['ADDs']
                 and leg['nested_MOVEs'] == bill['MOVEs'] and leg['rank_mass'] == 5129
                 and leg['copies'] == leg['erasures'] == 9, 'native lifetime invoice')
            same(dict(leg['paid_histogram']), {int(k): v for k, v in bill['paid_profile'].items()}, 'native profile')
        results[name] = {'record_sha256': binding['record_sha256'], 'legality': leg, 'columns': columns}
    same(results['stale_slot_tap']['legality'], results['multicolumn84']['legality'],
         'stale slot tap preserves frame and lifecycle invoice')
    return {'status': 'PASS_R439_MULTICOLUMN_NATIVE', 'replay_sha256': sha(canonical(replay_report)),
            'compile_flags': flags, 'column_defines': {'VPORTS': 111, 'RHELP': 439, 'KPAIRS': [2, 4, 5]},
            'exception_diagnostics_sha256': sha((HERE / 'native_diagnostics.cpp').read_bytes()),
            'results': results, 'scope': 'Finite native geometry/columns. No bank audit, hosted or physical supplier admission.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native', action='store_true')
    ap.add_argument('--write', action='store_true', help='regenerate receipts after all requested checks pass')
    args = ap.parse_args()
    if os.name != 'nt':
        import resource
        resource.setrlimit(resource.RLIMIT_CORE, (0, resource.getrlimit(resource.RLIMIT_CORE)[1]))
    with tempfile.TemporaryDirectory(prefix='r439-multicolumn-') as tmp:
        root = Path(tmp)
        report = replay(root)
        reports = {'REPLAY.json': report}
        if args.native:
            reports['NATIVE.json'] = native(root, report)
        for name, value in reports.items():
            if not args.write:
                same(value, load(HERE / name), name + ' receipt mismatch')
        if args.write:
            for name, value in reports.items():
                (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n',
                                         encoding='utf-8', newline='\n')
    print('PASS_R439_MULTICOLUMN_' + ('NATIVE' if args.native else 'PYTHON_ONLY')
          + ' scatter=84 ADDs=11057 windows=3 controls=3 receipts_' + ('written' if args.write else 'matched'))


if __name__ == '__main__':
    main()
