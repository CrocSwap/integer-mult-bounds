#!/usr/bin/env python3
"""List legal equal-frame scalar products at all native schedule cuts."""
from collections import defaultdict,Counter
from fractions import Fraction as F
import gzip,json
from hashlib import sha256
from pathlib import Path
import probe_readiness as p
HERE=Path(__file__).resolve().parent

def main():
    item=p.core['providers']['base'];word=item['canonical'];events=item['programs']['forward'];n=len(word['start'])
    sources=list(range(112))+list(range(224,n));allowed={i for i in range(224,n) if word['start'][i]==0}
    source_frame={i:word['start'][i] for i in sources};target_frame={i:0 for i in range(112)}
    source_groups=defaultdict(set);target_groups=defaultdict(set)
    for i,f in source_frame.items():source_groups[f].add(i)
    for i,f in target_frame.items():target_groups[f].add(i)
    tails=[{i:F(1)} for i in range(112)]
    source_pool=[];source_ids={};tail_pool=[];tail_ids={};products={};checks=0
    source_current={}
    def source_id(field,state):
        row=state[field]
        constrained=tuple(sorted((s,ops,c.numerator,c.denominator) for (s,ops),c in row.items() if s not in allowed or ops))
        if not constrained:return None
        if constrained not in source_ids:
            source_ids[constrained]=len(source_pool)
            source_pool.append({'constrained':constrained,'complete':tuple(sorted((s,ops,c.numerator,c.denominator) for (s,ops),c in row.items()))})
        return source_ids[constrained]
    def tail_id(target):
        row=tuple(sorted((i,c.numerator,c.denominator) for i,c in tails[target].items()))
        if row not in tail_ids:tail_ids[row]=len(tail_pool);tail_pool.append(row)
        return tail_ids[row]
    def consider(field,target,pos,state,frames):
        nonlocal checks
        checks+=1
        p.need(frames[field]==frames[112+target],'Equal actual frames')
        sid=source_current.get(field)
        if sid is None:return
        tid=tail_id(target);key=(sid,tid)
        if key not in products:
            products[key]={'source_row':sid,'tail_column':tid,'after_event':pos,'source_field':field,'target_Y_port':target,'frame':frames[field]}
    def changed_source(field,pos,state,frames):
        old=source_frame[field];new=frames[field]
        if old!=new:source_groups[old].remove(field);source_groups[new].add(field);source_frame[field]=new
        source_current[field]=source_id(field,state)
        for target in target_groups[new]:consider(field,target,pos,state,frames)
    def changed_target(target,pos,state,frames):
        old=target_frame[target];new=frames[112+target]
        if old!=new:target_groups[old].remove(target);target_groups[new].add(target);target_frame[target]=new
        for field in source_groups[new]:consider(field,target,pos,state,frames)
    def observe(pos,event,state,frames):
        if event is None:
            for field in sources:changed_source(field,pos,state,frames)
            return
        tag=event[0]
        if tag=='scalar':
            op=event[1];t=op[1]
            if t[0]=='L' and t[1] in source_frame:changed_source(t[1],pos,state,frames)
            if t[0]=='L' and 112<=t[1]<224:
                target=t[1]-112
                if op[0]=='add' and op[2][0]=='L' and 112<=op[2][1]<224:
                    source=op[2][1]-112;p.e.add(tails[source],tails[target],-F(*op[3:5]));changed_target(source,pos,state,frames)
                elif op[0]=='scale':
                    c=F(*op[2:4]);tails[target]={i:v/c for i,v in tails[target].items()};changed_target(target,pos,state,frames)
        elif tag=='climb':
            field=event[2]
            if field in source_frame:changed_source(field,pos,state,frames)
            elif 112<=field<224:changed_target(field-112,pos,state,frames)
        elif tag=='warp':
            field=event[1]
            if field[0]=='L' and field[1] in source_frame:changed_source(field[1],pos,state,frames)
    identity={i:{(i,()):F(1)} for i in range(n+8)}
    p.replay(events,identity,word,False,observe)
    p.need(tails==[{i:F(1)} for i in range(112)],'Y scalar endpoint identity')
    output={'schema':'native-all-cut-equal-frame-products-v1','source_core_sha256':p.PIN,'provider':'base','initial_I_helpers':sorted(allowed),'source_rows':source_pool,'tail_columns':tail_pool,'products':list(products.values()),'all_considered_pairs':checks,'scope':'New one-way X/helper-to-Y ADDs at exact equal-frame cuts. Existing native chains and Y scalar subword remain fixed. Raw I-helper debt is quotiented but complete representative source rows are retained.'}
    raw=(json.dumps(output,separators=(',',':'),sort_keys=True)+'\n').encode()
    (HERE/'ALL-CUT-EDGES.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    report={'source_rows':len(source_pool),'tail_columns':len(tail_pool),'distinct_products':len(products),'all_considered_pairs':checks,'payload_decompressed_sha256':sha256(raw).hexdigest(),'payload_compressed_sha256':sha256((HERE/'ALL-CUT-EDGES.json.gz').read_bytes()).hexdigest(),'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    (HERE/'ALL-CUT-EDGES.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(report,flush=True)
if __name__=='__main__':main()
