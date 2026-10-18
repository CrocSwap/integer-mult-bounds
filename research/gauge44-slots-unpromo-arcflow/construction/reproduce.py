#!/usr/bin/env python3
"""Rebuild the frozen gauge44 delta from two pinned upstream checkouts.

Prepared for icekylinx with OpenAI GPT-6 Astra assistance. Apache-2.0.
This driver calls the credited upstream constructors unchanged; it runs no
search or optimizer. See ../CONSTRUCTION.md and INPUTS.json.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path, content=False):
    raw = path.read_bytes()
    if content and path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert __debug__, 'Assertions are required; do not use python -O.'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, required=True,
                        help='integer-mult-bounds checkout at the pinned main commit')
    parser.add_argument('--pr635', type=Path, required=True,
                        help='integer-mult-bounds checkout at the pinned PR635 commit')
    parser.add_argument('--out', type=Path, required=True,
                        help='new output directory outside both checkouts')
    parser.add_argument('--until', choices=('word', 'local', 'phases'), default='word',
                        help='default: scalar constructor only; local adds exact native replay and wrappers')
    parser.add_argument('--frozen-cold', action='store_true',
                        help='splice the pinned cold recipe instead of deriving its exact Q/T matrices again')
    args = parser.parse_args()
    roots = {'main': args.main.resolve(), 'pr635': args.pr635.resolve(), 'delta': HERE}
    out = args.out.resolve()
    assert not out.exists(), 'Use a new output directory.'
    assert not any(out.is_relative_to(root) for root in roots.values())
    pins = read(HERE / 'INPUTS.json')
    for family, files in pins['files'].items():
        for relative, expected in files.items():
            path = roots[family] / relative
            assert sha(path) == expected, ('input pin', family, relative)
    out.mkdir(parents=True)
    upstream = roots['pr635'] / 'research/complex-571-cold14-st2'
    source = roots['main'] / 'research/complex-k492-owner-repair/vendor/multicold'
    joint = source.parent / 'joint_prefix'
    base = source / 'vendor/pr558'
    parent = base / 'vendor/pr552'
    gk = parent / 'complex-local/static44/gk'
    hamming = source.parent / 'direct_delivery/inputs/hamming'
    structural = roots['main'] / 'research/structural-gain/frontier-composition'
    runner = source / 'code/run_portable.py'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(source),
               GAIN_PR564_SOURCE=str(source))
    env.pop('PYTHONOPTIMIZE', None)
    records = []

    def run(label, script, *arguments):
        start = time.monotonic()
        log = out / (label + '.log')
        print('RUN', label, flush=True)
        with log.open('w', encoding='utf-8') as stream:
            result = subprocess.run([sys.executable, '-B', str(runner), str(script),
                                     *map(str, arguments)], env=env, stdout=stream,
                                    stderr=subprocess.STDOUT)
        records.append({'step': label, 'exit_code': result.returncode,
                        'seconds': round(time.monotonic() - start, 3)})
        (out / 'STEPS.json').write_text(json.dumps(records, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError(label + '\n' + log.read_text()[-6000:])
        print('PASS', label, flush=True)

    def check_word(label, path):
        assert sha(path, content=True) == pins['word_content_sha256'][label], ('step pin', label)
        return path

    raw504 = parent / 'complex-local/static44/inputs/RAW504.json.gz'
    promoted = structural / 'global-replay/base/split-centres/FULL-WORD.json.gz'
    multi = structural / 'multicold-eight-word/FULL-WORD.json.gz'
    early = out / 'shadow-early'
    run('shadow-early', source / 'code/build_cold_kernel.py', '--input', promoted,
        '--recipe', source / 'data/EIGHT-COLD.json', '--gk-dir', gk, '--out', early)
    early_word = check_word('shadow-early', early / 'FULL-WORD.json.gz')
    prefix = out / 'shadow-prefix'
    run('shadow-prefix', joint / 'code/build_joint_prefix.py', '--input', multi,
        '--recipe', joint / 'data/JOINT-PREFIX.json', '--variant', 'eightcold',
        '--gk-dir', gk, '--out', prefix)
    prefix_word = check_word('shadow-prefix', prefix / 'FULL-WORD.json.gz')

    inputs = out / 'hamming'
    inputs.mkdir()
    for name in ('PROTOTYPE.json', 'PACKET-PROGRAMS.json.gz'):
        shutil.copyfile(hamming / name, inputs / name)
    shutil.copyfile(HERE / 'COMPLETION-PRIORITY.json', inputs / 'COMPLETION-PRIORITY.json')
    raw = out / 'raw'
    run('gauge-forward', HERE / 'construct_gauge_xcentre.py', inputs, raw,
        upstream / 'data/TRI-SCHEDULE.json')
    word = check_word('raw', raw / 'FULL-WORD.json.gz')
    assert sha(raw / 'HELPER-MAP.json') == pins['helper_map_sha256']
    chain = [raw504, promoted, early_word, multi, prefix_word]
    for i, (before, after) in enumerate(zip(chain, chain[1:])):
        target = out / ('port' + str(i))
        run('port' + str(i), upstream / 'code/build_port_stage.py',
            '--shadow-input', before, '--shadow-output', after, '--input', word,
            '--map', raw / 'HELPER-MAP.json', '--gk-dir', gk, '--out', target)
        word = check_word('port' + str(i), target / 'FULL-WORD.json.gz')

    changed = read(word)
    regroup = read(upstream / 'data/recipes/k492-jp8-frame_regroup.json')
    # The inherited changes are B-only and are checked against the actual new gates.
    for edit in regroup['changes']:
        assert changed[edit['section']][edit['index']] == edit['before']
        changed[edit['section']][edit['index']] = edit['after']
    changed['report'].update(local_profile=regroup['after'],
                             local_rank_mass=sum(int(r)*n for r, n in regroup['after'].items()))
    word = out / 'regroup/FULL-WORD.json.gz'
    dump(word, changed)
    check_word('regroup', word)
    hpe = load_module('upstream_hpe', upstream / 'code/build_hpe.py')
    changed = hpe.apply(changed, read(upstream / 'data/recipes/k492-jp8-hyperplane_end.json')['changes'])
    word = out / 'hpe/FULL-WORD.json.gz'
    dump(word, changed)
    check_word('hpe', word)

    target = out / 'cold44'
    if args.frozen_cold:
        cold = load_module('upstream_cold', upstream / 'code/build_cold_end.py')
        changed = cold.apply(changed, read(HERE / 'COLD44-RECIPE.json.gz'))
        # Match the exact constructor's descriptive status; this is not an audit assertion.
        changed['report']['status'] = 'EXACT_COLD44_CONSTRUCTED_PENDING_INDEPENDENT_AUDIT'
        dump(target / 'FULL-WORD.json.gz', changed)
    else:
        run('cold44-exact', HERE / 'build_gauge_cold44.py', '--input', word,
            '--out', target, '--hamming', inputs, '--upstream-package', upstream)
        assert read(target / 'RECIPE.json.gz') == read(HERE / 'COLD44-RECIPE.json.gz')
    word = check_word('cold44', target / 'FULL-WORD.json.gz')
    report = read(word)['report']
    assert report['local_rank_mass'] == 5650
    assert report['local_profile'] == {'1': 2514, '2': 404, '3': 448, '4': 160, '5': 56, '8': 8}
    assert report['width_inventory'] == {'4': 52, '5': 48, '7': 34, '8': 114, '9': 244}
    print('PASS exact frozen scalar word', word, flush=True)
    if args.until == 'word':
        return

    local = out / 'local'
    routing = parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    run('native', upstream / 'code/hpe_audit_and_transport.py', '--raw', word,
        '--routing', routing, '--out', local)
    assert sha(local / 'CANONICAL-WORD.json.gz', content=True) == pins['canonical_content_sha256']
    run('ledgers', upstream / 'code/hpe_emit_local.py', local)
    run('local-replay', upstream / 'code/hpe_audit_local.py', local)
    run('wrappers', upstream / 'code/hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    checks = read(local / 'LOCAL-CHECKS.json')
    for orientation, expected in pins['local_program_sha256'].items():
        assert checks[orientation]['sha256'] == expected
    if args.until == 'phases':
        clifford = parent / 'complex-global/vendor531/vendor/clifford'
        run('phases', base / 'code/phases_full.py', local, clifford)
        assert sha(local / 'CLIFFORD-RECIPES.json') == pins['clifford_recipes_sha256']
    print('DONE', local, flush=True)


if __name__ == '__main__':
    main()
