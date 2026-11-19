"""Audit eight binary sender changes with exact set and bit-vector arithmetic."""
from collections import Counter
from graphlib import TopologicalSorter
from hashlib import sha1,sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import time

HERE=Path(__file__).resolve().parent
EDITS=((633,2323,2657,1599),(638,2342,2669,1617),(646,2381,2695,1634),(640,2453,2743,1621),(649,2496,2771,1646),(636,2497,2773,1609),(651,2513,2783,1662),(635,2532,2795,1608))


def need(ok,message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)


def bits(value):
    while value:
        bit=value&-value
        yield bit.bit_length()-1
        value^=bit


def extract(word):
    """Track field tags and sets of packet labels through every instruction."""
    public=word['public']
    fields=[{i} for i in range(public)]+[None]*word['owned_fields']
    charts=list(word['start'])+[None]*word['owned_fields']
    rows,routes,clocks={},{},{}
    for clock,event in enumerate(word['program']):
        kind,r,*args=event
        if kind=='INIT':
            need(fields[r] is None and r>=public,'fresh owned initialization')
            fields[r],charts[r]=set(),args[0]
        elif kind=='CLEAR':
            need(r>=public and fields[r] is not None and charts[r]==args[0],'owned clear chart')
            fields[r],charts[r]=None,None
        elif kind=='ADD':
            s,c=args
            need(fields[r] is not None and fields[s] is not None and charts[r]==charts[s]==c,'source XOR chart')
            fields[r]=fields[r]^fields[s]
        elif kind=='SWAP':
            s,=args
            need(fields[r] is not None and fields[s] is not None,'live field swap')
            fields[r],fields[s]=fields[s],fields[r]
            charts[r],charts[s]=charts[s],charts[r]
        else:
            need(kind=='MOVE','known source opcode')
            a,b=args
            need(fields[r] is not None and charts[r]==a,'source MOVE chart')
            k=public+len(routes)
            rows[k],routes[k],clocks[k]=set(fields[r]),(a,b),clock
            fields[r],charts[r]={k},b
    need(charts[:public]==word['final'] and all(v is None for v in fields[public:]),'complete source boundary and owned retirement')
    rows.update({~i:fields[i] for i in range(public)})
    return dict(enumerate(word['start'])),dict(enumerate(word['final'])),routes,rows,clocks


def evaluate(initial,final,routes,rows):
    need(set(rows)==set(routes)|{~i for i in final},'complete row inventory')
    chart=initial|{k:b for k,(a,b) in routes.items()}
    for k,row in rows.items():
        c=routes[k][0] if k>=0 else final[~k]
        need(all(j in chart and chart[j]==c for j in row),'available same-chart XOR donor')
    order=list(TopologicalSorter({k:row&routes.keys() for k,row in rows.items() if k>=0}).static_order())
    values={i:1<<i for i in initial}
    for k in order:
        value=0
        for j in rows[k]:
            value^=values[j]
        values[k]=value
    outputs={}
    for r in final:
        value=0
        for j in rows[~r]:
            value^=values[j]
        outputs[r]=value
    columns={j:0 for j in chart}
    for r in final:
        for j in rows[~r]:
            columns[j]^=1<<r
    for k in reversed(order):
        for j in rows[k]:
            columns[j]^=columns[k]
    return outputs,columns,order


def apply(initial,final,routes,rows,chosen,omit=()):
    erased=set()
    lost=[]
    for index in chosen:
        r,z,a,d=EDITS[index]
        erased|={r,659+z,659+a}
        lost.append(r)
    changed={k:row-erased for k,row in rows.items() if k not in erased and k not in {~r for r in lost}}
    for index in chosen:
        _,_,a,d=EDITS[index]
        if index not in omit:
            changed[659+d]^=rows[659+a]-erased
    return ({r:c for r,c in initial.items() if r not in lost},
            {r:c for r,c in final.items() if r not in lost},
            {k:pair for k,pair in routes.items() if k not in erased},changed)


def expected(r):
    return (1<<r)^((1<<(r-111)) if 111<=r<222 else 0)


def rank(vectors):
    pivots={}
    for value in vectors:
        while value:
            pivot=value.bit_length()-1
            if pivot in pivots:
                value^=pivots[pivot]
            else:
                pivots[pivot]=value
                break
    return len(pivots)


