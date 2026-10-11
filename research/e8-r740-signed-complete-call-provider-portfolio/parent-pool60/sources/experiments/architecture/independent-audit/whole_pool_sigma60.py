from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import gzip,json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2];P=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';B=ROOT/'experiments/architecture/pr454-signed-extra-v4/with-prefix60/global';rd=lambda p:json.loads(p.read_text())
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cols(a):return list(zip(*a))
T=json.loads(gzip.decompress((P/'GLOBAL-TEMPLATE.json.gz').read_bytes()));old=rd(B/'hosted/HOSTED-SIGMA.json');F=rd(B/'signed/records/frames.json')['frames'];st=rd(B/'signed/records/249-states.json')['initial'];G=rd(P/'GEOMETRY.json');src={}
for fid,r in old['source_orthogonal_completions'].items():
 C=cols([[Q(x)for x in row]for row in r['matrix']]);f=F[fid]
 assert all(dot(a,b)==int(i==j)for i,a in enumerate(C)for j,b in enumerate(C))
 assert C[:f['dim']]==[tuple(Q(x,2)for x in row)for row in f['B']]
 assert r['ordering']==list(range(f['dim'],8))+list(range(f['dim']))
 D={}
 for k,c in enumerate(C):
  nz=[j for j,x in enumerate(c)if x];assert len(nz)==1 and abs(c[nz[0]])==1;D[k]=(nz[0],c[nz[0]])
 src[fid]=(D,r['ordering'])
ports={}
for p in G['ports']:
 C=[tuple(Q(x,2)for x in p['q'])]+cols([[Q(x)for x in row]for row in p['complement_columns']]);assert all(dot(a,b)==int(i==j)for i,a in enumerate(C)for j,b in enumerate(C));ports[p['port']]=C
idle={e['idx']:e for e in T['schedule']if e['kind']=='idle'};seen=defaultdict(set);cache={};digest=hashlib.sha256();n=0
for i,cp,off,w,stage,h in T['hosting']['slots']:
 helper=h%740;fid=str(st[str(240+helper)]);e=idle[i];start=1 if e['source_level']==-1 else 8+7*e['source_level'];stop=8+7*e['target_level'];target=list(range(start,stop))[off:off+w];assert len(target)==w==8-F[fid]['dim']
 signature=(i,cp%120,off,w,fid)
 if signature not in cache:
  D,order=src[fid];so=order+list(range(8,78));to=target+[j for j in range(78)if j not in target];S=[None]*78
  for k,saxis in enumerate(so):
   physical,sign=D[saxis]if saxis<8 else(saxis,Q(1));taxis=to[k];v=ports[cp%120][taxis]if taxis<8 else tuple(Q(j==taxis)for j in range(78));assert S[physical]is None;S[physical]=tuple((j,str(sign*x))for j,x in enumerate(v)if x)
  assert None not in S;cache[signature]=tuple(S)
 key=cache[signature];family=(stage,e['pair'],cp);assert key not in seen[family];seen[family].add(key)
 digest.update(json.dumps([i,cp,off,w,stage,h,hashlib.sha256(repr(key).encode()).hexdigest()],separators=(',',':')).encode()+b'\n');n+=1
assert n==65120
out={'status':'PASS_INDEPENDENT_ALL65120_WHOLE_OWNER_POOLED_RATIONAL_SIGMA_AND_COVER_INJECTION','selected_helper_owners':n,'unique_source_slot_port_maps':len(cache),'selected_sigma_hash_stream':digest.hexdigest(),'all78_columns_reconstructed':True,'source_frame_basis_count':len(src),'port_charts':len(ports),'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [P/'GLOBAL-TEMPLATE.json.gz',P/'GEOMETRY.json',B/'hosted/HOSTED-SIGMA.json',B/'signed/records/frames.json',B/'signed/records/249-states.json']},'proof':'Source completions are signedcoordinatebases; targetcommonportbasis exactorthogonal, reorderedcolumns define rationalO78 sigma and transposeinverse. Wholeactualhelperresidualmaps toselectedpendinginterval. Distinctfull78columnsigma atfixedstage/ownerfamily(cp includesOWNERrep) imply distinct d*sigma^-1 for eachinvertibleFULLcoverd. Pairwise residualintervals within eachchild are separatelychecked byassignmentgate; samefamily Dfactorsand remainder completeparentprojector. Sourceframe orderdeterminedbyactualown60records, invocationrep excludedfromhelperindexonlybecauseunchangedlocalprograms useidenticalframes.','scope':'Exact finitegeometry/cover injection. Wholephysicaldirtyslot/compiler/commonprime/precision/tape interfaces conditional; arbitrary correlateddirt handled bycompleteinvocation endpoint and stagecutlemma, not by independence.'}
(O/'WHOLE-POOL60-BIT-SIGMA.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(cache))
