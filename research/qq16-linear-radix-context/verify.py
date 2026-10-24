"""Compare the actual source constructor, shared traversal and fused producer.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source loader and installation fixture retain Mihir Srivastava's credit.
"""
import argparse,ast,hashlib,json,sys,types
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    obj=types.ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(path.read_bytes(),str(path),'exec'),obj.__dict__);return obj


for row in json.loads((P/'SOURCES.json').read_text())['files']:
    if row['usage']=='input':path=ROOT/row['path']
    elif row.get('pin'):path=P/'vendor/installation_source.py'
    else:continue
    need(hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],'source hash')
old=load('installation_source',P/'vendor/installation_source.py');old.ROOT=ROOT
new=load('constructor',P/'constructor.py')
mods,ns,sources=old.load_source()
w=mods['words'];r=mods['records']
shared_path=ROOT/'research/r437-preparation-composition/predecessor4025/verify.py'
tree=ast.parse(shared_path.read_bytes());nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='high_power_shared']
need(len(nodes)==1,'exact shared source function');scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(shared_path),'exec'),scope)


def actions(m):return m.reads+m.writes+m.moves


def run_case(q,width,d,mode,dirty=0):
    M=q**width;B=M.bit_length()+1;arena=w.Arena(B,32);indices=w.Arena(8,8)
    modulus=arena.input(M);size,depth=indices.input(2*d),indices.input(1)
    highs,program,spectator=r.Tape(),r.Tape(),r.Tape()
    for _ in range(dirty):highs.append(1)
    highs.rewind()
    for tape in (program,spectator):
        for bit in (1,0,1,1,0):tape.append(bit)
        tape.rewind()
    protected=[(t,bytes(t.cells),t.head) for t in (modulus,size,depth,program,spectator)]
    pool=ns['ScratchPool'](1 if mode=='fused' else 2)
    runtime=object.__new__(ns['Machine']);runtime.arena,runtime.indices=arena,indices
    runtime.binding=types.SimpleNamespace(codes=types.SimpleNamespace(q=q,dimension=d,bits=7))
    runtime.roles={'highs':highs,'program':program,'spectator':spectator}
    old_context=ns['Context'];old_high=mods['counts'].high_power;old_div=w.Unsigned.divmod
    phase={};divisions=0
    def observed_div(self,a,b):
        nonlocal divisions
        divisions+=1;return old_div(self,a,b)
    def context_factory(ring,codes):
        start=actions(arena.meter);rec=sum(actions(t.meter) for t in pool.tapes)
        context=new.build(ring,codes,old_context,mods['counts'].Count) if mode=='fused' else old_context(ring,codes)
        phase['word']=actions(arena.meter)-start;phase['record']=sum(actions(t.meter) for t in pool.tapes)-rec
        return context
    ns['Context']=context_factory;w.Unsigned.divmod=observed_div
    if mode=='shared':mods['counts'].high_power=lambda value,ring,q,d:scope['high_power_shared'](value,ring,q,d,mods['cardinality'].radix_power)
    start=actions(arena.meter)+sum(actions(t.meter) for t in (*pool.tapes,highs,program,spectator))
    try:
        with old.allocated_from(mods,pool,r.Tape):runtime.new_context(modulus,size,depth)
    finally:ns['Context']=old_context;mods['counts'].high_power=old_high;w.Unsigned.divmod=old_div
    total=actions(arena.meter)+sum(actions(t.meter) for t in (*pool.tapes,highs,program,spectator))-start
    value=q**((width-1)*d*d);N=value.bit_length();encoding=bytes((value>>i)&1 for i in range(N))+bytes([w.RIGHT])
    need(old.body(highs,w.BLANK)==encoding,'actual installed high count')
    need(type(runtime.context) is old_context and runtime.context.cap.inspect()==q**(width-1),'genuine Context and cap')
    need(runtime.context.raw is runtime.context.ring.raw and runtime.context.ring.modulus is modulus,'numerical alias preservation')
    need(runtime.context.highs.tape is highs and runtime.program.tape is program,'literal installed Tape aliases')
    need(all(bytes(t.cells)==data and t.head==head for t,data,head in protected),'protected bytes and heads')
    need(arena.live=={modulus.slot,runtime.context.ring.one.slot,runtime.context.cap.slot},'constructor numerical cleanup')
    need(all(arena.words[i].head==1 for i in arena.live),'returned numerical heads')
    pool.empty()
    if mode=='fused':
        m=d*d*(width-1);sum_bits=sum((q**j).bit_length() for j in range(m))
        word=(14*width+59)*B+21*width+80
        record=23+6*sum_bits+4*(N-1)+5*m
        need(phase==dict(word=word,record=record),'exact fused production invoice')
        need(total==22*B+41+word+record+15*(N+1)+5*dirty+24,'exact complete constructor invoice')
        need(pool.peak==pool.allocations==1 and arena.meter.peak_live==4,'one lease and four numerical words')
        need(divisions==0,'no general division in fused constructor')
    else:need(divisions==((d*d+1)*width+1 if mode=='literal' else 2*width+1),'retained general-division count')
    result=dict(q=q,w=width,d=d,B=B,dirty=dirty,mode=mode,actions=total,production=phase,general_divisions=divisions,record_peak=pool.peak,numerical_peak=arena.meter.peak_live,count_bits=N)
    runtime.context.close();runtime.context.ring.close();arena.free(modulus);indices.free_many(size,depth)
    need(not arena.live and not indices.live and not old.body(highs,w.BLANK),'complete output disposal')
    return result


