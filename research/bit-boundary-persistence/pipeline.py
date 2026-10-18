"""Run the complete native and hosted checks on both supplier words.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The exporters, adapters, checkers and invoice engines are unchanged.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import struct
import subprocess
import sys
from collections import Counter, defaultdict


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def load_module(path):
    spec = importlib.util.spec_from_file_location('boundary_hosting', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selection(root, out, template):
    package = root / 'research/e8-bit-p111-tuned'
    source = package / 'vendor/pr510/e8-r480-nine-stage/vendor/idle-axis-hosting/hosting_core.py'
    engine = load_module(source)
    schedule = []
    for event in template['schedule']:
        if event['kind'] == 'local_cover_sweep':
            schedule.append(dict(kind='local', stage=event['stage'], pair=event['pair']))
        elif event['kind'] in ('bridge', 'idle'):
            schedule.append(event)
    # The parent assigns idle indices only during hosted emission.
    next_index = 0
    for event in schedule:
        if event['kind'] == 'idle':
            event['idx'] = next_index
            next_index += 1
    windows = {i: w for i, w in engine.windows(schedule).items() if w[1] and w[2]}
    ys, zs, _ = engine.load_selection(package / 'data/selection9-p111.json', 'bit')
    slots, old_remaining = engine.expand(windows, ys, zs,
        {s: [(h, 8) for h in range(439)] for s in range(9)}, 222)
    removed = [slot for slot in slots if slot[5] == 248]
    need(len(removed) == 9 and {x[4] for x in removed} == set(range(9)), 'Missing deleted owner')
    pieces = defaultdict(list)
    stages = Counter()
    for index, copy, offset, width, stage, helper in slots:
        if helper != 248:
            pieces[index, copy].append(width)
            stages[index, width, stage] += 1
    patterns = Counter((index, tuple(sorted(pieces[index, copy], reverse=True)))
                       for index in windows for copy in range(222))
    proxy = sum(count * (engine.cost(windows[index][1], 64)
                        - engine.cost(windows[index][1] - sum(pattern), 64))
                for (index, pattern), count in patterns.items())
    path = out / 'candidate-selection.json'
    engine.save_selection(path, 'bit', patterns, stages, proxy)
    new_slots, new_remaining = engine.expand(windows, patterns, stages,
        {s: [(h, 8) for h in range(438)] for s in range(9)}, 222)
    need(len(new_slots) == 9 * 438, 'Wrong hosted helper count')
    need(sum(new_remaining.values()) - sum(old_remaining.values()) == 72,
         'Deleted residuals were not charged to idle children')
    need(max(new_remaining.values()) == 42, 'Maximum child changed')
    return {'removed_slots': removed, 'old_remainders': dict(Counter(old_remaining.values())),
            'new_remainders': dict(Counter(new_remaining.values())),
            'returned_idle_rank_per_replica': 72, 'hosted_helpers_per_replica': len(new_slots)}


def run(root, out, words, local_receipts, literal_records):
    out.mkdir(parents=True, exist_ok=False)
    predecessor = root / 'research/e8-bit-carrier-skeleton'
    package = root / 'research/e8-bit-p111-tuned'
    bit = predecessor / 'code/bit'
    price = package / 'vendor/pr510/e8-r480-nine-stage'
    code = price / 'vendor/e8-r715-eleven-stage-whole/code'
    python = [sys.executable, '-E', '-s', '-B']
    commands = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1',
                       OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')

    def call(name, command):
        command = list(map(str, command))
        print('RUN', name, flush=True)
        commands.append({'name': name, 'command': command})
        with (out / (name + '.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=environment)
        write(out / 'COMMANDS.json', commands)
        need(result.returncode == 0, 'Command failed: ' + str(out / (name + '.log')))

    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    boost = Path(os.environ.get('BOOST_INCLUDE', '/usr/include'))
    flags = ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=111',
             '-I' + str(bit / 'checkers'), '-I' + str(boost),
             '-I' + str(predecessor / 'portable-include')]
    binaries = out / 'bin'
    binaries.mkdir()
    call('compile-legality', compiler + flags + [bit / 'checkers/legality_h.cpp', '-o', binaries / 'legality'])
    summary = {}
    for name in ('baseline', 'candidate'):
        base = out / name
        base.mkdir()
        word = out / (name + '.json.gz')
        word.write_bytes(words[name].read_bytes())
        call(name + '-interface', python + [package / 'code/xcheck_p.py', word, '--json', base / 'interface.json'])
        call(name + '-export', python + [bit / 'export_records.py', word, base / 'records'])
        records = list(struct.iter_unpack('<6i', (base / 'records/249-records.bin').read_bytes()))
        need(records == [tuple(row) for row in literal_records[name]], 'Independent record export differs')
        call(name + '-stage', python + [bit / 'regression/stage_cohort.py',
             base / 'records', base / 'records', base / 'cin', base / 'cout'])
        call(name + '-legality', [binaries / 'legality', base / 'cin', base / 'cout', base / 'cout/legality.json'])
        call(name + '-gram', python + [bit / 'checkers/gram_frames.py', base / 'records', '--gram', 'e8ham', '--h', '8', '--positive'])
        local = local_receipts[name]
        legality = read(base / 'cout/legality.json')
        need(legality['common_frame_ADDs'] == local['adds'] and legality['rank_mass'] == local['rank_mass'],
             'Native legality disagrees')
        columns = {}
        for k in (2, 4, 5):
            executable = binaries / (name + '-columns' + str(k))
            call(name + '-compile-' + str(k), compiler + flags + ['-DRHELP=' + str(local['helpers']),
                 '-DKPAIRS=' + str(k), bit / 'checkers/columns_k.cpp', '-o', executable])
            receipt = base / 'cout' / ('columns_k' + str(k) + '.json')
            call(name + '-columns-' + str(k), [executable, base / 'cout/COHORT249-RECORDS.bin', receipt])
            result = read(receipt)
            need(result['formal_columns_checked'] == 2 * k * 111 + local['helpers'], 'Native coverage changed')
            need(len(result['negative_controls']) == 6 * (k - 1)
                 and all(x['rejected'] for x in result['negative_controls']), 'A bridge control failed')
            need(result['local_scalar_additions'] == local['adds'], 'Native ADD price differs')
            result.pop('seconds', None)
            result.pop('local_scalar_stream', None)
            columns[str(2 * k + 1)] = result
        shutil.copy2(base / 'cout/columns_k2.json', base / 'cout/columns.json')
        summary[name] = {'interface': read(base / 'interface.json'), 'legality': legality, 'columns': columns}

    call('parameterize-geometry', python + [package / 'vendor/pr545/code/adapt.py', predecessor,
         out / 'baseline.json.gz', out / 'geometry-adapter'])
    call('geometry', python + [out / 'geometry-adapter/nine_geometry.py', '--source', predecessor,
         '--out', out / 'geometry', '--word', out / 'baseline.json.gz'])
    call('parent-audit-adapter', python + [price / 'code/adapt.py', code, out / 'adapted'])
    call('parameterize-supplier', python + [package / 'code/adapt9p.py', code, price / 'code',
         out / 'adapted/audit_parent_k.py', out / 'a9p'])
    assembly_root = out / 'assembly-root'
    (assembly_root / 'data').mkdir(parents=True)
    (assembly_root / 'code').symlink_to(predecessor / 'code', target_is_directory=True)
    shutil.copy2(package / 'data/complex-b.json', assembly_root / 'data/complex-b.json')
    hosting_receipt = None
    for name in ('baseline', 'candidate'):
        base = out / name
        parent = base / 'nine'
        parent.mkdir()
        shutil.copy2(out / 'geometry/GEOMETRY.json', parent / 'GEOMETRY.json')
        word = out / (name + '.json.gz')
        call(name + '-parent', python + [out / 'a9p/global_k.py', '--word', word,
             '--local-check', base, '--out', parent, '--isometries', predecessor / 'data/eleven/residual-isometries.json'])
        call(name + '-parent-audit', python + [out / 'a9p/audit_parent_k.py', '--word', word,
             '--local-check', base, '--out', parent])
        if name == 'baseline':
            import gzip
            template = json.loads(gzip.decompress((parent / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
            hosting_receipt = selection(root, out, template)
            plan = package / 'data/selection9-p111.json'
        else:
            plan = out / 'candidate-selection.json'
        hosted = base / 'hosted'
        call(name + '-hosted', python + [out / 'a9p/emit_k.py', parent, base, hosted, '--selection', plan, '--key', 'bit'])
        call(name + '-hosted-audit', python + [out / 'a9p/audit_hosted_k.py', base, hosted, hosted / 'AUDIT.json'])
        call(name + '-invoice', python + [out / 'a9p/assemble9.py', base, hosted, hosted / 'AUDIT.json',
             assembly_root, base / 'PRICE.json', 'pr548'])
        pg = read(parent / 'GLOBAL.json')
        audit = read(hosted / 'AUDIT.json')
        invoice = read(base / 'PRICE.json')
        parent_audit = read(parent / 'AUDIT.json')
        need(audit['hosted_residuals'] == 9 * 32 * local_receipts[name]['helpers']
             and audit['bank_assignments'] == 0, 'Whole residual hosting failed')
        need(len(parent_audit['mutations_rejected']) == 17 and len(audit['mutations_rejected']) == 16,
             'Inherited audit coverage changed')
        for item in (audit, pg, parent_audit):
            item.pop('seconds', None)
        summary[name]['hosted'] = {'parent': pg, 'parent_audit': parent_audit, 'audit': audit, 'invoice': invoice}
    summary['hosting_change'] = hosting_receipt
    summary['environment'] = {'python': sys.version, 'platform': platform.platform(), 'compiler': compiler,
                              'boost_version_sha256': hashlib.sha256((boost / 'boost/version.hpp').read_bytes()).hexdigest()}
    write(out / 'RESULT.json', summary)
    return summary
