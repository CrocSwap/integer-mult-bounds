"""Independent four-vertex permutation census and direct invoice replay."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];OLD=ROOT/'research/r439-helper-matching'


def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    expected=json.loads((P/'EXPECTED.json').read_text());pins=json.loads((P/'SOURCES.json').read_text())
    for source in ('research/r439-helper-matching/NOMINATION.json','research/r439-helper-matching/vendor/pr915/candidate.json.gz'):
        data=(ROOT/source).read_bytes();data=data if source.endswith('.gz') else data.replace(b'\r\n',b'\n')
        need(hashlib.sha256(data).hexdigest()==pins['files'][source],'source hash')
    parent=json.loads(gzip.decompress((OLD/'vendor/pr915/candidate.json.gz').read_bytes()))
    nominations=json.loads((OLD/'NOMINATION.json').read_text())['nominations'];v=parent['v'];n=2*v+parent['R']
    cols=[set() for _ in range(parent['R'])]
    for _,target,donors in parent['D'][306:306+v]:
        for donor in donors:cols[donor-2*v].symmetric_difference_update({target-v})
    def gain(pair):
        a,b=pair;return len(cols[b])-len(cols[a]^cols[b])-2
    keys=set();counts=[]
    for source in nominations:
        pairs=[tuple(x) for x in source['pairs']];local=set()
        for i,j in itertools.combinations(range(len(pairs)),2):
            required=gain(pairs[i])+gain(pairs[j])
            tail=tuple(p for k,p in enumerate(pairs) if k not in (i,j))
            # All 24 vertex permutations, modulo swapping the two directed edges.
            alternatives={tuple(sorted((p[:2],p[2:]))) for p in itertools.permutations(pairs[i]+pairs[j])}
            need(len(alternatives)==12,'four distinct endpoints')
            for new in alternatives:
                if sum(map(gain,new))==required:local.add(tuple(sorted(tail+new)))
        counts.append(len(local));keys.update(local)
    need(counts==expected['per_source_words'] and len(keys)==857,'complete neighborhood')
    by_hash={digest(p):p for p in keys}
    need(set(by_hash)=={r['pairs_sha256'] for r in expected['records']},'complete candidate hash inventory')
    minimum=None;adds=0
    for record in expected['records']:
        pairs=by_hash[record['pairs_sha256']];columns=[set(x) for x in cols]
        for a,b in pairs:columns[b]^=columns[a]
        helper=[(2*v+a,2*v+b) for a,b in pairs]
        target=[(t,s) for _,t,ss in parent['D'][:306] for s in ss]
        middle=[(v+i,2*v+j) for i in range(v) for j,col in enumerate(columns) if i in col]
        stream=[(1,t,s) for t,s in helper+target+middle+list(reversed(target))+list(reversed(helper))]
        for _,t,ss in parent['A']:stream.extend((1,t,s) for s in ss)
        for j,center in enumerate(parent['ret']):
            stream.append((2,n,center))
            stream.extend((1,v+i,n) for i,row in enumerate(parent['scatter']) if j in row)
            stream.append((3,n,center))
        for section in ('B','C'):
            for _,t,ss in parent[section]:stream.extend((1,t,s) for s in ss)
        bounds=[]
        for reverse in (False,True):
            values=[1]*(n+1);largest=1
            sequence=stream[::-1] if reverse else stream
            for kind,t,s in sequence:
                if reverse and kind!=1:kind=5-kind
                values[t]=values[t]+values[s] if kind==1 else values[s] if kind==2 else 0
                largest=max(largest,values[t])
            bounds.append(largest)
        need(bounds==[record['F'],record['B']],'independent literal bounds')
        price=sum(kind==1 for kind,t,s in stream);need(price==11948,'independent complete price')
        local=64*bounds[0]**3*bounds[1]**2;bound=2**18*bounds[0]**5*bounds[1]**4
        need(local==record['local_value'] and bound==record['nine_value'],'exact guard values')
        need(bound>=2**192,'finite negative')
        minimum=bound if minimum is None else min(minimum,bound);adds+=price
    need(minimum==expected['best']['nine_value'],'neighborhood minimum')
    print('PASS_INDEPENDENT13 words=857 complete_ADDs_replayed=%d admitted=0' % adds)


if __name__=='__main__':main()
