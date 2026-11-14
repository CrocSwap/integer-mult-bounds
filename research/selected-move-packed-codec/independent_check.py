"""Separate orchestrator review: sparse-tape interpreter and tuple-sort oracle.
Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
Only import paths/loading are adapted for this portable package.
"""
from pathlib import Path
import hashlib, importlib.util, json, sys
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('checked_codec',ROOT/'machine.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;exec(compile((ROOT/'machine.py').read_bytes(),str(ROOT/'machine.py'),'exec'),m.__dict__)
def need(x,s):
 if not x:raise ValueError(s)
def run(code,mem,heads,pc=0,cap=20000000):
 lo=heads[:];steps=0
 while steps<cap:
  ins=code[pc];steps+=1;op=ins[0]
  if op=='H':return ins[1],steps,lo
  if op=='J':pc=ins[1];continue
  t=ins[1];h=heads[t]
  if op=='R':
   pc=ins[2].get(mem[t].get(h,2),-1)
   if pc<0:return 'REJECT',steps,lo
  elif op=='W':
   need(ins[2] in (0,1,2,3),'finite alphabet')
   if ins[2]==2:mem[t].pop(h,None)
   else:mem[t][h]=ins[2]
   pc+=1
  elif op=='M':
   need(ins[2] in (-1,1),'unit move');heads[t]+=ins[2];lo[t]=min(lo[t],heads[t]);pc+=1
  else:raise ValueError('nonliteral instruction')
 raise TimeoutError('step cap')
def old(values,w):return [z for v in values for sym in [[0,0,(v>>j)&1] for j in range(w)]+[[0,1,0]] for z in sym]
def bits(values,w):return [int(c) for v in values for c in format(v,f'0{w}b')]
def supplied(payloads):
 origins=[5+2*(i%3) for i in range(43)];mem=[]
 for i,o in enumerate(origins):
  cells={o-1:3,o-3:1};cells.update({o+j:b for j,b in enumerate(payloads.get(i,[]))});mem.append(cells)
 return mem,origins[:],origins
def word(mem,i,o,n):return [mem[i].get(o+j,2) for j in range(n)]
def full(code,labels):
 a=9;w=3;r=2;n=1<<a
 h=dict.fromkeys(m.SCHEMA,0);h.update(outer=1,rows=1,within_bits=a,row_bits=n*6*r*(w+1),record_bits=6*r*(w+1),f=1,K=1,cutoff=(1<<137)+19,G=1,H=1,d=9,selected_axes=9,back_start=8)
 context=[]
 for key in m.SCHEMA:
  ds=[int(c) for c in format(h[key],'b')[::-1]];context += [1]*len(ds)+[0]+ds
 values=[(17*j+j*j+3)&7 for j in range(n*2*r)];packet=old(values,w)
 mem,heads,origins=supplied({0:packet,1:context});before=[dict(t) for t in mem]
 status,s1,lo1=run(code,mem,heads);need(status=='PACKED','entrance')
 need(mem[0]==before[0] and mem[1]==before[1],'old data/header unchanged')
 expect=bits(values,w);need(word(mem,2,origins[2],len(expect))==expect,'packed image')
 gamma=[int(c) for v in [1,r,1,1,w,h['cutoff']] for c in '0'*(v.bit_length()-1)+format(v,'b')]
 need(word(mem,3,origins[3],len(gamma))==gamma,'Gamma header')
 changed=[(v+1)&7 for v in values]
 for j,b in enumerate(bits(changed,w)):mem[2][origins[2]+j]=b
 status,s2,lo2=run(code,mem,heads,labels['EXIT']);need(status=='DONE','return')
 need(word(mem,0,origins[0],len(packet))==old(changed,w),'changed output old-owner image')
 need(mem[1]==before[1],'descriptor return')
 for i in range(43):
  need(heads[i]==origins[i] and min(lo1[i],lo2[i])>=origins[i]-1,'origin/guard')
  need(mem[i].get(origins[i]-3)==1 and mem[i].get(origins[i]-1)==3,'opaque exterior')
  if i>=2:need(mem[i]==before[i],'all private histories erased')
 return {'steps':s1+s2,'V_old':len(packet),'E':len(context),'width':w,'coefficients':r}
def shuffle():
 b=m.Builder();b.label('ENTER');b.shuffle();b.halt('PACKED');b.label('EXIT');b.shuffle(True);b.halt('DONE');code,labels=b.finish();receipts=[]
 for a,u,K,rho,g,rows in [(8,1,2,1,3,2),(9,0,3,2,3,1),(7,2,1,0,4,3)]:
  L=a+2;N=1<<a;records=[format(j,f'0{L}b') for j in range(rows*N)];payload=[int(c) for rec in records for c in rec]
  guides={'G':g,'K':K,'KM1':K-1,'PREFIX':rows*(1<<u),'HALF':L*(1<<(a-u-1)),'RUN':L*(1<<(a-u-rho-1)),'CHUNKS':1<<rho}
  data={m.PORT['PACK']:payload};data.update({m.PORT[k]:[1]*v for k,v in guides.items()});mem,heads,origins=supplied(data);before=[dict(t) for t in mem]
  status,s1,_=run(code,mem,heads);need(status=='PACKED','shuffle entrance')
  selected=[u+k*K+rho for k in range(g)];order=list(range(u))+selected+[p for p in range(u,a) if p not in selected];expected=[]
  for row in range(rows):
   perm=sorted(range(N),key=lambda i:tuple(format(i,f'0{a}b')[p] for p in order))
   expected += [int(c) for i in perm for c in records[row*N+i]]
  need(word(mem,2,origins[2],len(payload))==expected,'tuple-sort index oracle')
  status,s2,_=run(code,mem,heads,labels['EXIT']);need(status=='DONE','shuffle exit')
  need(word(mem,2,origins[2],len(payload))==payload,'inverse exact')
  for name in ('ZERO','ONE','OUT','TMP'):need(mem[m.PORT[name]]==before[m.PORT[name]],'shuffle history')
  receipts.append({'geometry':[a,u,K,rho,g,rows],'steps':s1+s2})
 return receipts
def main():
 code,labels=m.compile_bridge();out={'machine_sha256':hashlib.sha256((ROOT/'machine.py').read_bytes()).hexdigest(),'table_sha256':m.table_digest(code),'full':full(code,labels),'shuffle':shuffle()}
 bad=list(code)
 for k,ins in enumerate(bad):
  if ins[0]=='R' and ins[1]==0 and set(ins[2])=={0,1}:bad[k]=(ins[0],ins[1],{0:ins[2][1],1:ins[2][0]});break
 else:raise ValueError('no mutation site')
 try:full(tuple(bad),labels)
 except (ValueError,TimeoutError):out['codeword_branch_mutation']='detected'
 else:raise ValueError('mutation survived')
 print(json.dumps(out,indent=2));print('PASS_INDEPENDENT_CODEC_SPARSE_TAPE')
if __name__=='__main__':main()
