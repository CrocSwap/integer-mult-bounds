#!/usr/bin/env python3
"""Bounded literal scalar/ownership/grammar audit of Ali Romman's PR5392.

No submitted module, native checker or emitter is executed. Independent review
Chris R/Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256,sha1
from pathlib import Path
import gzip,json,time

HERE=Path(__file__).resolve().parent
CAP=HERE.parent/'source-capsule'
PKG=CAP/'research/native-transpose-owned'
OLD=HERE.parents[1]/'price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'

def need(x,m):
    if not x:raise ValueError(m)

def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def ceil_log2(x):
    k=0
    while x>1:x/=2;k+=1
    return k

def charge(q,add):
    need(q.denominator&(q.denominator-1)==0,'dyadic coefficient')
    return ceil_log2(1+abs(q) if add else max(Q(1),abs(q)))+q.denominator.bit_length()-1

def scalar_stats(program):
    kinds=Counter();ops=Counter();h=0
    for e in program:
        kinds[e[0]]+=1
        if e[0]!='scalar':continue
        g=e[1];op=g[0];ops[op]+=1
        if op in ('add','scale'):
            q=Q(*g[3:]) if op=='add' else Q(*g[2:])
            h+=charge(q,op=='add')
    return dict(kinds=dict(kinds),scalar_ops=dict(ops),scalar_height_upper=h)

def monomial_grammar(m):
    n=9; rows=m['matrix_rows']; qs=m['quadratic_rows']; alpha=m['linear_Z4']
    need(len(rows)==len(qs)==len(alpha)==n,'nine axis monomial')
    need(all(type(x)==int and 0<=x<512 for x in rows+qs),'binary matrix range')
    basis={}
    for x in rows:
        while x:
            j=x.bit_length()-1
            if j not in basis:basis[j]=x;break
            x^=basis[j]
    need(len(basis)==n,'invertible affine address map')
    need(type(m['offset'])==int and 0<=m['offset']<512,'affine offset')
    need(type(m['phase'])==int and 0<=m['phase']<4,'Z4 global phase')
    need(all(type(x)==int and 0<=x<4 for x in alpha),'Z4 linear phase')
    for i in range(n):
        need(alpha[i]%2==((qs[i]>>i)&1),'diagonal quadratic parity')
        for j in range(n):need(((qs[i]>>j)&1)==((qs[j]>>i)&1),'quadratic symmetry')

def initial_owned_check(program,owned,backward):
    initialized=set();first=[]
    def use(r):
        r=tuple(r)
        if r in owned:need(r in initialized,'owned entry read before clear '+str(r))
    for i,e in enumerate(program):
        if e[0]=='scalar':
            g=e[1];op=g[0];dst=tuple(g[1])
            if op=='clear':
                need(dst in owned,'borrowed clear');initialized.add(dst)
                continue
            if op=='copy':need(dst in owned,'borrowed overwrite')
            else:use(dst)
            if op in ('copy','add'):use(g[2]);need(g[1]!=g[2],'distinct scalar owners')
        elif e[0]=='warp':use(e[1])
        elif e[0]=='transpose_paid_source':
            src=backward[e[1]];use(['L',src[2]] if src[0]=='climb' else ['C',src[1]])
        elif e[0]=='climb':use(['L',e[2]])
        elif e[0]=='center':use(['C',e[1]])
    need(initialized==owned,'all owned fields initialized')
    return True

def main():
    start=time.monotonic();manifest=read(CAP/'ROOT-MANIFEST.json')
    need(manifest['head']=='329b2ff35d2994b11abbb59f770d12da75c494ac','head pin')
    for row in manifest['rows']:
        b=(CAP/row['path']).read_bytes()
        need(sha256(b).hexdigest()==row['sha256'],'root SHA256 '+row['path'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'root Git blob '+row['path'])
    w=read(PKG/'WORD.json.gz');old=read(OLD);back=w['backward'];forward=w['forward_body']
    need(back==old['programs']['backward'],'exact5383 backward byte-structure')
    need(w['source_word_sha256']=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d','exact source word payload')
    owned={tuple(r) for r in w['owned_roles']};need(len(owned)==17,'seventeen owned slots')
    expected=[];copies=0;omitted_zero=0
    for i in reversed(range(len(back))):
        e=back[i];kind=e[0]
        if kind=='scalar':
            g=e[1]
            if g[0]=='add':expected.append(['scalar',['add',g[2],g[1],*g[3:]],e[2]])
            elif g[0]=='copy':
                need(tuple(g[1]) in owned,'transpose copy clears owned destination')
                expected.extend([['scalar',['add',g[2],g[1],1,1],e[2]],['scalar',['clear',g[1]],e[2]]]);copies+=1
            else:expected.append(e)
        elif kind=='warp':expected.append(['warp',e[1],-e[2],e[4],e[3]])
        elif kind in ('climb','center'):expected.append(['transpose_paid_source',i,e[5] if kind=='climb' else e[4]])
        elif kind=='zero_retag':omitted_zero+=1
        else:need(kind in ('phase','adapter'),'known backward opcode');expected.append(['transpose_marker',i])
    need(expected==forward,'literal complete transpose including COPY ADD+CLEAR')
    need(copies==16 and omitted_zero==8,'all sixteen copies and eight physical identities')
    need(not any(e[0] in ('proof_bridge','zero_retag') for e in forward),'no physical ghost or reverse zero assumption')
    initial_owned_check(back,owned,back);initial_owned_check(forward,owned,back)
    phases=read(PKG/'PHASES.json.gz')
    for p in phases:monomial_grammar(p['left']);monomial_grammar(p['right'])
    boundary=w['forward_boundary'];need(boundary['both_ends']=={'X':'Q_squared_native','Y':'scalar_minus_one'},'scalar sign stays outside tensor')
    need(len(boundary['main_Q_squared_offsets'])==112,'112 main offsets used at both ends')
    helpers=boundary['helper_post_translations'];need(len(helpers)==400,'400 complete helper translations')
    need({h['role'] for h in helpers}==set(range(224,632))-{r[1] for r in owned if r[0]=='L'},'exact retained helper correction set')
    for h in helpers:need(h['offset']==2**h['rank']-1,'native Q squared helper offset')
    stats={d:scalar_stats(p) for d,p in [('backward',back),('forward_body',forward)]}
    need(stats['backward']['scalar_height_upper']==29183,'fresh backward height')
    need(stats['forward_body']['scalar_height_upper']==29199,'fresh transposed scalar height')
    result=dict(schema='5392-closure-light/1',status='PASS_LITERAL_TRANSPOSE_SCALAR_OWNED_GRAMMAR',candidate_head=manifest['head'],
      root_manifest_sha256=sha256((CAP/'ROOT-MANIFEST.json').read_bytes()).hexdigest(),root_bound_files=len(manifest['rows']),
      word_sha256=sha256((PKG/'WORD.json.gz').read_bytes()).hexdigest(),word_payload_sha256=sha256(gzip.decompress((PKG/'WORD.json.gz').read_bytes())).hexdigest(),
      exact_5383_backward_retained=True,owned_roles=sorted(map(list,owned)),all_641_entry_fields_required=True,
      source_copy_count=copies,source_zero_identities_omitted=omitted_zero,
      new_forward_copy_rule='ADD old_source += old_destination; CLEAR old_destination',reverse_rows_assumed_zero=False,
      local_stats=stats,scalar_sign_layers=2,scalar_sign_fields_per_layer=112,
      new_boundary_translation_passes=224+400,monomial_recipes_grammar_checked=2*len(phases),
      monomial_grammar_is_not_phase_equality=True,raw_full_local_owned_banks=18*17,
      preparation_input_range='Backward preparation at most9M, denominator*2. Forward transposed program uses fresh29199 scalar height, not a unit-input or reverse-preparation shortcut.',
      new_expanded_counts_required=True,old_expanded_caps_reused=False,seconds=time.monotonic()-start,
      scope='Literal syntactic transpose, dyadic heights, dirty-owned initialization and affine-quadratic grammar; no author code/native criterion/phase amplitude/emitter/cold/Lean executed. Physical all-column endpoints and phase equality separate01gate.')
    (HERE/'LIGHT-ARITHMETIC-v1.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'],transposed_height=29199,raw_full_local_owned_banks=306)))

if __name__=='__main__':main()
