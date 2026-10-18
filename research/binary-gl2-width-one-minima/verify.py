"""Exact BFS on normalized full-stream GL2,w=1,two-role operators."""
import argparse
from collections import Counter,deque
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
POINT_LABELS=((0,2,1),(2,1,0))  # actual point order1,2,3
IDENTITY=sum(1<<(7*i) for i in range(6))

def need(ok,message):
    if not ok: raise ValueError(message)

def read_json(path):
    def pairs(items):
        out={}
        for k,v in items:
            need(k not in out,'duplicate JSON key')
            out[k]=v
        return out
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=pairs)

def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'))

def source_check():
    manifest=read_json(HERE/'SOURCES.json')
    checked=[]
    rows=[(ROOT,row) for row in manifest['files'] if row['usage']=='input']
    rows += [(HERE,row) for row in manifest['retained_sources']]
    for parent,row in rows:
        raw=(parent/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA mismatch: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob mismatch')
        checked.append(row['path'])
    return checked

def point_paths():
    identity=(0,1,2)
    paths={identity:()}
    queue=deque([identity])
    while queue:
        p=queue.popleft()
        for k,g in enumerate(POINT_LABELS):
            q=tuple(g[p[i]] for i in range(3))
            if q not in paths:
                paths[q]=paths[p]+(k,)
                queue.append(q)
    need(len(paths)==6,'six point permutations')
    return paths

def generators():
    out=[]
    for k,pair in enumerate(((1,2),(0,2))):
        for u in (1,2,3):
            for v in (1,2,3):
                if (u&v).bit_count()%2!=1: continue
                dest=[3*r+p for r in range(2) if u>>r&1 for p in pair]
                src=[3*r+p for r in range(2) if v>>r&1 for p in pair]
                out.append((k,u,v,tuple(src),sum(1<<(6*i) for i in dest)))
    need(len(out)==12,'complete paid alphabet')
    return out

def step(state,gate):
    q=0
    for j in gate[3]: q^=(state>>(6*j))&63
    return state^(q*gate[4])

def target(p,q):
    return sum(1<<(6*(3*r+perm[i])+3*r+i) for r,perm in enumerate((p,q)) for i in range(3))

def replay(word,alphabet):
    state=IDENTITY
    for k in word:
        need(type(k) is int and 0<=k<len(alphabet),'paid index')
        state=step(state,alphabet[k])
    return state

def kernel_control(alphabet):
    source=read_json(HERE/'source/pr2599/RESULT.json')['legal_word']['word']
    coordinate={g[0]:i for i,g in enumerate(alphabet) if g[1:3]==(1,1)}
    state=IDENTITY
    for op,k in source:
        if op=='D': state=step(state,alphabet[coordinate[k]])
        else:
            need(op=='X','source word label')
            for point in range(3):
                state^=((state>>(6*(3+point)))&63)<<(6*point)
    need(state==IDENTITY,'source norm word aliases identity at this width')
    return {'credited_source':'PR2599','paid':18,'free':10,'actual_endpoint_identity':True}

def calculate():
    sources=source_check()
    gates=generators()
    seen={IDENTITY:(0,None,None)}
    queue=deque([IDENTITY])
    while queue:
        state=queue.popleft()
        distance=seen[state][0]+1
        for k,g in enumerate(gates):
            out=step(state,g)
            if out not in seen:
                seen[out]=(distance,state,k)
                queue.append(out)
    rows=[[state,value[0]] for state,value in sorted(seen.items())]
    paths=point_paths()
    targets=[]
    for p,ppath in paths.items():
        for q,qpath in paths.items():
            endpoint=target(p,q)
            need(endpoint in seen,'target reachable')
            distance=seen[endpoint][0]
            word=[]
            cursor=endpoint
            while seen[cursor][1] is not None:
                _,previous,k=seen[cursor]
                word.append(k)
                cursor=previous
            word.reverse()
            need(replay(word,gates)==endpoint,'complete target endpoint')
            direct=len(ppath)+len(qpath)
            need(distance==direct,'all target minima equal direct lengths')
            targets.append({'points':[list(p),list(q)],'state':endpoint,'distance':distance,'direct':direct,'word':word})
    layers=sorted(Counter(row[0] for row in seen.values()).items())
    result={'schema_version':1,'domain':{'d':2,'w':1,'roles':2,'payload_columns':8},
            'sources':sources,'alphabet':[list(g[:3]) for g in gates],
            'states':len(seen),'directed_edges':len(seen)*len(gates),'diameter':max(row[0] for row in seen.values()),
            'layers':[list(x) for x in layers],'distance_sha256':hashlib.sha256(canonical(rows).encode()).hexdigest(),
            'targets':targets,'target_minimum_histogram':dict(sorted(Counter(t['distance'] for t in targets).items())),
            'credited_alias_control':kernel_control(gates),'new_selected_exponent':False}
    return rows,result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-new',type=Path,help='create a new evidence directory; never overwrite')
    args=parser.parse_args()
    rows,result=calculate()
    if args.write_new:
        args.write_new.mkdir(exist_ok=False)
        for name,value in [('DISTANCES.json',rows),('RESULT.json',result)]:
            (args.write_new/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    else:
        need(canonical(read_json(HERE/'DISTANCES.json'))==canonical(rows),'complete distance evidence mismatch')
        need(canonical(read_json(HERE/'RESULT.json'))==canonical(result),'typed result mismatch')
    print('PASS_GL2_WIDTH_ONE_BFS states='+str(len(rows))+' edges='+str(result['directed_edges'])+' targets=36 no_saving')

if __name__=='__main__': main()
