#!/usr/bin/env python3
"""Replay a finite-family negative result and its closest factory witness.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Retains Alluri's PR681 extraction/native checks and Sagar Thakrar's PR696
primitive replay, on Jeremy Kothe's PR622 raw constructor. No new kappa.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / 'research/complex-factory5-resynthesis'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sources():
    pins = read(HERE / 'SOURCES.json')
    for relative, expected in pins['files'].items():
        need(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected,
             'source changed: ' + relative)
    return pins


def build(v, raw, blocks, events, reference):
    changed = copy.deepcopy(raw)
    for block in reversed(blocks):
        registers = [r - (16 if r >= 240 else 8)
                     for r in block['registers_before_112_port_restriction']]
        def relocate(es):
            result = copy.deepcopy(es)
            for e in result:
                e[1] = registers[e[1]]
                if e[0] == 'add':
                    e[2] = registers[e[2]]
                e[-1] = block['frame']
            return result
        lo, hi = block['A_window_zero_based']
        need(raw['A'][lo:hi] == relocate(reference['original']), 'raw constructor window differs')
        old, new = copy.deepcopy(reference['original']), copy.deepcopy(events)
        for e in old + new:
            e[-1] = block['frame']
        need(v.columns(old) == v.columns(new), 'block full map differs')
        need(all(e[-1] == block['frame'] for e in new), 'block gate frame differs')
        need(all(len(v.span(f)) == 8 and v.span(f) <= v.span(block['frame'])
                 for f in block['entry_frames']), 'block entry frame differs')
        need({r for e in new for r in (e[1:3] if e[0] == 'add' else e[1:2])}
             == set(range(8)), 'missing frame climb')
        changed['A'][lo:hi] = relocate(events)
    changed['cleanup'] = [e[:-1] + [[256,128,64,32,16,8,4,2,1]] for e in
        v.inverse([e for e in changed['A'] + changed['B'] if not 112 <= e[1] < 224])]
    return changed


def verify(out):
    pins = sources()
    v = module('factory681', PRIOR / 'verify.py')
    ref, blocks = read(PRIOR / 'CIRCUIT.json'), read(PRIOR / 'BLOCKS.json')
    candidate = read(HERE / 'candidate.json')
    events = candidate['replacement']
    local = {}
    for name, transform in [('forward',lambda x:x), ('inverse',v.inverse),
                            ('inverse_transpose',v.dual), ('transpose',lambda x:v.dual(v.inverse(x)))]:
        old, new = transform(ref['replacement']), transform(events)
        need(v.columns(old) == v.columns(new), 'exact local map differs')
        old_env, new_env = v.positive_envelopes(old), v.positive_envelopes(new)
        local[name] = {'historical_primitives_before':len(v.lowering(old)),
            'historical_primitives_candidate':len(v.lowering(new)),
            'endpoint_envelope_dominated_by_pr681':all(a <= b for ca,cb in
                zip(v.columns(new,True),v.columns(old,True)) for a,b in zip(ca,cb)),
            'every_prefix_dominated_by_pr681':all(any(all(a <= b for a,b in zip(row,cover))
                for cover in old_env) for row in new_env),
            'unit_input_prefix_before':str(max(map(sum,old_env))),
            'unit_input_prefix_candidate':str(max(map(sum,new_env)))}
    try:
        v.validate(ref['original'], events, ref['frame'], ref['entry_frames'])
    except ValueError as error:
        original_admission = {'passed':False,'first_failure':str(error)}
    else:
        original_admission = {'passed':True}
    need(v.columns(ref['replacement']) == v.columns(events), 'PR681 complete map changed')
    from_independent = module('factory_independent', HERE / 'independent.py').verify()
    factor = module('factory_factors', HERE / 'factor.py')
    search, rebuilt_candidate = factor.run()
    search, rebuilt_candidate = json.loads(json.dumps([search, rebuilt_candidate]))
    need(json.loads(json.dumps(search)) == read(HERE / 'SEARCH.json'), 'finite search receipt differs')
    need(json.loads(json.dumps(rebuilt_candidate)) == candidate, 'finite search witness differs')
    need(all(f['best_current_primitives'] >= search['baseline_current_primitives']
             for f in search['families']), 'finite family contains an improvement')
    v.run(PRIOR / 'extract.py', [out / 'original'], out / 'constructor.log')
    v.bind_blocks(blocks, read(out / 'original/WINDOWS.json'), ref)
    raw = read(out / 'original/FULL-WORD.json.gz')
    words, receipts = {}, {}
    lower_dir = ROOT / 'research/complex-dyadic-lowering'
    sys.path.insert(0, str(lower_dir))
    try:
        lower = module('factory696', lower_dir / 'verify.py')
    finally:
        sys.path.pop(0)
    for name, word_events in [('baseline681', ref['replacement']), ('butterfly', events)]:
        changed = build(v, raw, blocks, word_events, ref)
        p = out / (name + '.json.gz')
        p.write_bytes(gzip.compress(canon(changed), mtime=0))
        receipts[name], words[name] = v.native(p, out / name, out)
        programs = read(out / name / 'LOCAL-PROGRAMS.json.gz')
        receipts[name]['pr696'] = {}
        for direction in ('forward', 'backward'):
            r, coefficients = lower.replay(name, direction, programs[direction],
                receipts[name]['emitted'][direction], receipts[name]['local']['local'][direction])
            for q in coefficients:
                lower.macro_check(q, lower.lower(['add',['T',0],['S',0],q.numerator,q.denominator]))
            receipts[name]['pr696'][direction] = r
    # Recount the pinned invoice_allcold.py local allowance only. This is not
    # an executed whole-owner/global invoice or later provider admission.
    for name, receipt in receipts.items():
        word = words[name]
        m, compiler = 73, 64 * 74**3
        macros = max(r['scalar_macros'] for r in receipt['pr696'].values())
        children = sum(receipt['emitted']['forward']['paid_profile'].values())
        registers, centers = 2 * word['v'] + word['R'], len(word['centers'])
        adapters = 16 * (macros + children + registers + centers) + 64 * m
        primitives = max(r['new_real_primitives'] for r in receipt['pr696'].values())
        receipt['retained_local_recount'] = {
            'dimension':m, 'compiler_allowance':compiler, 'scalar_macros':macros,
            'recursive_children':children, 'registers':registers, 'centers':centers,
            'adapter_allowance':adapters, 'maximum_pr696_primitives':primitives,
            'local_bound':primitives + adapters * compiler,
            'scope':'Arithmetic recount of pinned local allowance; no global invoice execution.'}
    before, after = words['baseline681'], words['butterfly']
    for key in ('local_profile', 'start', 'final', 'compensation', 'ports', 'centers',
                'center_frames', 'frames', 'edges'):
        need(before[key] == after[key], 'native invariant changed: ' + key)
    saved_macros = 28 * (len(ref['replacement']) - len(events))
    need(receipts['baseline681']['native']['scalar_operations'] -
         receipts['butterfly']['native']['scalar_operations'] == saved_macros, 'macro bill mismatch')
    savings = {}
    for direction in ('forward','backward'):
        old, new = (receipts[k]['pr696'][direction] for k in ('baseline681','butterfly'))
        saved = old['new_real_primitives'] - new['new_real_primitives']
        need(saved <= 0, 'negative-result witness unexpectedly improves PR681+PR696: ' + direction)
        need(receipts['baseline681']['emitted'][direction]['paid_profile'] ==
             receipts['butterfly']['emitted'][direction]['paid_profile'], 'paid profile changed')
        savings[direction] = saved
    controls = v.block_controls(blocks,
        read(out / 'original/WINDOWS.json'), ref)
    bad = build(v, raw, blocks, events, ref)
    bad['cleanup'].pop()
    bad_path = out / 'missing-cleanup.json.gz'
    bad_path.write_bytes(gzip.compress(canon(bad), mtime=0))
    try:
        v.native(bad_path, out / 'bad-native', out)
    except ValueError:
        need('cleanup is not the literal reversed inverse' in
             (out / 'bad-native-native.log').read_text(), 'wrong cleanup rejection reason')
        controls.append({'name':'missing_cleanup', 'reason':'literal reversed inverse mismatch'})
    else:
        raise ValueError('missing cleanup accepted')
    return {'status':'PASS_FACTORY_BUTTERFLY', 'base_commit':pins['base_commit'],
        'candidate_sha256':hashlib.sha256((HERE / 'candidate.json').read_bytes()).hexdigest(),
        'source_files_checked':len(pins['files']), 'blocks':14,
        'search':{k:v for k,v in search.items() if k != 'families'},
        'families':[{k:v for k,v in f.items() if k != 'best_replacement'} for f in search['families']],
        'gates_per_window':{'baseline681':len(ref['replacement']),'butterfly':len(events)},
        'scalar_macros_saved_with_cleanup':saved_macros,
        'pr696_real_primitives_saved':savings, 'local_checks':local,
        'original87_stronger_envelope_admission':original_admission,
        'independent':from_independent, 'negative_controls':controls, 'receipts':receipts,
        'scope':'Historical raw PR622 map only; no transported provider, selected frontier, full phase proof, owner invoice or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='retain artifacts in a new directory')
    parser.add_argument('--write', type=Path, help='development receipt generation')
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), 'refusing to overwrite a receipt')
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='factory-butterfly-') as tmp:
            result = verify(Path(tmp))
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == read(HERE / 'EXPECTED.json'), 'frozen receipt differs')
    print('PASS_FACTORY_BUTTERFLY blocks=14 gates=' + str(result['gates_per_window']) +
          ' pr696_saved=' + str(result['pr696_real_primitives_saved']) + ' kappa=unchanged')


if __name__ == '__main__':
    main()
