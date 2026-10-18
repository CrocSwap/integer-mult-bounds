#!/usr/bin/env python3
"""Reproduce the literal pure44 fill from immutable borrow43 inputs."""
import argparse,collections,gzip,hashlib,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)
def packed(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)
def rank(vectors):
    piv={}
    for x in vectors:
        while x:
            b=x.bit_length()-1
            if b in piv:x^=piv[b]
            else:piv[b]=x;break
    return len(piv)
def helper_widths(word):
    origin=[r for r in range(224,704)if r not in word['removed']];full=[1<<i for i in range(9)]
    return origin,[rank(word['helper_final'].get(str(r),full))-rank(word['start_extra'].get(str(r),[]))for r in origin]
def family(key,plan):
    replica,child,port=key
    return replica*896+(2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112+port
def materialize(fill,order,widths,plan):
    result=[]
    for t,h,rep,child,port,offset in fill['rows']:
        need(type(t)is int and 0<=t<len(order)and type(h)is int and 0<=h<len(widths),'literal time/helper bounds')
        stage,replica=order[t];key=rep,child,port
        result.append(dict(stage=stage,replica=replica,time=t,helper=h,width=widths[h],owner_replica=rep,child=child,port=port,offset=offset,copy=112*rep+port,family=family(key,plan)))
    return sorted(result,key=lambda r:(r['time'],r['helper']))
def orthogonal_basis(q):
    z=next(i for i in range(9)if not(q>>i&1));u=q^(1<<z);indices=list(range(9));indices[0],indices[z]=indices[z],indices[0]
    columns=[(1<<i)^(u if u>>i&1 else 0)for i in indices]+[1<<i for i in range(9,73)]
    need(columns[0]==q and all((a&b).bit_count()%2==(i==j)for i,a in enumerate(columns)for j,b in enumerate(columns)),'actual full orthogonal port chart')
    return set(columns)
def validate(rows,order,widths,plan,windows,parent,phases):
    need(len(rows)==666*436,'complete finite role count')
    helpers=collections.defaultdict(set);families=collections.defaultdict(set);slots=collections.defaultdict(set)
    basis=[orthogonal_basis(r['q'])for r in phases['recipes']]
    axes={(c['child'],c['port']):phases['recipes'][c['port']]['idle_children'][c['child']]['orthogonal_axes']for c in parent['idle_children']}
    need(len(axes)==2016,'complete actual parent child/port axis records')
    for c in parent['idle_children']:
        a=axes[c['child'],c['port']]
        need(len(a)==c['rank']and len(set(a))==len(a)and set(a)<=basis[c['port']],'literal source child axes and rank')
    for r in rows:
        t,h=r['time'],r['helper'];need(type(t)is int and 0<=t<666 and type(h)is int and 0<=h<436,'literal role index bounds')
        need((r['stage'],r['replica'])==tuple(order[t])and r['width']==widths[h],'actual call and ordered helper width')
        rep,child,port=r['owner_replica'],r['child'],r['port'];key=rep,child,port
        need(type(rep)is int and 0<=rep<74 and type(port)is int and 0<=port<112,'physical owner bounds')
        need(r['family']==family(key,plan)and r['copy']==112*rep+port,'actual physical family and copy ABI')
        cap,times=windows[f'{rep},{child}'];need(t in times,'actual strict source-event window')
        need(h not in helpers[t]and r['family']not in families[t],'one complete helper per physical family per call')
        helpers[t].add(h);families[t].add(r['family'])
        offset,w=r['offset'],r['width'];need(type(offset)is int and 0<=offset and offset+w<=cap,'literal source axis bounds')
        owned=set(range(offset,offset+w));need(not slots[key]&owned,'disjoint same-family literal child factors');slots[key]|=owned
        literal=axes[child,port][offset:offset+w]
        need(len(literal)==w and len(set(literal))==w and set(literal)<=basis[port],'each role uses its literal source axes')
    need(set(helpers)==set(range(666))and all(h==set(range(436))for h in helpers.values()),'every complete helper occurs exactly once')
    idle=collections.Counter();hosted=remaining=translations=0
    for window,(cap,times)in windows.items():
        rep,child=map(int,window.split(','))
        for port in range(112):
            key=rep,child,port;occupied=slots[key];need(occupied==set(range(len(occupied))),'compacted pending prefix')
            source=axes[child,port];need(len(source)==cap,'capacity from actual source child rank')
            left=cap-len(occupied)
            if left:idle[left]+=1
            hosted+=len(occupied);remaining+=left;translations+=1
    return dict(idle_profile=dict(sorted(idle.items())),hosted_axis_factors=hosted,literal_remaining_axis_factors=remaining,source_child_translations_retained=translations)
def build():
    pins=read(HERE/'SOURCES.json')['files']
    for relative,pin in pins.items():need(sha(ROOT/relative)==pin,'frozen source drift: '+relative)
    before={p:sha(ROOT/p)for p in pins}
    plan=read(ROOT/'inputs/PLAN.json');parent=read(ROOT/'inputs/GLOBAL-TEMPLATE.json.gz');phases=read(HERE/'inputs/DATA-PHASES.json')
    need(plan['T']==37 and plan['M']==73,'retained37 geometry')
    order=[[s,r+37*g]for s,r in plan['order']for g in range(2)]
    need(len(order)==666 and len(set(map(tuple,order)))==666,'all74 replicas and9 stages')
    need(parent['exact_data_phase_recipe_sha256']==sha(HERE/'inputs/DATA-PHASES.json'),'parent-pinned exact phase recipe')
    sp=importlib.util.spec_from_file_location('repack_actual_parent_windows',ROOT/'vendor/build_parent.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    windows,schedule=mod.actual_windows(parent,order)
    mapping=read(ROOT/'new/borrow-extension/inputs/HELPER-MAPPING-44.json');providers=read(HERE/'inputs/PROVIDERS43.json')
    old_width=new_width=index_map=None
    for pid,kind in [('gauge44','base'),('extra','extra')]:
        old=read(ROOT/('new/borrow/words/BORROW-WORD-43'+kind+'.json.gz'));new=read(ROOT/('new/borrow-extension/words/BORROW-WORD-44'+kind+'.json.gz'))
        origin,ow=helper_widths(old);target,nw=helper_widths(new);imap=[target.index(x)if x in target else None for x in origin]
        need(ow==providers[pid]['widths'],'original ordered437 helper widths')
        need(imap==mapping[kind]['old_to_new']and nw==mapping[kind]['widths'],'actual44 endpoint helper map binding')
        need([i for i,j in enumerate(imap)if j is None]==[384]and origin[384]==619 and ow[384]==4,'pure original619 deletion')
        need(all(ow[i]==nw[j]for i,j in enumerate(imap)if j is not None),'no collateral residual width change')
        if index_map is None:old_width,new_width,index_map=ow,nw,imap
        else:need((old_width,new_width,index_map)==(ow,nw,imap),'common actual436 helper interfaces')
    oldrows=materialize(read(HERE/'inputs/FILL43.json.gz'),order,old_width,plan)
    need(hashlib.sha256(packed(oldrows)).hexdigest()==read(HERE/'SOURCES.json')['old_owner_payload_sha256'],'exact retained43 owner reconstruction')
    delta=read(HERE/'DELTA.json.gz');seen=set()
    for change in delta['changes']:
        i=change['row'];need(i not in seen and oldrows[i]==change['before'],'six-row packing delta source binding');seen.add(i)
        need(all(change['before'][k]==change['after'][k]for k in ['time','stage','replica','helper','width']),'packing preserves complete local invocation')
        oldrows[i]=change['after']
    need(len(seen)==6,'complete six-row packing delta')
    rows=[]
    for row in oldrows:
        h=index_map[row['helper']]
        if h is not None:rows.append(dict(row,helper=h))
    bins=collections.defaultdict(list)
    for r in rows:bins[r['owner_replica'],r['child'],r['port']].append(r)
    for rr in bins.values():
        offset=0
        for r in sorted(rr,key=lambda r:(r['time'],r['helper'])):r['offset']=offset;offset+=r['width']
    receipt=validate(rows,order,new_width,plan,windows,parent,phases)
    controls=[]
    def rejects(label,changed):
        try:validate(changed,order,new_width,plan,windows,parent,phases)
        except (ValueError,KeyError):controls.append(label)
        else:raise ValueError('mutation accepted: '+label)
    bad=list(rows);bad[0]=dict(rows[0],width=rows[0]['width']+1);rejects('wrong_helper_residual_width',bad)
    bad=list(rows);bad[0]=dict(rows[0],offset=73);rejects('literal_axis_out_of_bounds',bad)
    bad=list(rows);bad[1]=dict(rows[1],**{k:rows[0][k]for k in ['owner_replica','child','port','copy','family']});rejects('cross_role_physical_family_alias',bad)
    bad=list(rows);key=(73,17,0);bad[0]=dict(rows[0],owner_replica=73,child=17,port=0,copy=112*73,family=family(key,plan));rejects('owner_outside_actual_pending_window',bad)
    native=collections.Counter()
    for pid,count in [('extra',666)]:
        pp={int(r):n for r,n in providers[pid]['actual_paid_profile'].items()};pp[4]-=1;native.update({r:n*count for r,n in pp.items()})
    profile=native+collections.Counter(receipt['idle_profile']);rank_mass=sum(r*n for r,n in profile.items())
    need(73*plan['live']*2-rank_mass==2*plan['deficit'],'exact paid mass deficit')
    fill={'columns':['time','helper','owner_replica','child','port','offset'],'dispatch_overrides':[[s,r,'extra']for s,r in order],'rows':[[r[k]for k in ['time','helper','owner_replica','child','port','offset']]for r in rows]}
    result=dict(status='PASS_SOURCE_BOUND_PURE44_LITERAL_REPACK',roles=len(rows),helpers=436,calls=666,provider_counts={'extra':666},profile=dict(sorted(profile.items())),rank_mass=rank_mass,mutations_rejected=controls,fill_payload_sha256=hashlib.sha256(packed(fill)).hexdigest(),owners_payload_sha256=hashlib.sha256(packed(rows)).hexdigest(),**receipt)
    need({p:sha(ROOT/p)for p in pins}==before,'source changed during replay')
    return fill,rows,result
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    need(not args.out.resolve().is_relative_to(ROOT),'output must be outside source package');need(not args.out.exists(),'fresh output directory required')
    fill,rows,result=build();expected=read(HERE/'EXPECTED.json');need(json.loads(packed(result))==expected,'exact repack receipt differs')
    args.out.mkdir(parents=True,exist_ok=False)
    for name,value in [('FILL.json.gz',fill),('OWNERS.json.gz',rows)]:
        data=bytearray(gzip.compress(packed(value),mtime=0));data[9]=255;(args.out/name).write_bytes(data)
    (args.out/'PROFILE.json').write_text(json.dumps(result['profile'],sort_keys=True,separators=(',',':'))+'\n');(args.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
