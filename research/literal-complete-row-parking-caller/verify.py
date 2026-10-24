"""Finite independent row oracle; diagnostics do not enter machine control."""
from pathlib import Path
import hashlib,json,sys,itertools
sys.path.insert(0,str(Path(__file__).resolve().parent))
from caller import *
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
def rejected(fn):
    try:fn()
    except ValueError:return
    raise RuntimeError('negative control accepted')
def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for pin in pins['files']:
        path=pin['path']
        check(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==pin['sha256'],'source drift: '+path)
    m,*_=dependencies(ROOT)
    def identity(w):w.io.perform((None,0)) # Literal one-step child.
    cases=0;receipts=[]
    for b,r in itertools.product((1,2,3,7),(1,2,4)):
        v=2*r*b
        samples=['0'*v,'1'*v,''.join(str((i*i+i//3)%2) for i in range(v))]
        samples += ['0'*i+'1'+'0'*(v-i-1) for i in range(v)]
        for bits in samples:
            t=[m.Tape.marked(x) for x in (bits,'','1'*b,'','','')]+[m.Tape.stack('10|_01'*17,-31),m.Tape.marked()]
            before=[x.snapshot() for x in t];c=Caller(ROOT,t)
            got=c.run((m.flip_child,identity));n=v//2
            expected=''.join(('1' if x=='0' else '0') if (i//b)%2==0 else x for i,x in enumerate(bits))
            check(''.join(t[OUTPUT].bits())==expected,'row oracle')
            for i in (SOURCE,GUIDE,PARK):check(t[i].snapshot()==before[i],'borrowed frame')
            for i in (ROLE0,ROLE1,IO,TEMP):check(t[i].snapshot()==before[i],'owned cleanup')
            check([x.head for x in t]==[0,0,0,0,0,0,-31,0],'heads')
            check(got=={'split':17*v+16*r+35,'boundary':[9*n+16]*2,'merge':18*v+16*r+36,'dispatch':4,'wrapper':44*v+32*r+107},'invoice')
            check((len(c.split),len(c.merge))==(73,78),'fixed tables')
            bounds=[(-1,v),(-1,v),(-1,b),(-1,n),(-1,n),(-1,n),(-32,-31+n+1),(-1,n)]
            for tape,(lo,hi) in zip(t,bounds):check(all(lo<=p<=hi for p in tape.visits+tape.writes),'physical span')
            rejected(lambda:c.run((identity,identity)))
            cases+=1
        receipts.append({'width':b,'row_pairs':r,'V':v,'wrapper':got['wrapper']})
    def fixture(bits='010101',guide='111'):
        return [m.Tape.marked(x) for x in (bits,'',guide,'','','')]+[m.Tape.stack('1',5),m.Tape.marked()]
    controls=0
    for bits,guide in [('','1'),('01',''),('01','111'),('010','111'),('0101','111'),('010101','101')]:
        rejected(lambda:Caller(ROOT,fixture(bits,guide)).run((identity,identity)));controls+=1
    t=fixture();t[OUTPUT]=t[SOURCE];rejected(lambda:Caller(ROOT,t));controls+=1
    c=Caller(ROOT,fixture())
    def alias(w):w.roles[0]=w.io
    rejected(lambda:c.run((alias,identity)));controls+=1
    # A dirty-output child is outside the semantic contract: the finite oracle
    # must detect it; no unpriced runtime semantic admission is claimed.
    t=fixture();c=Caller(ROOT,t)
    def corrupt(w):t[SOURCE].cells[0]='1'
    c.run((corrupt,identity));check(''.join(t[SOURCE].bits())!='010101','semantic mutant discriminates');controls+=1
    check(run_router([('done',)],[],budget=None)==1,'unbounded default')
    rejected(lambda:run_router([('goto',0)],[],budget=2));controls+=1
    return {'status':'PASS_FINITE_CALLER','cases':cases,'controls':controls,'tables':[73,78],'receipts':receipts,'scope':'conditional wrapper; child contracts retained'}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,indent=2))
