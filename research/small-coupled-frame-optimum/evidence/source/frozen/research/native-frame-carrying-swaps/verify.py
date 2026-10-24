from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import sys,json,gzip,hashlib,copy
P=Path(__file__).resolve().parent
S=P
if hashlib.sha256((S/'native_core.py').read_bytes()).hexdigest() != 'c510b8c171a57a92b2cfe2ad516cde00fa8a1148b457bb8de2197635e37f3296': raise ValueError('Retained core hash')
sys.path.insert(0,str(S));import native_core as V
raw=gzip.decompress((S/'SOURCE-WORD.json.gz').read_bytes())
V.need(hashlib.sha256(raw).hexdigest()==V.SOURCE_SHA,'Frozen source payload')
a=json.loads(raw);c=a['canonical']
def space(b):
 s={0}
 for v in b:s|={x^v for x in tuple(s)}
 return s
spaces=list(map(space,c['frames']))

def construct(program):
 p=[copy.deepcopy(e)for e in program if e[0]!='climb'];cur=c['start'][:];out=[];count=0;i=0;unequal=0
 def climb(r,f):
  old=cur[r]
  if old!=f:
   V.need(spaces[old]<spaces[f],'Nested constructed transport')
   out.append(['climb','retimed',r,old,f,len(c['frames'][f])-len(c['frames'][old])]);cur[r]=f
 while i<len(p):
  es=p[i:i+3];tr=None
  if len(es)==3 and all(e[0]=='scalar'and e[1][0]=='add'and all(r[0]=='L'for r in e[1][1:3])for e in es):
   g,h,k=[e[1]for e in es];aa,bb,dd=[Q(z[3],z[4])for z in [g,h,k]]
   if g[1]==h[2]and g[2]==h[1]and g[1:3]==k[1:3]and aa*bb==-1 and aa==dd:tr=g[1][1],g[2][1],aa
  if tr:
   d,s,coef=tr;before=[cur[d],cur[s]];cur[d],cur[s]=cur[s],cur[d]
   out.append(['weighted_swap',d,s,str(coef),str(-1/coef),before,[cur[d],cur[s]]]);count+=1;unequal+=before[0]!=before[1];i+=3;continue
  e=p[i]
  if e[0]=='scalar':
   g,f=e[1:]
   if g[0]=='scale'and g[1][0]=='L':e[2]=cur[g[1][1]]
   else:
    for r in g[1:3]if g[0]in('add','copy')else g[1:2]:
     if r[0]=='L':climb(r[1],f)
  elif e[0]=='warp':climb(e[1][1],e[3]);cur[e[1][1]]=e[4]
  out.append(e);i+=1
 for r,f in enumerate(c['final']):climb(r,f)
 return out,count,unequal

def replay(program,back=False):
 rows={i:V.identity(i)for i in range(632)};rows[632]={};cur=c['start'][:]+[None];paid=Counter()
 def reg(r):return r[1]+(632 if r[0]=='C'else 0)
 for e in program:
  if e[0]=='weighted_swap':
   _,d,s,aa,bb,before,after=e
   V.need([cur[d],cur[s]]==before,'Swap actual incoming frames')
   rd,rs=rows[d],rows[s]
   rows[d]={k:Q(aa)*v for k,v in rs.items()};rows[s]={k:Q(bb)*v for k,v in rd.items()}
   cur[d],cur[s]=cur[s],cur[d];V.need([cur[d],cur[s]]==after,'Swap carries frames')
  elif e[0]=='scalar':
   g,f=e[1:];r=reg(g[1])
   if g[0]=='clear':V.need(r==632,'Owned clear');rows[r]={};cur[r]=f
   else:
    V.need(cur[r]==f,'Scalar target frame')
    if g[0]in('copy','add'):
     s=reg(g[2]);V.need(cur[s]==f,'Scalar source frame')
     if g[0]=='copy':V.need(r==632,'Owned copy');rows[r]=rows[s].copy()
     else:V.add(rows[r],rows[s],Q(g[3],g[4]))
    elif g[0]=='scale':rows[r]={k:Q(g[2],g[3])*v for k,v in rows[r].items()}
    else:raise ValueError('scalar')
  elif e[0]=='warp':
   _,role,op,f,g=e;r=reg(role);V.need(cur[r]==f,'Warp frame');rows[r]=V.warp(rows[r],op,back);cur[r]=g
  elif e[0]in('climb','center'):
   if e[0]=='climb':_,_,r,f,g,rank=e;V.need(spaces[f]<spaces[g],'Strict nested climb')
   else:_,r,f,g,rank=e;r+=632
   V.need(cur[r]==f,'Paid input frame');V.need(rank==abs(len(c['frames'][g])-len(c['frames'][f])),'Paid rank');cur[r]=g;paid[rank]+=1
  else:V.need(e[0]in('phase','adapter','residual_adapter'),'Known inherited event')
 V.need(cur[:632]==c['final']and not rows[632],'All final frames and owned clear')
 return rows,paid
res={'source_payload_sha256':V.SOURCE_SHA,'scope':'Exact normalized all-input and chronological-frame control. Inherited native physical maps remain source premises; no new kappa.'}
for back,d in [(False,'forward'),(True,'backward')]:
 source=a['programs'][d];word,count,unequal=construct(source);rows,paid=replay(word,back)
 baseline,old,_=V.replay(c,source,back)
 V.need(rows==baseline,'All 632 normalized input rows unchanged')
 V.need(all(rows[i]==V.expected(i,back)for i in range(632)),'Original specified shear and arbitrary helpers')
 V.need(paid==old,'Paid profile unchanged')
 bad=copy.deepcopy(word);e=next(e for e in bad if e[0]=='weighted_swap');e[3]=str(-Q(e[3]))
 badrows,_=replay(bad,back);V.need(badrows!=baseline,'Wrong signed swap rejected by endpoint comparison')
 bad=copy.deepcopy(word);e=next(e for e in bad if e[0]=='weighted_swap' and e[5][0]!=e[5][1]);e[6]=e[5][:]
 try:replay(bad,back)
 except ValueError as error:V.need(str(error)=='Swap carries frames','Frame mutation failure reason')
 else:raise ValueError('Missing frame carry accepted')
 res[d]={'frame_carry_mutation_rejected':True,'swaps':count,'unequal_input_frames':unequal,'paid':dict(paid),'rows_checked':632,'wrong_sign_rejected':True}
 print(d,res[d],flush=True)
if '--write' in sys.argv:
 (P/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
else:
 V.need(json.loads(json.dumps(res))==json.loads((P/'RESULT.json').read_text(encoding='utf-8')),'Committed result matches fresh replay')
 print('PASS: all-input endpoints, chronological frames, paid profile and mutation controls')

