import pathlib,sys,json,itertools,importlib.util,hashlib
P=pathlib.Path('/tmp/pr-efficient1300');pkg=P/'sources/2274/research/three-total-classical-configs';sys.path.insert(0,str(pkg/'lib'));from classical import pappus,det3
sp=json.load(open(pkg/'data/special.json'));out=[]
for r in sp['configs']['pappus']['realisations']:
 c=pappus(**{k:tuple(v)for k,v in r['params'].items()});inc=set(map(tuple,c['incidences']));pn=c['pnames'];ln=c['lnames'];ec=[];el=[]
 for t in itertools.combinations(range(9),3):
  if det3(*[c['points'][i]for i in t])==0 and not any(all((pn[i],l)in inc for i in t)for l in ln):ec.append(list(t))
  if det3(*[c['lines'][j]for j in t])==0 and not any(all((p,ln[j])in inc for j in t)for p in pn):el.append(list(t))
 assert ec==r['extra_point_triples'] and el==r['extra_line_triples']
 out.append({'params':r['params'],'extra_point_triples':ec,'extra_line_triples':el})
assert len(out)==12
result={'status':'PASS','number':2274,'head':json.load(open(P/'2274.json'))['headRefOid'],'scope':'Independently recompute every reported special-realization extra-triple signature from exact determinants and incidence lists; no claim the parameter grid covers all rational realizations.','signatures':out}
(P/'combined-2274-signatures.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS all 12 actual signatures')
