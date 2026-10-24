#!/usr/bin/env python3
"""One actual source prefix and a homogeneous tall interface, not a caller.
Apache-2.0. Credit Cao Yifan #4610, Cinna Davis #4698, native/Clifford
contributors; substantial OpenAI Codex assistance. Source files read-only.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import ast, gzip, json, os, subprocess, sys, types

HERE = Path(__file__).resolve().parent
PIN = '20bb93cd990d2ff683e4d0fc56b87a42cd5d3296'
PATHS = {
 'word': 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz',
 'ce': 'research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py',
 'prune': 'research/kappa-function-composition/complex/prune_native.py',
 'data': 'research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json',
}

def need(v, m):
    if not v:
        raise ValueError(m)

def load():
    raw = {k: subprocess.check_output(['git', '--no-replace-objects', 'show', PIN+':'+v]) for k,v in PATHS.items()}
    need(sha256(raw['word']).hexdigest() == '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05', 'actual native payload')
    need(sha256(raw['ce']).hexdigest() == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962', 'exact engine')
    ce = types.ModuleType('one496_independent_ce')
    sys.modules[ce.__name__] = ce
    exec(compile(raw['ce'], PATHS['ce'], 'exec'), ce.__dict__)
    definitions = [x for x in ast.parse(raw['prune']).body if isinstance(x, ast.FunctionDef) and x.name == 'conjugate']
    env = {}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), PATHS['prune'], 'exec'), env)
    return raw, ce, lambda op: env['conjugate'](ce, op)

def forward(word, cut):
    # Independently propagate ALL632 original columns, opposite to A's pullback.
    rows = {('L',r): {(r, ()): Fraction(1)} for r in range(632)}
    def plus(a,b,k):
        result = a.copy()
        for key,value in b.items():
            result[key] = result.get(key, Fraction(0)) + k*value
            if not result[key]: del result[key]
        return result
    for e in word[:cut]:
        if e[0] == 'scalar':
            s=e[1]; t=tuple(s[1]); v=rows.get(t,{})
            if s[0]=='add': rows[t]=plus(v,rows.get(tuple(s[2]),{}),Fraction(s[3],s[4]))
            elif s[0]=='scale': rows[t]={k:z*Fraction(s[2],s[3])for k,z in v.items()}
            elif s[0]=='copy': rows[t]=rows.get(tuple(s[2]),{}).copy()
            elif s[0]=='clear': rows[t]={}
            else: raise ValueError(s)
        elif e[0]=='warp':
            t=tuple(e[1]); a=e[2]
            rows[t]={(owner, (u[1:] if u and u[0]==-a else (a,)+u)):value for (owner,u),value in rows.get(t,{}).items()}
    return rows

def main():
    raw,ce,bar=load()
    p=json.loads(gzip.decompress(raw['word'])); c=p['canonical']; frames=c['frames']; w=p['programs']['backward']
    need(w[15372]==['climb','warp_retimed',496,911,1,3], 'guard exact replaced child')
    def span(v):
        out={0}
        for a in v: out|={x^a for x in tuple(out)}
        return out
    need(span(frames[911]) < span(frames[181]) < span(frames[1]), 'literal nested legal climb subspaces')
    need([len(span(frames[j])) for j in (911,181,1)]==[64,256,512], 'true6/8/9 ranks')
    state=forward(w,15372)
    need(state[('L',496)]=={(496,()):Fraction(1)}, 'ALL632 columns independent clean helper at cut')
    need(state[('L',151)]=={(151,()):Fraction(1)}, 'ALL632 columns independent clean Y at cut')
    final=forward(w,len(w))
    need(final[('L',39)]=={(39,()):Fraction(1),(151,()):Fraction(-1)}, 'complete actual X row')
    need(final[('L',151)]=={(151,()):Fraction(1)} and final[('L',496)]=={(496,()):Fraction(1)}, 'complete Y/helper rows')
    need({r for r,row in final.items() if any(owner in (39,151) for owner,u in row)}=={('L',39),('L',151)}, 'other original outputs do not depend on selected main inputs')
    need({r for r,row in final.items() if any(owner==496 for owner,u in row)}=={('L',496)}, 'other original outputs do not depend on helper496')
    I=ce.ident(9)
    grade=lambda x:ce.rank([a for a,b,z in x.tab[9:]])
    same=lambda a,b:a.tab==b.tab and a.zero_state()==b.zero_state()
    # compose(A,B)=A*B, while source then is chronological.
    def mul(*ops):
        out=I
        for op in reversed(ops): out=out.then(op)
        return out
    FU=ce.canonical_frame(9,frames[911]); FM=ce.canonical_frame(9,frames[181]); FV=ce.canonical_frame(9,frames[1])
    for conv in (lambda z:z,bar):
        old=conv(mul(FV,FU.adjoint())); first=conv(mul(FM,FU.adjoint())); last=conv(mul(FV,FM.adjoint()))
        need([grade(z)for z in (old,first,last)]==[3,2,1] and same(mul(last,first),old), 'independent exact local split phase and ranks in both orientations')
    F=bar(ce.canonical_frame(9,frames[1])); S=bar(ce.canonical_frame(9,frames[181])); E=bar(ce.canonical_frame(9,frames[41]))
    need(c['start'][39]==41 and frames[41]==[162] and c['ports'][39]==162, 'actual nonempty X input header')
    recipe=json.loads(raw['data'])['recipes'][39]; axes=recipe['idle_children'][0]['orthogonal_axes'][:8]
    need(axes==[161,4,8,16,131,64,35,256] and recipe['q']==162, 'one native transverse basis')
    need(all((a&162).bit_count()%2==0 for a in axes), 'transverse q-orthogonality')
    need(all((a&b).bit_count()%2==(i==j) for i,a in enumerate(axes) for j,b in enumerate(axes)), 'orthonormal transverse basis')
    D=I
    for a in axes:D=D.then(ce.cgate(9,a))
    Q=ce.cgate(9,162); q=Q.adjoint(); T=ce.xgate(9,510)
    need(same(mul(D,q),mul(q,D)), 'phase-exact commuting central query')
    need(same(F,mul(T,D,q)), 'actual full helper forward-sign translation in rawdual')
    N=mul(S,D.adjoint()); B=mul(E,Q)
    need(grade(N)==grade(B)==0, 'actual prefix and input normalization are monomial')
    Nrec,Nword=ce.monomial(N)[1],ce.monomial(N)[0]
    Brec,Bword=ce.monomial(B)[1],ce.monomial(B)[0]
    need(same(N,Nword) and same(B,Bword), 'absolute phase of free maps')
    need(same(mul(N.adjoint(),S),D), 'both actual prefix and Y normalize to D')
    need(same(mul(T.adjoint(),F,E.adjoint(),B),D), 'header-normalized main self is exact D')
    need(same(mul(T.adjoint(),F),mul(D,q)), 'main cross and independent helper are Dq')
    Gamma=mul(F,S.adjoint())
    need(grade(Gamma)==1 and grade(mul(Gamma,Gamma))==2, 'raw tail not a free-square central query')
    need(same(mul(q,q),ce.xgate(9,162)), 'normalized q-square is a monomial involution')
    need(same(mul(q,q,q,q),I), 'normalized q-order4')
    # Each matrix entry below is a single literal Clifford unit, with scalar
    # signs kept outside its tensor power. No width1 sum equality is lifted.
    blocks={
      'X_from_a':mul(T.adjoint(),F,E.adjoint(),B),
      'X_from_y':mul(T.adjoint(),F),
      'Y_from_y':mul(N.adjoint(),S),
      'Y_from_h':mul(T.adjoint(),F),
      'C_from_h':mul(N.adjoint(),S),
      'H_from_h':mul(T.adjoint(),F),
    }
    expected={k:(mul(D,q) if k in ('X_from_y','Y_from_h','H_from_h') else D) for k in blocks}
    def valid_tall(candidate):
        return candidate.keys()==expected.keys() and all(same(v,expected[k])for k,v in candidate.items())
    need(valid_tall(blocks), 'all tall4x3 group-word coefficients')
    controls={
      'omit_prefix_normalizer':not same(S,D),
      'omit_X_input_header_correction':not same(mul(T.adjoint(),F,E.adjoint()),D),
      'omit_Y_plus_helper_ADD':not valid_tall({k:v for k,v in blocks.items()if k!='Y_from_h'}),
      'replace_raw_Gamma_by_bare_query':not same(Gamma,q),
      'wrong_query_orientation':not same(mul(T.adjoint(),F),mul(D,Q)),
    }
    # Dedicated actual phase mutation: N has nonzero phase3, dropping it fails.
    mutated=ce.Op(9,Nword.tab,[e for e in Nword.circuit if e[0]!='phase'])
    controls['erase_normalizer_absolute_phase']=not same(mutated,N)
    need(all(controls.values()), 'six discriminating mutation boundaries')
    # Fixed source profile surcharge, via independently retained rational code.
    iv={ '__name__':'one496_iv', '__file__':str(HERE.parent/'check.py') }; exec(compile((HERE.parent/'check.py').read_bytes(),'conditional_interval_library','exec'),iv)
    costs={}
    for C in (Fraction('.0030217758'),Fraction('.0034')):
        delta=iv['add_intervals']([(1,iv['power_interval'](2,C)),(1,iv['power_interval'](1,C)),(-1,iv['power_interval'](3,C))])
        costs[str(C)]=iv['decimal_interval'](delta)
    out={
      'status':'PASS_ONE_NATIVE_HOMOGENEOUS_TALL_OFFER_NOT_TWO_CALL_CONSUMER',
      'source_commit':PIN,'sources':{PATHS[k]:sha256(v).hexdigest()for k,v in raw.items()},
      'actual_child':{'role':496,'event':15372,'from':911,'mid':181,'to':1,'paid_delta':{'1':1,'2':1,'3':-1}},
      'source_basis':{'q':162,'axes':axes,'X_input_header':41,'X_input_basis':frames[41]},
      'normalizers':{'N_S_Dinv':Nrec,'B_E_Q':Brec,'T':510},
      'grades':{'S':grade(S),'F':grade(F),'E':grade(E),'D':grade(D),'Gamma':grade(Gamma),'Gamma_squared':grade(mul(Gamma,Gamma)),'q_squared':grade(mul(q,q))},
      'literal_word_blocks':{k:v.circuit for k,v in blocks.items()},
      'tall_offer_rows':[['D','Dq','0'],['0','D','Dq'],['0','0','D'],['0','0','Dq']],
      'scalar_pre_post':'Input X=-B a; output X=-T^-1 rawX. Y=N^-1 rawY plus T^-1 rawH. C=N^-1 savedC. Original helper rawH restored after the ADD.',
      'three_original_owners':['a','y','h496'],'copied_prefix_independent_input':False,'helper_productive_credit_once':True,
      'allwidth':'Every nonzero block checked as an individual absolute-phase Clifford word; tensor each word then add external scalar blocks, never tensor a sum.',
      'controls':controls,'split_surcharge':costs,
      'additional_single_offer_pass_bound':17,'physical_split_pass_bound':19,'total_one_offer_extra_pass_bound':36,
      'finite_scope':'Conservative literal passes: pre(-B)<=4; post X translation1+sign1; Y/C N^-1 at4 each; helper translation/restore2; ADD1. C init/COPY/CLEAR already in19. No complete caller/compiler precision proof.',
      'second_call_obligation':'Two FULL invocations have independent original helpers h and k. The three-field4698 template needs the same third owner, so identifying h with k loses a productive job. Need a four-owner exact endpoint with both helper jobs retained; none emitted here.',
      'capacity112_claim':False,'new_kappa':False,'consumer_complete':False,
    }
    out=json.loads(json.dumps(out))
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:need(json.loads((HERE/'RESULT.json').read_text())==out,'frozen receipt')
    print(out['status'])

if __name__=='__main__':main()