def quotient_cases():
    n=0
    for B in range(2,8):
        for q in range(2,8):
            for value in range(2**B):
                arena=w.Arena(B,1);word=arena.input(value);before=actions(arena.meter)
                rem=new.divide_fixed(word,q)
                need(actions(arena.meter)-before==5*B+7,'exact quotient scan invoice')
                need((word.inspect(),rem)==divmod(value,q),'independent quotient identity');n+=1
    return n


def rejecting():
    n=0
    for q,M in ((2,3),(3,12),(5,26),(3,2)):
        arena=w.Arena(M.bit_length()+1,8);modulus=arena.input(M);ring=w.Ring(modulus)
        before=set(arena.live);saved=[(t,bytes(t.cells),t.head) for t in (modulus,ring.one)]
        pool=ns['ScratchPool'](1)
        try:
            with old.allocated_from(mods,pool,r.Tape):new.build(ring,types.SimpleNamespace(q=q,dimension=2),ns['Context'],mods['counts'].Count)
        except ValueError as error:need('radix' in str(error),'specific radix rejection');n+=1
        else:raise ValueError('accepted non-power')
        need(arena.live==before and all(bytes(t.cells)==data and t.head==head for t,data,head in saved),'rejection rollback')
        pool.empty();ring.close();arena.free(modulus)
    return n


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    quotient=quotient_cases();rows=[]
    fixtures=[(q,width,d,dirty) for q,width,d,dirty in ((2,1,1,0),(3,2,2,0),(5,3,2,7),(3,4,4,31),(5,8,4,0),(3,2,8,0),(3,1,64,0))]
    for q,width,d,dirty in fixtures:
        triple=[run_case(q,width,d,mode,dirty) for mode in ('literal','shared','fused')]
        need(triple[2]['actions']<triple[1]['actions']<=triple[0]['actions'],'matched full constructor improvement');rows.append(triple)
    result=dict(status='PASS_LINEAR_RADIX_CONTEXT',quotient_cases=quotient,constructor_comparisons=rows,rejection_controls=rejecting(),constructor_sha256=hashlib.sha256((P/'constructor.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'complete typed receipt')
    print(json.dumps(dict(status=result['status'],quotient_cases=quotient,contexts=3*len(rows),rejection_controls=result['rejection_controls'],largest_comparison=rows[4]),sort_keys=True))


if __name__=='__main__':main()
