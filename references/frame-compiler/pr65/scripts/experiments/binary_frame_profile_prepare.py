"""Extract positive-rank transitions from independently replayed block words."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json,struct,sys,gzip,argparse


def prepare(path,destination):
    raw=Path(path).read_bytes();raw=gzip.decompress(raw) if str(path).endswith('.gz') else raw;d=json.loads(raw)
    h,v,R=d['h'],d['v'],d['R']
    frames=[(0,0,0),(0,0,h)]+[(c,u,1 if c==u else u.bit_count()-c.bit_count()) for c,u in d['frames']]
    physical=[None]*R;transitions=Counter()
    for s,a,b in d['events']:
        assert 0<=s<R and -1<=a<len(d['frames']) and 0<=b<len(d['frames'])
        assert physical[s]==(None if a==-1 else a)
        if a!=-1:
            c,u=d['frames'][a];cc,uu=d['frames'][b]
            assert not cc&~c and not u&~uu
        source=0 if a==-1 else a+2
        target=b+2
        if source!=target:
            transitions[source,target]+=1
        physical[s]=b
    # Independently derive the same transition multiset from the actual XOR
    # word, without trusting the compiler's auxiliary event list.
    actual=[None]*R;from_word=Counter()
    def incidence(s,g):
        a=actual[s]
        if a is not None:
            c,u=d['frames'][a];cc,uu=d['frames'][g]
            assert not cc&~c and not u&~uu
        source=0 if a is None else a+2
        target=g+2
        if source!=target:from_word[source,target]+=1
        actual[s]=g
    triples=list(combinations(range(h),3))
    frame_lookup={tuple(f):i for i,f in enumerate(d['frames'])}
    assert len(frame_lookup)==len(d['frames'])
    for i,s in d['sources'].items():
        mask=sum(1<<j for j in triples[int(i)])
        incidence(s,frame_lookup[mask,mask])
    for a,b,g in d['ops']:
        assert a!=b
        incidence(a,g);incidence(b,g)
    for s,g,common,triple in d['outputs']:
        incidence(s,g)
    assert from_word==transitions and actual==physical
    out=set();singles=0;centers=0
    for s,g,common,triple in d['outputs']:
        assert s not in out and physical[s]==g
        out.add(s)
        c,u,r=frames[g+2]
        if len(triple)==1:
            assert c==1<<common and u==(1<<h)-1 and r==h-1
            transitions[0,g+2]+=1  # copied retained center
            transitions[g+2,1]+=1 # cleanup of original, rank one
            centers+=1
        else:
            assert c==1<<common and u==((1<<h)-1)^sum(1<<j for j in triple if j!=common)
            singles+=h-r # growth into target orthogonal complement + target line
    assert centers==h
    for s,g in enumerate(physical):
        assert g is not None
        if s not in out:
            transitions[g+2,1]+=1
    mass=singles+sum((frames[b][2]-frames[a][2])*count for (a,b),count in transitions.items())
    assert mass==h*R+h*(h-1)
    histogram=Counter({1:singles})
    for (a,b),count in transitions.items():
        r=frames[b][2]-frames[a][2]
        assert r>0
        histogram[r]+=count
    with Path(destination).open('wb') as f:
        f.write(struct.pack('<6I2Q',h,v,R,len(frames),len(transitions),singles,mass,h*(h-1)))
        for c,u,r in frames:f.write(struct.pack('<2QI',c,u,r))
        for (a,b),count in sorted(transitions.items()):f.write(struct.pack('<2Iq',a,b,count))
    receipt=dict(h=h,v=v,R=R,frames=len(frames),distinct_transitions=len(transitions),singles=singles,rank_mass=mass,
                 rank_histogram_with_side_growth_split_into_singletons=dict(sorted(histogram.items())),word_sha256=sha256(raw).hexdigest(),copied_centers=centers,
                 transition_events_equal_independent_xor_word_reconstruction=True)
    Path(str(destination)+'.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('word',type=Path);parser.add_argument('destination',type=Path)
 args=parser.parse_args();print(json.dumps(prepare(args.word,args.destination),indent=2))
