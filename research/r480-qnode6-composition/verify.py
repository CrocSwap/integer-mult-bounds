#!/usr/bin/env python3
"""Finite Q-node6 and all-subset composition replay; Apache-2.0.

Prepared for @CubeJerry with OpenAI Codex assistance. Reuses martinxxx9's
PR1089 record/geometry/set-column/stage evaluators unchanged. This wrapper's
splice, exhaustive local truth tables and source checks do not import search.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
BASE = '410026dc5513b87db92ae98571d1d5984c69a983'
CORE_INPUTS = {
    SOURCE,
    'research/r480-qnode-seed02/RECIPE.json',
    'research/r480-qnode5-seed05/CANDIDATE.json',
    'research/r480-qnode5-seed05/search.py',
    'research/r480-qnode5-seed05/verify.py',
    'research/e8-bit-p111-tuned/code/xcheck_p.py',
    'research/e8-bit-carrier-skeleton/code/bit/export_records.py',
    'research/e8-bit-carrier-skeleton/code/bit/independent/interface.py',
    'research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/columns_h.cpp',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp',
    'research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp',
    'research/e8-bit-carrier-skeleton/portable-include/bits/stdc++.h',
}
OBJECTS = [(2, 484, 2250, 2302), (5, 487, 2409, 2460), (6, 488, 2460, 2511)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pins():
    data = json.loads((HERE / 'SOURCES.json').read_text())
    need(data['base_commit'] == BASE, 'base pin')
    need(CORE_INPUTS <= set(data['files']), 'missing required source pin')
    for path, pin in data['files'].items():
        raw = (ROOT / path).read_bytes()
        need(digest(raw) == pin['sha256'], 'source digest: ' + path)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob: ' + path)
    return data


def transfer(gates, registers, frame, value):
    """Direct Boolean values, with no packed-matrix synthesis operations."""
    state = {r: (value >> i) & 1 for i, r in enumerate(registers)}
    for f, dst, sources in gates:
        need(type(f) is int and f == frame and type(dst) is int and dst in state,
             'block frame/destination')
        need(len(sources) == 1 and type(sources[0]) is int and
             sources[0] in state and sources[0] != dst, 'block operand')
        state[dst] ^= state[sources[0]]
    return sum(state[r] << i for i, r in enumerate(registers))


def build(base, programs, mask):
    """Independent splice: walk original indices forwards without offset edits."""
    out = copy.deepcopy(base)
    out['A'] = []
    cursor = 0
    for bit, (_, _, start, stop) in enumerate(OBJECTS):
        out['A'].extend(copy.deepcopy(base['A'][cursor:start]))
        out['A'].extend(copy.deepcopy(programs[bit] if mask & (1 << bit)
                                      else base['A'][start:stop]))
        cursor = stop
    out['A'].extend(copy.deepcopy(base['A'][cursor:]))
    out['C'] = [[1, dst, list(sources)] for _, dst, sources in reversed(out['A'] + out['B'])
                if not 120 <= dst < 240]
    need(all(base[k] == out[k] for k in base if k not in ('A', 'C')),
         'unrelated word field changed')
    return out


def call(command, directory, name):
    result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
    (directory / (name + '.log')).write_text(result.stdout + result.stderr)
    need(result.returncode == 0, name + ' failed: ' + (result.stdout + result.stderr)[-1800:])
    return result.stdout


def reject(function, label, controls):
    try:
        function()
    except ValueError:
        controls.append(label)
    else:
        raise ValueError('control accepted: ' + label)


def replay(out, replay_search=False):
    source_pins = pins()
    lib = load_module('qnode6_check_dependency', ROOT / 'research/r480-qnode5-seed05/verify.py')
    base = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    q2 = json.loads((ROOT / 'research/r480-qnode-seed02/RECIPE.json').read_text())
    q5 = json.loads((ROOT / 'research/r480-qnode5-seed05/CANDIDATE.json').read_text())
    candidate = json.loads((HERE / 'CANDIDATE.json').read_text())
    need((candidate['assignment_seed'], candidate['seed'], candidate['trajectories']) ==
         (6, 2026101406, 1000), 'search seed/coverage')
    need((candidate['frame'], candidate['start'], candidate['stop']) == (488, 2460, 2511),
         'candidate object')
    need(sum(candidate['histogram'].values()) == 1000, 'search histogram coverage')
    programs = [q2['replacement_A_events'], q5['best']['gates'], candidate['best']['gates']]
    need(list(map(len, programs)) == [43, 41, 43], 'expected circuit counts')
    controls, block_checks = [], []
    for (node, frame, start, stop), gates in zip(OBJECTS, programs):
        original = base['A'][start:stop]
        registers = sorted({r for _, d, ss in original for r in [d] + ss})
        need(len(registers) == 12, 'block register count')
        if node == 6:
            need(registers == candidate['registers'], 'Q-node6 physical outputs')
        for value in range(4096):
            wanted = transfer(original, registers, frame, value)
            got = transfer(gates, registers, frame, value)
            need(wanted == got, 'fixed physical output mismatch')
            need(transfer(list(reversed(gates)), registers, frame, got) == value,
                 'Boolean inverse mismatch')
        # An omitted gate must fail the map, not just the recipe length.
        for index in range(len(gates)):
            damaged = gates[:index] + gates[index + 1:]
            reject(lambda g=damaged: need(all(
                transfer(g, registers, frame, 1 << i) ==
                transfer(original, registers, frame, 1 << i) for i in range(12)),
                'omission changes transfer'), f'node{node}:omit_ADD_{index}', controls)
        block_checks.append(dict(node=node, old=len(original), new=len(gates), inputs=4096))
    dimensions = [lib.rank(base['lines'][i] for i in frame) for frame in base['frames']]
    need([dimensions[f] for _, f, _, _ in OBJECTS] == [4, 4, 4], 'Q-node frame ranks')
    reference_raw, reference_paths, reference_paid, reference_copies = lib.records(base, dimensions)
    need(reference_paid == {1:1200, 2:1440, 4:180, 6:120, 8:9}, 'baseline paid profile')
    rows, retained = [], {}
    for mask in range(8):
        word = build(base, programs, mask)
        raw, paths, paid, copies = lib.records(word, dimensions)
        need((paths, paid, copies) == (reference_paths, reference_paid, reference_copies),
             'paid paths changed')
        endpoint = lib.formal_endpoint(raw, 720)
        precision = lib.positive_bounds(raw, 720)
        count = sum(r[0] == 1 for r in raw)
        saved = sum(2 * (stop - start - len(programs[bit]))
                    for bit, (_, _, start, stop) in enumerate(OBJECTS) if mask & (1 << bit))
        need(count == 33958 - saved, 'complete ADD bill including cleanup')
        stages = [lib.stage_replay(raw, pairs) for pairs in (2, 4, 5)]
        work = out / f'mask-{mask}'
        work.mkdir()
        word_path = work / 'word.json.gz'
        word_path.write_bytes(gzip.compress(canonical(word), mtime=0))
        python = [sys.executable, '-I', '-B']
        call(python + [ROOT / 'research/e8-bit-p111-tuned/code/xcheck_p.py',
                       word_path, '--json', work / 'interface.json'], work, 'xcheck')
        iface = json.loads((work / 'interface.json').read_text())
        need(iface['status'] == 'PASS_EXACT_REPLAY_AND_INTERLEAVED_INTERFACE' and
             all(iface['hypotheses'].values()) and all(iface['conclusion'].values()),
             'original H1-H5 or conclusion')
        call(python + [ROOT / 'research/e8-bit-carrier-skeleton/code/bit/independent/interface.py',
                       word_path], work, 'pr425')
        call(python + [ROOT / 'research/e8-bit-carrier-skeleton/code/bit/export_records.py',
                       word_path, work / 'export'], work, 'export')
        encoded = b''.join(struct.pack('<6i', *r) for r in raw)
        need((work / 'export/249-records.bin').read_bytes() == encoded, 'official record export')
        if mask >= 4:
            need([precision['forward'], precision['reverse'], int(precision['payload'])] ==
                 candidate['best']['budgets'][mask - 4], 'search/replay precision mismatch')
        rows.append(dict(mask=mask, nodes=[n for bit, (n, _, _, _) in enumerate(OBJECTS)
                                          if mask & (1 << bit)], adds=count, records=len(raw),
                         saved=saved, precision=precision, stages=stages,
                         word_sha256=digest(canonical(word)), records_sha256=digest(encoded),
                         endpoint_sha256=endpoint, original_H1_H5=True))
        retained[mask] = (word, raw)
        print(f'PASS_SUBSET mask={mask} ADDs={count} payload_bits={precision["payload_bits"]}', flush=True)
    word, raw = retained[7]
    bad = copy.deepcopy(word)
    bad['D'][0][2].pop()
    reject(lambda: lib.formal_endpoint(lib.records(bad, dimensions)[0], 720),
           'missing dirt compensation', controls)
    stale = copy.deepcopy(word)
    stale['C'] = base['C']
    lib.formal_endpoint(lib.records(stale, dimensions, check_cleanup=False)[0], 720)
    reject(lambda: lib.records(stale, dimensions),
           'endpoint-valid stale cleanup violates literal contract', controls)
    bad_frame = copy.deepcopy(word)
    # Find the first Q-node6 gate after the earlier replacements.
    first = next(i for i, g in enumerate(bad_frame['A']) if g[0] == 488)
    bad_frame['A'][first][0] = 0
    reject(lambda: lib.records(bad_frame, dimensions), 'illegal frame descent', controls)
    inflated = copy.deepcopy(word)
    a, b = candidate['registers'][:2]
    inflated['A'][first:first] = [[488, a, [b]]] * 1000
    inflated['C'] = [[1, d, list(ss)] for _, d, ss in reversed(inflated['A'] + inflated['B'])
                      if not 120 <= d < 240]
    inflated_raw = lib.records(inflated, dimensions)[0]
    lib.formal_endpoint(inflated_raw, 720)
    reject(lambda: lib.positive_bounds(inflated_raw, 720),
           'endpoint-valid precision overflow', controls)
    for pairs in (2, 4, 5):
        for skip in range(6 * (pairs - 1)):
            reject(lambda k=pairs, s=skip: lib.stage_replay(raw, k, s),
                   f'omit bridge {pairs}/{skip}', controls)
    if replay_search:
        output = out / 'regenerated-search.json'
        call([sys.executable, '-I', '-B', HERE / 'search.py', '--output', output], out, 'search')
        need(json.loads(output.read_text()) == candidate, 'deterministic complete search replay')
    return dict(format='r480-qnode6-composition-certificate-v1', base_commit=BASE,
                assignment_seed=6, candidate_sha256=digest(canonical(candidate)),
                source_pins_sha256=digest(canonical(source_pins)), block_checks=block_checks,
                subsets=rows, paid_profile={str(k): v for k, v in reference_paid.items()},
                rank_mass=sum(k * v for k, v in reference_paid.items()), copies=reference_copies,
                register_paths_preserved=720, full_dirty_columns_per_subset=720,
                rejected_controls=controls, no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='new output directory')
    parser.add_argument('--replay-search', action='store_true')
    parser.add_argument('--native', action='store_true', help='also compile and replay all C++ cohorts')
    parser.add_argument('--write-certificate', type=Path, help='development: new certificate file')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='r480-qnode6-') as temporary:
        out = args.output.resolve() if args.output else Path(temporary) / 'run'
        out.mkdir(parents=True, exist_ok=False)
        report = replay(out, args.replay_search)
        encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
        if args.write_certificate:
            with args.write_certificate.open('x') as output:
                output.write(encoded)
        else:
            need(json.loads((HERE / 'CERTIFICATE.json').read_text()) == report, 'certificate drift')
        (out / 'REPORT.json').write_text(encoded)
        if args.native:
            native = load_module('qnode6_native', HERE / 'native.py')
            native_report = native.run(out, out / 'native')
            need(native_report == json.loads((HERE / 'NATIVE.json').read_text()),
                 'native certificate drift')
            print('PASS_R480_QNODE6_NATIVE subsets=8 stages=5,9,11 bridge_controls=384')
        print('PASS_R480_QNODE6_COMPOSITION Q6=51->43 ADDs=33958->33904 subsets=8 '
              f'columns=720 controls={len(report["rejected_controls"])} no_new_kappa')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print('REJECT:', error, file=sys.stderr)
        raise SystemExit(1)
