"""Check complete counter domains and actual monomial coefficient streams.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse,hashlib,itertools,json,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def module(name,path):
    obj=types.ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(path.read_bytes(),str(path),'exec'),obj.__dict__);return obj


for row in json.loads((P/'SOURCES.json').read_text())['files']:
    if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash')
c=module('phase',P/'phase.py');source=ROOT/'research/selected-complex-compact-adapters'
streams=module('streams',source/'streams.py');compact=module('compact',source/'compact.py');old=module('monomial',source/'monomial.py')
actual=json.loads((ROOT/'research/complex-segment-boundary/RIGHT-RECIPE.json').read_text())


def dirty(n,salt=0):return [(i*7+i//3+salt)%2 for i in range(n)]


def snapshot(tape):
    cells=tape.cells[:]
    while cells and cells[-1]==c.BLANK:cells.pop()
    return cells,tape.head


def prepare(recipe,maskbits,prefix):
    meter=c.Meter();mask=c.Tape(dirty(prefix,1),meter)
    for bit in (*maskbits,c.END):c.emit(mask,bit)
    c.rewind(mask)
    counters=[c.Tape(dirty(prefix,i),meter) for i in range(len(recipe['linear_Z4']))]
    before=[snapshot(t) for t in (mask,*counters)];start=meter.total
    producer=c.Phases(recipe,mask,counters)
    return producer,meter,start,before


def oracle(recipe,maskbits,index):
    b=len(maskbits);m=len(recipe['linear_Z4']);coords=[]
    for _ in range(m):coords.append(index%(1<<b));index>>=b
    coords.reverse();phase=sum(maskbits)*recipe['phase']
    for k,active in enumerate(maskbits):
        if not active:continue
        x=[(v>>k)&1 for v in coords]
        phase+=sum(a*bit for a,bit in zip(recipe['linear_Z4'],x))
        phase+=2*sum(x[i]*x[j]*((recipe['quadratic_rows'][i]>>j)&1) for i in range(m) for j in range(i+1,m))
    return phase%4


def domain(recipe,maskbits,prefix,source_oracle=False):
    p,meter,start,before=prepare(recipe,maskbits,prefix);count=0;digest=hashlib.sha256()
    if source_oracle:
        layout=compact.Layout(tuple(('v'+str(i),len(maskbits)) for i in range(len(recipe['linear_Z4']))),8)
        active=[i for i,x in enumerate(maskbits) if x];rho=active[0];K=active[1]-rho if len(active)>1 else len(maskbits)
    while True:
        expected=old.tensor_phase(recipe,layout.decode(count),len(active),K,rho) if source_oracle else oracle(recipe,maskbits,count)
        need(p.phase==expected,'complete phase endpoint');digest.update(bytes([p.phase]));count+=1
        if not p.advance():break
    need(p.phase==oracle(recipe,maskbits,0),'complete phase endpoint at wrap')
    p.close();m=len(recipe['linear_Z4']);b=len(maskbits)
    need(count==1<<(m*b),'complete counter domain')
    need([snapshot(t) for t in (p.mask,*p.counters)]==before,'counter mask and dirty return')
    used=meter.total-start;bound=32*(m+1)*(count+b+1)
    need(used<=bound,'uniform complete phase bill')
    return dict(m=m,b=b,mask=list(maskbits),records=count,actions=used,bound=bound,sha256=digest.hexdigest())


def generic():
    rows=[]
    for alpha,p0 in itertools.product(range(4),repeat=2):
        recipe=dict(linear_Z4=[alpha],quadratic_rows=[1],phase=p0)
        for mask in ((1,),(0,1),(1,0,1),(0,0),(1,1,1,1)):rows.append(domain(recipe,mask,7))
    for a,b,edge,p0 in itertools.product(range(4),range(4),range(2),range(4)):
        recipe=dict(linear_Z4=[a,b],quadratic_rows=[1+2*edge,3],phase=p0)
        rows.append(domain(recipe,(1,0,1),9))
    for seed in range(16):
        recipe=dict(linear_Z4=[seed%4,(seed//2)%4,(seed//3)%4],quadratic_rows=[(seed*3)%8,(seed*5)%8,(seed*7)%8],phase=seed%4)
        rows.append(domain(recipe,(1,1),11))
    return dict(contexts=len(rows),records=sum(r['records'] for r in rows),actions=sum(r['actions'] for r in rows))


def payload_case(prefix,inverse):
    recipe={**actual,'matrix_rows':actual['matrix_rows']+[1<<9],'linear_Z4':actual['linear_Z4']+[0],'quadratic_rows':actual['quadratic_rows']+[0]}
    p,meter,start,before=prepare(recipe,(1,),prefix)
    layout=compact.Layout(tuple(('v'+str(i),1) for i in range(10)),8)
    raw=bytes(bit for i in range(layout.records) for bit in streams.bit_key((37*i+19)%256,8))
    source_meter=streams.Meter();ref=old.phase_pass(streams.Tape(source_meter,raw),layout,actual,1,1,0,4,inverse)
    target_meter=streams.Meter();got=c.apply_phase(streams.Tape(target_meter,raw),p,4,streams.Tape,streams.copy,inverse)
    need(bytes(got.data)==bytes(ref.data),'actual Gaussian source endpoint')
    independent=bytearray()
    for i in range(layout.records):
        phase=oracle(recipe,(1,),i)
        if inverse:phase=-phase%4
        real=sum(raw[8*i+j]<<j for j in range(4));imag=sum(raw[8*i+4+j]<<j for j in range(4))
        for _ in range(phase):real,imag=-imag,real
        independent.extend(streams.bit_key(real%16,4));independent.extend(streams.bit_key(imag%16,4))
    need(bytes(got.data)==bytes(independent),'independent Gaussian rotation')
    need(vars(source_meter)==vars(target_meter),'unchanged coefficient invoice')
    need([snapshot(t) for t in (p.mask,*p.counters)]==before,'source consumer counter return')
    used=meter.total-start;need(used<=32*11*(layout.records+2),'source producer bound')
    return dict(prefix=prefix,inverse=inverse,records=layout.records,phase_actions=used,coefficient_meter=vars(target_meter),output_sha256=hashlib.sha256(got.data).hexdigest())


def controls():
    count=0
    for fault in ('empty_mask','bad_mask','bad_counter','early_close','extent','after_done'):
        recipe=dict(linear_Z4=[1,2],quadratic_rows=[2,0],phase=1)
        try:
            p,meter,start,before=prepare(recipe,() if fault=='empty_mask' else (1,),5)
            if fault=='bad_mask':p.mask.cells[p.mask.head]=c.BLANK
            if fault=='bad_counter':p.counters[1].cells[p.counters[1].head]=c.END
            if fault=='early_close':p.close()
            if fault=='extent':p.counters[0].cells[p.counters[0].head+1]=c.BLANK
            while p.advance():pass
            if fault=='after_done':p.advance()
        except ValueError:count+=1
        else:raise ValueError('accepted phase control: '+fault)
    return count


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    small=generic()
    source_rows=[domain(actual,mask,17,True) for mask in ((1,),(1,1),(0,1))]
    payload=[payload_case(prefix,inverse) for inverse in (False,True) for prefix in (16,257,4096)]
    need(len({r['phase_actions'] for r in payload})==1,'source cost independent of ancestor and sign')
    result=dict(status='PASS_SEQUENTIAL_MONOMIAL_PHASE',generic=small,source_domains=source_rows,payload_cases=payload,controls=controls(),phase_sha256=hashlib.sha256((P/'phase.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'complete typed receipt')
    print(json.dumps(dict(status=result['status'],generic=small,source_domains=source_rows,payload_cases=len(payload),controls=result['controls']),sort_keys=True))


if __name__=='__main__':main()
