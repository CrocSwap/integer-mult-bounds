#!/usr/bin/env python3
"""Exact two-generation coupled-output transport. Apache-2.0.
New checker by zxv with substantial OpenAI Codex assistance. No subagents.
The pinned native endpoint is a premise; this does not replay its implementation.
"""
import argparse
import json
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

def need(ok,message):
 if not ok:raise ValueError(message)

def table(word):
 out=[]
 for x in range(512):
  y=x;phase=0
  for g in word:
   if g[0]=='P':y=sum(((q&y).bit_count()%2)<<j for j,q in enumerate(g[1]))
   elif g[0]=='D':
    need(len(g[1])==len(g[2])==9,'nine-axis phase')
    phase+=sum(a for j,a in enumerate(g[2]) if y>>j&1)
    phase+=2*sum(((g[1][j]>>(j+1))&(y>>(j+1))).bit_count()%2 for j in range(9) if y>>j&1)
   elif g[0]=='X':y^=g[1]
   elif g[0]=='phase':phase+=g[1]
   else:raise ValueError(g)
  out.append((y,phase%4))
 if len({y for y,ph in out})!=512:raise ValueError('not monomial')
 return out

def inverse(t):
 o=[None]*512
 for x,(y,p) in enumerate(t):o[y]=(x,-p%4)
 return o

def compose(a,b):
 return [(a[y][0],(p+a[y][1])%4) for y,p in b]
def rot(v,p):
 a,b=v
 return [(a,b),(-b,a),(-a,-b),(b,-a)][p%4]
def mul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def power(a,k):
 v=(1,0)
 for _ in range(k):v=mul(v,a)
 return v
def experiment(m,w,z,address):
 """D1 W1 columns on central 0, private 1..8, private 9..16.
 V uses Gaussian integer numerators /512; Z3 V uses /1024.
 Each of the eight independent mode columns is tested on the same input
 address. Owner coefficients stay outside the columnwise tensor product.
 """
 VS=[];ZS=[]
 M=m
 for mode in range(8):
  V=[]
  for i in range(112):
   d={}
   if M[mode][i]:
    a,ph=w[mode][i][address]
    for mask in range(256):
     v=rot(mul(power((1,1),8-mask.bit_count()),power((1,-1),mask.bit_count())),ph)
     d[a^(mask<<1)]=(M[mode][i]*v[0],M[mode][i]*v[1])
   V.append(d)
  zv=[]
  for k in range(8):
   d={}
   for i in range(112):
    if not M[k][i] or not V[i]:continue
    t=z[k][i]
    for a,v in V[i].items():
     local=(a&1)|((a>>9)<<1);b,ph=t[local]
     dest=(a&510)|(b&1)|((b>>1)<<9)
     v=rot(v,ph);old=d.get(dest,(0,0));d[dest]=(old[0]+M[k][i]*v[0],old[1]+M[k][i]*v[1])
   zv.append(d)
  VS.append(V);ZS.append(zv)
 
 return VS,ZS

def inner(a,b,denominator):
 re=im=0
 for x,y in zip(a,b):
  for at,(u,v) in x.items():
   r,s=y.get(at,(0,0));re+=u*r+v*s;im+=u*s-v*r
 need(im==0,'real exact Gram entry')
 return F(re,denominator**2)

def residual_gram(v,zv):
 need([[inner(a,b,512) for b in v] for a in v]==
      [[F(14*(i==j)) for j in range(8)] for i in range(8)],'image Gram = 14 I')
 return [[F(14*(i==j))-inner(a,b,1024)/14 for j,b in enumerate(zv)] for i,a in enumerate(zv)]

def determinant(gram):
 a=[r[:] for r in gram];det=F(1);pivots=[]
 for j in range(8):
  pivot=a[j][j];need(pivot>0,'positive residual pivot');pivots.append(pivot);det*=pivot
  for k in range(j+1,8):
   factor=a[k][j]/pivot
   for t in range(j,8):a[k][t]-=factor*a[j][t]
 return det,pivots

