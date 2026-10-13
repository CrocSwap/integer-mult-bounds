"""Fresh record, geometry, owner and invoice replay for the sliced/minimum-frame candidate.
Uses pinned PR493/510 tools without weakening checks; records the inherited vacuous-route adaptation.
"""
from pathlib import Path
import subprocess,os,json,sys,time,hashlib
R=Path(__file__).resolve().parent;O=R/'trace541-frozen-admission';assert not O.exists();O.mkdir();(O/'tmp').mkdir();(O/'bin').mkdir();(O/'logs').mkdir()
P=R/'source493-review';C=P/'code';B=C/'bit';CK=B/'checkers';S=R/'bit510-review/research/e8-r480-nine-stage';VK=S/'vendor/e8-r715-eleven-stage-whole/code';W=R/'trace541-frozen-minimum/WORD.json.gz';PY=sys.executable;env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',TMPDIR=str(O/'tmp'));steps=[];start=time.monotonic()
def run(name,cmd):
 t=time.monotonic();print('START',name,flush=True)
 with (O/'logs'/(name+'.log')).open('w')as log:ret=subprocess.run(list(map(str,cmd)),cwd=O,env=env,stdout=log,stderr=subprocess.STDOUT)
 steps.append(dict(name=name,returncode=ret.returncode,seconds=time.monotonic()-t,command=list(map(str,cmd))));(O/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
 if ret.returncode:print((O/'logs'/(name+'.log')).read_text()[-5000:],flush=True);raise SystemExit('FAIL '+name)
 print('PASS',name,round(steps[-1]['seconds'],2),flush=True)
for p in [P/'MANIFEST.sha256']:
 for line in p.read_text().splitlines():
  sha,name=line.split('  ',1);assert hashlib.sha256((P/name).read_bytes()).hexdigest()==sha,name
run('export',[PY,'-B',B/'export_records.py',W,O/'records'])
run('cohort',[PY,'-B',B/'regression/stage_cohort.py',O/'records',O/'records',O/'cin',O/'cout'])
incs=['-I'+str(P/'portable-include'),'-I'+str(CK),'-I'+os.environ.get('BOOST_INCLUDE','/usr/include')]
for name,src,defs in [('legality','legality_h.cpp',['-DNCOPY=9']),('legality-default','legality_h.cpp',[]),('columns','columns_h.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=480']),('columns_k4','columns_k.cpp',['-DNCOPY=9','-DVPORTS=120','-DRHELP=480','-DKPAIRS=4'])]:
 run('compile-'+name,[os.environ.get('CXX','c++'),'-O2','-std=c++17','-DHDIM=8']+defs+incs+['-o',O/'bin'/name,CK/src])
run('legality',[O/'bin/legality',O/'cin',O/'cout',O/'cout/legality.json'])
run('columns',[O/'bin/columns',O/'cout/COHORT249-RECORDS.bin',O/'cout/columns.json'])
run('columns_k4',[O/'bin/columns_k4',O/'cout/COHORT249-RECORDS.bin',O/'cout/columns_k4.json'])
run('mutate-records',[PY,'-B',B/'mutate_records.py',O/'records',O/'cin',O/'cout',O/'bin/legality',O/'bin/columns_k4',O/'bin/legality-default'])
run('mutate-mutable-records',[PY,'-B',B/'mutate_records_mut.py',W,O/'records',O/'cin',O/'cout',O/'bin/legality',O/'bin/columns',O/'bin/columns_k4'])
run('gram',[PY,'-B',CK/'gram_frames.py',O/'records','--gram','e8ham','--h','8','--positive'])
V=O/'v9';V.mkdir();(V/'records').symlink_to(O/'records')
run('geometry',[PY,'-B',C/'nine/geometry.py','--source',P,'--out',V/'nine'])
run('parent-template',[PY,'-B',VK/'global_k.py','--word',W,'--local-check',O,'--out',V/'nine','--isometries',P/'data/eleven/residual-isometries.json'])
run('audit-adaptation',[PY,'-B',S/'code/adapt.py',VK,O/'adapted'])
run('parent-audit',[PY,'-B',O/'adapted/audit_parent_k.py','--local-check',O,'--out',V/'nine','--word',W])
run('hosted-emission',[PY,'-B',VK/'emit_k.py',V/'nine',O,V/'hosted','--selection',S/'data/selection9-r480.json','--key','bit'])
run('hosted-audit',[PY,'-B',VK/'audit_hosted_k.py',V,V/'hosted',V/'hosted/AUDIT.json'])
run('invoice',[PY,'-B',S/'code/assemble9.py',V,V/'hosted',V/'hosted/AUDIT.json',P,O/'BIT-INVOICE.json','pr484'])
x=json.loads((O/'BIT-INVOICE.json').read_text());e=json.loads((R/'trace541-frozen-minimum-price/RESULT.json').read_text());assert x['bit_profile']==e['profile'];assert x['bit']['charged_two_level_coefficient_bits']<=512 and x['bit']['row_coefficient']==18355
assert x['bit']['live']==30720 and x['bit']['hosted_residuals']==138240 and x['bit']['bank_assignments']==0
r=dict(status='PASS_FRESH_TRACE_AND_FROZEN_FRAMES_RECORDS_HOSTING_AND_INVOICE',seconds=time.monotonic()-start,word_sha256=hashlib.sha256(W.read_bytes()).hexdigest(),profile=e['profile'],kappa=e['kappa_decimal'],bit_invoice=x['bit'],steps=len(steps),scope='Fresh finite record/formal-column/geometry/template/whole-owner/invoice replay, with inherited mutation controls. Cited complex535 operator unchanged. Exact sharp-charge prospective profile now matches physically emitted audited profile and retained finite allowances. All-size supplier/compiler/realization/hosting/analytic assumptions remain conditional.')
(O/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(r,flush=True)
