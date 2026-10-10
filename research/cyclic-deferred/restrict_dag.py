"""Exact first22-coordinate restriction of the immutable PR117 scalar DAG.

Original searched witness: eumemic with Anthropic Claude assistance.
Restriction and replay integration for eumemic with OpenAI Codex assistance.
Apache-2.0; original witness and upstream provenance remain unchanged.
"""
import argparse,gzip,json
from hashlib import sha256
from itertools import combinations
from pathlib import Path
HERE=Path(__file__).resolve().parent
WITNESS_SHA256='3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'
OMITTED=(22,23)

def canonical(record):return json.dumps(record,separators=(',',':')).encode()

def restrict_record(w,omitted=OMITTED):
    assert (w['h'],w['v'],w['central_disjoint'],w['center_denominator'])==(24,2024,24,21)
    assert tuple(omitted)==OMITTED,'Only the certified first22 restriction is supported'
    keep=[i for i in range(24)if i not in omitted];rename={i:j for j,i in enumerate(keep)};h=len(keep)
    oldtrip=list(combinations(range(24),3));oldtid={t:i for i,t in enumerate(oldtrip)}
    oldstars=[(a,b,i)for a,b in combinations(range(24),2)for i in range(24)if i not in(a,b)]
    trip=list(combinations(keep,3));v=len(trip);newtid={t:i+1 for i,t in enumerate(trip)}
    mapping={0:0};support=[0]+[1<<i for i in range(v)];args=[(0,0)]*(v+1);lookup={S:i for i,S in enumerate(support)}
    for i,t in enumerate(oldtrip,1):mapping[i]=newtid.get(t,0)
    erased=collapsed=merged=0
    for j in range(0,len(w['args']),2):
        old=len(oldtrip)+1+j//2;a,b=(mapping[x]for x in w['args'][j:j+2])
        if not a or not b:
            mapping[old]=a or b;erased+=not(a or b);collapsed+=bool(a or b);continue
        assert not support[a]&support[b], 'Restriction introduced overlapping summands'
        S=support[a]|support[b]
        if S in lookup:mapping[old]=lookup[S];merged+=1;continue
        x=len(support);support.append(S);lookup[S]=x;args.append((a,b));mapping[old]=x
    D=[mapping[w['D'][oldtid[t]]]for t in trip]
    P=[mapping[n]for t,n in zip(oldstars,w['P'])if all(x in rename for x in t)]
    A=[mapping[w['A'][i]]for i in keep]
    result=dict(h=h,v=v,central_disjoint=h,center_denominator=h-3,args=[x for ab in args[v+1:]for x in ab],D=D,P=P,A=A)
    assert len(D)==1540 and len(P)==4620 and len(A)==22
    # Independently validate every restricted root support. The replay module
    # also rederives every internal support, rank, type and nesting relation.
    point=[sum(1<<j for j,t in enumerate(trip)if i in t)for i in keep];full=(1<<v)-1
    for t,node in zip(combinations(range(h),3),D):assert support[node]==full&~(point[t[0]]|point[t[1]]|point[t[2]])
    stars=[(a,b,i)for a,b in combinations(range(h),2)for i in range(h)if i not in(a,b)]
    for (a,b,i),node in zip(stars,P):assert support[node]==point[a]&point[b]&~point[i]
    for i,node in enumerate(A):assert support[node]==full&~point[i]
    stats=dict(original_dimension=24,restricted_dimension=h,kept_coordinates=keep,omitted_coordinates=list(omitted),original_additions=len(w['args'])//2,restricted_additions=len(result['args'])//2,zero_nodes_removed=erased,single_summands_collapsed=collapsed,equal_support_nodes_merged=merged,all_restricted_root_supports_checked=True,ordinary_additions_remain_cancellation_free=True,canonical_restricted_sha256=sha256(canonical(result)).hexdigest())
    return result,stats

def reconstruct():
    witness=HERE/'inputs/complex-dag.json.gz';assert sha256(witness.read_bytes()).hexdigest()==WITNESS_SHA256,'Immutable PR117 DAG pin mismatch'
    original=json.loads(gzip.decompress(witness.read_bytes()));result,stats=restrict_record(original)
    stats.update(original_compressed_sha256=WITNESS_SHA256,restriction_helper_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    return result,stats

def checked_record():
    result,stats=reconstruct();path=HERE/'inputs/restricted-dag.json.gz'
    assert json.loads(gzip.decompress(path.read_bytes()))==result,'Frozen restricted DAG differs from exact original-witness restriction'
    return result,stats

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();result,stats=reconstruct();path=HERE/'inputs/restricted-dag.json.gz';receipt=HERE/'restriction-audit.json';encoded=json.dumps(stats,indent=2,sort_keys=True)+'\n'
    if a.write:path.write_bytes(gzip.compress(canonical(result),mtime=0));receipt.write_text(encoded)
    else:
        assert json.loads(gzip.decompress(path.read_bytes()))==result,'Restricted DAG mismatch'
        assert receipt.read_text()==encoded,'Restriction receipt mismatch'
    print('PASS exact PR117 restriction tofirst22, omitted22,23, canonical',stats['canonical_restricted_sha256'],flush=True)
if __name__=='__main__':main()
