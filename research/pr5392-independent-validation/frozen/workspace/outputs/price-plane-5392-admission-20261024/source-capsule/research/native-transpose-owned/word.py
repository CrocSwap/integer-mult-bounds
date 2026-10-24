"""Check the literal transpose and its formal bridge cancellation.

The bridge is a coordinate proof symbol, not an emitted physical operation.
The source zero_retag is physical identity. Its transpose is identity.
Credit the classical transposition principle and PR5383 by Ali Romman,
Cao Yifan's word, Cinna Davis and the retained native authors. Apache-2.0.
Prepared by Ali Romman with OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json,sys
from support import HERE,ROOT,need,load,packed
sys.path.insert(0,str(HERE/'source/cutoff'))
from native_identity import decide
base=load('research/native-transpose-owned/source/owned/native.py','transpose_owned_source')
ROLES=632+base.COUNT+1
OWNED=set(base.BASIS)|set(range(632,ROLES))

def recipes(c):
    from phases import ce
    from native import Native
    out={}
    for w in c['warps']:
        rows=ce.transpose(tuple(w['G_columns']),9)
        tr=ce.transpose(ce.inv(rows,9),9)
        q=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
        op=ce.perm(9,rows).then(ce.diag(9,q));_,r=ce.monomial(op)
        out[str(w['op'])]=Native.parse({k:list(v) if isinstance(v,tuple) else v for k,v in r.items()},9).json()
    return out

def number(r):return r[1] if r[0]=='L' else 632+r[1]

def build(word):
 out=[];paid=Counter();count=Counter();cost=0
 for i in reversed(range(len(word))):
  e=word[i];kind=e[0]
  if kind=='scalar':
   g=e[1];op=g[0]
   if op=='add':new=['add',g[2],g[1],*g[3:]];out.append(['scalar',new,e[2]]);cost+=base.allowance(new)
   elif op=='copy':
    a=['add',g[2],g[1],1,1];b=['clear',g[1]]
    out.extend([['scalar',a,e[2]],['scalar',b,e[2]]]);cost+=base.allowance(a)+base.allowance(b)
   else:out.append(e);cost+=base.allowance(g)
  elif kind=='warp':out.append(['warp',e[1],-e[2],e[4],e[3]])
  elif kind in ('climb','center'):
   rank=e[5] if kind=='climb' else e[4];paid[rank]+=1
   out.append(['transpose_paid_source',i,rank])
  elif kind=='zero_retag':out.append(['proof_bridge',e[1],10000001+i])
  else:
   if kind not in ('phase','adapter'):raise ValueError(kind)
   out.append(['transpose_marker',i])
  count[kind]+=1
 return out,dict(paid),cost,dict(count)

def replay(word):
 rows=[{(r,()):Q(1)} for r in range(ROLES)];peak=Q(1);den=1
 for e in word:
  if e[0]=='scalar':
   g=e[1];r=number(g[1]);op=g[0]
   if op=='clear':rows[r]={}
   elif op=='add':base.add(rows[r],rows[number(g[2])],Q(g[3],g[4]))
   elif op=='scale':rows[r]={k:v*Q(g[2],g[3]) for k,v in rows[r].items()}
   else:raise ValueError(op)
  elif e[0] in ('warp','proof_bridge'):
   r=number(e[1]);op=e[2]
   rows[r]={(j,w[1:] if w and w[0]==-op else (op,)+w):v for (j,w),v in rows[r].items()}
  else:continue
  peak=max(peak,sum(map(abs,rows[r].values()),Q(0)))
  den=max(den,max((v.denominator for v in rows[r].values()),default=1))
 for r in range(ROLES):
  want={} if r in OWNED else {(r,()):Q(1)}
  if 112<=r<224:want[r-112,()]=Q(-1)
  if rows[r]!=want:raise ValueError(('Endpoint',r,len(rows[r]),rows[r]))
 return {'all_entry_columns':ROLES,'ghost_terms_at_return':0,'max_formal_prefix_l1':str(peak),'max_denominator':den}

def run(x):
 candidate=base.construct(x)
 need(sha256(packed(candidate)).hexdigest()=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d','Exact published PR5383 word')
 old=base.replay(candidate['canonical'],candidate['programs']['backward'],True,True)
 t,paid,cost,counts=build(candidate['programs']['backward'])
 result={'source_replay':old,'transpose':replay(t),'paid':paid,'real_scalar_allowance_before_wrappers':cost,'source_counts':counts}
 native_rec=recipes(x['canonical']);p=[]
 for e in t:
  if e[0]=='scalar':
   g=e[1];op=g[0];r=number(g[1])
   if op=='clear':p.append(dict(op='scale',dst=r,coefficient=0))
   elif op=='scale':p.append(dict(op='scale',dst=r,coefficient=str(Q(g[2],g[3]))))
   else:p.append(dict(op='add',dst=r,src=number(g[2]),coefficient=str(Q(g[3],g[4]))))
  elif e[0]=='warp':p.append(dict(op='apply',dst=number(e[1]),generator=str(abs(e[2])),inverse=e[2]<0))
 # The native checker is a separate concrete normalization check. The formal
 # replay above covers an arbitrary bridge, including nonmonomial operators.
 ref=[dict(op='add',dst=r+112,src=r,coefficient=-1) for r in range(112)]
 ref.extend(dict(op='scale',dst=r,coefficient=0) for r in OWNED)
 problem=dict(axes=9,roles=ROLES,generators=native_rec,program=p,reference=ref)
 result['native']=decide(problem)
 # The physical word contains no proof bridge. It refers to the exact
 # source operators, including their absolute phases and whole-job wrappers.
 emitted={'schema':'owned-transpose-word/v1','source_word_sha256':sha256(packed(candidate)).hexdigest(),
          'backward':candidate['programs']['backward'],
          'forward_body':[e for e in t if e[0]!='proof_bridge'],
          'forward_boundary':{'both_ends':{'X':'Q_squared_native','Y':'scalar_minus_one'},
                              'main_Q_squared_offsets':x['canonical']['ports'],
                              'helper_post_translations':[{
                                  'role':r, 'rank':len(x['canonical']['frames'][x['canonical']['final'][r]])-len(x['canonical']['frames'][x['canonical']['start'][r]]),
                                  'offset':(1 << (len(x['canonical']['frames'][x['canonical']['final'][r]])-len(x['canonical']['frames'][x['canonical']['start'][r]])))-1}
                                  for r in range(224,632) if r not in base.BASIS],
                              'source_wrappers':'transpose the normalized backward whole-job wrappers'},
          'owned_roles':candidate['owned']['backward'],
          'paid_profiles':{'forward':paid,'backward':paid},
          'helper_profiles':{'forward':old['helpers'],'backward':old['helpers']}}
 result['real_scalar_allowance']=cost+448
 result['new_monomial_passes_bound']=2*112+400
 result['source_word_sha256']=emitted['source_word_sha256']
 result['literal_word_sha256']=sha256(packed(emitted)).hexdigest()
 controls={}
 from copy import deepcopy
 variants={}
 bad=deepcopy(t)
 hit=next(e for e in bad if e[0]=='scalar' and e[1][0]=='add')
 hit[1][1],hit[1][2]=hit[1][2],hit[1][1];variants['wrong_transposed_add']=bad
 bad=deepcopy(t)
 i=next(i for i,e in enumerate(bad) if e[0]=='scalar' and e[1][:2]==['clear',['C',1]])
 del bad[i];variants['missing_owned_clear']=bad
 bad=deepcopy(t)
 hit=next(e for e in bad if e[0]=='warp');hit[2]*=-1;variants['wrong_native_transpose']=bad
 bad_source=base.construct(x)
 bad_source['programs']['backward'][1][1][3]*=-1
 variants['wrong_prepared_relation']=build(bad_source['programs']['backward'])[0]
 for name,word in variants.items():
  try:replay(word)
  except ValueError as error:controls[name]=str(error)[:180]
  else:raise ValueError('Accepted native control: '+name)
 result['controls']=controls
 bad=deepcopy(problem)
 hit=next(e for e in bad['program'] if e['op']=='apply')
 hit['inverse']=not hit['inverse']
 wrong=decide(bad)
 need(wrong['status']=='COUNTEREXAMPLE','Actual native sign control')
 from check_certificate import check
 check(bad,wrong)
 result['native_sign_counterexample']=wrong
 return result,emitted,problem