# Q and D_s commute. W_s and Z_s retain literal noncommuting order.
def word_normal(word):
 out=[];run=Counter()
 def flush():
  for label in sorted(run):
   e=run[label];out.extend([(label,1 if e>0 else -1)]*abs(e))
  run.clear()
 for label,e in word:
  if label=='Q' or label.startswith('D'):run[label]+=e
  else:flush();out.append((label,e))
 flush();return tuple(out)

def term(source,*ops):return {(source,word_normal(tuple((op,1) for op in ops))):F(1)}

def plus(a,b,c=1):
 out=dict(a)
 for key,value in b.items():
  total=out.get(key,F(0))+c*value
  if total:out[key]=total
  else:out.pop(key,None)
 return out

def left(a,*ops):
 out={}
 for (source,word),value in a.items():
  key=source,word_normal(tuple(ops)+word);out[key]=out.get(key,F(0))+value
 return {k:v for k,v in out.items() if v}

def encoded(row):
 return [{'input':s,'word':[[x,e] for x,e in w],'coefficient':str(c)} for (s,w),c in sorted(row.items())]

def chronology(controller,wrong_query=False):
 events=controller['physical_events']
 need(events[1]==['LOCAL',1,0,True] and events[8]==['LOCAL',3,1,True],'actual first backward FULLs')
 need(events[5]==['QUERY_SHEAR',2,0,False] and events[12]==['QUERY_SHEAR',4,1,False],'actual thin consumers')
 rows=[{} for _ in range(6)];observations={};snapshots={};helper_cross={}
 for index in range(1,15):
  e=events[index]
  if e[0]=='LOCAL':
   _,stage,pair,backward=e;need(backward and stage in (1,3),'declared FULL clip')
   x,y=2*pair,2*pair+1
   if stage==3:helper_cross={k:-v for k,v in left(rows[y],('D3',1),('Z3',1)).items()}
   rows[x]=plus(left(rows[x],('D'+str(stage),1)),left(rows[y],('D'+str(stage),1),('Q',1)),-1)
   rows[x]=plus(rows[x],term('h'+str(stage),'D'+str(stage),'Q','W'+str(stage)))
   rows[y]=left(rows[y],('D'+str(stage),1))
  elif e[0]=='IDLE':
   _,pair,stages=e
   for j in (2*pair,2*pair+1):rows[j]=left(rows[j],*[(('D'+str(stage)),1) for stage in reversed(stages)])
  elif e[0]=='ADD':rows[e[1]]=plus(rows[e[1]],rows[e[2]],e[3])
  elif e[0]=='QUERY_SHEAR':
   _,stage,pair,backward=e;need(not backward,'lower thin shear')
   x,y=2*pair,2*pair+1;response=left(rows[x],('Q',1 if wrong_query else -1))
   observations[str(stage)]=encoded(response);rows[y]=plus(rows[y],response)
  else:raise ValueError('unexpected clip event')
  if index in (7,14):snapshots[str(index)]=[encoded(r) for r in rows]
 expected=[term('h1','D1','Q','W1'),term('h1','D1','W1'),
  plus(term('h3','D3','Q','W3'),term('h1','D3','Q','D1','W1'),-1),term('h3','D3','W3'),{},
  plus(term('h3','D3','W3'),term('h1','D3','D1','W1'),-1)]
 need(rows==expected,'two-generation literal debt transport')
 need(helper_cross=={k:-v for k,v in term('h1','D3','Z3','D1','W1').items()},'second helper cross-contamination')
 return {'event_indices_inclusive':[1,14],'observations':observations,'snapshots':snapshots,
  'second_helper_cross_contamination':encoded(helper_cross),'required_transfer_equation':'W3 T = D1 W1',
  'retained_paid_calls':{'coupled_FULL':2,'thin_H1':224,'IDLE_H16':224,'IDLE_H24':224},
  'extra_coupled_target_credit':0}

