"""Local arithmetic composition of PR1536 endpoint engines with a deeper positive-margin outer witness.
Contribution dataisfire, substantial OpenAI Codex assistance. Inherited constructions and methods retain credit.
No trusted source is edited; derived expected values are followed by the original strict assembly replay.
"""
import os,sys,json,hashlib,importlib.util,copy,argparse,subprocess
from pathlib import Path
from fractions import Fraction as Q
from decimal import Decimal,localcontext
assert __debug__;sys.set_int_max_str_digits(0)
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];P=ROOT/'research/gmx-t74-ep200r'
ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--base-native-from',type=Path);ap.add_argument('--extra-native-from',type=Path);args=ap.parse_args();work=args.work.resolve();assert not work.exists() and not work.is_relative_to(HERE);work.mkdir();out=work/'candidate'
def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
own=json.loads((HERE/'MANIFEST.json').read_text());assert set(own)=={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
for name,h in own.items():assert file_sha(HERE/name)==h,name
pins=json.loads((HERE/'SOURCES.json').read_text());assert file_sha(P/'MANIFEST.json')==pins['parent_manifest_sha256']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',PYTHONUTF8='1')
for key in ['PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC']:env.pop(key,None)
cmd=[sys.executable,'-B',str(P/'verify.py'),'--work',str(work/'parent')]
for key,path in [('base',args.base_native_from),('extra',args.extra_native_from)]:
 if path:cmd.extend(['--'+key+'-native-from',str(path.resolve())])
with (work/'parent.log').open('w') as log:proc=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
assert proc.returncode==0,(work/'parent.log').read_text()[-4000:]
R=work
rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=rd(P/'MANIFEST.json');assert all(sha(P/k)==v for k,v in manifest.items())
parent=rd(R/'parent/RESULT.json');assert parent['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
assert parent['manifest_sha256']==pins['parent_manifest_sha256']
assert 'PASS_FINE_ENGINE_LOG_ORACLE' in (R/'parent/fine-engine-oracle.log').read_text()
assert any(x['name']=='fine-engine-oracle' and x['exit_code']==0 for x in parent['stages'])
asm=rd(R/'parent/strict/ASSEMBLY.json');spec=rd(P/'SPEC.json');b=Q(asm['complex_lower']);bc=Q(asm['conservative_complex_lower']);c=Q(asm['bit_lower']);payload=spec['geometry']['charged_prefix_bits']
up=R/'parent/parent/layout/joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold'
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
A=load('refinement_outer',up/'engines/outer.py');MF=load('refinement_mercator',P/'code/fine_mercator.py');BF=load('refinement_base_two',P/'code/fine_moment.py')
H={int(k):v for k,v in asm['complex_profile'].items()};ownerpath=R/'parent/strict/global/audit/OWNERS-AND-PROFILE.json';invoicepath=ownerpath.parent/'PREFIX-AND-INVOICE.json';owner=rd(ownerpath);invoice=rd(invoicepath)
assert owner['paid_profile']==asm['complex_profile'] and invoice['owner_audit_sha256']==sha(ownerpath)
moments=[]
for label,lower,bad in [('native',b,False),('conservative',bc,True)]:
 for z,ok in [(lower,True),(lower+Q(1,10**200),False)]:
  l,u=MF.moment(H,73,owner['live'],z,bad);ll,uu=BF.moment(73,owner['live'],list(H.items()),z)
  if bad:
   fl,fu=BF.moment(73,owner['live'],[(1,32*73*73*sum(H.values()))],z);ll+=fl/10**16;uu+=fu/10**16
  assert (u<1 and uu<1) if ok else (l>1 and ll>1)
  moments.append(dict(side=label,endpoint=str(z),accept=ok,mercator=[str(l-1),str(u-1)],base_two=[str(ll-1),str(uu-1)]))
eta=beta=Q(1,10**220);grid=Q(1,10**210);steps=82;ceil=lambda x:-(-x.numerator//x.denominator)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
def witness(lower):
 s=min(c,(1-beta)*lower)-eta/1000;seed=Q(384599,10**10);prev=seed;cuts=[]
 for n in range(1,steps+1):
  a=s-(s-seed)*s**n;gap=min(s-a,1-a-s,1-a-s*(1-prev),1-s);assert prev<a<s<1-a and gap>0
  assert a==(1-s)*s+s*prev
  cutoff=max(ceil(36/gap**2),ceil(2*(4+payload)/gap));assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+payload)
  cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cutoff)));prev=a
 q=prev*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin/grid;k=Q((ticks.numerator-1)//ticks.denominator)*grid
 outer=A.assembly(prev,lower,bridge,k,eta=eta,beta=beta);assert len(outer['strict_constraints'])==47 and all(x>0 for x in outer['strict_constraints'].values());assert k<margin<=k+grid
 controls=[]
 for name,kk,ee,bb in [('next_grid',k+grid,eta,beta),('zero_eta',k,Q(0),beta),('zero_beta',k,eta,Q(0)),('unit_beta',k,eta,Q(1))]:
  try:A.assembly(prev,lower,bridge,kk,eta=ee,beta=bb)
  except AssertionError:controls.append(name)
  else:raise AssertionError(name)
 return k,cuts,outer,controls
k,cuts,outer,controls=witness(b);ck,ccuts,couter,ccontrols=witness(bc);oldk=Q(parent['kappa']);assert k>oldk
fmt=lambda x:format(Decimal(x.numerator)/Decimal(x.denominator),'f')
with localcontext() as ctx:
 ctx.prec=260;kd=fmt(k);ckd=fmt(ck)
assert Q(kd)==k and Q(ckd)==ck
out.mkdir();spec['outer_refinement']=dict(grid_digits=210,margin_digits=220,bootstrap_steps=82,endpoint_digits=200);spec['expected']['kappa']=str(k);spec['expected']['kappa_decimal']=kd;spec['expected']['conservative_kappa_decimal']=ckd;(out/'data').mkdir();(out/'data/SPEC.json').write_text(json.dumps(spec,indent=2))
recipe=spec['pivot_swap']['recipe'];target=(out/recipe).resolve();assert target.is_relative_to(out.resolve());target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((P/recipe).read_bytes());assert sha(target)==spec['pivot_swap']['sha256']
# Replay every original admission/invoice/moment/bootstrap/outer assertion in strict mode.
os.environ['WITNESS_SPEC']=str(out/'data/SPEC.json');os.environ['GAIN_PR564_SOURCE']=str(up)
for key in ['WITNESS_DISCOVER','WITNESS_RECORD','PYTHONOPTIMIZE']:os.environ.pop(key,None)
sys.path.insert(0,str(P/'code'));original=load('unchanged1510_assembly',P/'code/assemble.py');actual=original.assemble(owner,invoice,sha(ownerpath),sha(invoicepath));assert Q(actual['kappa'])==k and actual['bootstrap']==cuts and actual['controls']==controls and Q(actual['conservative_kappa'])==ck
(out/'ASSEMBLY.json').write_text(json.dumps(actual,indent=2))
assert all(sha(P/key)==v for key,v in manifest.items())
result=dict(status='PASS_LOCAL_PR1536_REPAIRED_ENDPOINT200_OUTER210_COMPOSITION',kappa=str(k),kappa_decimal=kd,parent_kappa=str(oldk),gain=str(k-oldk),parent_sha='527d7623009f295b7311e98ae36f5e2fbdbbc3e5',parent_manifest_sha256=sha(P/'MANIFEST.json'),original_assembly_sha256=sha(P/'code/assemble.py'),physical_changes=False,parameters=spec['outer_refinement'],moments=moments,controls=controls,strict_constraints=47,fine_engine_oracle_sha256=sha(R/'parent/fine-engine-oracle.log'),native_reuse=parent['native_reuse'],native_scope='Full immutable PR1536 verifier: native providers freshly rebuilt by default; optional explicit source-bound reuse',proof_scope=parent['scope'],source_hashes={str(p.relative_to(R)):sha(p) for p in [ownerpath,invoicepath,R/'parent/RESULT.json']})
expected=rd(HERE/'EXPECTED.json');assert result['kappa']==expected['kappa'] and result['kappa_decimal']==expected['kappa_decimal'];assert result['parameters']==expected['parameters'];assert result['controls']==expected['controls']
assert rd(HERE/'CLAIM.json')['kappa']==result['kappa']
(out/'RESULT.json').write_text(json.dumps(result,indent=2))
check=[sys.executable,'-B',str(HERE/'check_outer_closed.py'),'--assembly',str(out/'ASSEMBLY.json'),'--legacy',str(HERE/'inputs/LEGACY-ASSEMBLY.json'),'--spec',str(out/'data/SPEC.json'),'--out',str(out/'INDEPENDENT-OUTER.json')]
with (work/'independent.log').open('w') as log:proc=subprocess.run(check,env=env,stdout=log,stderr=subprocess.STDOUT)
assert proc.returncode==0,(work/'independent.log').read_text()[-4000:]
assert rd(out/'INDEPENDENT-OUTER.json')['kappa']==result['kappa']
for name,h in own.items():assert file_sha(HERE/name)==h,name
(work/'RESULT.json').write_text(json.dumps(dict(status='PASS_T74_REPAIRED_OUTER210_COMPLETE_FINITE_ADMISSION',kappa=result['kappa'],kappa_decimal=result['kappa_decimal'],parent_manifest_sha256=pins['parent_manifest_sha256'],native_reuse=parent['native_reuse'],controls=parent['controls'],outer_controls=result['controls'],independent_controls=rd(out/'INDEPENDENT-OUTER.json')['rejected'],scope=parent['scope']),indent=2));print('PASS_T74_REPAIRED_OUTER210_COMPLETE_FINITE_ADMISSION');print('KAPPA',kd);print('GAIN',k-oldk)
