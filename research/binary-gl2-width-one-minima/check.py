"""Independent complete-domain distance proof using full eight-column operators.

Does not import verify.py, its generator, its BFS or a predecessor executable.
"""
import hashlib
from itertools import permutations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
POINTS=(1,2,3,5,6,7)
ID8=tuple(1<<i for i in range(8))
EVEN=(10,12,160,192)

def need(ok,message):
    if not ok: raise ValueError(message)

def read(path):
    def unique(items):
        out={}
        for k,v in items:
            need(k not in out,'duplicate JSON key')
            out[k]=v
        return out
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique)

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'))

def authenticate():
    manifest=read(HERE/'SOURCES.json')
    for home,rows in ((ROOT,manifest['files']),(HERE,manifest['retained_sources'])):
        for row in rows:
            if row.get('usage')=='provenance': continue
            raw=(home/row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA mismatch')
            need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source blob mismatch')

def apply(columns,value):
    result=0
    for j,column in enumerate(columns):
        if value>>j&1: result^=column
    return result

def full_from_active(columns):
    images=[apply(EVEN,col) for col in columns]
    result=[]
    for role in range(2):
        c=14<<(4*role)
        a,b=images[2*role:2*role+2]
        result.extend((1<<(4*role),c^b,c^a,c^a^b))
    return tuple(result)

# This is merely an injective serialization of the six nonzero-address rows.
# All semantic calculations and word checks use full eight-column operators.
KEY_PARTS=tuple(tuple(sum(((value>>POINTS[i])&1)<<(6*i+j) for i in range(6)) for value in range(256)) for j in range(6))
def key(columns):
    return sum(KEY_PARTS[j][columns[p]] for j,p in enumerate(POINTS))

def domain():
    out={}
    for a in range(1,16):
        first={0,a}
        for b in range(1,16):
            if b in first: continue
            second=first|{x^b for x in first}
            for c in range(1,16):
                if c in second: continue
                third=second|{x^c for x in second}
                for d in range(1,16):
                    if d in third: continue
                    full=full_from_active((a,b,c,d))
                    encoded=key(full)
                    need(encoded not in out,'active embedding injective')
                    out[encoded]=full
    need(len(out)==15*14*12*8==20160,'entire active GL4 domain')
    return out

def alphabet():
    out=[]
    labels=((0,1,3,2),(0,3,2,1))
    for which,g in enumerate(labels):
        for u in range(1,4):
            for v in range(1,4):
                if ((u&v).bit_count()&1)==0: continue
                columns=[]
                for source in range(2):
                    for point in range(4):
                        image=1<<(4*source+point)
                        if v>>source&1:
                            for target in range(2):
                                if u>>target&1:
                                    image^=(1<<(4*target+point))^(1<<(4*target+g[point]))
                        columns.append(image)
                table=tuple(apply(columns,x) for x in range(256))
                need(all(table[table[x]]==x for x in range(256)),'each full paid map involutive')
                out.append(((which,u,v),tuple(columns),table))
    need(len(out)==12 and len({x[1] for x in out})==12,'twelve distinct actual paid maps')
    return out

def target_columns(p,q):
    return tuple(1<<(4*r+(0 if x==0 else perm[x-1]+1)) for r,perm in enumerate((p,q)) for x in range(4))

def direct_length(p):
    order=(0,2,1)  # point order1,3,2 makes the two labels adjacent swaps
    ranks=tuple(order.index(p[x]) for x in order)
    return sum(ranks[i]>ranks[j] for i in range(3) for j in range(i+1,3))

def audit(rows,receipt):
    operators=domain()
    need(type(rows) is list and all(type(row) is list and len(row)==2 and all(type(x) is int for x in row) for row in rows),'typed distance rows')
    need(rows==sorted(rows),'sorted complete distance rows')
    distances=dict(rows)
    need(len(distances)==len(rows),'unique distance states')
    need(set(distances)==set(operators),'complete independently enumerated domain')
    identity=key(ID8)
    need(distances[identity]==0 and all(d>0 for state,d in rows if state!=identity),'unique zero and positive distances')
    gates=alphabet()
    edges=0
    for state,columns in operators.items():
        distance=distances[state]
        descending=state==identity
        for _,_,table in gates:
            following=tuple(table[col] for col in columns)
            neighbor=key(following)
            need(neighbor in operators and operators[neighbor]==following,'full operator graph closure')
            need(abs(distance-distances[neighbor])<=1,'distance edge inequality')
            descending |= distances[neighbor]==distance-1
            edges+=1
        need(descending,'nonidentity descending neighbor')
    need(edges==241920,'all directed transitions checked')
    need(receipt['alphabet']==[list(g[0]) for g in gates],'independent paid alphabet')
    observed=[]
    for row in receipt['targets']:
        p,q=map(tuple,row['points'])
        need(sorted(p)==sorted(q)==[0,1,2],'monomial target points')
        full=target_columns(p,q)
        state=key(full)
        distance=distances[state]
        direct=direct_length(p)+direct_length(q)
        need(row['state']==state and row['distance']==distance==row['direct']==direct,'exact actual target minimum')
        actual=ID8
        for index in row['word']:
            need(type(index) is int and 0<=index<12,'paid witness index')
            table=gates[index][2]
            actual=tuple(table[x] for x in actual)
        need(actual==full and len(row['word'])==distance,'all eight dirty witness columns')
        observed.append((p,q))
    all_targets={(p,q) for p in permutations(range(3)) for q in permutations(range(3))}
    need(len(observed)==36 and set(observed)==all_targets,'all ordered targets exactly once')
    need(receipt['distance_sha256']==hashlib.sha256(canonical(rows).encode()).hexdigest(),'complete distance digest')
    histogram={d:sum(value==d for value in distances.values()) for d in set(distances.values())}
    need(receipt['layers']==[list(x) for x in sorted(histogram.items())],'full graph layers')
    need(receipt['states']==20160 and receipt['directed_edges']==edges and receipt['diameter']==max(histogram),'graph summary')
    return {'states':len(operators),'edges':edges,'targets':len(observed),'full_columns':len(observed)*8,'diameter':max(histogram)}

def main():
    authenticate()
    result=audit(read(HERE/'DISTANCES.json'),read(HERE/'RESULT.json'))
    print('PASS_GL2_WIDTH_ONE_INDEPENDENT '+canonical(result))

if __name__=='__main__': main()
