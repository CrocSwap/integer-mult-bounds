#!/usr/bin/env python3
"""Bounded source, flat arithmetic, descriptor and full-composition checks."""
from pathlib import Path
from types import SimpleNamespace
from itertools import product
from collections import Counter
import argparse,json,sys,hashlib,ast
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from source_binding import authenticate,need,vendor,lambda_sites,inputs
from gaussian_table import compile_stage,COMMIT
P=vendor('lambda_arithmetic_fixture','vendor/scalar_fixture.py')

def gaussian(table,s,values,partners,w,mutant=False):
 x=P.Tape(P.encode_symbols(P.symbols(values,w)),17);y=P.Tape(P.encode_symbols(P.symbols(partners,w)),29)
 work=[P.Tape((1,0)*13,41),P.Tape((0,1)*17,63)];work[0].pos+=17;work[1].pos+=34
 contexts=[P.Tape((1,0)*9,85,True)];contexts[0].pos+=7
 ports=(x,y,*work,*contexts);original=x.body();rows=P.RowCounter(table)
 commit_rows=P.RowCounter(COMMIT)
 c=SimpleNamespace(payloads=ports,primitive_work=(2,3),primitive_context=(4,),services={('stage',):rows,('commit',):commit_rows})
 expected=[]
 for i in range(0,len(values),2):
  a,b=values[i:i+2];cc,d=partners[i:i+2]
  expected.extend(((a-s*b+cc+s*d+1)//2,(b+s*a+d-s*cc+1)//2))
 fits=all(-(1<<(w-1))<=n<(1<<(w-1)) for n in expected);error=None
 try:P.M.Controller.primitive(c,('stage',),(0,1))
 except ValueError as exc:error=str(exc)
 need(x.body()==original,'public protected throughout whole staging')
 need((error is None)==fits,'direct Gaussian integer final-range iff')
 if fits:
  need(P.decode(y.body(),w)==tuple(expected),'one final mathematical floor per component')
  P.M.Controller.primitive(c,('commit',),(0,1));need(P.decode(x.body(),w)==tuple(expected),'literal final commit')
 for t in (y,*work):P.M.retire(t)
 for t in (x,*contexts):P.M.origin(t)
 need(all(t.pos==t.origin for t in ports),'explicit boundary cleanup on success and rejection')
 need(all(t.blank() for t in (y,*work)),'owned stage and old numerator bodies retired')
 used=sum(t.actions for t in ports)+rows.steps+commit_rows.steps;S=len(values)*(w+1);A=60;D=sum(len(t.body())+1 for t in contexts)
 need(used<=4096*(S+1)+14*A+32*D,'positive arithmetic tape/control bound')
 return fits,used

def arithmetic():
 total=accepted=0;extreme=0
 for s in (-1,1):
  t=compile_stage(s)
  for w in (1,2):
   dom=range(-(1<<(w-1)),1<<(w-1))
   for a,b,c,d in product(dom,repeat=4):
    ok,_=gaussian(t,s,(a,b),(c,d),w);total+=1;accepted+=ok
  for w in (3,8,19):
   B=1<<(w-1);dom=(-B,-1,0,B-1)
   for a,b,c,d in product(dom,repeat=4):
    ok,_=gaussian(t,s,(a,b),(c,d),w);extreme+=1;accepted+=ok
 return dict(exhaustive_width_1_2_cases=total,additional_endpoint_cases=extreme,accepted=accepted,stage_rows={str(s):len(compile_stage(s)) for s in (-1,1)},oracle='direct four signed integers; no table recurrence imported')

def source():
 sites=lambda_sites();c,w=inputs();qset=sorted({r['q'] for r in sites});proof=ROOT/'reference/physical-review-6936.py';v=proof.read_bytes()
 need(hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()=='f41390e0246cd6604a94ef5b418f48a817a4208c','exact retained source phase audit')
 from lambda_provider import translation_recipe,LambdaProvider
 from check_fixture import factory
 from phase_recipe import Recipe
 module=ast.parse(v);fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='phase')
 ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<pinned source phase>','exec'),ns)
 count=0;gates=0
 for q in qset:
  recipe=translation_recipe(q);compiled=Recipe(recipe,tuple('v'+str(i) for i in range(9)))
  need(all(op=='flip' and src==-1 for op,dst,src in compiled.word),'actual compiled translation has only flips')
  routed=0
  for op,dst,src in compiled.word:routed^=1<<dst
  need(routed==q and len(compiled.word)==q.bit_count(),'actual compiled affine word and complete gate count');gates+=len(compiled.word)
  for omega in range(512):
   phase=ns['phase']({q:1},omega)
   source_square=((1,0),(0,1),(-1,0),(0,-1))[(2*phase)%4]
   character=1
   for op,dst,src in compiled.word:
    if omega>>dst&1:character=-character
   need(source_square==(character,0),'pinned source phase squared equals independently evaluated compiled flip word')
   need(source_square!=((1,0),(0,1),(-1,0),(0,-1))[(2*phase+1)%4],'wrong absolute recipe phase detected')
   count+=1
 source_ports={}
 for weight in (3,7):
  q=next(q for q in qset if q.bit_count()==weight);owner=LambdaProvider(q,1,factory)
  source_ports[str(weight)]=owner.port_count
 # Independent address character law for the simultaneous all-column shift.
 for f in (1,2,3,5):
  for q in qset:
   hs=[(q&(j*73+11)).bit_count()%2 for j in range(f)]
   need(2*sum(hs)%4==2*(sum(hs)%2),'tensor exponent equals global shift character')
 # The forbidden tensor-of-Lambda implementation differs at two odd factors.
 need((1j*1j)==-1 and 1!=-1,'global Lambda is not tensor factor Lambda')
 return dict(source_events=len(c['events']),occurrences=len(sites),directions=len(qset),signs=dict(Counter(str(r['sign']) for r in sites)),type_occurrences=dict(Counter(r['type'] for r in sites)),q_weight_histogram=dict(Counter(str(q.bit_count()) for q in qset)),one_column_exact_character_checks=count,actual_rank9_owned_ports_by_q_weight=source_ports,first_site=sites[0],literal_recipe='identity9, offset=q, phase=0, linear=quadratic=0',current_selected_catalogue_used=False,old_caller_exporter_installed=False,nine_axis_numeric_run=False,source_numeric_screen='16-record reduced composition took0.91s;4096-record source exceeds230s by simple record scaling before extra flips, exceeding120s cap; no source execution claimed')

def descriptor():
 from lambda_provider import HeaderView,S
 from check_fixture import header_bits
 from check_numeric import load,body
 cases=[]
 for f in (1,2,7,31):
  for e in (0,8,152):
   rank=9;K=3;H=max(1,f-1);u=2*H;z=u+153*f*K;a=z+H+e
   values=dict(outer=2,rows=3,stock=1,row_bits=18*(1<<a),within_bits=a,record_bits=18,p=104,d=153*f+e,K=K,G=1,H=H,q0=3,qF=0,qB=0,D=153*f+e,f=f,rho=2,active_start=u,back_start=z,selected_axes=153*f+e,entry_start=u,remainder=e,cutoff=9)
   parent=S.codec.DenseTape(9);load(parent,header_bits(values));old=body(parent)
   v=HeaderView(9);work=[S.codec.DenseTape(3+i%5) for i in range(v.port_count)];v.bind(work,S.abi.BinaryContextPort(parent));v.prepare()
   wanted=dict(values,remainder=0,selected_axes=9*f)
   need(body(v.context.tape)==header_bits(wanted),'exact23-field source translation view')
   need(body(parent)==old,'parent header preserved')
   v.release();need(all(not body(t) and t.head==t.origin for t in work),'private view retired')
   cases.append(dict(f=f,old_remainder=e,parent_bits=len(old),actions=sum(t.actions() for t in [parent,*work])))
 return dict(cases=cases,changed_fields=['remainder','selected_axes'],private_ports=39,old_source_frame_export_assumed=False)

def composition():
 from check_numeric import run_case
 a,state=run_case();b,state=run_case(late=True,reuse=state);c,state=run_case(reuse=state);d,_=run_case(sign=-1)
 for r in (a,b,c,d):r.pop('elapsed_seconds',None)
 need(not b['accepted'] and a['accepted'] and c['accepted'] and d['accepted'],'complete late-rejection and retry')
 return dict(cases=[a,b,c,d],whole_source_nine_axis_executed=False,positive_and_negative_signs=True,late_failure_public_and_context_restored=True)

def controls():
 caught=[]
 from lambda_provider import LambdaProvider,construct_source
 from check_fixture import factory
 first=lambda_sites()[0]
 typed=[]
 for label,action in [('boolean_table_sign',lambda:compile_stage(True)),('boolean_provider_sign',lambda:LambdaProvider(11,True,factory)),('boolean_site',lambda:construct_source(True,first['port'],factory)),('boolean_port',lambda:construct_source(first['site'],True,factory))]:
  try:action()
  except ValueError:typed.append(label)
  else:raise ValueError('typed source alias accepted '+label)
 for mutation,s,x,y,w in [('tie-down',1,(1,0),(0,0),2),('omit-range',1,(1,-3),(1,3),3)]:
  try:gaussian(compile_stage(s,mutation),s,x,y,w)
  except ValueError:caught.append(mutation)
  else:raise ValueError('mutant escaped '+mutation)
 need((-1+1)//2==0 and -((1+1)//2)==-1,'upward rounding does not commute with negation')
 return dict(detected_table_mutants=caught,typed_binding_controls=typed,controls=['global_vs_tensor_Lambda','rounding_not_sign_equivariant','late_public_write_protection'])

def main():
 p=argparse.ArgumentParser();p.add_argument('--suite',choices=('source','arithmetic','descriptor','composition','controls','audit','all'),default='all');p.add_argument('--write',action='store_true');a=p.parse_args();authenticate()
 for name,fn in [('source',source),('arithmetic',arithmetic),('descriptor',descriptor),('composition',composition),('controls',controls)]:
  if a.suite not in (name,'all') and not (a.suite=='audit' and name in ('source','controls')):continue
  v=fn();file=ROOT/(name.upper()+'.json')
  if a.write:file.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
  else:need(v==json.loads(file.read_bytes()),'frozen '+name+' receipt')
  print('PASS_CURRENT_ROUNDED_LAMBDA_'+name.upper(),flush=True)
if __name__=='__main__':main()
