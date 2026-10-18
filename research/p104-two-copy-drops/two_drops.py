"""Exact simultaneous two-term COPY-drop threshold on a fixed P104 decoder.
Apache-2.0; woklerx with substantial OpenAI Codex assistance.
"""
from itertools import combinations,product
from pathlib import Path
import argparse,hashlib,json
from collections import Counter
HERE=Path(__file__).resolve().parent
def need(x,s):
    if not x:raise ValueError(s)
def bits(x):
    while x:
        b=x&-x;yield b.bit_length()-1;x^=b
def basis(rows):
    piv={}
    for v in rows:
        while v:
            b=v&-v
            if b in piv:v^=piv[b]
            else:piv[b]=v;break
    return list(piv.values())
def code(rows):
    words=[0]
    for b in basis(rows):words += [v^b for v in words]
    return words[1:]
def run():
    raw=(HERE/'inputs/PREDECESSOR.json').read_bytes();pin=json.loads((HERE/'DEPENDENCY.json').read_text());need(hashlib.sha256(raw).hexdigest()==pin['sha256'],'source receipt pin')
    old=json.loads(raw)['witness'];rs=[]
    for i,j in combinations(range(8),2):
        for sign in (1,-1):
            r=[0]*8;r[i]=2;r[j]=2*sign;rs.append(r)
    rs.extend([list(r) for r in product((1,-1),repeat=8) if r[0]==1 and r.count(-1)%2==0])
    need(len(rs)==120,'120source-ordered lines')
    ip=[[sum(x*y for x,y in zip(r,s))//4 for s in rs] for r in rs]
    binary=[sum(((v+1)&1)<<j for j,v in enumerate(row)) for row in ip]
    base=set(old['frame0']+old['frame1']);live=[i for i in range(120) if i not in base];lm=sum(1<<i for i in live)
    need(len(base)==16 and len(live)==104,'fixedP104')
    pairs=old['pairs'];need(len(pairs)==8,'eightterms')
    need(all((abs(ip[a][b])==1 if k==l else ip[a][b]==0) for k,(a,_) in enumerate(pairs) for l,(_,b) in enumerate(pairs)),'exact dual root bases')
    supports=[(sum(1<<i for i in live if ip[a][i]),sum(1<<i for i in live if ip[b][i])) for a,b in pairs]
    def ranks(deleted):return [len(basis(binary[i]&r&~deleted for i in bits(l&~deleted))) for l,r in supports]
    need(ranks(0)==[7]*8,'P104 baseline')
    original=sum(1<<i for i in old['added_punctures']);need(ranks(original)==old['ranks'],'first-drop source control')
    dictionary=[]
    for l,r in supports:
        a=code(binary[j]&l for j in bits(r));b=code(binary[i]&r for i in bits(l))
        need(len(a)==len(b)==127,'127cuts per side')
        cuts=sorted(set(a+b));need(all(c&~lm==0 for c in cuts),'cuts within live set')
        need(min(c.bit_count() for c in cuts)==22,'first-drop threshold')
        need(all(ranks(c)[len(dictionary)]<7 for c in cuts),'everycutdropsitsterm')
        dictionary.append(cuts)
    boundary=sorted({c for cuts in dictionary for c in cuts if c.bit_count()==22})
    bh=Counter();boundary_best=None
    for cut in boundary:
        p=ranks(cut);bh[tuple(p)]+=1
        if boundary_best is None or (sum(p),cut)<(sum(boundary_best[1]),boundary_best[0]):boundary_best=(cut,p)
    pair_records=[];cases=0;best=(121,None);stream=hashlib.sha256()
    for i,j in combinations(range(8),2):
        minimum=121;count=0;witness=None
        for a in dictionary[i]:
            for b in dictionary[j]:
                cases+=1;u=a|b;n=u.bit_count()
                if n<minimum:minimum=n;count=0;witness=(a,b,u)
                if n==minimum:count+=1
        a,b,u=witness
        pair_records.append(dict(terms=[i,j],minimum=minimum,attaining_ordered_cut_pairs=count,cuts=[hex(a),hex(b)],union=hex(u)))
        if (minimum,u)<(best[0],best[1] if best[1] is not None else 1<<121):best=(minimum,u)
        stream.update(f'{i},{j}:{minimum}:{count}:{a:x}:{b:x}\n'.encode())
    need(sum(boundary_best[1])==54 and len(boundary)==360,'sharpboundary54')
    n,u=best;profile=ranks(u);need(sum(r<7 for r in profile)>=2,'two-term attainment')
    restores=[]
    for i in bits(u):
        p=ranks(u&~(1<<i));need(sum(r<7 for r in p)<2,'everyone-portrestorebreakstwo-drop');restores.append([i,p])
    # Verify the full rational coefficient identity on the witness live pairs,
    # clearing doubled-coordinate denominators with integer products.
    remaining=[i for i in live if not u>>i&1]
    need(all(sum(ip[i][a]*2*ip[a][b]*ip[j][b] for a,b in pairs)==2*ip[i][j] for i in remaining for j in remaining),'all-pairs exact coefficient identity')
    return dict(boundary_profiles_sha256=hashlib.sha256(json.dumps([[hex(c),ranks(c)] for c in boundary],separators=(',',':')).encode()).hexdigest(),boundary_cut_count=len(boundary),boundary_total_cost_histogram={str(c):sum(v for p,v in bh.items() if sum(p)==c) for c in sorted(set(map(sum,bh)))},boundary_min_cost=sum(boundary_best[1]),boundary_best_deleted=list(bits(boundary_best[0])),boundary_best_profile=boundary_best[1],status='PASS_P104_TWO_TERM_DROP',fixed_pairs=pairs,fixed_puncture=sorted(base),cut_dictionary_sizes=[len(c) for c in dictionary],cut_pairs_checked=cases,pair_records=pair_records,minimum_extra_punctures=n,total_punctures=16+n,attaining_deleted=list(bits(u)),attaining_profile=profile,attaining_copy_cost=sum(profile),live_ports=len(remaining),identity_entries=len(remaining)**2,restore_controls=restores,stream_sha256=stream.hexdigest(),controls=['unchangedP104allrank7','pinned22dropwitnessonlyoneterm','everyone-portrestorefailstwo-terms','fullcoefficientidentity'])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();x=run();p=HERE/'CERTIFICATE.json'
    if a.write:p.write_text(json.dumps(x,indent=2)+'\n')
    else:need(x==json.loads(p.read_text()),'complete receipt')
    print('PASS_P104_TWO_TERM_DROP extra='+str(x['minimum_extra_punctures'])+' copy='+str(x['attaining_copy_cost'])+' ports='+str(x['live_ports'])+' cutpairs='+str(x['cut_pairs_checked']))