def exit_contract(m):
 # Typed relations only: Qm Dm=Rm, Qh Dh=Rh, W Rh=Rm W, Rh Z=Z Rm.
 rules={('Qm','Dm'):('Rm',),('Qh','Dh'):('Rh',),('W','Rh'):('Rm','W'),('Rh','Z'):('Z','Rm')}
 def reduce(word):
  word=tuple(word)
  while True:
   for j in range(len(word)-1):
    if word[j:j+2] in rules:word=word[:j]+rules[word[j:j+2]]+word[j+2:];break
   else:return word
 def t(source,*word):return {(source,reduce(word)):F(1)}
 def app(row,*word):
  out={}
  for (s,w),c in row.items():
   key=s,reduce(word+w);out[key]=out.get(key,F(0))+c
  return {k:v for k,v in out.items() if v}
 x=plus(plus(t('x','Dm'),t('y','Rm'),-1),t('h','Rm','W'))
 y=t('y','Dm');h=plus(t('h','Dh'),t('y','Dh','Z'),-1)
 b=app(app(y,'Qm'),'Z');restored=plus(app(h,'Qh'),b)
 need(restored==t('h','Rh'),'all-input helper restoration from compressed response')
 need(plus(x,app(restored,'W'),-1)==plus(t('x','Dm'),t('y','Rm'),-1),'ordinary main return')
 need(plus(app(h,'Qh'),plus(b,t('dirty')))!=restored,'dirty response control')
 need(plus(app(h,'Qh'),b,-1)!=restored,'wrong repair sign control')
 edges=sum(bool(x) for r in m for x in r);need(edges==448,'actual code edge census')
 return {'required_response':'b = Z Q Y (eight fields)',
  'ordinary_output':'Hout=QH+b=Rh; Xout=X-W Hout=Dx-Ry; Yout=Y',
  'with_compressed_response':{'paid_H1':8,'ADD':edges+8,'monomial_fieldmaps':240,'new_owned_fields':0,'borrowed_response_restored':True},
  'with_full_response_QY':{'paid_H1':8,'ADD':2*edges,'monomial_fieldmaps':464,'new_owned_fields':0,'borrowed_response_restored':True},
  'from_no_response':{'paid_H1':120,'ADD':2*edges,'monomial_fieldmaps':464,'COPY':112,'CLEAR':224,'new_owned_fields':112},
  'existing_QUERY_source':'Q^-1(X+neighboring_X), rather than Z Q Y',
  'source_relative_no_response_rank_delta':120-8-8*8,
  'unfunded':['embedding of compressed observation at actual cut','complete compiler','recursive precision, tape movement and storage','outer admission']}

