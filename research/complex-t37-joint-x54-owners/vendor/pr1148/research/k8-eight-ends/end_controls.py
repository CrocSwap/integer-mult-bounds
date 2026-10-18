import gzip,json,copy,contextlib,io,importlib.util,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
s=importlib.util.spec_from_file_location('a',ROOT/'research/gauge44-slots/independent/audit_local.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
w=json.loads(gzip.decompress((P/'FULL-WORD.json.gz').read_bytes()));recipe=json.loads((P/'RECIPE.json').read_text());results=[]
with tempfile.TemporaryDirectory(prefix='k8-eight-controls-') as d:
 d=Path(d)
 for q,old,new in recipe['ends']:
  touching=[(ti,ci,fr) for ti,(ci,fr) in enumerate(w['early_cleanup']) if q in a.registers(w['cleanup'][ci])];assert touching
  bchanged=[(i,o,n) for i,o,n in recipe['B'] if q in a.registers(w['B'][i])];assert bchanged
  for label in ['missing-tail','rank6-end','rank8-read','bad-restore']:
   z=copy.deepcopy(w)
   if label=='missing-tail':z['early_cleanup'].pop(touching[0][0])
   elif label=='rank6-end':z['helper_final'][str(q)]=new[:-1]
   elif label=='rank8-read':i,o,n=bchanged[0];z['B'][i][-1]=o
   else:
    e=z['cleanup'][touching[0][1]]
    if e[0]=='add':e[3]=-e[3]
    else:e[2]*=2
   raw=d/'WORD.json.gz';raw.write_bytes(gzip.compress(json.dumps(z).encode()))
   try:
    with contextlib.redirect_stdout(io.StringIO()):a.run(raw,d/'AUDIT.json',ROOT)
   except RuntimeError as e:results.append(dict(helper=q,mutation=label,status='REJECTED',reason=str(e)))
   else:raise AssertionError(('escaped',q,label))
(Path(__import__('sys').argv[1])).write_text(json.dumps(dict(status='PASS_EIGHT_ENDS_32_NEGATIVE_CONTROLS',rejected=results),indent=2)+'\n');print('PASS',len(results),'negative controls')
