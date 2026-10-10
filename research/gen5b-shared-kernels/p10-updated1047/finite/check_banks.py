"""Original literal role/replica/stage inventory and bank-address verifier.
Each bank coordinate is assigned exactly once; whole-bank endpoint swaps replay.
"""
from collections import Counter,defaultdict
import json,struct,gzip,hashlib
import context as c

def validate_table(raw,widths,banks):
    assert len(raw)==20*len(widths)*60
    seen=set();last=0;end=0;rows=list(struct.iter_unpack('>IIIII',raw))
    for role,replica,bank,offset,width in rows:
        assert role in widths and 0<=replica<60 and width==widths[role]
        if bank!=last:assert bank==last+1 and end==100;last=bank;end=0
        assert offset==end and offset+width<=100;end+=width
        assert(role,replica)not in seen;seen.add((role,replica))
    assert end==100 and last+1==banks and seen=={(r,t)for r in widths for t in range(60)}
    return rows

def run():
    c.verify();word,frames,roles,physical,entrance,ends,widths,origin=c.inventory()
    price_path=c.ARITHMETIC/'weighted890-price.json';price=c.load(price_path)
    census=Counter(widths.values());assert dict(census)=={int(k):v for k,v in price['residual_census'].items()}
    assert price['physical_R']==len(roles)==8223
    patterns=price['packing_patterns'];source_patterns=c.source('word-pins.json')['bank_patterns']
    assert patterns==[dict(widths=w,count=n)for w,n in source_patterns]
    bywidth=defaultdict(list)
    for role in roles:bywidth[widths[role]].append(role)
    queues={w:iter((r,t)for r in rs for t in range(60))for w,rs in bywidth.items()}
    encoded=bytearray();bank=0;endpoints=[];normalizers=[]
    for pattern,row in enumerate(patterns):
        ws=row['widths'];assert sum(ws)==100 and row['count']>0
        offsets=[];end=0
        for w in ws:offsets.append(end);end+=w
        def swap(blocks):
            state=list(range(200))
            for b in blocks:
                for j in range(offsets[b],offsets[b]+ws[b]):state[j],state[100+j]=state[100+j],state[j]
            return state
        blocks=list(range(len(ws)));assert swap(blocks)==list(range(100,200))+list(range(100))
        assert swap(blocks+blocks[::-1])==list(range(200))
        assert swap(blocks[:-1])!=swap(blocks) and swap(blocks+[0])!=swap(blocks)
        endpoints.append(dict(pattern=pattern,forward_inverse_columns=200,omission_rejected=True,repetition_rejected=True))
        for stage in range(5):
            witness=[]
            outside=next(j for j in range(100)if not 20*stage<=j<20*(stage+1))
            for block,(w,start)in enumerate(zip(ws,offsets)):
                original=list(range(20*stage,20*stage+w));target=list(range(start,start+w))
                src=original+[j for j in range(100)if j not in original];dst=target+[j for j in range(100)if j not in target]
                pi=dict(zip(src,dst));assert set(pi)==set(pi.values())==set(range(100))
                assert [pi[j]for j in original]==target
                witness.append((pi[outside],block+1))
            assert len(set(witness))==len(ws)
            normalizers.append(dict(stage=stage,pattern=pattern,unit_column_witnesses=witness))
        for _ in range(row['count']):
            offset=0
            for w in ws:
                role,replica=next(queues[w]);encoded.extend(struct.pack('>IIIII',role,replica,bank,offset,w));offset+=w
            assert offset==100;bank+=1
    assert all(next(q,None)is None for q in queues.values())
    assert bank==price['banks_per_stage']==85578
    rows=validate_table(encoded,widths,bank);allstages=hashlib.sha256()
    for stage in range(5):
        for role,replica,b,offset,width in rows:
            address=stage*bank+b;assert stage*bank<=address<(stage+1)*bank
            allstages.update(struct.pack('>IIIIII',stage,role,replica,address,offset,width))
    stock=60*4*960+5*bank;assert stock==price['literal_stock']==658290
    out=c.OUTPUT/'bank-addresses.bin.gz'
    with gzip.GzipFile(filename=str(out),mode='wb',mtime=0)as stream:stream.write(encoded)
    receipt=dict(status='PASS_EXPLICIT_ALL_ROLE_REPLICA_BANKS',head=c.HEAD,word_sha256=c.WORD_SHA,checker_sha256=c.sha(__file__),context_sha256=c.sha(c.HERE/'context.py'),source_manifest_sha256=c.sha(c.MANIFEST),pricing_sha256=c.sha(price_path),physical_R=len(roles),replicas=60,stages=5,assignments_per_stage=len(rows),total_assignments=5*len(rows),banks_per_stage=bank,total_banks=5*bank,literal_stock=stock,residual_census=dict(sorted(census.items())),
        entrance_count=sum(x is not None for x in entrance.values()),entrance_rank_mass=sum(x['dim']for x in entrance.values()if x is not None),restored_endpoints=sum(x is not None for x in ends.values()),
        all_blocks_full=True,all_role_replica_pairs_exactly_once=True,stage_bank_ranges_disjoint=True,endpoint_checks=endpoints,normalizer_witnesses=normalizers,
        one_stage_table_format='Big-endian uint32: role, replica, relative stage bank, coordinate start, width; stage translates bank by stage*85578; data occupies independent230400 families.',
        one_stage_table_uncompressed_sha256=hashlib.sha256(encoded).hexdigest(),five_stage_assignment_sha256=allstages.hexdigest(),compressed_table_sha256=c.sha(out),scope='Literal completed-bank role addresses and endpoint swap/normalizer permutation witnesses. Downstream full production-word address substitution and compiler semantics remain inherited interfaces.')
    (c.OUTPUT/'bank-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items()if k not in('normalizer_witnesses','endpoint_checks')},indent=2))
if __name__=='__main__':run()
