"""Deterministic declared staged entrance edit; Python standard library only.

The record contains every scalar edit and solved-frame preimage. This applier
does not search or optimize frames and derives inverse cleanup literally.
"""
import copy,gzip,hashlib,json,sys
from pathlib import Path

def canonical(w):
    return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def require(ok,why):
    if not ok:raise ValueError(why)

def cleanup(w):
    n=2*w['report']['v']+w['report']['R'];rest=set(map(int,w['helper_final']))
    full=[256,128,64,32,16,8,4,2,1];fw=list(w['A'][w['prelude_events']:]);by={}
    for op,rec in enumerate(w['warps'],1):by.setdefault(rec[0],[]).append(['warp',rec[1],op])
    for i in range(len(w['B'])+1):
        fw+=by.get(i,[])
        if i<len(w['B']):fw.append(w['B'][i])
    fw+=w['restore'];out=[]
    buf=lambda r:r+n if r in rest else r
    for g in reversed(fw):
        if g[0]=='warp':out.append(['warp',buf(g[1]),-g[2],list(full)])
        elif 112<=g[1]<224:continue
        elif g[0]=='add':out.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],list(full)])
        else:
            require(g[0]=='scale','unknown cleanup primitive')
            out.append(['scale',buf(g[1]),g[3],g[2],list(full)])
    return out

def apply(parent,record):
    require(record['schema']=='staged-entering-pair-v1','record schema')
    require(canonical(parent)==record['source_canonical_sha256'],'source word digest')
    require(set(record['pivots'])=={644,660},'exact two pivots')
    x=copy.deepcopy(parent)
    deleted={r['index']:r['old'] for r in record['B_deleted']}
    require(set(deleted)==set(range(184,188))|set(range(216,220)),'exact deleted indices')
    require(all(parent['B'][i]==g for i,g in deleted.items()),'deleted scalar preimages')
    added={r['before']:r['gates'] for r in record['B_inserted']}
    require(set(added)=={599,647},'exact release cuts')
    require([[g[:-1] for g in added[i]] for i in (599,647)]==[
        [['add',640,644,2,1],['add',496,644,-2,1]],
        [['add',656,660,-1,1],['add',520,660,-2,1]]],'exact release scalars')
    bframes={r['parent_index']:r for r in record['B_frame_edits']};nb=[];positions={}
    for i in range(len(parent['B'])+1):
        positions[i]=len(nb);nb+=copy.deepcopy(added.get(i,[]))
        if i==len(parent['B']) or i in deleted:continue
        g=copy.deepcopy(parent['B'][i])
        if i in bframes:
            r=bframes[i];require(g[-1]==r['old'],'B frame preimage')
            g[-1]=copy.deepcopy(r['new'])
        nb.append(g)
    require(set(bframes)<=set(range(len(parent['B'])))-set(deleted),'B frame index')
    x['B']=nb
    for rec in x['warps']:rec[0]=positions[rec[0]]
    for sec in ('A','restore'):
        seen=set()
        for r in record[sec+'_frame_edits']:
            i=r['index'];require(i not in seen,'duplicate frame edit');seen.add(i)
            require(x[sec][i][-1]==r['old'] and x[sec][i][0]!='warp',sec+' frame preimage')
            x[sec][i][-1]=copy.deepcopy(r['new'])
    require(record['start_frames']=={'644':{'old':[30],'new':[429,30]},'660':{'old':[30],'new':[429,30]}},'exact paired entrances')
    for h,r in record['start_frames'].items():
        require(x['start_extra'][h]==r['old'] and h not in x['helper_final'],'ordinary FULL helper entrance')
        x['start_extra'][h]=list(r['new'])
    require(set(record['report'])=={'local_profile','width_inventory'},'only derived report fields')
    x['report'].update(copy.deepcopy(record['report']))
    x['cleanup']=cleanup(x)
    require(canonical(x)==record['target_canonical_sha256'],'reconstructed target digest')
    return x

def main():
    p,r,o=map(Path,sys.argv[1:]);raw=p.read_bytes();recraw=r.read_bytes()
    parent=json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
    record=json.loads(gzip.decompress(recraw) if r.suffix=='.gz' else recraw)
    require(hashlib.sha256(raw).hexdigest()==record['source_compressed_sha256'],'source compressed digest')
    out=bytearray(gzip.compress(json.dumps(apply(parent,record),separators=(',',':')).encode(),compresslevel=9,mtime=0))
    # CPython versions differ in the non-semantic gzip OS header byte.
    # The frozen word uses the recorded byte; the DEFLATE payload is retained.
    out[9]=record['gzip_os_byte'];out=bytes(out)
    require(hashlib.sha256(out).hexdigest()==record['target_compressed_sha256'],'literal target byte digest')
    o.write_bytes(out);print('PASS_DETERMINISTIC_STAGED_ENTRANCE_PAIR',record['provider'])

if __name__=='__main__':main()
