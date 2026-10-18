#!/usr/bin/env python3
"""Exact copied-information completion ranks for the fixed P112 [7,0] parent.
Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip,hashlib,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise RuntimeError(message)

def indices(mask):
    while mask:
        bit=mask&-mask;yield bit.bit_length()-1;mask^=bit

def basis(rows):
    pivots={}
    for vector in rows:
        while vector:
            pivot=vector.bit_length()-1
            if pivot in pivots:vector^=pivots[pivot]
            else:pivots[pivot]=vector;break
    return list(pivots.values())

def rank(rows):return len(basis(rows))

def span(vectors):
    result=[0]
    for vector in vectors:result += [x^vector for x in result]
    return sorted(result[1:])

def transpose(rows,width):return [sum(((row>>j)&1)<<i for i,row in enumerate(rows)) for j in range(width)]

def model():
    raw=(HERE/'inputs/MODEL.json').read_bytes();data=json.loads(raw)
    roots=data['lines'];live=data['live']
    require(len(roots)==120 and len(live)==112,'pinned P112 domain')
    ip=[[sum(x*y for x,y in zip(a,b))//4 for b in roots] for a in roots]
    pairing=[sum(((value+1)&1)<<j for j,value in enumerate(row)) for row in ip]
    supports=[]
    for i in range(120):
        support=sum(1<<j for j in live if ip[i][j])
        supports.extend((support,support&~(1<<i)))
    left,right=supports[7],supports[0]
    matrix=[pairing[i]&right if left>>i&1 else 0 for i in range(120)]
    require(rank(matrix)==7,'parent copy rank changed')
    return data,pairing,left,right,matrix,hashlib.sha256(raw).hexdigest()

def frames(data):
    roots=data['lines'];live=data['live'];adj=[]
    for i in range(120):
        adj.append(sum(1<<j for j in live if i!=j and sum(x*y for x,y in zip(roots[i],roots[j]))==0))
    result=[]
    def extend(selected,candidates):
        if len(selected)==8:result.append(selected);return
        while candidates.bit_count()>=8-len(selected):
            bit=candidates&-candidates;candidates^=bit;i=bit.bit_length()-1
            extend(selected+[i],candidates&adj[i])
    extend([],sum(1<<i for i in live));require(len(result)==1260,'orthogonal frame coverage')
    incidence=[0]*120
    for number,frame in enumerate(result):
        for root in frame:incidence[root]|=1<<number
    def hit(mask):
        result=0
        for i in indices(mask):result|=incidence[i]
        return result
    return hit

def cut(matrix,rowmask,colmask):return [row&colmask if rowmask>>i&1 else 0 for i,row in enumerate(matrix)]

def completion(matrix,part):
    remainder=[a^b for a,b in zip(matrix,part)]
    mt=transpose(matrix,120);kt=transpose(part,120)
    r=rank(part)
    return {'rank':r,'remainder_rank':rank(remainder),
            'column_source_joint_rank':rank(matrix+part),
            'row_source_joint_rank':rank(mt+kt),
            'separately_copied_rank':r+rank(remainder),
            'symmetric_joint_rank':rank(matrix+part)+rank(mt+kt)}

def run():
    data,pair,left,right,matrix,model_hash=model();hit=frames(data)
    rowcode=span(basis([pair[j]&left for j in indices(right)]))
    colcode=span(basis([pair[i]&right for i in indices(left)]))
    require(len(rowcode)==len(colcode)==127,'all rank-seven dual codewords')
    hyper={};planes={};intersections={}
    for name,code,side,other in [('row',rowcode,left,right),('column',colcode,right,left)]:
        def projected_rank(mask):return rank([pair[i]&other for i in indices(mask)])
        spectrum=Counter(projected_rank(mask) for mask in code)
        require(spectrum=={7:127},'nonzero complementary support does not span full rank')
        hyper[name]={str(k):v for k,v in spectrum.items()}
        counts=Counter(projected_rank(a|b) for a,b in itertools.combinations(code,2) if a<b<(a^b))
        require(counts=={7:2667},'two-plane complementary support changed');planes[name]={str(k):v for k,v in counts.items()}
        intersections[name]=min((a&b).bit_count() for a,b in itertools.product(code,repeat=2))
        require(intersections[name]>0,'disjoint nonzero codeword supports')
    candidates=[]
    for name,code,side,other in [('row2',rowcode,left,right),('col2',colcode,right,left)]:
        for a,b in itertools.combinations(code,2):
            if not a<b<(a^b):continue
            selected=side&~(a|b)
            candidates.append((name,selected,other)) if name=='row2' else candidates.append((name,other,selected))
    candidates += [('joint11',left^a,right^b) for a,b in itertools.product(rowcode,colcode)]
    allowed=Counter();spectrum=Counter();stream=hashlib.sha256();best_hits=-1;maximizers=[];kind_best={}
    for kind,rows,cols in candidates:
        part=cut(matrix,rows,cols);r=rank(part)
        if r>5:continue
        bill=completion(matrix,part);hits=(hit(rows)&hit(cols)).bit_count()
        require(bill['symmetric_joint_rank']>=14+r,'all-support completion inequality failed')
        allowed[kind]+=1;spectrum[(kind,r,bill['remainder_rank'],bill['column_source_joint_rank'],bill['row_source_joint_rank'],hits)]+=1
        record={'kind':kind,'rows':rows,'columns':cols,'frame_hits':hits,**bill}
        stream.update((json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode())
        if kind not in kind_best or hits>kind_best[kind]['frame_hits']:kind_best[kind]=record
        if hits>best_hits:best_hits=hits;maximizers=[record]
        elif hits==best_hits:maximizers.append(record)
    require(sum(allowed.values())==13335 and best_hits==1060,'complete canonical low-rank census changed')
    # Sharp witnesses for every exact rank 1..6: independent original rows, all columns.
    independent=[];prior=0
    for i in indices(left):
        new=rank([matrix[j] for j in independent+[i]])
        if new>prior:independent.append(i);prior=new
    require(len(independent)==7,'independent row witness basis')
    witnesses=[]
    for r in range(1,7):
        rows=sum(1<<i for i in independent[:r]);part=cut(matrix,rows,right);bill=completion(matrix,part)
        require(bill['rank']==r and bill['symmetric_joint_rank']==14+r,'sharp rank witness failed')
        require(bill['remainder_rank']==7,'witness remainder changed')
        witnesses.append({'rank':r,'rows':list(indices(rows)),'columns':list(indices(right)),**bill})
    # The rank-seven identity lacks the complement property: its rank-five split costs 14.
    identity=[1<<i for i in range(7)];part=[1<<i if i<5 else 0 for i in range(7)]
    require(rank(identity+part)+rank(transpose(identity,7)+transpose(part,7))==14,'scope counterexample failed')
    best=sorted(maximizers,key=lambda x:(x['rows'],x['columns']))[36%len(maximizers)]
    result={'status':'PASS_P112_CUT_COMPLETION','assignment_seed':36,'parent_tags':[7,0],
            'parent_support_sizes':[left.bit_count(),right.bit_count()],'parent_rank':7,
            'model_sha256':model_hash,'hyperplane_complement_rank':hyper,'dual_plane_complement_rank':planes,
            'minimum_codeword_intersections':intersections,'canonical_candidates_tested':len(candidates),
            'admitted_candidates':dict(allowed),'max_frame_hits':best_hits,'maximizer_count':len(maximizers),
            'maximizer_bills':dict(Counter(json.dumps({k:x[k] for k in ['rank','remainder_rank','column_source_joint_rank','row_source_joint_rank','separately_copied_rank','symmetric_joint_rank']},sort_keys=True) for x in maximizers)),
            'canonical_bill_spectrum':[{'kind':key[0],'rank':key[1],'remainder_rank':key[2],'column_source_joint_rank':key[3],'row_source_joint_rank':key[4],'frame_hits':key[5],'count':count} for key,count in sorted(spectrum.items())],
            'canonical_stream_sha256':stream.hexdigest(),'kind_maximum_witnesses':kind_best,'sharp_witnesses':witnesses,'seed_selected_maximizer':best,
            'scope_control':'I7 rank-five split has remainder rank2 and symmetric joint rank14; geometry premise is essential'}
    return result,matrix

def factor(rows):
    original=[];pivots={}
    for row in rows:
        value=row;combination=0
        while value:
            pivot=value.bit_length()-1
            if pivot in pivots:
                vector,code=pivots[pivot];value^=vector;combination^=code
            else:
                code=(1<<len(original))^combination;original.append(row)
                pivots[pivot]=(value,code);break
    decoder=[]
    for row in rows:
        value=row;code=0
        while value:
            pivot=value.bit_length()-1;vector,coefficient=pivots[pivot]
            value^=vector;code^=coefficient
        decoder.append(code)
    require(all(reconstruct(original,code)==row for row,code in zip(rows,decoder)),'factorization identity')
    return original,decoder

def reconstruct(rows,mask):
    result=0
    for i in indices(mask):result^=rows[i]
    return result

def compile_program(rows,source_labels,output_labels):
    encoder,decoder=factor(rows);n=len(source_labels);d=len(encoder);outputs=len(rows);width=n+d+outputs
    gates=[]
    def readout():
        for i,code in enumerate(decoder):
            for j in indices(code):gates.append([n+j,n+d+i])
    def load():
        for i,row in enumerate(encoder):
            for j in indices(row):gates.append([j,n+i])
    readout();load();readout();load()
    state=[1<<i for i in range(width)]
    for source,target in gates:state[target]^=state[source]
    desired=[1<<i for i in range(width)]
    for i,row in enumerate(rows):desired[n+d+i]^=row
    require(state==desired,'literal dirty fork endpoint')
    for source,target in reversed(gates):state[target]^=state[source]
    require(state==[1<<i for i in range(width)],'literal fork inverse')
    record_bits=2*(width-1).bit_length();count=len(gates);moves=sum(2*max(a,b) for a,b in gates)
    cost={'xor_gates':count,'source_reads':count,'target_reads':count,'target_writes':count,
          'data_head_steps':moves,'instruction_record_bits':record_bits,'instruction_reads':record_bits*count,
          'instruction_head_steps':2*record_bits*count,'decode_dispatch':count,
          'unit_steps':moves+(5+3*record_bits)*count}
    return {'source_labels':source_labels,'output_labels':output_labels,'source_count':n,'scratch_count':d,
            'output_count':outputs,'wire_count':width,'matrix_rows':rows,'encoder_rows':encoder,
            'decoder_rows':decoder,'gates':gates,'cost':cost}

def programs(matrix,result):
    data,pair,left,right,_,_=model();rows=list(indices(left));cols=list(indices(right))
    selected=result['seed_selected_maximizer'];part=cut(matrix,selected['rows'],selected['columns'])
    result_programs={}
    for direction,source_labels,target_labels,parent,kernel in [
            ('column-source',cols,rows,matrix,part),
            ('row-source',rows,cols,transpose(matrix,120),transpose(part,120))]:
        compact=lambda values:[sum(((values[i]>>j)&1)<<k for k,j in enumerate(source_labels)) for i in target_labels]
        parent_rows=compact(parent);partial=compact(kernel);remainder=[a^b for a,b in zip(parent_rows,partial)]
        labels=[['cut',i] for i in target_labels]+[['remainder',i] for i in target_labels]
        result_programs[direction]=compile_program(partial+remainder,source_labels,labels)
    return {'format':'dirty-linear-forks-v1','field':'F2','assignment_seed':36,'selected_cut':selected,'programs':result_programs}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();result,matrix=run()
    word=programs(matrix,result);raw=(json.dumps(word,sort_keys=True,separators=(',',':'))+'\n').encode()
    result['program_payload_sha256']=hashlib.sha256(raw).hexdigest()
    result['witness_programs']={k:{'copy_rank':v['scratch_count'],'symbolic_input_columns':v['wire_count'],**v['cost']} for k,v in word['programs'].items()}
    expected=HERE/'EXPECTED.json'
    if args.write:
        expected.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        (HERE/'GATES.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    else:
        require(result==json.loads(expected.read_text()),'complete receipt differs')
        require(gzip.decompress((HERE/'GATES.json.gz').read_bytes())==raw,'literal gate transcript differs')
    print(json.dumps({k:result[k] for k in ['status','canonical_candidates_tested','admitted_candidates','max_frame_hits','maximizer_count','maximizer_bills','witness_programs']},sort_keys=True))
if __name__=='__main__':main()