def integer_root(n,k):
 x=1<<((n.bit_length()+k-1)//k)
 while True:
  y=((k-1)*x+n//x**(k-1))//k
  if y>=x:break
  x=y
 need(x**k<=n<(x+1)**k,'directed integer-root enclosure')
 return x

def budget(provider,controller):
 selected=json.loads((HERE/'inputs/SELECTED-ARITHMETIC.json').read_text())
 original_local=Counter({int(k):v for k,v in provider['paid'].items()})
 original_local.update({1:8,8:8})
 helpers=Counter({int(k):v for k,v in provider['autonomous_native_helpers'].items()});helpers[9]+=8
 need(dict(original_local)=={int(k):v for k,v in selected['local_paid'].items()},'selected paid source binding')
 need(dict(helpers)=={int(k):v for k,v in selected['local_helpers'].items()},'selected helper source binding')
 paid=Counter();targets=Counter();backward=0
 for e in controller['physical_events']:
  if e[0]=='LOCAL':paid.update(original_local);targets.update(helpers);backward+=int(e[3])
  elif e[0]=='QUERY_SHEAR':paid[1]+=112
  elif e[0]=='IDLE':paid[8*len(e[2])]+=224
 for row in controller['diagonal']:targets[1+8*sum(row[1:])]+=112
 need(dict(paid)=={int(k):v for k,v in selected['paid'].items()},'complete selected paid census')
 need(dict(targets)=={int(k):v for k,v in selected['targets'].items()},'complete selected target census')
 need(backward==16,'sixteen applicable backward calls, not all eighteen FULLs')
 supplied=paid.copy();supplied[8]-=8*backward
 bought=supplied.copy();bought[1]+=112*backward
 need(sum(r*(targets[r]-paid[r]) for r in set(targets)|set(paid))==752,'selected rank surplus')
 need(sum(r*(targets[r]-bought[r]) for r in set(targets)|set(bought))==-16,'fully charged rank screen')
 # At a=1/250, r^(1-a)=r^(249/250), enclosed using integer roots.
 scale=2**80
 powers={r:integer_root(r**249*scale**250,250) for r in set(targets)|set(bought)}
 def margin(p):
  lo=hi=0
  for r in powers:
   c=targets[r]-p[r];v=powers[r]
   lo+=c*(v if c>=0 else v+1);hi+=c*(v+1 if c>=0 else v)
  return [str(F(lo,scale)),str(F(hi,scale))]
 supplied_margin=margin(supplied);bought_margin=margin(bought)
 need(F(supplied_margin[0])>0>F(bought_margin[1]),'charged .004 budget decision')
 # PR5413's declared neutral completion: provider+8 H8 paid, and the
 # eight coupled modes restored as H8 targets. This is a price comparison,
 # not a replay or admission of that completion's native implementation.
 neutral_paid=paid.copy();neutral_paid[1]-=18*8
 neutral_targets=targets.copy();neutral_targets[9]-=18*8;neutral_targets[8]+=18*8
 need(sum(neutral_paid.values())==64260 and sum(neutral_targets.values())==10928,'declared neutral comparison counts')
 need(sum(r*n for r,n in neutral_paid.items())==238990 and sum(r*n for r,n in neutral_targets.items())==239742,'declared neutral comparison masses')
 neutral_bought=neutral_paid.copy();neutral_bought[1]+=120*backward;neutral_bought[8]-=8*backward
 new_targets=neutral_targets.copy();new_targets[9]+=8*backward;new_targets[8]-=8*backward
 old_targets=targets;targets=new_targets
 neutral_bought_margin=margin(neutral_bought);targets=old_targets
 need(F(neutral_bought_margin[1])<0,'purchased response also fails neutral comparison')
 return {'saving_tested':'1/250','applicable_backward_FULLs':backward,
  'target_rank_mass':sum(r*n for r,n in targets.items()),'selected_paid_rank_mass':sum(r*n for r,n in paid.items()),
  'selected_rank_surplus':752,'compressed_response_supplied_rank_surplus':1776,
  'compressed_response_bought_rank_surplus':-16,
  'supplied_response_signed_moment_interval':supplied_margin,'bought_response_signed_moment_interval':bought_margin,
  'bought_response_delta_over_selected':{'H1':1792,'H8':-128},
  'neutral_completion_comparison':{'source_PR':5413,'head':'0c1fa2f47fb5ea17b93a4b67063d08e49cc38e51','scope':'Declared price profile only; no primary native or admission replay.',
   'replaced_unwrapped_backward_calls':16,'signed_moment_interval_at_004':neutral_bought_margin,
   'bought_response_rank_surplus':sum(r*(new_targets[r]-neutral_bought[r]) for r in set(new_targets)|set(neutral_bought))},
  'interpretation':'Supplying b is an unresolved enabling assumption. Buying QY independently fails the charged screen; all old thin queries remain paid.'}

def exit_program(m,kind):
 """Literal field program; monomials reference the pinned Kp/Km words."""
 ops=[]
 def mono(bank,n,label,sign=1):
  ops.extend([['MONOMIAL',bank+str(i),label+str(i),sign] for i in range(n)])
 if kind=='purchased':
  for i in range(112):ops.extend([['CLEAR','v'+str(i)],['COPY','v'+str(i),'y'+str(i)],['H1','v'+str(i)]])
 ops.extend([['H1','h'+str(k)] for k in range(8)])
 if kind=='compressed':ops.extend([['ADD','h'+str(k),'b'+str(k),'1'] for k in range(8)])
 mono('h',8,'Km')
 if kind!='compressed':
  mono('v',112,'Kp')
  for k in range(8):
   for i in range(112):
    if m[k][i]:ops.append(['ADD','h'+str(k),'v'+str(i),str(F(m[k][i],2))])
  mono('v',112,'Kp',-1)
 mono('x',112,'Kp')
 for i in range(112):
  for k in range(8):
   if m[k][i]:ops.append(['ADD','x'+str(i),'h'+str(k),str(F(-m[k][i],2))])
 mono('x',112,'Kp',-1);mono('h',8,'Km',-1)
 if kind=='purchased':ops.extend([['CLEAR','v'+str(i)] for i in range(112)])
 return ops

def check_exit_program(m,kind,ops):
 # Free signed monomial words retain the source index and operator order.
 def reduce(word):
  out=[]
  for x in word:
   if out and out[-1]==(x[0],-x[1]):out.pop()
   else:out.append(x)
  return tuple(out)
 def app(row,*word):
  out={}
  for (s,w),c in row.items():
   key=s,reduce(word+w);out[key]=out.get(key,F(0))+c
  return {k:v for k,v in out.items() if v}
 names=['x'+str(i) for i in range(112)]+['y'+str(i) for i in range(112)]+['h'+str(k) for k in range(8)]
 names+=['b'+str(k) for k in range(8)] if kind=='compressed' else ['v'+str(i) for i in range(112)]
 original={name:{(name,()):F(1)} for name in names};rows={k:dict(v) for k,v in original.items()};counts=Counter()
 for e in ops:
  op,dst=e[:2];need(dst in rows,'actual exit field ID');counts[op]+=1
  if op=='CLEAR':need(kind=='purchased' and dst.startswith('v'),'CLEAR only owned observation');rows[dst]={}
  elif op=='COPY':need(kind=='purchased' and not rows[dst] and e[2] in rows,'COPY owned zero');rows[dst]=dict(rows[e[2]])
  elif op=='H1':rows[dst]=app(rows[dst],('Q',1))
  elif op=='ADD':need(dst!=e[2] and e[2] in rows,'distinct exit ADD');rows[dst]=plus(rows[dst],rows[e[2]],F(e[3]))
  elif op=='MONOMIAL':need(e[2].startswith(('Kp','Km')) and e[3] in (-1,1),'source signed monomial');rows[dst]=app(rows[dst],(e[2],e[3]))
  else:raise ValueError('unknown exit instruction')
 expected={k:dict(v) for k,v in original.items()};ho=[]
 for k in range(8):
  h=app(original['h'+str(k)],('Q',1))
  if kind=='compressed':h=plus(h,original['b'+str(k)])
  else:
   for i in range(112):
    if m[k][i]:
     value=app(original['y'+str(i)],('Q',1)) if kind=='purchased' else original['v'+str(i)]
     h=plus(h,app(value,('Km'+str(k),-1),('Kp'+str(i),1)),F(m[k][i],2))
  ho.append(h);expected['h'+str(k)]=h
 for i in range(112):
  for k in range(8):
   if m[k][i]:expected['x'+str(i)]=plus(expected['x'+str(i)],app(ho[k],('Kp'+str(i),-1),('Km'+str(k),1)),F(-m[k][i],2))
 if kind=='purchased':
  for i in range(112):expected['v'+str(i)]={}
 need(rows==expected,'all exit inputs, borrowed values and owned returns')
 expected_counts={'compressed':{'H1':8,'ADD':456,'MONOMIAL':240},'full_response':{'H1':8,'ADD':896,'MONOMIAL':464},'purchased':{'H1':120,'ADD':896,'MONOMIAL':464,'COPY':112,'CLEAR':224}}
 need(dict(counts)==expected_counts[kind],'literal complete exit census')
 payload=json.dumps(ops,separators=(',',':')).encode()
 return {'operation_counts':dict(counts),'literal_operations':len(ops),'program_payload_sha256':sha256(payload).hexdigest(),'all_adapter_input_columns_checked':len(names)}

def compute():
 pins=json.loads((HERE/'SOURCES.json').read_text())
 for p in pins['files']:
  if p['usage']=='input':need(sha256((ROOT/p['path']).read_bytes()).hexdigest()==p['sha256'],'changed input '+p['path'])
 normal=json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
 provider=json.loads((HERE/'inputs/PROVIDER.json').read_text())
 controller=json.loads((ROOT/'research/joint-helper-lattice/CONTROLLER.json').read_text())
 m=normal['mode_columns'];need(len(m)==8 and all(len(r)==112 for r in m),'8 by 112 modes')
 need(all(x in (-1,0,1) for r in m for x in r),'signed mode entries')
 need([[sum(a*b for a,b in zip(r,s)) for s in m] for r in m]==[[56*(i==j) for j in range(8)] for i in range(8)],'M transpose M = 56 I')
 kt=[table(p['K_word']) for p in normal['ports']]
 mt=[table(p['input_K']['literal_word']) for p in provider['mode_boundaries']]
 need(len(kt)==112 and len(mt)==8,'120 literal physical maps')
 identity=[(i,0) for i in range(512)]
 need(all(compose(inverse(t),t)==identity for t in kt+mt),'all signed inverse products')
 w=[[compose(inverse(kt[i]),mt[k]) for i in range(112)] for k in range(8)]
 z=[[compose(inverse(mt[k]),kt[i]) for i in range(112)] for k in range(8)]
 need(all(z[k][i]==inverse(w[k][i]) for k in range(8) for i in range(112)),'Z = W adjoint')
 v,zv=experiment(m,w,z,0);g0=residual_gram(v,zv);need(g0==[[0]*8 for _ in range(8)],'zero-address false positive')
 # A one-stage absolute-phase mismatch preserves all address permutations.
 badw=[[list(t) for t in row] for row in w]
 for k in range(8):badw[k][0]=[(a,(ph+1)%4) for a,ph in badw[k][0]]
 bv,bz=experiment(m,badw,z,0)
 try:phase_rejected=residual_gram(bv,bz)!=g0
 except ValueError:phase_rejected=True
 need(phase_rejected,'absolute-phase-only stage mutation rejected')
 v,zv=experiment(m,w,z,1);gram=residual_gram(v,zv);det,pivots=determinant(gram)
 need(gram[0][0]==F(173,14),'nonzero-address physical witness')
 need(det==F(1389039784345493055,26985857024),'full-rank eight-mode residual')
 successor=json.loads((HERE/'inputs/SUCCESSOR-CONTROLLER.json').read_text())
 need(successor['physical_events'][5:19]==controller['physical_events'][1:15],'successor preserves both actual query contacts')
 trace=chronology(controller)
 trace['successor_event_indices_inclusive']=[5,18]
 trace['successor_clip_is_identical']=True
 try:chronology(controller,wrong_query=True)
 except ValueError:pass
 else:raise ValueError('accepted reversed query')
 programs={kind:exit_program(m,kind) for kind in ('compressed','full_response','purchased')}
 adapter_checks={kind:check_exit_program(m,kind,ops) for kind,ops in programs.items()}
 bad=[e[:] for e in programs['purchased']];bad.pop(next(i for i,e in enumerate(bad) if e[0]=='CLEAR'))
 try:check_exit_program(m,'purchased',bad)
 except ValueError:pass
 else:raise ValueError('accepted uncleared borrowed observation input')
 return {'schema_version':1,'status':'PASS_TWO_GENERATION_COUPLED_QUERY_TRANSPORT',
  'scope':'First two backward FULLs and following thin consumers. No complete supplier or kappa.',
  'physical_witness':{'fiber_width':1,'global_address_bits':17,'input_address':1,'input_modes':8,
   'zero_address_residual_rank':0,'nonzero_address_residual_Gram':[[str(x) for x in r] for r in gram],
   'positive_elimination_pivots':list(map(str,pivots)),'determinant':str(det),'residual_rank':8,
   'conclusion':'No linear T, including arbitrary address operators, satisfies W3 T = D1 W1.'},
  'chronology':trace,'exit_contract':exit_contract(m),'literal_exit_program_checks':adapter_checks,'complete_recursive_screen':budget(provider,controller),
  'controls':['120 signed monomial inverse identities','Z = W adjoint','M transpose M = 56 I',
   'zero-address acceptance and nonzero-address rejection','absolute-phase-only stage mutation rejected','wrong chronological query rejected','dirty response rejected','wrong repair sign rejected','missing owned observation initialization rejected'],
  'provider_native_replay':'Not run; source endpoint is an explicit premise.','new_kappa':None}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');ap.add_argument('--emit-exits',type=Path);args=ap.parse_args()
 result=compute();path=HERE/'RESULT.json'
 if args.write_result:path.write_text(json.dumps(result,indent=2)+'\n')
 else:need(json.loads(path.read_text())==result,'result does not reproduce')
 if args.emit_exits:
  m=json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())['mode_columns']
  args.emit_exits.write_text(json.dumps({kind:exit_program(m,kind) for kind in ('compressed','full_response','purchased')},indent=2)+'\n')
 print(result['status'])

if __name__=='__main__':main()
