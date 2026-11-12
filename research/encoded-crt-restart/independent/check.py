"""Independent CRT arithmetic and persistent-history audit; Apache-2.0.
Prepared for CubeJerry with OpenAI assistance; no author verifier import.
"""
import hashlib,json,sys
from pathlib import Path
from types import ModuleType

def module(name,path):
    m=ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def load(root):
    b=root/'predecessor/source/research'
    paths=[('words',b/'r437-preparation-composition/predecessor4025/source/words.py'),('direct_records',b/'r437-preparation-composition/predecessor4025/source/records.py'),('direct_entry',b/'encoded-crt-entry-lifecycle/entry.py'),('direct_numeric',b/'encoded-current-crt/producer.py'),('direct_owner',b/'crt-persistent-numerical-owner/owner.py'),('direct_canonical',b/'crt-mixed-row-entry/bridge.py'),('direct_front',b/'encoded-balanced-crt-entry/frontend.py'),('direct_writer',b/'encoded-balanced-crt-endpoint/endpoint.py'),('direct_inverse',root/'predecessor/inverse_frontend.py'),('direct_subtractive',root/'predecessor/inverse_producer.py'),('direct_restart',root/'restart.py')]
    return dict(zip(('w','r','e','n','o','c','f','wr','iv','sub','restart'),[module(*p) for p in paths]))

def acquire(m):
    return m['restart'].Restart(m['w'],m['r'],m['e'],m['n'],m['o'],m['c'],m['f'],m['iv'],m['sub'],m['wr'])

def encode(m,source,mods,widths,values):
    w,r=m['w'],m['r'];raw=[w.LEFT];positions=[]
    for s,h,x in zip(mods,widths,values):
        raw.extend([r.ROOT]+[w.ONE]*h+[r.WORD_END]);raw.extend(int(b) for b in reversed(format(s,f'0{h}b')));raw.append(r.WORD_END)
        positions.append(tuple(range(len(raw),len(raw)+h)));raw.extend(int(b) for b in reversed(format(x,f'0{h}b')));raw.append(r.RECORD_END)
    raw.extend([w.RIGHT,w.ONE,w.LEFT,w.RIGHT,w.ZERO,w.ONE])
    while len(source.cells)<len(raw):source.cells.append(w.BLANK)
    source.cells[:len(raw)]=bytearray(raw);source.head=1;return positions

def read(source,positions):
    return tuple(int(''.join(str(source.cells[i]) for i in reversed(row)),2) for row in positions)

def direct(mods,values,reverse):
    x=list(values);d=len(mods);levels=list(range(1,d.bit_length()))
    for level in levels[::-1] if reverse else levels:
        half=1<<(level-1)
        for start in range(0,d,2*half):
            lower,product=0,1;good=True
            for j in range(start,start+half):
                s=mods[j];good=good and x[j]<s;target=(product*x[j])%s
                lower+=product*((target-lower)*pow(product,-1,s)%s);product*=s
            if not good:lower=0
            for j in range(start+half,start+2*half):
                s=mods[j]
                if x[j]<s:
                    offset=lower*pow(product,-1,s)%s;x[j]=(x[j]+(-offset if reverse else offset))%s
                product*=s
    return tuple(x)

def main():
    root=(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve();m=load(root);owner=acquire(m);source=m['e'].Port(m['w'])
    ids=tuple(id(p.cells) for p in owner.ports);meters=tuple(id(p.meter) for p in owner.ports)
    old=tuple(len(p.cells) for p in owner.ports);calls=nodes=largest=dmax=0
    def forbidden(*a,**k):raise AssertionError('fresh physical allocation')
    m['e'].Port.__init__=m['w'].Word.__init__=m['w'].Arena.__init__=forbidden
    shapes=[((3,5),(2,3)),((3,5,7,11),(3,3,3,4)),((3,5,7,11,13,17,19,23),(5,)*8),((3,7),(3,3))]
    for k,(mods,widths) in enumerate(shapes):
        for padded in (False,True):
            x=tuple(((1<<h)-1 if padded and j%2==0 else (j*3+k+1)%s) for j,(s,h) in enumerate(zip(mods,widths)))
            positions=encode(m,source,mods,widths,x);current=x
            for reverse in (True,False,False,True):
                before=bytes(source.cells);allowed=set(i for row in positions for i in row)
                current=direct(mods,current,reverse);owner.run(source,reverse)
                if read(source,positions)!=current:raise AssertionError('independent CRT endpoint')
                if any(source.cells[i]!=b for i,b in enumerate(before) if i not in allowed):raise AssertionError('source metadata/tail')
                if source.head!=1 or len(source.cells)!=len(before):raise AssertionError('source return/history')
                if tuple(id(p.cells) for p in owner.ports)!=ids or tuple(id(p.meter) for p in owner.ports)!=meters:raise AssertionError('physical identity reset')
                if any(len(p.cells)<n for p,n in zip(owner.ports,old)):raise AssertionError('history shortened')
                if any(p.head!=1 or any(b!=m['w'].BLANK for b in p.cells) for p in owner.ports):raise AssertionError('retirement')
                old=tuple(len(p.cells) for p in owner.ports);largest=max(largest,sum(widths));dmax=max(dmax,len(mods))
                if sum(old)>3*largest*dmax+74*largest+23*dmax+223:raise AssertionError('storage polynomial')
                calls+=1;nodes+=len(mods)-1
            if current!=x:raise AssertionError('round trip')
    print(json.dumps(dict(status='PASS_INDEPENDENT_CRT_RESTART',calls=calls,nodes=nodes,roles=len(ids),retained=sum(old),source_sha256=hashlib.sha256((root/'restart.py').read_bytes()).hexdigest()),sort_keys=True))

if __name__=='__main__':main()
