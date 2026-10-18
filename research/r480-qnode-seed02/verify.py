#!/usr/bin/env python3
"""Source-bound finite R480 Q-node construction; no new exponent.

Prepared for ToikY with substantial OpenAI Codex assistance; Apache-2.0.
See NOTICE.md for the retained circuit, checker and synthesis lineage.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
WORD = 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
BASE = '407d52ff15b2217b6e22bce44728b4c3907b6515'
REGS = [17,25,32,43,52,58,64,77,82,90,99,104]
REFERENCES = {
    'research/e8-r480-dead-totals/MANIFEST.json',
    'research/e8-r480-dead-totals/README.md',
    'research/e8-r480-dead-totals/NOTICE.md',
    'research/e8-r480-nine-stage/README.md',
    'research/e8-bit-carrier-skeleton/code/skeleton/wordkit.py',
    'research/e8-bit-carrier-skeleton/code/skeleton/gen.py',
    'research/e8-bit-carrier-skeleton/NOTICE.md',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def inputs():
    from native import NATIVE_INPUTS
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    need(pins['base_commit'] == BASE, 'source base')
    need(set(pins['files']) == set(pins['required_files']) == REFERENCES | set(NATIVE_INPUTS), 'source inventory')
    need(WORD in pins['files'], 'word pin missing')
    for name, pin in pins['files'].items():
        raw = (ROOT / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source hash: '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source blob: '+name)
    need(hashlib.sha256((ROOT / WORD).read_bytes()).hexdigest() ==
         '92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c', 'fixed source hash')
    return json.loads(gzip.decompress((ROOT / WORD).read_bytes()))


def local_rows(events):
    rows = {r:1 << i for i,r in enumerate(REGS)}
    for f,d,ss in events:
        need(type(f) is int and f == 484 and type(d) is int and d in rows,
             'Q-node frame or target')
        need(len(ss) == 1 and type(ss[0]) is int and ss[0] in rows and ss[0] != d,
             'Q-node source')
        rows[d] ^= rows[ss[0]]
    return [rows[r] for r in REGS]


def cleanup(word):
    return [[1,d,list(ss)] for _,d,ss in reversed(word['A']+word['B']) if not 120 <= d < 240]


def build(original, recipe):
    need(recipe['base_commit'] == BASE, 'recipe base')
    need(canonical(recipe['object']) == canonical(dict(phase='A',slice_start_inclusive=2250,
         slice_end_exclusive=2302,frame=484,registers_in_matrix_order=REGS)), 'recipe object')
    old = original['A'][2250:2302]
    new = recipe['replacement_A_events']
    need(len(old) == 52 and len(new) == 43, 'recipe length')
    need(local_rows(old) == local_rows(new) == recipe['fixed_output_f2_rows'], 'local fixed outputs')
    need({r for _,d,ss in new for r in [d]+ss} == set(REGS), 'frame visit coverage')
    need(original['C'] == cleanup(original), 'inherited literal cleanup')
    out = copy.deepcopy(original)
    out['A'][2250:2302] = copy.deepcopy(new)
    out['C'] = cleanup(out)
    return out


def stream(word):
    for section in ('D','A'):
        for _,d,ss in word[section]:
            for s in ss: yield ('add',d,s)
    for index,center in enumerate(word['ret']):
        yield ('copy',720,center)
        for target,indices in enumerate(word['scatter']):
            if index in indices: yield ('add',120+target,720)
        yield ('erase',720,center)
    for section in ('B','C'):
        for _,d,ss in word[section]:
            for s in ss: yield ('add',d,s)


def frame_paths(word):
    paths = [[f] for f in word['start']]
    for section in ('D','A','B','C'):
        for f,d,ss in word[section]:
            for r in [d]+ss:
                if paths[r][-1] != f: paths[r].append(f)
    for r,f in enumerate(word['final']):
        if paths[r][-1] != f: paths[r].append(f)
    return paths


def word_contract(original,candidate):
    need(candidate['C'] == cleanup(candidate), 'literal cleanup differs')
    need(all(original[k] == candidate[k] for k in original if k not in ('A','C')), 'unrelated field changed')
    need(frame_paths(original) == frame_paths(candidate), 'frame paths changed')


def replay(word):
    events = list(stream(word)); rows = [1 << i for i in range(720)]+[0]
    opened = None
    for tag,d,s in events:
        if tag == 'add':
            need(0 <= d < 720 and d != s and 0 <= s <= 720, 'scalar registers')
            need(s != 720 or opened is not None, 'closed copy read')
            need(d != opened, 'copied source modified')
            rows[d] ^= rows[s]
        elif tag == 'copy':
            need(opened is None, 'overlapping copy'); opened = s; rows[d] = rows[s]
        else:
            need(opened == s, 'erase binding'); opened = None; rows[d] = 0
    need(opened is None and rows[720] == 0, 'copy closure')
    expected = [(1 << i)^((1 << (i-120)) if 120 <= i < 240 else 0) for i in range(720)]
    need(rows[:720] == expected, 'all-column endpoint')
    bounds=[]
    for reverse in (False,True):
        norms=[1]*721; peak=1; opened=None
        for tag,d,s in (reversed(events) if reverse else events):
            if reverse and tag != 'add': tag='erase' if tag=='copy' else 'copy'
            if tag == 'add': norms[d]+=norms[s]; peak=max(peak,norms[d])
            elif tag == 'copy':
                need(opened is None,'prefix copy'); opened=s; norms[d]=norms[s]
            else:
                need(opened == s,'prefix erase');opened=None;norms[d]=0
        need(opened is None,'prefix closure');bounds.append(peak)
    payload=64*bounds[0]**3*bounds[1]**2
    need(payload < 1 << 104, '104-bit native payload exceeded')
    return dict(adds=sum(e[0]=='add' for e in events), copies=len(word['ret']), erasures=len(word['ret']),
                formal_columns=720, forward_positive_prefix=bounds[0], inverse_positive_prefix=bounds[1],
                payload_upper=str(payload),payload_bits=payload.bit_length(),
                word_sha256=digest(word),scalar_stream_sha256=digest(events),
                frame_paths_sha256=digest(frame_paths(word)))


def controls(original,candidate,recipe):
    rejected=0
    for index in range(43):
        changed=copy.deepcopy(recipe);changed['replacement_A_events'].pop(index)
        # Check the mathematical map directly, without the fixed-length guard.
        need(local_rows(changed['replacement_A_events']) != recipe['fixed_output_f2_rows'], 'vacuous deletion control')
        rejected+=1
    bad=copy.deepcopy(candidate);bad['C']=copy.deepcopy(original['C'])
    # Both old and new local maps are equal, so old cleanup is endpoint-valid!
    try: word_contract(original,bad)
    except ValueError as e: need('literal cleanup' in str(e), 'wrong stale cleanup rejection')
    else: raise ValueError('stale cleanup accepted')
    # This catches accounting/literal-interface drift rather than claiming a
    # false endpoint failure. Literal cleanup is required for this construction.
    stale=replay(bad)
    need(stale['adds'] == 33949, 'stale cleanup bill')
    rejected+=1
    bad=copy.deepcopy(candidate)
    x,y=REGS[:2]
    identity_cycle=[[484,d,[s]] for d,s in ((x,y),(y,x))*3]
    need(local_rows(identity_cycle) == [1<<i for i in range(12)], 'identity control setup')
    bad['A'][2250:2250]=identity_cycle*40;bad['C']=cleanup(bad)
    try: replay(bad)
    except ValueError as e:
        need('104-bit' in str(e), 'wrong growth rejection')
    else: raise ValueError('large endpoint-valid growth accepted')
    rejected+=1
    return dict(deleted_candidate_gates_rejected=43,stale_cleanup_endpoint_valid_adds=stale['adds'],
                stale_cleanup_rejected_by_literal_contract=True,identity_growth_rejected=True,total=rejected)


def verify(replay_search=False):
    original=inputs();recipe=json.loads((HERE/'RECIPE.json').read_text());candidate=build(original,recipe)
    if replay_search:
        import search
        need(canonical(search.receipt()) == canonical(recipe), 'search receipt')
    word_contract(original,candidate)
    before,after=replay(original),replay(candidate)
    need(before['adds'] == 33958 and after['adds'] == 33940, 'complete ADD saving')
    need(after['forward_positive_prefix'] == before['forward_positive_prefix'] and
         after['inverse_positive_prefix'] < before['inverse_positive_prefix'], 'complete prefix comparison')
    import independent
    other=independent.run()
    need(other['frame_paths_sha256'] == before['frame_paths_sha256'], 'independent frame paths')
    for label,primary in (('original',before),('replacement',after)):
        alt=other[label]
        need(alt['positive_forward']['adds'] == primary['adds'], 'independent ADD price')
        need(int(alt['positive_forward']['max_row_l1_upper']) == primary['forward_positive_prefix'] and
             int(alt['positive_reverse']['max_row_l1_upper']) == primary['inverse_positive_prefix'], 'independent prefix')
        need(alt['five_stage_payload_upper'] == primary['payload_upper'], 'independent payload')
    return dict(status='PASS_R480_QNODE_SEED02',base_commit=BASE,assignment_seed=2,
                recipe_sha256=digest(recipe),before=before,after=after,saved_adds=18,
                controls=controls(original,candidate,recipe),independent=other,no_new_kappa=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--replay-search',action='store_true')
    p.add_argument('--write',type=Path,help='write receipt to a new path')
    p.add_argument('--emit',type=Path,help='emit both words to a new directory')
    p.add_argument('--json',action='store_true');args=p.parse_args()
    for dest in (args.write,args.emit):
        if dest is not None:need(not dest.exists(),'output already exists')
    result=verify(args.replay_search)
    if args.write:
        with args.write.open('x') as f:f.write(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(canonical(result)==canonical(json.loads((HERE/'EXPECTED.json').read_text())),'receipt mismatch')
    if args.emit:
        original=inputs();candidate=build(original,json.loads((HERE/'RECIPE.json').read_text()))
        args.emit.mkdir()
        for label,word in (('original',original),('replacement',candidate)):
            (args.emit/(label+'.json.gz')).write_bytes(gzip.compress(canonical(word),mtime=0))
    if args.json:print(json.dumps(result,sort_keys=True))
    print('PASS_R480_QNODE_SEED02 block=52->43 ADDs=33958->33940 columns=720 payload_bits=102 no_new_kappa')


if __name__=='__main__':main()
