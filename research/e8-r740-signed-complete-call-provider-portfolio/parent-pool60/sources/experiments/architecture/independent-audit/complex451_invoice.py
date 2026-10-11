from pathlib import Path
from fractions import Fraction as Q
import json,gzip,hashlib,importlib.util,math
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/complex-direct8-eleven451';rd=lambda p:json.loads(p.read_text());g=rd(P/'hosted/GLOBAL.json');inv=rd(P/'FINITE-INVOICE.json');t=json.loads(gzip.decompress((P/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()));primitive=rd(O/'COMPLEX451-PRIMITIVE.json');H=rd(O/'COMPLEX451-GEOMETRY.json')['paid_profile'];H={int(r):n for r,n in H.items()};m=89;W=9600;physical=10178;Rhelpers=560;E=sum(H.values());mass=sum(r*n for r,n in H.items());assert m*W-mass==3264
# Count macro and child events from actual serialized local programs.
sc={d:sum(e[0]=='scalar'for e in es)for d,es in t['local_programs'].items()};children={d:sum(e[0]in ['climb','center']for e in es)for d,es in t['local_programs'].items()};assert len(set(children.values()))==1
comp=64*(m+1)**3;adapters=16*(max(sc.values())+children['forward']+240+Rhelpers+16)+64*m
local=max(x['real_primitives']for x in primitive['orientations'].values())+adapters*comp
scalar=8*(6*primitive['orientations']['forward']['real_primitives']+5*primitive['orientations']['backward']['real_primitives']);bridges=6*4*120*8;shifts=5*120*8;moves=2*5*120*8
items=4*120*8*11+2*120*8*11+4*11*8*560+(6*5-4)*120*8+bridges+shifts+moves+W+physical
outside=8*items+64*m;fee=scalar+bridges+shifts+moves+W+(11*8*adapters+outside)*comp+64*physical
assert (adapters,local,scalar,fee)==(inv['adapters'],inv['local_bound'],inv['scalar_primitives'],inv['pervertex'])
group=2**(44**2)*math.prod(2**(2*i)-1 for i in range(1,45));stock=group*physical;logical=group*fee+64;s=group*mass;router=comp*(logical+1)*(stock+1)**2;literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*m
assert stock.bit_length()==3929 and router<1<<30000 and literal<1<<100000;B=s+(1<<100000);assert 32*m*B**2<1<<210000 and 2*B+18<1<<210000
# Every nine recursion steps shrink by at least factor16, so depth<=9/4 log2(e)+9.
assert 89**9>16*64**9 and 89**9<=32*64**9;slope=Q(9,4)*3929+9909+252;add=9*3929;margin=(20161-slope)*32-add;assert slope==Q(76005,4) and margin==1751>0;assert(20161-slope)*30<add
peak=max(Q(x['cancellation_free_prefix'])for x in primitive['orientations'].values());assert peak<2**33;bound=11*33+24+6;assert bound==393<512;assert(fee+1)**3*(E+1)**3<2**1024
eng=R/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines/base_two_moment.py';sp=importlib.util.spec_from_file_location('independent451_base',eng);M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M);nom=rd(P/'MOMENT.json');roots=[]
for side in ['lower','upper']:
 a=Q(nom[side]);lo,hi=M.moment(m,W,list(H.items()),a);x,y=M.moment(m,W,[(1,32*m*m*E)],a);lo+=x/10**16;hi+=y/10**16;assert hi<1 if side=='lower'else lo>1;roots.append(dict(side=side,rate=str(a),moment=[str(lo),str(hi)]))
out={'status':'PASS_INDEPENDENT_COMPLEX451_FINITE_INVOICE_FRACTIONAL_ROWS_AND_RATIONAL_CAP','pervertex':fee,'physical_stock_bits':3929,'row_slope':str(slope),'row_additive':add,'row_cutoff_log2':32,'row_margin':str(margin),'retained_row':20161,'prefix_bound_bits':393,'charged_prefix_bits':512,'coefficient_envelope_bits':((fee+1)**3*(E+1)**3).bit_length(),'live':W,'mass':mass,'deficit':3264,'cap_lower':str(Q(nom['lower'])),'second_engine_roots':roots,'scope':'Fractional9step/4halving depth and stockcharge rederived under inherited restored-row reserve9909+252 and smallwidth leaf cutoff. Those ancestor constants/smallleaf/allsize weightedcompiler are retainedconditional premises, not newly derived. Commonprime/precision/tape/recovery/C_full and fullouterassembly separate.','pins':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [P/'FINITE-INVOICE.json',P/'PREFIX.json',P/'MOMENT.json',P/'hosted/GLOBAL-TEMPLATE.json.gz',P/'hosted/GLOBAL.json']}};(O/'COMPLEX451-INVOICE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],fee)
