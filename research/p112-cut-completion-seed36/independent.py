#!/usr/bin/env python3
"""Independent compact column elimination and scalar dirty-wire replay.
Imports no primary verifier. Cinna Davis with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import gzip,hashlib,itertools,json
from pathlib import Path
import time
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise RuntimeError(message)

def bits(mask):return [i for i in range(mask.bit_length()) if mask>>i&1]

def column_basis(vectors):
    work=list(vectors);chosen=[]
    for j,value in enumerate(work):
        if not value:continue
        chosen.append(vectors[j]);pivot=value&-value
        for k in range(j+1,len(work)):
            if work[k]&pivot:work[k]^=value
    return chosen

def rank(columns):return len(column_basis(columns))

def codewords(vectors):
    code={0}
    for value in column_basis(vectors):code |= {x^value for x in list(code)}
    return sorted(code-{0})

def expand(mask,labels):return sum(1<<labels[i] for i in bits(mask))

def run():
    started=time.monotonic();m=json.loads((HERE/'inputs/MODEL.json').read_text());roots=m['lines'];live=set(m['live'])
    need(all(len(r)==8 and all(isinstance(x,int) for x in r) and sum(x*x for x in r)==8 for r in roots),'invalid E8 root coordinates')
    dot=[[sum(a*b for a,b in zip(x,y)) for y in roots] for x in roots]
    need(all(v%4==0 for row in dot for v in row),'unscaled root pairing')
    left=[i for i in sorted(live) if dot[3][i]!=0 and i!=3];right=[j for j in sorted(live) if dot[0][j]!=0]
    columns=[sum(int(dot[i][j]%8==0)<<k for k,i in enumerate(left)) for j in right]
    rows=[sum(int(dot[i][j]%8==0)<<k for k,j in enumerate(right)) for i in left]
    need(rank(columns)==7 and rank(rows)==7,'parent rank')
    rowcode=codewords(columns);colcode=codewords(rows);need(len(rowcode)==len(colcode)==127,'missing dual codewords')
    # A different finite premise: no two nonzero codewords are disjoint.
    intersections={'row':min((x&y).bit_count() for x,y in itertools.product(rowcode,repeat=2)),
                   'column':min((x&y).bit_count() for x,y in itertools.product(colcode,repeat=2))}
    need(min(intersections.values())>0,'complement-spanning premise fails')
    # Enumerate frames with set intersections, independently of bit adjacency.
    neighbors={i:{j for j in live if j>i and dot[i][j]==0} for i in live};frame_masks=[]
    def clique(prefix,candidates):
        if len(prefix)==8:frame_masks.append(sum(1<<i for i in prefix));return
        while len(candidates)>=8-len(prefix):
            i=min(candidates);candidates.remove(i);clique(prefix+[i],candidates&neighbors[i])
    clique([],set(live));need(len(frame_masks)==1260,'frame completeness')
    fullrows=(1<<len(left))-1;fullcols=(1<<len(right))-1
    candidates=[]
    for name,code,full,other in [('row2',rowcode,fullrows,fullcols),('col2',colcode,fullcols,fullrows)]:
        for a,b in itertools.combinations(code,2):
            if not a<b<(a^b):continue
            selected=full&~(a|b)
            candidates.append((name,selected,other)) if name=='row2' else candidates.append((name,other,selected))
    candidates += [('joint11',fullrows^a,fullcols^b) for a,b in itertools.product(rowcode,colcode)]
    spectrum=Counter();allowed=Counter();stream=hashlib.sha256();maximum=-1;maximizers=[]
    for name,rmask,cmask in candidates:
        partial=[(value&rmask) if cmask>>j&1 else 0 for j,value in enumerate(columns)]
        r=rank(partial)
        if r>5:continue
        remainder=[a^b for a,b in zip(columns,partial)];rr=rank(remainder)
        jcol=rank([a|(b<<len(left)) for a,b in zip(columns,partial)])
        jrow=rank(columns+partial)
        rowmask=expand(rmask,left);colmask=expand(cmask,right)
        hits=sum(bool(frame&rowmask) and bool(frame&colmask) for frame in frame_masks)
        spectrum[(name,r,rr,jcol,jrow,hits)]+=1;allowed[name]+=1
        record={'kind':name,'rows':rowmask,'columns':colmask,'frame_hits':hits,'rank':r,'remainder_rank':rr,
                'column_source_joint_rank':jcol,'row_source_joint_rank':jrow,'separately_copied_rank':r+rr,
                'symmetric_joint_rank':jcol+jrow}
        stream.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        if hits>maximum:maximum=hits;maximizers=[record]
        elif hits==maximum:maximizers.append(record)
    expected=json.loads((HERE/'EXPECTED.json').read_text())
    observed=[{'kind':k[0],'rank':k[1],'remainder_rank':k[2],'column_source_joint_rank':k[3],
               'row_source_joint_rank':k[4],'frame_hits':k[5],'count':v} for k,v in sorted(spectrum.items())]
    need(observed==expected['canonical_bill_spectrum'],'independent complete spectrum mismatch')
    need(stream.hexdigest()==expected['canonical_stream_sha256'],'independent complete stream mismatch')
    need(intersections==expected['minimum_codeword_intersections'],'code intersection mismatch')
    need(maximum==1060 and len(maximizers)==384,'capacity witness coverage')
    return expected,len(candidates),intersections,round(time.monotonic()-started,6)

def execute(word,data):
    data=data[:]
    for source,target in word:data[target]^=data[source]
    return data

def literal_controls(expected):
    raw=gzip.decompress((HERE/'GATES.json.gz').read_bytes());word=json.loads(raw)
    need(hashlib.sha256(raw).hexdigest()==expected['program_payload_sha256'],'program payload pin')
    columns=0;controls=0
    for direction,program in word['programs'].items():
        n=program['source_count'];d=program['scratch_count'];q=program['output_count'];width=n+d+q
        need(d==12,'maximal-cut copied information changed')
        gates=program['gates'];moves=0
        for source,target in gates:
            moves += abs(source)+abs(target-source)+abs(target)
        need(moves==program['cost']['data_head_steps'],'independent head walk mismatch')
        for input_index in range(width):
            initial=[int(i==input_index) for i in range(width)];actual=execute(gates,initial);desired=initial[:]
            if input_index<n:
                for i,row in enumerate(program['matrix_rows']):desired[n+d+i]^=(row>>input_index)&1
            need(actual==desired,'dirty scalar endpoint failure')
            need(execute(list(reversed(gates)),actual)==initial,'literal inverse failure');columns+=1
        # A full dirty fixture exercises simultaneous nonzero source/helper/output inputs.
        initial=[(i*36+3*i*i+1)%2 for i in range(width)];actual=execute(gates,initial)
        need(execute(list(reversed(gates)),actual)==initial,'dense dirty fixture inverse')
        # Dropping the complete erase word must change at least one helper column.
        erase=sum(row.bit_count() for row in program['encoder_rows']);corrupt=gates[:-erase]
        need(any(execute(corrupt,[int(i==j) for i in range(width)])!=execute(gates,[int(i==j) for i in range(width)]) for j in range(n)),'erase omission control is vacuous');controls+=1
    return columns,controls

if __name__=='__main__':
    expected,candidates,intersections,elapsed=run();columns,controls=literal_controls(expected)
    print(json.dumps({'status':'PASS_INDEPENDENT_P112_COMPLETION','canonical_candidates':candidates,
                      'admitted_candidates':sum(expected['admitted_candidates'].values()),'codeword_pair_checks':2*127*127,
                      'minimum_codeword_intersections':intersections,'dirty_input_columns':columns,
                      'omitted_erase_controls':controls,'census_seconds':elapsed},sort_keys=True))
