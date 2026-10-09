"""Scratch PR69 coarse-column + PR71 split/anchor/live-cost composition.

All inherited files remain byte-identical. PR69/eumemic supplies the exact
coarse-column reassociation. PR71/Chafik Boukhalfa and its named predecessors
supply split grouping, global pair anchors, schedules and compiler. This new
composition experiment is prepared with OpenAI Codex assistance. No all-size
theorem or global optimization claim. See audit report for source boundaries.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
import argparse, gzip, hashlib, json, subprocess, types, os, shlex
from collections import Counter
from fractions import Fraction as Q
from math import comb
from bindings import producer, compile_axis
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
import binary_frame_math as arithmetic
from bindings import refine, audit

BEFORE = '''            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}'''
AFTER = '''            def coarse_sum(i, j):
                columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                return self.total(columns)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''

def activate(choices='ccc'):
    original = producer._graph
    path = Path(original.__file__)
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'
    source = raw.decode()
    assert source.count(BEFORE) == 1
    module = types.ModuleType('balanced_split_private_pair_graph')
    module.__file__ = str(path)
    replacement = '''            def coarse_sum(i, j):
                orientation = COARSE_CHOICES[level] if level < len(COARSE_CHOICES) else 'c'
                if orientation == 'r':
                    parts = [self.total([e(a,b) for b in groups[j]]) for a in groups[i]]
                else:
                    parts = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                return self.total(parts)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''
    assert len(choices)==3 and set(choices)<=set('cr')
    module.COARSE_CHOICES = choices
    exec(compile(source.replace(BEFORE, replacement), str(path)+':depth-coarse-factoring', 'exec'), module.__dict__)
    producer._graph = module
    return dict(pr71_head='1bef94fd40a746452548c84a4a8f8834670a3113',
                producer_sha256=hashlib.sha256(raw).hexdigest(),
                replacement_sha256=hashlib.sha256(replacement.encode()).hexdigest(),choices=choices,
                before=BEFORE, after=replacement, attribution='PR69/eumemic column reassociation generalized to deterministic depth row/column choices on PR71/Chafik Boukhalfa split+anchor+cost/live; predecessor notices retained')

def axis(h, out, pins):
    compiled, word = compile_axis(h)
    path = out/f'word-{h}.json.gz'
    raw = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0))
    receipt = replay(path)
    binfile = out/f'transitions-{h}.bin'
    prepared = prepare(path, binfile)
    profiler = out/f'profiles-{h}'
    if not profiler.exists():
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(profiler)], check=True)
    subprocess.run([str(profiler),str(binfile)], check=True)
    profile = json.loads(Path(str(binfile)+'.profiles.json').read_text())
    assert profile['crt_disagreements'] == 0
    assert profile['R'] == compiled['roles'] == receipt['roles'] == prepared['R']
    assert sum(t*n for t,n in enumerate(profile['blocks'])) == h*profile['R']+h*(h-1)
    result = dict(source=pins, compiled=compiled, replay=receipt, transitions=prepared, profile=profile,
                  word_sha256=hashlib.sha256(raw).hexdigest(),gzip_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (out/f'axis-{h}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS AXIS',h,'PHYSICAL ROLES',profile['R'],'CRT',profile['crt_matrices'],flush=True)

def compose(out,require_improvement=True):
    axes = [json.loads((out/f'axis-{h}.json').read_text()) for h in (23,25)]
    m,N = 575,comb(23,3)*comb(25,3)
    W=2*N+sum((N//x['profile']['v'])*x['profile']['R'] for x in axes)
    rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    for x in axes:
        p=x['profile'];h=p['h'];rep=N//p['v'];bank=rep*p['R']
        assert p['blocks'][0]==p['blocks'][h]==0
        rows.update({t:n*rep for t,n in enumerate(p['blocks']) if t and n})
        rows.update({h:bank,m-2*h:bank})
        rows.update({1:2*N,h-2:2*N})
    mass=sum(t*n for t,n in rows.items())
    assert mass==m*W-1846900 and max(rows)==529
    d=10**18;lo,hi=1,refine.floor_scaled(Q(717,10**7),d)
    while lo+1<hi:
        mid=(lo+hi)//2;r=refine.exact_moment(m,W,rows,Q(mid,d))
        if r['upper']<1:lo=mid
        elif r['lower']>1:hi=mid
        else:raise ValueError('Inconclusive exact enclosure')
    saving=Q(lo,d);accepted=refine.exact_moment(m,W,rows,saving);rejected=refine.exact_moment(m,W,rows,Q(hi,d))
    assert accepted['upper']<1<rejected['lower']
    independent=audit.independent_moment(dict(m=m,W=W,child_multiplicities=dict(rows)),saving,arithmetic.js(accepted['terms']))
    independent_rejected=audit.independent_moment(dict(m=m,W=W,child_multiplicities=dict(rows)),Q(hi,d),arithmetic.js(rejected['terms']))
    assert independent[1]<1<independent_rejected[0]
    old=json.loads((Path(__file__).resolve().parent/'comparisons/pr71.json').read_text())
    bridge=old['finite_bridge'];bridge['bit']['W']=W
    assert W.bit_length()==bridge['bit']['wire_bits']
    assembly=refine.assemble(bridge,saving,Q(1,10**12),d)
    oldrows={int(t):n for t,n in old['bit']['child_multiplicities'].items()}
    oldlower=refine.exact_moment(m,old['bit']['W'],oldrows,saving)['lower']
    if require_improvement:
        assert oldlower>1 and assembly['kappa']>Q(old['kappa'])
    result=dict(status='PASS selected finite words, dirty replay, literal frame reconstruction, CRT profiles and exact arithmetic only',
        W=W,total_rank=mass,deficit=m*W-mass,roles={str(x['profile']['h']):x['profile']['R'] for x in axes},
        bit_saving=saving,kappa=assembly['kappa'],child_multiplicities=dict(rows),accepted=accepted,rejected=rejected,
        independent_accepted=independent,independent_rejected=independent_rejected,
        exactness=[arithmetic.exactness(h) for h in (23,25)],
        assembly=assembly,old_pr71_lower_at_new_saving=oldlower,
        old_pr71_kappa=Q(old['kappa']),gain=assembly['kappa']-Q(old['kappa']),relative_gain=assembly['kappa']/Q(old['kappa'])-1,
        scope='All-size transfer, tape, routing, primes, recovery and analytic hypotheses remain inherited; full repository checks not run')
    (out/'certificate.json').write_text(json.dumps(arithmetic.js(result),indent=2,sort_keys=True)+'\n')
    print('RESULT',json.dumps(arithmetic.js({k:result[k] for k in ('W','roles','bit_saving','kappa','gain','relative_gain','old_pr71_lower_at_new_saving')})),flush=True)

def check_axis(h,out):
    selected=json.loads((out/f'axis-{h}.json').read_text())
    path=out/f'word-{h}.json.gz';packed=path.read_bytes()
    assert hashlib.sha256(packed).hexdigest()==selected['gzip_sha256']
    assert hashlib.sha256(gzip.decompress(packed)).hexdigest()==selected['word_sha256']
    assert json.loads(json.dumps(replay(path)))==selected['replay']
    target=out/f'check-transitions-{h}.bin'
    prepared=prepare(path,target)
    assert json.loads(json.dumps(prepared))==selected['transitions']
    profiler=out/f'profiles-{h}'
    if not profiler.exists():profiler=out/'profiles'
    subprocess.run([str(profiler),str(target)],check=True)
    profile=json.loads(Path(str(target)+'.profiles.json').read_text())
    assert profile==selected['profile']
    print('PASS independently rechecked axis',h,'roles',profile['R'],'CRT',profile['crt_matrices'],flush=True)
