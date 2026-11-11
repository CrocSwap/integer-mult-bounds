#!/usr/bin/env python3
"""Independent review: no author verifier, fixtures or oracle imported."""
import argparse
from hashlib import sha256
import json
from math import comb, prod
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys

def need(condition,label):
    if not condition: raise ValueError(label)

def load(name,path):
    module=ModuleType(name); module.__file__=str(path); sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__)
    return module

def context(package):
    root=package.parents[1]; pins={}
    for row in json.loads((package/'SOURCES.json').read_text())['files']:
        if row['usage']!='input': continue
        digest=sha256((root/row['path']).read_bytes()).hexdigest()
        need(digest==row['sha256'],'source pin '+row['path']); pins[row['path']]=digest
    w=load('words',root/'research/r437-preparation-composition/predecessor4025/source/words.py')
    r=load('records',root/'research/r437-preparation-composition/predecessor4025/source/records.py')
    e=load('_review_entry',root/'research/encoded-crt-entry-lifecycle/entry.py')
    n=load('_review_numeric',root/'research/encoded-current-crt/producer.py')
    o=load('_review_owner',root/'research/crt-persistent-numerical-owner/owner.py')
    c=load('_review_canonical',root/'research/crt-mixed-row-entry/bridge.py')
    f=load('_review_frontend',package/'frontend.py')
    return SimpleNamespace(w=w,r=r,e=e,n=n,o=o,c=c,f=f,pins=pins)

