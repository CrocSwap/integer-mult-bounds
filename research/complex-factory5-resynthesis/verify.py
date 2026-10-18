#!/usr/bin/env python3
"""Exact standalone local circuit check plus the unchanged inherited raw-word audits.

Prepared for alluri-ritual with substantial OpenAI Codex assistance. Apache-2.0.
No producer/search code is imported. No new kappa or selected-word admission.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODE = ROOT / 'research/complex-k492-owner-repair/code'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def inverse(events):
    result = copy.deepcopy(events[::-1])
    for e in result:
        if e[0] == 'add':
            e[3] = -e[3]
        else:
            e[2], e[3] = e[3], e[2]
    return result


def dual(events):
    result = inverse(events)[::-1]
    for e in result:
        if e[0] == 'add':
            e[1], e[2] = e[2], e[1]
    return result


def span(vectors):
    values = {0}
    for v in vectors:
        values |= {x ^ v for x in values}
    return values


def scalar_step(state, e, positive=False):
    t = e[1]
    if e[0] == 'add':
        q = Q(e[3], e[4])
        state[t] += (abs(q) if positive else q) * state[e[2]]
    else:
        q = Q(e[2], e[3])
        state[t] *= abs(q) if positive else q


def columns(events, positive=False):
    # Column-oriented replay, independent of the search's row elimination.
    result = []
    for j in range(8):
        state = [Q(i == j) for i in range(8)]
        for e in events:
            scalar_step(state, e, positive)
        result.append(state)
    return result


def lowering(events):
    """Literal one-real-component lowering, using private register 8.

    clear, double, halve, negate and signed unit add each cost one.
    Complex arithmetic has two real components. Coefficient work is cleared.
    """
    out = []
    for e in events:
        t = e[1]
        if e[0] == 'scale':
            q = Q(e[2], e[3])
            if q < 0:
                out.append(('negate', t))
            shift = abs(q.numerator).bit_length() - q.denominator.bit_length()
            out.extend([('double' if shift > 0 else 'halve', t)] * abs(shift))
        else:
            q = Q(e[3], e[4])
            out.append(('clear', 8))
            for i, bit in enumerate(bin(abs(q.numerator))[2:]):
                if i:
                    out.append(('double', 8))
                if bit == '1':
                    out.append(('add', 8, e[2], 1))
            out.extend([('halve', 8)] * (q.denominator.bit_length()-1))
            out.extend([('add', t, 8, 1 if q > 0 else -1), ('clear', 8)])
    return out


def lowered_columns(events):
    primitives = lowering(events)
    result = []
    for j in range(9):
        state = [Q(i == j) for i in range(9)]
        for e in primitives:
            op, t = e[:2]
            if op == 'clear':
                state[t] = Q(0)
            elif op == 'double':
                state[t] *= 2
            elif op == 'halve':
                state[t] /= 2
            elif op == 'negate':
                state[t] *= -1
            else:
                state[t] += e[3] * state[e[2]]
        require(state[8] == 0, 'private coefficient work not cleared')
        result.append(state[:8])
    require(result[8] == [0]*8, 'incoming private coefficient work leaks')
    return result[:8]


def positive_envelopes(events):
    # Rows bound every prefix register, for ANY nonnegative incoming envelope.
    state = [[Q(i == j) for j in range(8)] for i in range(8)]
    seen = copy.deepcopy(state)
    for e in events:
        t = e[1]
        if e[0] == 'add':
            q = abs(Q(e[3], e[4]))
            source = state[e[2]]
            # Largest Horner accumulator occurs just before halving.
            seen.append([q.numerator*x for x in source])
            state[t] = [a+q*b for a, b in zip(state[t], source)]
        else:
            q = abs(Q(e[2], e[3]))
            state[t] = [q*a for a in state[t]]
        seen.append(state[t][:])
    return seen


def validate(original, candidate, frame, entry_frames):
    require(len(entry_frames) == 8 and len(span(frame)) == 16, 'invalid frame dimension')
    require(all(len(span(f)) == 8 and span(f) <= span(frame) for f in entry_frames),
            'entry frame is not a rank-three subspace')
    for events in (original, candidate):
        touched = set()
        for e in events:
            require(e[0] in ('add', 'scale'), 'unknown scalar operation')
            require(len(e) == (6 if e[0] == 'add' else 5), 'invalid scalar arity')
            ids = e[1:3] if e[0] == 'add' else e[1:2]
            require(all(type(r) is int and 0 <= r < 8 for r in ids), 'invalid register')
            require(e[-1] == frame, 'changed frame path')
            touched.update(ids)
            if e[0] == 'add':
                require(e[1] != e[2], 'self addition')
                q = Q(e[3], e[4])
            else:
                q = Q(e[2], e[3])
            require(q != 0 and q.denominator & (q.denominator-1) == 0, 'non-dyadic coefficient')
            if e[0] == 'scale':
                a = abs(q.numerator)
                require(a & (a-1) == 0, 'non-binary scale')
        require(touched == set(range(8)), 'missing physical frame climb')
    require(columns(candidate) == columns(original), 'exact local map differs')
    variants = {'main': lambda x: x, 'cleanup': inverse,
                'dual_main': dual, 'dual_cleanup': lambda x: dual(inverse(x))}
    receipt = {}
    for name, transform in variants.items():
        old, new = transform(original), transform(candidate)
        require(columns(old) == columns(new), name + ': exact map differs')
        require(lowered_columns(new) == columns(new), name + ': lowering differs')
        require(lowered_columns(old) == columns(old), name + ': reference lowering differs')
        require(all(a <= b for ca, cb in zip(columns(new, True), columns(old, True))
                    for a, b in zip(ca, cb)), name + ': endpoint growth increased')
        old_env, new_env = positive_envelopes(old), positive_envelopes(new)
        require(all(any(all(a <= b for a, b in zip(row, cover)) for cover in old_env)
                    for row in new_env), name + ': prefix growth increased')
        old_cost, new_cost = len(lowering(old)), len(lowering(new))
        require(new_cost < old_cost, name + ': no primitive improvement')
        receipt[name] = {'old_real_primitives': old_cost, 'new_real_primitives': new_cost,
                         'old_unit_input_prefix': str(max(map(sum, old_env))),
                         'new_unit_input_prefix': str(max(map(sum, new_env))),
                         'endpoint_entrywise_dominance': True,
                         'every_new_prefix_dominated_by_an_old_prefix': True}
    return receipt


def controls(cert):
    original, good, frame = cert['original'], cert['replacement'], cert['frame']
    mutants = {}
    mutants['missing_gate'] = good[1:]
    m = copy.deepcopy(good)
    next(e for e in m if e[0] == 'add')[3] *= -1
    mutants['wrong_sign'] = m
    m = copy.deepcopy(good)
    e = next(e for e in m if e[0] == 'add')
    e[2] = next(r for r in range(8) if r not in e[1:3])
    mutants['wrong_source'] = m
    m = copy.deepcopy(good)
    m[0][-1][0] ^= 1
    mutants['wrong_frame'] = m
    m = copy.deepcopy(good)
    e = next(e for e in m if e[0] == 'add')
    e[4] = 3
    mutants['non_dyadic_add'] = m
    mutants['non_binary_scale'] = good + [['scale', 0, 3, 1, frame]]
    # Same exact endpoint, but an enormous intermediate and endpoint envelope.
    mutants['neutral_growth_inflation'] = good + [
        ['add', 0, 1, 2**40, 1, frame], ['add', 0, 1, -(2**40), 1, frame]]
    # Same endpoint envelope, but a large transient scaling exceeds the prefix bill.
    mutants['neutral_prefix_inflation'] = good + [
        ['scale', 0, 2**40, 1, frame], ['scale', 0, 1, 2**40, frame]]
    # Same endpoint AND same absolute envelopes, but finite cost is worse.
    mutants['neutral_cost_inflation'] = good + [['scale', 0, -1, 1, frame]] * 400
    rejected = []
    for name, mutant in mutants.items():
        try:
            validate(original, mutant, frame, cert['entry_frames'])
        except ValueError as e:
            rejected.append({'name': name, 'reason': str(e)})
        else:
            raise ValueError('Accepted negative control: ' + name)
    require(columns(mutants['neutral_growth_inflation']) == columns(good),
            'growth control must preserve exact map')
    require(columns(mutants['neutral_prefix_inflation'], True) == columns(good, True),
            'prefix control must preserve the absolute endpoint map')
    require(columns(mutants['neutral_cost_inflation']) == columns(good),
            'cost control must preserve exact map')
    return rejected


def run(script, args, log):
    # -I ignores PYTHONOPTIMIZE; inherited assertions are always enabled.
    process = subprocess.run([sys.executable, '-I', '-B', str(script), *map(str, args)],
                             text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write_text(process.stdout)
    require(process.returncode == 0, f'{script.name} failed; see {log}\n{process.stdout[-1800:]}')


def native(raw, out, logs):
    route = ROOT / 'research/direct-delivery504-global/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    # Pairwise transport auditor; k492 code/ path ships integer rows after production rewrite.
    auditor = ROOT / 'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
    run(auditor, ['--raw', raw, '--routing', route, '--out', out],
        logs / (out.name + '-native.log'))
    run(CODE / 'hpe_emit_local.py', [out], logs / (out.name + '-emit.log'))
    run(CODE / 'hpe_audit_local.py', [out], logs / (out.name + '-local.log'))
    audit = read(out / 'SCALAR-FRAME-AUDIT.json')
    audit.pop('seconds')
    local = read(out / 'INDEPENDENT-LOCAL-REPLAY.json')
    # Container hashes vary with zlib; semantic identity covers all JSON fields.
    local.pop('canonical_word_sha256')
    local.pop('local_programs_sha256')
    checks = read(out / 'LOCAL-CHECKS.json')
    word = read(out / 'CANONICAL-WORD.json.gz')
    return {'native': audit, 'local': local, 'emitted': checks,
            'canonical_json_sha256': digest(word),
            'programs_json_sha256': digest(read(out / 'LOCAL-PROGRAMS.json.gz'))}, word


def bind_blocks(blocks, windows, cert):
    require([b['index'] for b in blocks] == list(range(14)), 'block inventory is not exactly 0..13')
    require(set(windows) == {str(i) for i in range(14)}, 'constructor inventory differs')
    seen, last_end = set(), 0
    for b in blocks:
        w = windows[str(b['index'])]
        require(b['block'] == w['block'], 'wrong block support')
        require(b['registers_before_112_port_restriction'] == w['registers'], 'wrong block registers')
        require(b['A_window_zero_based'] == [w['start'], w['end']], 'wrong block window')
        require(b['frame'] == w['frame'] and b['entry_frames'] == w['entry_frames']
                and b['exit_frames'] == w['exit_frames'], 'wrong block boundary frames')
        require(b['exit_frames'] == [b['frame']]*8, 'wrong block exit frames')
        require(len(set(w['registers'])) == 8 and not seen.intersection(w['registers']),
                'aliased factory registers')
        seen.update(w['registers'])
        require(w['start'] >= last_end, 'overlapping factory windows')
        last_end = w['end']
        original = []
        for e in w['gates']:
            e = copy.deepcopy(e)
            e[1] = w['registers'].index(e[1])
            if e[0] == 'add':
                e[2] = w['registers'].index(e[2])
            original.append(e)
        require([e[:-1] for e in original] == [e[:-1] for e in cert['original']],
                'original gates are not the literal constructor window')
        require(all(e[-1] == b['frame'] for e in original), 'nonconstant constructor frame')
    require(blocks[5] == {k: cert[k] for k in ('block', 'registers_before_112_port_restriction',
                'A_window_zero_based', 'frame', 'entry_frames', 'exit_frames')} | {'index': 5},
            'seed block differs from original certificate')


def block_controls(blocks, windows, cert):
    mutants = {'missing_block': blocks[:-1], 'duplicate_block': blocks[:-1]+[blocks[0]]}
    m = copy.deepcopy(blocks)
    m[3]['registers_before_112_port_restriction'][0] += 1
    mutants['wrong_block_register'] = m
    m = copy.deepcopy(blocks)
    m[8]['frame'][0] ^= 1
    mutants['wrong_block_frame'] = m
    rejected = []
    for name, mutant in mutants.items():
        try:
            bind_blocks(mutant, windows, cert)
        except ValueError as e:
            rejected.append({'name': name, 'reason': str(e)})
        else:
            raise ValueError('Accepted family control: ' + name)
    return rejected


def verify(out):
    pins = read(HERE / 'SOURCE-PINS.json')
    for rel, expected in pins['files'].items():
        require(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected,
                'Source pin mismatch: ' + rel)
    cert = read(HERE / 'CIRCUIT.json')
    blocks = read(HERE / 'BLOCKS.json')
    run(HERE / 'extract.py', [out / 'original'], out / 'constructor.log')
    windows = read(out / 'original/WINDOWS.json')
    require(cert['block_index'] == 33 % 14, 'wrong seed block')
    bind_blocks(blocks, windows, cert)
    original = cert['original']
    matrix_rows = list(map(list, zip(*columns(original))))
    require([[str(x) for x in row] for row in matrix_rows] == cert['matrix'], 'wrong claimed matrix')
    local = validate(original, cert['replacement'], cert['frame'], cert['entry_frames'])
    rejected = controls(cert) + block_controls(blocks, windows, cert)
    raw = read(out / 'original/FULL-WORD.json.gz')
    changed = copy.deepcopy(raw)
    bindings = []
    for block in reversed(blocks):
        index, frame = block['index'], block['frame']
        # The scalar template is identical, but every physical boundary is checked.
        old_events, new_events = copy.deepcopy(original), copy.deepcopy(cert['replacement'])
        for e in old_events + new_events:
            e[-1] = frame
        require(validate(old_events, new_events, frame, block['entry_frames']) == local,
                'block-specific local certificate differs')
        registers = [r-16 if r >= 240 else r-8
                     for r in block['registers_before_112_port_restriction']]

        def relocate(events):
            es = copy.deepcopy(events)
            for e in es:
                e[1] = registers[e[1]]
                if e[0] == 'add':
                    e[2] = registers[e[2]]
            return es

        begin, end = block['A_window_zero_based']
        require(raw['A'][begin:end] == relocate(old_events), 'raw 112-port window mismatch')
        # Descending splice order leaves all earlier source indices unchanged.
        changed['A'][begin:end] = relocate(new_events)
        bindings.append({'block_index': index, 'registers': registers,
                         'old_gates': len(old_events), 'new_gates': len(new_events),
                         'exact_map_and_frame_checked': True})
    changed['cleanup'] = inverse([e for e in changed['A'] + changed['B']
                                  if not 112 <= e[1] < 224])
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    for e in changed['cleanup']:
        e[-1] = full
    require(raw['cleanup'] == [e[:-1] + [full] for e in inverse(
        [e for e in raw['A'] + raw['B'] if not 112 <= e[1] < 224])],
        'reference cleanup is not literal inverse')
    (out / 'replacement').mkdir()
    new_path = out / 'replacement/FULL-WORD.json.gz'
    new_path.write_bytes(gzip.compress(canonical(changed), mtime=0))
    before, bw = native(out / 'original/FULL-WORD.json.gz', out / 'before-native', out)
    after, aw = native(new_path, out / 'after-native', out)
    for key in ('local_profile', 'start', 'final', 'compensation', 'ports', 'centers', 'center_frames'):
        require(bw[key] == aw[key], 'changed native invariant: ' + key)
    require(bw['frames'] == aw['frames'] and bw['edges'] == aw['edges'], 'changed phase-edge inventory')
    saved_macros = 2*len(blocks)*(len(original)-len(cert['replacement']))
    saved_primitives = 2*len(blocks)*sum(
        local[name]['old_real_primitives']-local[name]['new_real_primitives']
        for name in ('main', 'cleanup'))
    require(before['native']['scalar_operations']-after['native']['scalar_operations'] == saved_macros,
            'native scalar saving differs from local bill')
    for direction in ('forward', 'backward'):
        require(before['emitted'][direction]['scalar_macros']-
                after['emitted'][direction]['scalar_macros'] == saved_macros,
                'emitted scalar saving differs from local bill')
        require(before['emitted'][direction]['real_component_primitive_bound']-
                after['emitted'][direction]['real_component_primitive_bound'] == saved_primitives,
                'emitted primitive saving differs from local bill')
        require(before['emitted'][direction]['paid_profile'] == after['emitted'][direction]['paid_profile'],
                'changed paid profile')
        require(Q(after['local']['local'][direction]['prefix_l1_upper']) <=
                Q(before['local']['local'][direction]['prefix_l1_upper']), 'worse full-word prefix')
        require(after['emitted'][direction]['real_component_primitive_bound'] <
                before['emitted'][direction]['real_component_primitive_bound'], 'worse emitted cost')
    # Reject missing cleanup using the actual inherited all-column checker.
    bad = copy.deepcopy(changed)
    bad['cleanup'].pop()
    bad_path = out / 'missing-cleanup.json.gz'
    bad_path.write_bytes(gzip.compress(canonical(bad), mtime=0))
    try:
        native(bad_path, out / 'bad-native', out)
    except ValueError:
        log = (out / 'bad-native-native.log').read_text()
        require('cleanup is not the literal reversed inverse' in log,
                'cleanup control failed for an unrelated reason')
        rejected.append({'name': 'missing_cleanup', 'reason': 'literal reversed inverse mismatch'})
    else:
        raise ValueError('Missing cleanup accepted')
    result = {'status': 'PASS_COMPLEX_FACTORY_RESYNTHESIS', 'base_commit': pins['base_commit'],
              'circuit_sha256': hashlib.sha256((HERE / 'CIRCUIT.json').read_bytes()).hexdigest(),
              'source_files_checked': len(pins['files']), 'seed_block_index': 5,
              'block_count': len(blocks), 'block_bindings': bindings[::-1],
              'blocks_sha256': hashlib.sha256((HERE / 'BLOCKS.json').read_bytes()).hexdigest(),
              'old_gates': len(original), 'new_gates': len(cert['replacement']),
              'scalar_operations_saved_with_cleanup': saved_macros,
              'real_component_primitives_saved_per_orientation': saved_primitives,
              'local_checks': local, 'negative_controls': rejected,
              'before': before, 'after': after,
              'scope': 'Raw PR622 constructor only. No transported provider, hosted invoice, new kappa, phase lowering, or full multiplication theorem.'}
    write(out / 'RESULT.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='retain artifacts in a new directory')
    parser.add_argument('--write', type=Path, help='write a receipt instead of comparing the frozen result')
    args = parser.parse_args()
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='complex-factory5-') as tmp:
            result = verify(Path(tmp))
    if args.write:
        write(args.write, result)
    else:
        require(result == read(HERE / 'RESULT.json'), 'receipt differs from frozen result')
    print('PASS_COMPLEX_FACTORY_RESYNTHESIS windows=14 gates=1218->476 saved_with_cleanup=1484 columns=716 controls=14')


if __name__ == '__main__':
    main()
