#!/usr/bin/env python3
"""Independent small grammar/count/guard check. No candidate evaluator imports.

This checks finite applicability conditions, not unrestricted source identities,
Clifford factors, directed moments, or complete conditional admission.
Substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
REPO = BASE / 'repository'

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def allowance(g):
    if g[0] in ('clear', 'copy'):
        return 2
    q = Q(*g[3:]) if g[0] == 'add' else Q(*g[2:])
    a, b = abs(q.numerator), q.denominator
    require(a and not b & (b-1), 'Dyadic finite scalar grammar')
    if g[0] == 'scale':
        require(not a & (a-1), 'Dyadic unit SCALE')
        return 2*(abs(a.bit_length()-b.bit_length()) + int(q < 0))
    require(g[0] == 'add', 'Scalar opcode')
    return 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)

def inspect(word, old, label):
    pivots = {225,227,229,230,241,245,257,288 if label == '5383' else 261}
    require(word['programs']['forward'] == old['programs']['forward'], 'Unchanged forward word')
    require(word['canonical'] == {k:v for k,v in old['canonical'].items() if k != 'local_profile'}, 'Unchanged canonical geometry')
    expected = {('C', j) for j in range(9)} | {('L', j) for j in pivots}
    require({tuple(r) for r in word['owned']['backward']} == expected, 'Seventeen distinct backward owners')
    stats = {}
    for direction in ('forward','backward'):
        program = word['programs'][direction]
        require([e for e in program if e[0] in ('warp','adapter','phase')] ==
                [e for e in old['programs'][direction] if e[0] in ('warp','adapter','phase')],
                'Exact retained phase/warp/adapter itinerary')
        owned = {tuple(r) for r in word['owned'][direction]}
        frames = {('L', i):f for i,f in enumerate(word['canonical']['start'])}
        cleared = set(); live = set(); peak = 0; scalar = 0; paid = Counter(); zeros = []
        first_native = next(i for i,e in enumerate(program) if e[0] != 'scalar')
        prepared = set()
        for i,e in enumerate(program):
            kind = e[0]
            if kind == 'scalar':
                g, f = e[1:]; dst = tuple(g[1]); op = g[0]
                scalar += allowance(g)
                if op == 'clear':
                    require(dst in owned, 'Borrowed erase prohibited')
                    cleared.add(dst); frames[dst] = f
                    if dst[0] == 'C' and dst[1]: live.discard(dst)
                else:
                    require(frames.get(dst) == f, 'Scalar destination exact frame')
                    if op in ('add','copy'):
                        src = tuple(g[2]); require(src != dst and frames.get(src) == f, 'Distinct same-frame scalar source')
                    if op == 'copy' and dst[0] == 'C' and dst[1]:
                        require(dst in cleared and src[0] == 'L', 'Initialized owned snapshot')
                        live.add(dst); peak=max(peak,len(live))
                    if i < first_native:
                        require(direction == 'backward' and dst == ('L',dst[1]) and dst[1] in pivots and dst in cleared, 'Owned cold pivot preparation')
                        require(op == 'add' and src[0] == 'L' and src[1] not in pivots and f == 0, 'No pivot dependency or extra preparation oracle')
                        prepared.add(dst[1])
            elif kind == 'climb':
                r=('L',e[2]); require(frames[r] == e[3], 'Paid current frame');frames[r]=e[4];paid[e[5]]+=1
            elif kind == 'center':
                r=('C',e[1]); frames[r]=e[3];paid[e[4]]+=1
            elif kind == 'zero_retag':
                r=tuple(e[1]);require(frames[r] == e[2] and e[3] == 1, 'Zero site exact source/target frames');frames[r]=e[3];zeros.append(r)
            elif kind == 'warp':
                r=tuple(e[1]); require(frames[r] == e[3], 'Warp current exact frame');frames[r]=e[4]
            else:
                require(kind in ('phase','adapter'), 'Known unchanged event species')
        require(not live, 'All snapshots erased at return')
        if direction == 'backward':
            require(prepared == pivots and peak == 8 and len(zeros) == 8, 'Joint preparation, eight simultaneous snapshots, eight zero sites')
            require(paid == {1:2193,2:412,3:510,4:127,5:40}, 'Complete backward paid census')
        stats[direction] = dict(scalar_allowance=scalar, owned=len(owned), simultaneous_snapshots=peak, paid=dict(paid), zero_sites=len(zeros))
    require(stats['backward']['scalar_allowance'] == {'5383':158744,'5387':158776}[label], 'Candidate-specific fresh scalar allowance')
    return stats

def main():
    start=time.monotonic()
    resource.setrlimit(resource.RLIMIT_CPU,(15,15))
    resource.setrlimit(resource.RLIMIT_AS,(128*1024**2,128*1024**2))
    old=read(REPO/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    packages={'5383':REPO/'research/kappa-joint-relations-20261023',
              '5387':BASE/'agents/sources/pr5387/research/eight-owned-relations'}
    out={'status':'PASS_SCOPED_APPLICABILITY_COUNTS_AND_GUARDS','candidates':{},'full_uniform_word_materialized':False}
    for label,path in packages.items():
        word=read(path/'WORD.json.gz'); result=read(path/'RESULT.json')
        stats=inspect(word,old,label); price=result['bound'] if 'bound' in result else result.get('price',result)
        # Receipt keys are discovered explicitly, never evaluated as code.
        if 'compiler' not in price:
            price=next(v for v in result.values() if isinstance(v,dict) and 'compiler' in v)
        c=price['compiler'];s=price['strictification'];gap=Q(c['gap']);h=c['H'];j=c['integer_test_exponent']
        require(gap.numerator == 1 and h == j*gap.denominator, 'Exact integer compiler grid')
        require((h+1)**1000 < 2**j and (gap.denominator*(j-1)+1)**1000 >= 2**(j-1), 'Candidate threshold and preceding sufficient grid')
        rho=Q(s['reserve']); normalized=1/(1+1024*rho)+Q(4,2**32)
        require(normalized < 1 and Q(s['normalized_paid_upper']) == normalized, 'Funded paid-completion rounding budget')
        require(20**64 < 21**63 and Q(97,100)**128 < Q(1,16), 'Splitting separation and two charged tail-block guard')
        require(h > 8192 and 1000*gap > Q(1,h+1), 'Threshold covers product rank and eventual logarithmic derivative')
        out['candidates'][label]=dict(word_sha256=sha256((path/'WORD.json.gz').read_bytes()).hexdigest(),
            result_sha256=sha256((path/'RESULT.json').read_bytes()).hexdigest(),local=stats,
            raw_controller_owned_LOCAL_banks=16*17+2,compiler_H=h,compiler_j=j,gap=str(gap),
            reserve=str(rho),paid_completion_slack=str(1-normalized),
            expanded_count_majorant='D=2^262144; F(0)=D; F(n)=((n+1)*(D+1)*(F(n-1)+1))^(16*(n+1)^2); M=F(2^H)',
            expanded_bounds={name:'M' for name in ['W','P','O','R','G']},
            semantic={'Z':'2*M','E':'64*(2*M+2^H+2*M+1)^3','B':'M+E','C0':'32*2^H*B^2'},
            endpoint_scope='Fixed finite template and eventual thresholds under the five selected assumptions; semantic source identities and interval moment premises are separate review obligations')
    # Symbolic induction exponents behind F(n), with concrete arbitrary n controls.
    require(all(9*n+20 <=16*(n+1)**2 for n in range(1,1000)), 'Router/denominator-clearing majorant exponent')
    require(2*(82*1024+10+2*8192)+6+3*8193 < 262144, 'Strictified-unit D exponent including squared complete role inventory')
    controls={}
    del word
    original=read(packages['5383']/'WORD.json.gz')
    def bad_warp(w):
        i=next(i for i,e in enumerate(w['programs']['backward']) if e[0]=='warp')
        w['programs']['backward'][i]=list(w['programs']['backward'][i])
        w['programs']['backward'][i][2]=0
    for name,edit in [
        ('borrowed_erase',lambda w:w['programs']['backward'].insert(0,['scalar',['clear',['L',324]],0])),
        ('snapshot_owner_alias',lambda w:w['owned']['backward'].pop(8)),
        ('phase_itinerary',bad_warp),
    ]:
        bad=dict(original);bad['programs']=dict(original['programs'])
        bad['programs']['backward']=list(original['programs']['backward'])
        bad['owned']=dict(original['owned']);bad['owned']['backward']=list(original['owned']['backward'])
        edit(bad)
        try: inspect(bad,old,'5383')
        except ValueError as error: controls[name+'_rejected']=str(error)
        else: raise ValueError('Accepted mutation '+name)
    controls.update({'old_1e9_as_expanded_cap_rejected':2**262144>10**9,
      'one_bank_per_depth_rejected':out['candidates']['5383']['local']['backward']['simultaneous_snapshots']>1,
      '5387_reserve_1e_minus13_rounding_rejected':1/(1+Q(1024,10**13))+Q(4,2**32)>=1})
    require(all(controls.values()),'Meaningful stock/reserve controls')
    out.update(controls=controls,seconds=time.monotonic()-start,
      limitations=['No candidate evaluator imported','No free-word identity or Clifford phase replay','Moment alpha/gamma/delta interval hypotheses supplied by independent pricing review','Expanded count bound is a terminating integer recursion; its astronomical value was not numerically expanded','No independent human or formal proof; no unconditional physical theorem'])
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