def emit_source(m,moduli,widths,values,tail=37):
    p=m.e.Port(m.w)
    for modulus,width,value in zip(moduli,widths,values,strict=True):
        data=[m.r.ROOT]+[m.w.ONE]*width+[m.r.WORD_END]
        data += [(modulus>>j)&1 for j in range(width)]+[m.r.WORD_END]
        data += [(value>>j)&1 for j in range(width)]+[m.r.RECORD_END]
        for symbol in data: p.append(symbol)
    p.append(m.w.RIGHT); p.rewind()
    p.cells.extend(([m.r.STEP,m.w.ONE,m.w.BLANK,m.r.ROOT]*((tail+3)//4))[:tail])
    return p

def canonical_bytes(m,moduli,values):
    data=[m.w.LEFT]
    for modulus,value in zip(moduli,values,strict=True):
        data.append(m.r.ROOT)
        for item in (modulus,value):
            data.extend((item>>j)&1 for j in range(max(1,item.bit_length())))
            data.append(m.r.WORD_END)
        data.append(m.r.RECORD_END)
    return bytes(data+[m.w.RIGHT])

def logical_bytes(m,port):
    return bytes(port.cells[:port.cells.index(m.w.RIGHT,1)+1])

def word(m,value):
    end=value.cells.index(m.w.RIGHT,1)
    return sum(value.cells[j]<<(j-1) for j in range(1,end))

def node_order(count):
    # Root-interval breadth-first refinement, then bottom-up layers.
    layer=[(0,count)]; layers=[]
    while layer:
        layers.append(layer); next_layer=[]
        for start,size in layer:
            if size>2:
                next_layer.extend(((start,size//2),(start+size//2,size//2)))
        layer=next_layer
    return [interval for layer in reversed(layers) for interval in layer]

def dummy_produce(arena,left,right,w,r):
    output=r.Tape(); output.append(w.RIGHT); output.rewind()
    return {'lower':arena.zero(),'product':arena.zero(),'stream':output}

def crt_sum(moduli,values):
    modulus=prod(moduli)
    if any(value>=base for base,value in zip(moduli,values,strict=True)):
        return 0,modulus
    total=0; prefix=1
    for base,value in zip(moduli,values,strict=True):
        cofactor=modulus//base
        total+=(value*prefix%base)*cofactor*pow(cofactor,-1,base)
        prefix*=base
    return total%modulus,modulus

def run_tree(m,moduli,widths,values,actual=False,mutate_cursor=False):
    count=len(moduli); total_width=sum(widths); logical=2+3*total_width+4*count
    source=emit_source(m,moduli,widths,values)
    snapshot=bytes(source.cells),source.head
    iterator=m.f.Iterator(m.w,m.r,m.e,m.n if actual else SimpleNamespace(produce=dummy_produce),
                          m.o,m.c,source)
    ports=(*iterator.bank.ports,*iterator.guards,*iterator.counters.values())
    need(len(ports)==78 and len({id(p.cells) for p in ports})==78,'78 distinct backings')
    identities=tuple(id(p.cells) for p in ports); pstar=total_width+1
    bounds=([pstar+1]+[2*total_width+2*count+2]*2+[pstar+2]*57+
            [count*(pstar+2)+2]*3+[pstar+2]*8+[count+2]*6+[total_width+2])
    need(len(bounds)==78,'role envelope shape')
    original_init=m.e.Port.__init__
    def forbidden(*args,**kwargs): raise ValueError('new physical Port during node traversal')
    m.e.Port.__init__=forbidden; seen=[]
    try:
        for start,size in node_order(count):
            axis=iterator.counters['axis']
            need(axis.cells[1:count+1].count(m.r.STEP)==1,'unique current STEP')
            need(axis.cells[start+1]==m.r.STEP,'independent interval start')
            need(m.r.VALUE not in axis.cells[1:count+1],'no pending VALUE before entry')
            lease=iterator.next(); entry=lease.actual; half=size//2
            need(logical_bytes(m,entry.left)==canonical_bytes(m,moduli[start:start+half],values[start:start+half]),
                 'independent canonical left bytes')
            need(logical_bytes(m,entry.right)==canonical_bytes(m,moduli[start+half:start+size],values[start+half:start+size]),
                 'independent canonical right bytes')
            precision=1+sum(widths[start:start+size])
            need(entry.guide.cells[1:precision+1]==bytes([m.w.ONE])*precision,'exact current guide')
            need(len(entry.guide.cells)<=precision+1 or entry.guide.cells[precision+1]==m.w.BLANK,
                 'guide ends at current precision')
            last=start+size==count
            need(entry.last==last,'actual rightmost marker')
            if not last:
                need(axis.cells[start+size+1]==m.r.VALUE,'pending VALUE at interval successor')
                if mutate_cursor: axis.cells[start+size+1]=m.w.ONE
            need(axis.cells[start+1]==m.r.STEP,'current cursor retained until retirement')
            for guard in iterator.guards:
                need(guard.cells[:precision+2]==bytes([m.w.LEFT]+[m.w.ZERO]*precision+[m.w.RIGHT]),
                     'actual exact-width protected word')
                need(all(x==m.w.BLANK for x in guard.cells[precision+2:]),'protected old tail blank')
            if actual:
                lower,product=crt_sum(moduli[start:start+half],values[start:start+half])
                offsets=[]; targets=[]; current=product
                for base,value in zip(moduli[start+half:start+size],values[start+half:start+size],strict=True):
                    offset=lower*pow(current,-1,base)%base
                    offsets.append(offset); targets.append((value+offset)%base if value<base else value)
                    current*=base
                need(word(m,entry.result['lower'])==lower,'independent CRT sum lower')
                need(word(m,entry.result['product'])==product,'independent prefix product')
                out=entry.result['stream'].cells; cursor=1
                for offset,target in zip(offsets,targets,strict=True):
                    need(out[cursor]==m.r.ROOT,'actual output tag'); cursor+=1
                    for expected in (offset,target):
                        observed=sum(out[cursor+j]<<j for j in range(precision))
                        cursor+=precision; need(out[cursor]==m.r.WORD_END,'actual output delimiter'); cursor+=1
                        need(observed==expected,'independent inverse-congruence output')
                    need(out[cursor]==m.r.RECORD_END,'actual output record'); cursor+=1
                need(out[cursor]==m.w.RIGHT,'complete actual output')
            need((bytes(source.cells),source.head)==snapshot,'borrowed source and nonblank old tail preserved')
            lease.close()
            need(tuple(id(p.cells) for p in ports)==identities,'all historical backing identities')
            need(all(len(p.cells)<=bound for p,bound in zip(ports,bounds,strict=True)),'78 separate historical maxima')
            need(all(p.head==1 and all(x==m.w.BLANK for x in p.cells)
                     for p in (*iterator.bank.ports,*iterator.guards)),'numerical and protected retirement')
            seen.append([start,size,precision])
        need(iterator.next() is None and iterator.closed,'final root boundary completes exactly')
        need(all(p.head==1 and all(x==m.w.BLANK for x in p.cells) for p in ports),'all 78 histories retired')
        need((bytes(source.cells),source.head)==snapshot,'final source preservation')
    finally: m.e.Port.__init__=original_init
    need(sum(bounds)==3*count*total_width+71*total_width+19*count+221,'independent envelope simplification')
    return {'axes':count,'actual_numeric':actual,'nodes':seen,'source_logical':logical,
            'source_history':len(source.cells),'retained_owned':sum(len(p.cells) for p in ports),
            'owned_bound':sum(bounds),'role_count':len(ports)}

def guard_counts(m):
    iterator=object.__new__(m.f.Iterator); iterator.w=m.w
    iterator.guards=tuple(m.e.Port(m.w) for _ in range(8))
    for p in iterator.guards: p.retire()
    identities=tuple(id(p.cells) for p in iterator.guards); rows=[]
    def actions(ports): return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)
    for precision in (5,31,6,127,5):
        guide=m.e.Port(m.w)
        for _ in range(precision): guide.append(m.w.ONE)
        guide.rewind(); all_ports=(guide,*iterator.guards); before=actions(all_ports)
        iterator._prepare_guards(guide); prepared=actions(all_ports)-before
        before=actions(all_ports)
        for p in iterator.guards: p.retire()
        retired=actions(all_ports)-before
        need(prepared==8*(9*precision+14),'exact guide-based preparation count')
        need(retired==8*(5*precision+15),'exact protected retirement count')
        need(tuple(id(p.cells) for p in iterator.guards)==identities,'same eight historical guards')
        need(all(p.head==1 and all(x==m.w.BLANK for x in p.cells) for p in iterator.guards),
             'complete decreasing-width guard histories')
        rows.append([precision,prepared,retired])
    need(any(a+b>8*(14*p+28) for p,a,b in rows),'one-action understated guard bill rejected')
    return rows

def rejected_shape(m):
    source=emit_source(m,[3,5,7],[4,4,4],[1,2,3]); before=bytes(source.cells),source.head
    old=m.e.Port.__init__; created=[]
    def capture(port,*args,**kwargs): old(port,*args,**kwargs); created.append(port)
    m.e.Port.__init__=capture
    try:
        try: m.f.Iterator(m.w,m.r,m.e,SimpleNamespace(produce=dummy_produce),m.o,m.c,source)
        except ValueError as exc: need('dyadic source axis count' in str(exc),'actual nondyadic guard')
        else: raise ValueError('nondyadic source accepted')
    finally: m.e.Port.__init__=old
    need(len(created)==78,'rejected construction fixed roles')
    need(all(p.head==1 and all(x==m.w.BLANK for x in p.cells) for p in created),'rejected entire-history cleanup')
    need((bytes(source.cells),source.head)==before,'rejected source and old tail preserved')
    return len(created)

def record_counts(m):
    rows=[]
    def actions(ports): return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)
    for width in (2,3,9,257):
        for selected in (False,True):
            for value in (0,(1<<width)-1):
                iterator=object.__new__(m.f.Iterator)
                iterator.w,iterator.r,iterator.canonical=m.w,m.r,m.c
                iterator.source=emit_source(m,[value],[width],[value],tail=0)
                iterator.counters={'width':m.e.Port(m.w)}
                target,guide=m.e.Port(m.w),m.e.Port(m.w)
                ports=(iterator.source,iterator.counters['width'],target,guide)
                before=actions(ports)
                iterator._record(target if selected else None,guide if selected else None)
                used=actions(ports)-before
                bound=(39*width+72) if selected else (24*width+46)
                need(used<=bound,'independent expanded record-action bound')
                rows.append([width,selected,value==0,used,bound])
    return rows

def run(package):
    m=context(package); primes=[]; candidate=2
    while len(primes)<32:
        if all(candidate%p for p in primes if p*p<=candidate): primes.append(candidate)
        candidate+=1
    trees=[]
    for count in (2,4,8,16,32):
        selected=primes[:count]; ell=selected[-1].bit_length()+1
        widths=[ell-(j%2) for j in range(count)]
        values=[(j*j+1)%(1<<width) for j,width in enumerate(widths)]
        trees.append(run_tree(m,selected,widths,values))
    trees.append(run_tree(m,[5,7,11,13],[4,4,4,4],[4,6,10,12],actual=True))
    trees.append(run_tree(m,[5,7,11,13],[4,4,4,4],[4,8,10,15],actual=True))
    controls=[]
    try: run_tree(m,[3,5,7,11],[4,4,4,4],[1,2,3,4],mutate_cursor=True)
    except ValueError as exc:
        need('next-node interval' in str(exc),'pending-cursor mutation detection'); controls.append('omitted pending VALUE')
    else: raise ValueError('pending cursor corruption accepted')
    rejected=rejected_shape(m); controls.append('nondyadic source with full cleanup')
    guards=guard_counts(m); controls.append('understated exact guard invoice')
    # With ell=t+2, t>=0: multiply the quartic difference by7.
    quartic=[7*715*comb(4,k)-8*comb(4,k)*5**(4-k) for k in range(5)]
    quadratic=[32*comb(2,k)-2*comb(2,k)*4**(2-k) for k in range(3)]
    need(all(v>=0 for v in quartic+quadratic),'positive all-ell geometric constants')
    return {'schema':1,'core_hashes':{name:sha256((package/name).read_bytes()).hexdigest()
                                      for name in ('PROOF.md','frontend.py','SOURCES.json')},
            'scientific_input_pins':m.pins,'trees':trees,'guard_counts':guards,'record_counts':record_counts(m),
            'quartic_scaled_positive_coefficients':quartic,'quadratic_positive_coefficients':quadratic,
            'controls':controls,'rejected_roles':rejected,
            'total_nodes':sum(len(t['nodes']) for t in trees),'roles':78,
            'topology_uses_actual_entry_bank':True,'topology_uses_dummy_numeric':True,
            'actual_numeric_nodes':6,'control_cost_scope':'raw bound and unspecified finite C_front; not an exact full-control coefficient'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--package-root',type=Path)
    parser.add_argument('--write-result',action='store_true'); args=parser.parse_args()
    here=Path(__file__).resolve().parent; package=(args.package_root or here.parent).resolve()
    result=run(package); serialized=json.dumps(result,sort_keys=True,separators=(',',':'))
    if args.write_result: (here/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((here/'RESULT.json').read_text())
        need(serialized==json.dumps(expected,sort_keys=True,separators=(',',':')),'typed independent receipt')
    print('PASS_INDEPENDENT_BALANCED_ENTRY',result['total_nodes'],result['roles'],result['actual_numeric_nodes'],len(result['controls']))

if __name__=='__main__': main()
