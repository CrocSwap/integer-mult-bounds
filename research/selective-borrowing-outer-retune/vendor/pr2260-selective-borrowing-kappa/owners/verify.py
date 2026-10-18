"""Independent full literal ownership and physical orthogonal chart reconstruction.

Consumes source DATA-PHASES, actual serialized parent schedule and fixed local
endpoint trace. Imports no emitter, optimizer, flow or upstream audit module.
"""
from collections import Counter,defaultdict
from pathlib import Path
import argparse,gzip,hashlib,json,copy

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
BASE=HERE/'inputs'
PHASE=BASE/'DATA-PHASES.json'
WORD=PACKAGE/'local/inputs/selected-complex-word.json.gz'
PINS={
 'OWNERS.json.gz':'892b49f97d4caa7e92918262ea3a8cfa8cbf273c92d574ae53bb89a61ee5e847',
 'inputs/HOSTED-PARENT.json.gz':'f713f8e66aaeaebb8202fe72bf36c7d23497152497342c27892e0fda3092f95b',
 'inputs/PLAN.json':'7b3122026e82b9d9e964d2a50c7bffdc976ae3dfea64bb98b2fdad5cfbdbaa20',
 'inputs/DATA-PHASES.json':'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
 '../local/data/forward.json':'a9d513bc1d85eb11184d73242a4016119f3968bb2a1ff9b365e78109778c17ee',
 '../local/inputs/selected-complex-word.json.gz':'16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def span(xs):
    out={0}
    for x in xs:out|={z^x for z in list(out)}
    return out
def basis(q):
    zero=next(i for i in range(9)if not(q>>i&1));a=q^(1<<zero);order=list(range(9));order[zero],order[0]=order[0],order[zero]
    b=[(1<<i)^(a if a>>i&1 else 0)for i in order]+[1<<i for i in range(9,73)]
    need(len(b)==73 and all((x&y).bit_count()%2==(i==j)for i,x in enumerate(b)for j,y in enumerate(b)),'actual orthonormal 73-column port chart')
    return b

def context(trace_path):
    need(sha(PHASE)=='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa','immutable actual DATA-PHASES')
    parent_path=BASE/'HOSTED-PARENT.json.gz';parent=read(parent_path);plan=read(BASE/'PLAN.json');ph=read(PHASE);word=read(WORD);trace=read(trace_path)
    need(parent['exact_data_phase_recipe_sha256']==sha(PHASE),'parent/phase binding')
    need((parent['m'],parent['live'],len(parent['calls']))==(73,7168,72),'actual parent dimensions')
    need([p['q']for p in ph['recipes']]==word['ports'],'local provider actual port labels')
    phase_rank={i:item['rank']for i,item in enumerate(ph['recipes'][0]['idle_children'])}
    stage_pair={e['stage']:e['pair']for e in parent['recipe']if e['kind']=='local'}
    calls={(e['stage'],e['replica']):e for e in parent['calls']};call_pos={};last={};windows={};pairs={};sides={}
    for pos,e in enumerate(parent['execution_schedule']):
        if 'replica'not in e:continue
        rep=e['replica'];kind=e['kind']
        if kind=='local_cover_sweep':call_pos[e['stage'],rep]=pos;last[rep,stage_pair[e['stage']]]=pos
        elif kind=='bridge':last[rep,e['src']]=last[rep,e['dst']]=pos
        elif kind=='idle_cover_sweep':
            for side,child in enumerate(e['child_indices']):
                if child not in phase_rank:continue
                need((child not in pairs)or(pairs[child],sides[child])==(e['pair'],side),'consistent pending family role')
                pairs[child],sides[child]=e['pair'],side;windows[rep,child]=(last.get((rep,e['pair']),-1),pos)
    need(len(call_pos)==72,'all physical calls in serialized schedule')
    for key,(cap,allowed)in plan['windows'].items():
        rep,child=map(int,key.split(','));lo,hi=windows[rep,child]
        actual=[t for t,call in enumerate(plan['order'])if lo<call_pos[tuple(call)]<hi]
        need(cap==phase_rank[child]and actual==allowed,'PLAN windows equal actual physical touch intervals including every bridge')
    charts=[]
    for port,recipe in enumerate(ph['recipes']):
        b=basis(recipe['q']);need(recipe['port']==port,'literal phase port')
        index={x:i for i,x in enumerate(b)}
        for child,record in enumerate(recipe['idle_children']):
            axes=list(map(int,record['orthogonal_axes']));need(len(axes)==phase_rank[child]and len(set(axes))==len(axes),'actual pending-child rank')
            need(all(x in index for x in axes),'pending axes belong to actual orthogonal physical chart')
        charts.append((b,index))
    widths={int(h):w for h,w in trace['helper_widths'].items()}
    for helper,width in widths.items():
        ep=trace['endpoints'][str(helper)];need(len(ep['final'])-len(ep['initial'])==width,'actual relative helper endpoint width')
        need(span(ep['initial'])<=span(ep['final']),'nested whole-helper endpoint frames')
    return dict(parent=parent,plan=plan,phase=ph,trace=trace,widths=widths,calls=calls,windows=windows,pairs=pairs,sides=sides,positions=call_pos,charts=charts,parent_path=parent_path,trace_path=trace_path)

def check(rows,c,export=False):
    p=c['plan'];widths=c['widths'];by=defaultdict(list);seen=set();used=defaultdict(set);sigmas={};routes=[];digest=hashlib.sha256();enters=0;cross=0
    need(len(rows)==72*len(widths),'exact complete role cardinality')
    for r in rows:
        t=r['time'];need(0<=t<72,'call time');stage,replica=p['order'][t]
        need((stage,replica)==(r['stage'],r['replica']),'literal call/order binding');h=r['helper'];w=r['width'];need(h in widths and w==widths[h],'actual helper width')
        role=(stage,replica,h);need(role not in seen,'unique helper role');seen.add(role)
        owner,child,port=r['owner_replica'],r['child'],r['port'];need(0<=owner<8 and 0<=port<112,'physical family coordinate')
        copy_id=owner*112+port;family=owner*896+(2*c['pairs'][child]+c['sides'][child])*112+port
        need((r['copy'],r['family'])==(copy_id,family),'actual data family identity')
        lo,hi=c['windows'][owner,child];need(lo<c['positions'][stage,replica]<hi,'actual owner untouched during entire invocation')
        actual=c['calls'][stage,replica];need(family not in{f for f,route in actual['owners'][:224]},'helper disjoint from all active source/target data families')
        b,index=c['charts'][port];pending=list(map(int,c['phase']['recipes'][port]['idle_children'][child]['orthogonal_axes']));off=r['offset']
        need(0<=off and off+w<=len(pending),'literal pending-axis block')
        block=pending[off:off+w];occupied=[index[x]for x in block];spectators=[j for j in range(73)if j not in occupied][:9-w]
        perm=occupied+spectators+[j for j in range(73)if j not in occupied and j not in spectators]
        need(sorted(perm)==list(range(73))and len(set(occupied+spectators))==9,'full 73-axis permutation and complete local 9-dimensional chart')
        sigma=[b[j]for j in perm];need(sigma[:w]==block,'actual normalized child axes equal inherited pending block')
        sid=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigmas[sid]=sigma
        cells=set(range(off,off+w));key=(owner,child,port);need(not used[key]&cells,'all physical pending blocks disjoint');used[key]|=cells
        by[t].append(family);cross+=owner!=replica;enters+=w<9
        route=[3,child,off]if w==9 else[4,child,off,w,spectators]
        descriptor=[stage,replica,h,family,sid,route];digest.update(json.dumps(descriptor,separators=(',',':')).encode()+b'\n')
        if export:routes.append(descriptor)
    need(seen=={(s,r,h)for s,r in p['order']for h in widths},'every literal role present')
    need(all(len(fs)==len(set(fs))==len(widths)for fs in by.values()),'one helper per complete physical family invocation')
    idle=Counter();idle_rows=[]
    for owner in range(8):
        for port,recipe in enumerate(c['phase']['recipes']):
            for child,record in enumerate(recipe['idle_children']):
                cells=used[owner,child,port];need(cells==set(range(len(cells))),'chronological coordinate blocks form exact occupied prefix')
                axes=list(map(int,record['orthogonal_axes']));tail=axes[len(cells):]
                if tail:
                    idle[len(tail)]+=1
                    if export:idle_rows.append([owner,child,port,len(cells),tail])
    profile=Counter(idle)
    for rank,count in c['trace']['local_profile'].items():profile[int(rank)]+=count*72
    mass=sum(r*n for r,n in profile.items());need(mass==520704,'complete inherited coverage rank mass');need(73*7168-mass==2560,'actual exact deficit')
    result=dict(status='PASS_INDEPENDENT_ACTUAL_OWNER_CHARTS',roles=len(rows),helpers_per_call=len(widths),actual_source_data_families_per_call=224,actual_73column_charts=len(sigmas),relative_endpoint_types=len({(tuple(ep['initial']),tuple(ep['final']))for h,ep in c['trace']['endpoints'].items()if int(h)>=224}),entering_helper_roles=enters,cross_replica_roles=cross,derived_windows=len(c['windows']),chart_digest=digest.hexdigest(),idle=dict(sorted(idle.items())),profile=dict(sorted(profile.items())),paid_mass=mass,deficit=2560)
    return result,dict(schema='actual-whole-owner-orthogonal-charts/1',unique_73column_charts=sigmas,whole_helper_routes=routes,actual_idle_complements=idle_rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,help='Optional external directory for regenerated receipt and chart certificate')
    args=parser.parse_args()
    if args.out is not None:
        dest=args.out.resolve()
        need(not dest.is_relative_to(PACKAGE.resolve()),'--out must be outside the published package')
        need(not (dest/'OWNERS-RECEIPT.json').exists() and not (dest/'OWNERS-CHARTS.json.gz').exists(),'refuse to overwrite an existing replay receipt')
    for rel,expected in PINS.items():
        need(sha(HERE/rel)==expected,'immutable source pin: '+rel)
    owners=HERE/'OWNERS.json.gz'
    trace=PACKAGE/'local/data/forward.json'
    c=context(trace)
    rows=read(owners)
    result,charts=check(rows,c,True)
    need(charts==read(HERE/'CHARTS.json.gz'),'complete regenerated physical chart certificate')
    controls=[]
    for name in ('wrong-copy-index','wrong-family','overflow-offset','wrong-width','omitted-role'):
        bad=copy.deepcopy(rows)
        if name=='wrong-copy-index':bad[0]['copy']+=112
        elif name=='wrong-family':bad[0]['family']+=1
        elif name=='overflow-offset':bad[0]['offset']=73
        elif name=='wrong-width':bad[0]['width']+=1
        else:bad.pop()
        try:check(bad,c)
        except (ValueError,KeyError):controls.append(name)
        else:raise ValueError('owner mutation accepted: '+name)
    result.update(owners_sha256=sha(owners),source_trace_sha256=sha(trace),parent_template_sha256=sha(c['parent_path']),source_plan_sha256=sha(BASE/'PLAN.json'),actual_DATA_PHASES_sha256=sha(PHASE),controls_rejected=controls)
    # JSON round-trip normalizes integer rank keys to the public JSON ABI.
    result=json.loads(json.dumps(result))
    need(result==read(HERE/'EXPECTED.json'),'complete expected mathematical receipt')
    if args.out is not None:
        dest.mkdir(parents=True,exist_ok=True)
        (dest/'OWNERS-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        (dest/'OWNERS-CHARTS.json.gz').write_bytes(gzip.compress(json.dumps(charts,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
