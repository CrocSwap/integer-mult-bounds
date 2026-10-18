#!/usr/bin/env python3
"""Compose pinned supplier circuits and reprice their actual emitted programs.

Alluri, with substantial OpenAI Codex assistance. Apache-2.0.
The imported circuits and replay infrastructure retain their original authors.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(p):
    data = Path(p).read_bytes()
    return json.loads(gzip.decompress(data) if str(p).endswith('.gz') else data)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def write(p, x):
    p.write_text(json.dumps(x, indent=2) + '\n')


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def source_check():
    pins = read(HERE / 'SOURCES.json')
    for rel, pin in pins['files'].items():
        data = (ROOT / rel).read_bytes()
        if pin['representation'] == 'gzip-payload':
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source changed: ' + rel)
    dispositions = read(HERE / 'DISPOSITIONS.json')
    rows = {x['number']: x for x in dispositions['pull_requests']}
    need(len(rows) == len(dispositions['pull_requests']), 'duplicate disposition')
    for item in pins['imports']:
        row = rows[item['pr']]
        need(row['reviewed_head'] == item['head'], 'disposition head differs')
        retained = {x['path']: x for x in row['coverage'] if x['disposition'] == 'retained byte for byte'}
        expected = {name for name in pins['files'] if name.startswith(item['path']+'/')}
        need(set(retained) == expected, 'incomplete retained-file coverage')
        for name, record in retained.items():
            need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == record['sha256'],
                 'disposition retained bytes differ: '+name)
    return pins


def d_columns(word):
    """Independent full D operator, allowing restored helper AND target bases."""
    rows = [{i} for i in range(660)]
    for f, dst, sources in word['D']:
        need(f == 0 and word['frames'][f] == [] and 120 <= dst < 660,
             'D destination or frame')
        need(sources and len(set([dst]+sources)) == len(sources)+1, 'D alias')
        need(all(120 <= s < 660 and word['start'][s] == 0 for s in sources)
             and word['start'][dst] == 0, 'D source/frame')
        for src in sources:
            rows[dst].symmetric_difference_update(rows[src])
    return rows


def payload(helper, word):
    events = helper.scalar_events(word)
    f, r = [helper.interpret(events, 120, 420, reverse=rev, positive=True)['peak']
            for rev in (False, True)]
    return 64*f**3*r**2


def compose():
    helpers = module('consolidated_helpers', 'research/r420-compensation-basis/verify.py')
    targets = module('consolidated_targets', 'research/r420-target-basis/verify.py')
    quad = module('consolidated_quad', 'research/r420-quad13/verify.py')
    decoder = module('consolidated_decoder', 'research/r420-decoder-sharing/verify.py')
    blocks = module('consolidated_blocks', 'research/r420-two-block-composition/verify.py')
    original = read(BIT)
    hr = read(helpers.HERE / 'RECIPE.json')
    tr = read(HERE / 'TARGET-RECIPE.json')
    dr = read(HERE / 'DECODER-RECIPE.json')
    qr = read(quad.HERE / 'WITNESS.json')
    stages = [{'stage': 'selected R420', 'additions': blocks.additions(original)}]
    word = helpers.build(original, hr)
    stages.append({'stage': 'PR694 helper basis', 'additions': blocks.additions(word)})
    n = len(hr['pairs'])
    middle = copy.deepcopy(original)
    middle['D'] = word['D'][n:-n]
    need(targets.nominate(middle) == tr, 'target matching does not reproduce on transformed matrix')
    target_word = targets.build(middle, tr)
    word['D'] = word['D'][:n] + target_word['D'] + word['D'][-n:]
    need(d_columns(word) == d_columns(original), 'combined D operator differs')
    stages.append({'stage': 'PR713 target method on transformed rows', 'additions': blocks.additions(word)})
    word = quad.build(word, qr)
    stages.append({'stage': 'PR691 quad', 'additions': blocks.additions(word)})
    word = blocks.build(word, blocks.blocks())
    stages.append({'stage': 'PR670/674 via PR688 blocks', 'additions': blocks.additions(word)})
    need(dr['source_pairs'] == read(decoder.HERE / 'recipe.json')['pairs'], 'decoder source recipe')
    need(dr['pairs'] == [dr['source_pairs'][i] for i in dr['selected_indices']], 'decoder subset')
    # Reproduce the bounded compatibility pass, including the failed full batch.
    all_pairs = decoder.construct(word, dr['source_pairs'])
    need(payload(helpers, all_pairs).bit_length() == 105, 'full batch precision counterexample')
    need(blocks.additions(all_pairs) == 18370, 'full batch count')
    valid_leave_one_out = 0
    for omit in range(27):
        trial = decoder.construct(word, [p for i, p in enumerate(dr['source_pairs']) if i != omit])
        valid_leave_one_out += payload(helpers, trial) < 2**104
    need(valid_leave_one_out == dr['leave_one_out_valid'] == 0, 'leave-one-out receipt')
    chosen, pending, tried, history = [], list(range(27)), 0, []
    while pending:
        options = []
        for i in pending:
            trial = decoder.construct(word, [dr['source_pairs'][j] for j in sorted(chosen+[i])])
            price = payload(helpers, trial)
            tried += 1
            if price < 2**104:
                options.append((blocks.additions(trial), price, i))
        if not options:
            break
        count, price, i = min(options)
        chosen.append(i)
        pending.remove(i)
        history.append({'accepted_index': i, 'additions': count, 'payload_bits': price.bit_length()})
    need(sorted(chosen) == dr['selected_indices'] and tried == dr['variants_tested']
         and history == dr['history'], 'compatibility selection does not reproduce')
    before_decoder = copy.deepcopy(word)
    word = decoder.construct(word, dr['pairs'])
    stages.append({'stage': 'PR708 compatible 23/27 pairs', 'additions': blocks.additions(word)})
    need(decoder.scalar(before_decoder['A'], 660) == decoder.scalar(word['A'], 660),
         'complete A operator changed')
    need(set(original) == set(word) and all(original[k] == word[k] for k in original
         if k not in ('D','A','B','C')), 'field outside scalar phases changed')
    need(blocks.paths(original) == blocks.paths(word), 'register frame chronology differs')
    return original, word, helpers, blocks, quad, stages, all_pairs


def local(out):
    original, word, helper, blocks, quad, stages, excessive = compose()
    xcheck = module('consolidation_xcheck', 'research/e8-bit-r420/code/xcheck.py')
    checked, labels, full, h, c, _ = xcheck.check(original)
    need(all(h.values()) and all(c.values()), 'original interface')
    actual = copy.copy(checked)
    actual.w = word
    changed_full = actual.full()
    # Prove the canonical H1-H5 contract for the changed A/B/C map, then substitute
    # the exact same D boundary. Literal H2 is never relabelled as a pass.
    canonical_word = copy.deepcopy(word)
    canonical_word['D'] = copy.deepcopy(original['D'])
    boundary = copy.copy(checked)
    boundary.w = canonical_word
    boundary.full()
    hypotheses, conclusions, _ = boundary.interface()
    need(all(hypotheses.values()) and all(conclusions.values()), 'canonical interface fails')
    need(d_columns(word) == d_columns(canonical_word), 'semantic D substitution fails')
    dims = dict(enumerate(checked.fdim))
    receipts = {name: helper.word_receipt(w, dims) for name, w in [('baseline', original), ('replacement', word)]}
    for name, w in [('baseline', original), ('replacement', word)]:
        (out/(name+'.json.gz')).write_bytes(gzip.compress(canonical(w)+b'\n', mtime=0))
        folder = out/(name+'-export')
        folder.mkdir()
        helper.export_check(ROOT, w, receipts[name], folder)
    need(receipts['baseline']['paid_histogram'] == receipts['replacement']['paid_histogram'], 'paid profile changed')
    need(receipts['baseline']['rank_mass'] == receipts['replacement']['rank_mass'] == 5112, 'rank mass')
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except (ValueError, helper.Reject, xcheck.Reject):
            rejected.append(name)
        else:
            raise ValueError('accepted control: '+name)
    for name, index in [('missing_helper_preparation', 0), ('missing_helper_restoration', -1),
                        ('missing_target_preparation', 201), ('wrong_middle_read', 257)]:
        mutant = copy.deepcopy(word)
        del mutant['D'][index]
        reject(name, lambda m=mutant: need(d_columns(m) == d_columns(original), 'D map changed'))
    mutant = copy.deepcopy(word)
    mutant['D'][0][0] = 1
    reject('nonzero_D_frame', lambda: d_columns(mutant))
    mutant = copy.deepcopy(word)
    mutant['C'] = original['C']
    reject('stale_cleanup', lambda: need(mutant['C'] == quad.cleanup(mutant), 'literal cleanup differs'))
    for phase, index in [('A', 873), ('B', 263)]:
        mutant = copy.deepcopy(word)
        del mutant[phase][index]
        mutant['C'] = quad.cleanup(mutant)
        reject('wrong_'+phase+'_with_rebuilt_cleanup', lambda m=mutant: helper.interpret(helper.scalar_events(m),120,420))
    reject('all_27_decoder_pairs_exceed_precision', lambda: helper.word_receipt(excessive,dims))
    need(word['C'] == quad.cleanup(word), 'cleanup binding')
    result = {'status': 'PASS_CONSOLIDATED_BIT_CIRCUIT', **receipts, 'stages': stages,
              'saved_additions': receipts['baseline']['binary_additions']-receipts['replacement']['binary_additions'],
              'D_columns': 660, 'canonical_hypotheses': hypotheses, 'canonical_conclusions': conclusions,
              'actual_full_word': changed_full, 'labels': labels, 'controls': rejected,
              'semantic_D_contract': True, 'literal_H2_claimed': False,
              'compatibility_candidates': 1+27+372, 'retained_decoder_pairs': 23}
    need(result['saved_additions'] == 8538 and receipts['replacement']['binary_additions'] == 18378, 'combined savings')
    write(out/'LOCAL.json', result)
    return result


def emit_primitives(lower, programs, destination, receipts):
    """Emit one real-component primitive stream; complex replay charges two copies.

    Keep every phase, climb, adapter and residual event literally unchanged.
    This is an opt-in derived artifact, not an edit of selected source records.
    """
    result = {}
    for direction, events in programs.items():
        lowered = []
        primitive_hash = hashlib.sha256()
        for event in events:
            if event[0] == 'scalar':
                op, frame = event[1:]
                for primitive in lower.lower(op):
                    lowered.append(['primitive', list(primitive), frame])
                    primitive_hash.update(json.dumps([frame, primitive], separators=(',', ':')).encode()+b'\n')
            else:
                lowered.append(copy.deepcopy(event))
        need(primitive_hash.hexdigest() == receipts[direction]['primitive_word_sha256'],
             'emitted primitive stream differs from independently replayed stream')
        need([e for e in lowered if e[0] != 'primitive'] ==
             [e for e in events if e[0] != 'scalar'], 'non-scalar wrapper changed')
        need(2*sum(e[0] == 'primitive' for e in lowered) == receipts[direction]['new_real_primitives'],
             'emitted primitive count differs from checked bill')
        result[direction] = lowered
    destination.write_bytes(gzip.compress(canonical(result)+b'\n', mtime=0))
    return {'canonical_sha256': digest(result), 'one_real_component': True,
            'artifact_name': destination.name}


def complex_replay(out):
    """Run the imported selected-word proof, then compose its lowering with PR681."""
    folder = ROOT/'research/complex-dyadic-lowering'
    sys.path.insert(0, str(folder))
    lower = module('consolidated_complex', 'research/complex-dyadic-lowering/verify.py')
    selected = lower.verify()
    need(selected == read(folder/'EXPECTED.json'), 'selected complex receipt mismatch')
    factory_out = out/'factory'
    subprocess.run([sys.executable, '-I', '-B', str(ROOT/'research/complex-factory5-resynthesis/verify.py'),
                    '--out', str(factory_out)], check=True)
    emitted = {}
    for provider in ('ck', 'jp8'):
        receipts = {d: selected['programs'][provider+'/'+d] for d in ('forward','backward')}
        emitted[provider] = emit_primitives(lower, read(lower.PROVIDERS/provider/'LOCAL-PROGRAMS.json.gz'),
            out/(provider+'-PRIMITIVES.json.gz'), receipts)
    raw = {}
    for version in ('before', 'after'):
        base = factory_out/(version+'-native')
        events = read(base/'LOCAL-PROGRAMS.json.gz')
        checks = read(base/'LOCAL-CHECKS.json')
        inherited = read(base/'INDEPENDENT-LOCAL-REPLAY.json')
        for direction in ('forward', 'backward'):
            receipt, coefficients = lower.replay('raw-'+version, direction, events[direction],
                                                 checks[direction], inherited['local'][direction])
            for q in coefficients:
                lower.macro_check(q, lower.lower(['add',['T',0],['S',0],q.numerator,q.denominator]))
            raw[version+'/'+direction] = receipt
        emitted['raw-'+version] = emit_primitives(lower, events, out/('raw-'+version+'-PRIMITIVES.json.gz'),
            {d: raw[version+'/'+d] for d in ('forward','backward')})
    return {'selected_programs': selected, 'raw_factory_with_lowering': raw, 'emitted': emitted}


def run(out, hosted):
    source_check()
    result = {'status': 'PASS_SUPPLIER_CIRCUIT_CONSOLIDATION', 'bit': local(out),
              'complex': complex_replay(out), 'new_kappa_claim': False}
    write(out/'RESULT.json', result)
    if hosted:
        result['native'] = module('consolidation_native', HERE/'native.py').run(ROOT,out)
        write(out/'RESULT.json', result)
        result['hosted'] = module('consolidation_hosted', HERE/'hosted.py').run(ROOT,out)
        write(out/'RESULT.json', result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path)
    p.add_argument('--hosted',action='store_true')
    p.add_argument('--write',type=Path)
    args=p.parse_args()
    need(not sys.flags.optimize, 'Run without -O: inherited auditors require assertions')
    if args.out:
        out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
        result=run(out,args.hosted)
    else:
        with tempfile.TemporaryDirectory(prefix='supplier-consolidation-') as tmp:
            result=run(Path(tmp),args.hosted)
    if args.write:
        write(args.write,result)
    else:
        expected=read(HERE/('HOSTED.json' if args.hosted else 'EXPECTED.json'))
        need(result==expected,'frozen consolidation receipt differs')
    print('PASS_SUPPLIER_CIRCUIT_CONSOLIDATION bit_ADDs=26916->18378 saved=8538 hosted='+str(args.hosted)+' kappa=unchanged')


if __name__=='__main__':
    main()
