"""Guarded native scalar splice and whole-word replay. Apache-2.0.
Dugongue with substantial OpenAI assistance. No new kappa claim.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import ast,gzip,hashlib,json,types
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))

def authenticated():
    inputs={}
    for row in read('SOURCES.json')['files']:
        if row['usage']=='input':
            data=(ROOT/row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest()==row['sha256'],'Changed pinned source: '+row['path'])
            inputs[row['path']]=data
    return inputs

def extract(data,names):
    tree=ast.parse(data.decode('utf-8'));nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
    need({x.name for x in nodes}==set(names),'Exact audited function inventory')
    namespace={'Q':Q,'need':need,'Counter':Counter}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'authenticated source functions','exec'),namespace)
    return types.SimpleNamespace(**namespace)

def sources(inputs):
    def pick(ending):return next(v for k,v in inputs.items() if k.endswith(ending))
    word=json.loads(gzip.decompress(pick('-NATIVE.json.gz')))
    chart=json.loads(gzip.decompress(pick('-CANONICAL.json.gz')))
    v=extract(pick('/verify_buffers.py'),{'identity','add','warp','span','expected','replay'})
    n=extract(pick('/rebuild_native.py'),{'primitive_allowance','replay_extended'})
    return word,chart,v,n

def local_check(source,replacement,rule):
    xs=rule['source_roles'];ys=rule['target_roles'];frame=rule['frame'];M=[[Q(x) for x in row] for row in rule['matrix']]
    need(xs and ys and len(set(xs+ys))==len(xs+ys),'Disjoint injective source roles')
    need(all(type(i)==int and 0<=i<632 for i in xs+ys),'Original persistent field ABI')
    need(len(M)==len(ys) and all(len(row)==len(xs) for row in M),'Matrix dimensions')
    allowed={('L',i) for i in xs+ys};roles=sorted(allowed);size=len(roles)
    def replay(program):
        rows={role:[Q(i==j) for j in range(size)] for i,role in enumerate(roles)}
        for e in program:
            need(e[0]=='scalar' and len(e)==3 and e[2]==frame,'Pure common-frame scalar window')
            op=e[1];dst=tuple(op[1]);need(dst in rows,'No new field')
            if op[0]=='add':
                src=tuple(op[2]);q=Q(op[3],op[4]);need(src in rows and src!=dst and q,'Legal ADD roles')
                need(q.denominator&(q.denominator-1)==0,'Native dyadic ADD')
                rows[dst]=[a+q*b for a,b in zip(rows[dst],rows[src])]
            else:
                need(op[0]=='scale','No owned clear, copy or query')
                q=Q(op[2],op[3]);num,den=abs(q.numerator),q.denominator
                need(q and not num&(num-1) and not den&(den-1),'Native unit SCALE')
                rows[dst]=[q*a for a in rows[dst]]
        return rows
    a=replay(source);b=replay(replacement);need(a==b,'Exact local all-column operator')
    original={role:[Q(i==j) for j in range(size)] for i,role in enumerate(roles)}
    for x in xs:need(a['L',x]==original['L',x],'Source input restored')
    for j,y in enumerate(ys):
        expected=[original['L',y][k]+sum(M[j][i]*original['L',x][k] for i,x in enumerate(xs)) for k in range(size)]
        need(a['L',y]==expected,'Declared shear matrix')
    return size

def install(words,patches,price):
    need(set(words)=={'forward','backward'} and len(patches)==8,'Complete two-direction input and eight rules')
    out={};receipts=[]
    for direction in ('forward','backward'):
        rules=sorted([r for r in patches if r['direction']==direction],key=lambda x:x['source_indices'])
        need(len(rules)==4,'Four rules per orientation');program=words[direction];cursor=0;new=[]
        for rule in rules:
            lo,hi=rule['source_indices'];need(type(lo)==int and type(hi)==int and cursor<=lo<=hi<len(program),'Disjoint in-range frozen windows')
            window=program[lo:hi+1];need(digest(window)==rule['source_window_sha256'],'Exact frozen window hash')
            repl=rule['replacement'];columns=local_check(window,repl,rule)
            old_cost=sum(price(e[1]) for e in window);new_cost=sum(price(e[1]) for e in repl)
            need(new_cost<old_cost,'Strict fully charged local saving')
            start=len(new)+(lo-cursor);new.extend(program[cursor:lo]);new.extend(repl);cursor=hi+1
            receipts.append({'direction':direction,'source_indices':[lo,hi],'new_indices':[start,start+len(repl)-1],'old_cost':old_cost,'new_cost':new_cost,'columns':columns})
        new.extend(program[cursor:]);out[direction]=new
        need([e for e in program if e[0]!='scalar']==[e for e in new if e[0]!='scalar'],'Exact retained non-scalar chronology')
        def role_set(events):
            found=set()
            for e in events:
                if e[0]=='scalar':
                    op=e[1];found.update(tuple(r) for r in (op[1:3] if op[0] in ('add','copy') else op[1:2]))
                elif e[0]=='warp':found.add(tuple(e[1]))
                elif e[0]=='climb':found.add(('L',e[2]))
                elif e[0]=='center':found.add(('C',e[1]))
            return found
        need(role_set(program)==role_set(new),'Exact original field inventory')
    return out,receipts

def retained_event_segments(words,receipts):
    """Map surviving original event indices after scalar splicing.
    Replaced scalar indices have no one-to-one image and are deliberately absent.
    """
    out={}
    for direction in ('forward','backward'):
        cursor=shift=0;segments=[]
        for r in sorted((r for r in receipts if r['direction']==direction),key=lambda r:r['source_indices']):
            lo,hi=r['source_indices'];a,b=r['new_indices']
            if cursor<lo:segments.append({'old_range':[cursor,lo-1],'new_start':cursor+shift})
            shift+=(b-a)-(hi-lo);cursor=hi+1
        if cursor<len(words[direction]):segments.append({'old_range':[cursor,len(words[direction])-1],'new_start':cursor+shift})
        out[direction]=segments
    return out

def check_whole(words,chart,v,n):
    geo={'H':[{i:Q(1)} for i in range(112)]};checks={}
    for direction in ('forward','backward'):
        b=direction=='backward'
        prefix=n.replay_extended(v,words[direction],chart,geo,b,expected_profile=chart['local_profile'])
        # Independent retained main loop, without a rounded-error or phase rebuild.
        literal=v.replay(words[direction],chart,[],b,False)
        need(prefix['exact_endpoint'] and literal['free_warp_operator_endpoint_matches'],'Full ideal identity-shear endpoint')
        need(prefix['real_scalar_allowance']==literal['conservative_real_scalar_primitive_allowance'],'Independent complete scalar invoice')
        # replay_extended calls its generic matrix parameter H; here H is exactly I.
        prefix['endpoint']='identity-shear'
        checks[direction]={'prefix':prefix,'independent_literal':literal,'semantic_word_sha256':digest(words[direction])}
    return checks

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description='Generate the guarded two-direction native replacement from authenticated inputs.')
    ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    words,chart,v,n=sources(authenticated());out,receipts=install(words,read('PATCHES.json'),n.primitive_allowance)
    need(not args.output.exists(),'Preserve existing output; choose a new path')
    args.output.write_bytes(canonical(out)+b'\n')
    print(json.dumps({'status':'WROTE_GUARDED_NATIVE_WORD','rules':len(receipts),'semantic_sha256':digest(out)}))
