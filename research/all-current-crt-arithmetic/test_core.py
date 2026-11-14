"""Read-only primary integer tests of the three new arithmetic entries."""
from pathlib import Path
import types,sys,json,random
HERE=Path(__file__).resolve().parent
def load(path,name):
 m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def need(x,s):
 if not x:raise ValueError(s)
class Tape:
 def __init__(self,cells,head):self.cells=list(cells);self.head=head
 def read(self):return self.cells[self.head]
 def write(self,s):self.cells[self.head]=s
 def step(self,d):
  need(d in(-1,1) and 0<=self.head+d<len(self.cells),'backed frame');self.head+=d
def bits(x,p):return [str((x>>i)&1) for i in range(p)]
def fixture(hw,p,x,y,alias=False,slots=(19,37,62),history=0):
 a,b,q=slots;b=a if alias else b;need(not alias or x==y,'alias fixture')
 ports=[Tape(['L']+['_']*(p+1+history)+['OUTSIDE'],1) for _ in range(64)]
 for k,v in ((a,x),(b,y)):ports[k].cells[1:p+2]=bits(v,p)+['R']
 for k in range(8):
  if k not in(a,b,q):ports[k].cells[1:p+2]=bits((17*k+3)%(1<<p),p)+['R']
 ports.extend(hw.GrantedSelector(Tape(list('10101010')+['_']*history+['EXTERIOR'],0),granted_extent=8) for _ in range(4))
 return ports,(a,b,q)
def expected(kind,p,x,y):
 if kind=='COMPARE':return 'CMP_'+('NEG' if x<y else 'POS' if x>y else 'EQ'),None
 z=x+y if kind=='ADD' else x-y;flag=int(z>=1<<p) if kind=='ADD' else int(z<0)
 return ('ADD_C' if kind=='ADD' else 'SUB_B')+str(flag),z%(1<<p)
def run(hw,c,l,m,kind,p,x,y,alias=False,slots=(19,37,62),history=0,corrupt=None):
 ports,slots=fixture(hw,p,x,y,alias,slots,history);a,b,q=slots;before=[list(t.cells) for t in ports]
 program=hw.Program(c,l,m);program.run(ports,'ACQUIRE');hw.setters(program,ports,(a,b,a,b) if kind=='COMPARE' else (a,b,q,q))
 if corrupt:corrupt(ports,slots)
 r=program.run(ports,kind)
 if corrupt:need(r['status']=='MALFORMED','malformed domain');return r
 want,z=expected(kind,p,x,y);need(r['status']==want,'finite flag oracle')
 for k in range(64):
  need(ports[k].head==1,'numeric heads')
  if kind!='COMPARE' and k==q:need(ports[k].cells==before[k][:1]+bits(z,p)+['R']+before[k][p+2:],'complete output and exterior')
  else:need(ports[k].cells==before[k],'incoming live/exterior unchanged')
 for k in range(64,68):need(ports[k].head==0 and ports[k].cells==['_']*8+before[k][8:],'selector cleanup/history')
 ls,lc=((7,181) if alias else(11,188)) if kind=='COMPARE' else((13,291) if alias else(17,298))
 ps,pc=((125,388) if alias else(247,602)) if kind=='COMPARE' else((279,735) if alias else(401,949))
 need(r['logical_instructions']==ls*p+lc,'exact logical count');need(r['instructions']==ps*p+pc,'exact physical count')
 need(r['instructions']+124<=401*p+1073,'full new call bill')
 return {'kind':kind,'p':p,'alias':alias,'slots':list(slots),'instructions':program.total,'history':history}
def main():
 d=load(HERE/'inputs/all-divisions/inputs/divider/divider.py','B12d');hw=load(HERE/'inputs/all-divisions/inputs/divider/hardware.py','B12hw');a=load(HERE/'arithmetic.py','B12a')
 c,l,m=a.compile_arithmetic(d);old,_,_=d.compile_divider();need(c[:len(old)]==old and len(old)==336150,'unchanged entire divider prefix');cases=[]
 for kind in('COMPARE','ADD','SUBTRACT'):
  for x in range(16):
   for y in range(16):cases.append(run(hw,c,l,m,kind,4,x,y))
   cases.append(run(hw,c,l,m,kind,4,x,x,True))
 rng=random.Random(5053)
 for p in(5,17,97,257):
  for kind in('COMPARE','ADD','SUBTRACT'):
   for alias in(False,True):
    x=rng.randrange(1<<p);y=x if alias else rng.randrange(1<<p);cases.append(run(hw,c,l,m,kind,p,x,y,alias,tuple(rng.sample(range(8,64),3)),1025))
 controls=[]
 for name,kind,p,corrupt in(('short_word','ADD',3,lambda ts,ss:None),('invalid_digit','COMPARE',4,lambda ts,ss:ts[ss[0]].cells.__setitem__(2,'|')),('short_second','SUBTRACT',4,lambda ts,ss:ts[ss[1]].cells.__setitem__(3,'R')),('dirty_output','ADD',4,lambda ts,ss:ts[ss[2]].cells.__setitem__(2,'1')),('descriptor_digit','COMPARE',4,lambda ts,ss:ts[64].cells.__setitem__(3,'|'))):
  run(hw,c,l,m,kind,p,3,2,corrupt=corrupt);controls.append(name)
 for kind,good,badstatus in(('ADD','ADD_C0','ADD_C1'),('SUBTRACT','SUB_B0','SUB_B1'),('COMPARE','CMP_POS','CMP_NEG')):
  bad=tuple(('H',badstatus) if row==('H',good) else row for row in c)
  ports,slots=fixture(hw,4,3,2);aa,bb,q=slots;program=hw.Program(bad,l,m);program.run(ports,'ACQUIRE');hw.setters(program,ports,(aa,bb,aa,bb) if kind=='COMPARE' else(aa,bb,q,q));r=program.run(ports,kind)
  need(r['status']==badstatus and all(t.head==1 for t in ports[:64]) and all(t.head==0 and t.cells[:8]==['_']*8 for t in ports[64:]),'returning flag corruption cleans up')
  need(r['status']!=expected(kind,4,3,2)[0],'finite flag corruption detected');controls.append('returning_'+kind+'_flag')
 print(json.dumps({'status':'PASS','graph':d.digest(c),'locations':len(c),'new_logical_locations':m['new_logical_locations'],'cases':len(cases),'instructions':sum(x['instructions'] for x in cases),'controls':controls,'wide_cases':cases[-24:]},indent=2,sort_keys=True))
if __name__=='__main__':main()