def run():
    pins=read(HERE/'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw=(HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256'],'retained source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'retained Git blob')
    word=read(HERE/'retained/native/retained/inputs/BIT-NATIVE-WORD.json.gz')
    initial,final,routes,rows,clocks=extract(word)
    outputs,columns,_=evaluate(initial,final,routes,rows)
    need(len(initial)==659 and len(routes)==2871 and len(word['program'])==34137,'exact source inventory')
    need(all(v==expected(r) for r,v in outputs.items()),'source public map')
    dims={int(c):f['dim'] for c,f in word['frames'].items()}
    profile=lambda rs:Counter(abs(dims[a]-dims[b]) for a,b in rs.values())
    original_profile=profile(routes)
    controls=[]
    for r,z,a,d in EDITS:
        z,a,d=659+z,659+a,659+d
        need(columns[z]==1<<r and columns[a]^columns[d]==1<<r,'original transpose equations')
        need(routes[a][0]==routes[d][0] and clocks[d]<clocks[a],'same sender with changed deadline')
        need(sorted([abs(dims[x]-dims[y]) for x,y in [routes[z],routes[a]]])==[1,3],'removed paid ranks')
        need(dims[final[r]]-dims[initial[r]]==4,'surrendered rank-four helper')
        controls.append(dict(helper=r,packets=[z-659,a-659,d-659],clocks=[clocks[z],clocks[a],clocks[d]],routes=[routes[z],routes[a],routes[d]],target_rank=4))
    receipts=[]
    coefficients=0
    for mask in range(256):
        chosen=list(bits(mask))
        state=apply(initial,final,routes,rows,chosen)
        out,col,order=evaluate(*state)
        need(all(value==expected(r) for r,value in out.items()),'all surviving public output rows')
        active=sum(1<<r for r in state[0])
        transposed={r:0 for r in state[0]}
        for r,value in out.items():
            for j in bits(value):
                transposed[j]^=1<<r
        need(all(col[r]==transposed[r] for r in state[0]),'independent forward and reverse map')
        # The old reverse potentials solve every changed backward equation.
        need(all(col[k]==columns[k]&active for k in col),'simultaneous transpose-contraction invariant')
        p=profile(state[2])
        need(dict(p-original_profile)=={} and original_profile-p==Counter({1:len(chosen),3:len(chosen)}),'all-subset paid debit')
        need(rank(out.values())==len(out),'each retained public direction stays independent')
        coefficients+=len(out)**2
        receipts.append(dict(mask=mask,public=len(out),paid=len(state[2]),operator_sha256=sha256(encoded(sorted(out.items()))).hexdigest()))
    all_chosen=list(range(8))
    full=apply(initial,final,routes,rows,all_chosen)
    residuals=[]
    for index in all_chosen:
        bad=apply(initial,final,routes,rows,all_chosen,omit=[index])
        out,_,_=evaluate(*bad)
        errors={r:v^expected(r) for r,v in out.items() if v!=expected(r)}
        need(errors,'missing sender correction must fail')
        output=min(errors)
        input_id=min(bits(errors[output]))
        controls[index]['omitted_sender']=dict(error_rank=rank(errors.values()),affected_outputs=len(errors),input=input_id,output=output,error=1)
        residuals.append(errors)
    need(all(len(e)==1 for e in residuals) and len({next(iter(e)) for e in residuals})==8,'disjoint nonzero main-output responses')
    for omitted in range(256):
        selected=list(bits(omitted))
        out,_,_=evaluate(*apply(initial,final,routes,rows,all_chosen,omit=selected))
        errors={r:v^expected(r) for r,v in out.items() if v!=expected(r)}
        predicted={r:value for i in selected for r,value in residuals[i].items()}
        need(errors==predicted,'all correction patterns have the exact disjoint residual law')
    # Compare the independent graph with the submitted implementation and receipt.
    spec=importlib.util.spec_from_file_location('source7776',HERE/'retained/source7776/bit_native.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    si,sf,sm,sr,sc=source.extract(word)
    need((si,sf,sm,sc)==(initial,final,routes,clocks),'independent source extraction')
    need(sr=={k:sum(1<<j for j in row) for k,row in rows.items()},'all extracted source coefficients')
    for r,z,a,d in EDITS:
        si,sf,sm,sr=source.puncture(si,sf,sm,sr,r,659+z,659+a,659+d)
    need((si,sf,sm)==full[:3] and sr=={k:sum(1<<j for j in row) for k,row in full[3].items()},'submitted final packet graph')
    emitted=source.emit_word(word,si,sf,sm,sr,source.schedule(si,sf,sm,sr))
    receipt=read(HERE/'retained/source7776/BIT-RESULT.json')
    need(source.digest(emitted)==receipt['native']['program_sha256'],'published physical word binding')
    return dict(source_files=len(pins),source_events=len(word['program']),subsets=receipts,checked_forward_matrix_entries=coefficients,checked_reverse_matrix_entries=coefficients,controls=controls,correction_patterns=256,correction_parameter_rank=8,unique_correction_mask=255,correction_residuals=[[[r,hex(v)] for r,v in sorted(e.items())] for e in residuals],final_paid=dict(sorted(profile(sm).items())),final_public=len(si),final_rank=len(si),surrendered_independent_targets=8,caller_multiplicity=36,margin_gain='288*(1+3^(1-C)-4^(1-C))',published_word_sha256=source.digest(emitted),word_binding_only=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args();start=time.monotonic();result=json.loads(json.dumps(run()))
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==read(HERE/'RESULT.json'),'deposited certificate')
    print('PASS_BIT_EIGHT_SENDER_AUDIT','256 subsets',result['checked_forward_matrix_entries'],'entries each way','8 omission controls',round(time.monotonic()-start,2),'seconds')
