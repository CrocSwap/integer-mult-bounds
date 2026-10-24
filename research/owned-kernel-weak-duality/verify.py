#!/usr/bin/env python3
"""Check a full-source exact weak-duality witness; no numerical optimizer needed."""
import argparse, gzip, hashlib, json, random, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import certificate as K

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def rejected(f, text):
    try: f()
    except (ValueError, KeyError) as e:
        K.need(text in str(e), 'wrong control failure: '+str(e));return
    raise ValueError('mutant accepted: '+text)
def profile(S, model, selected):
    paid,helpers=S.M.invoice(model,selected)
    return tuple(paid.get(r,0)-helpers.get(r,0) for r in range(10))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');ap.add_argument('--generate-flow',action='store_true');args=ap.parse_args()
    S,model,variables,unary,pairs=K.source();n=len(variables)
    K.need(n==9188 and len(pairs)==14480,'complete source dimension')
    K.need(len(model['owned_copies'])==8 and len(model['shared_late_maps'])==72 and len(model['prelude_lines'])==12,'full owned/native domain')
    K.need(all(min(rs)>0 for _,a,b,rs in model['helpers']),'all helpers productive')
    graph,arcs,src,sink=K.network(n,unary,pairs)
    if args.generate_flow:
        K.generate(graph,src,sink)
        flows=[list(K.sub(c,graph[a][j][2])) for a,j,b,c in arcs]
        blob={'schema_version':1,'flows':flows}
        (K.P/'FLOW.json.gz').write_bytes(gzip.compress((canonical(blob)+'\n').encode(),mtime=0))
    raw=gzip.decompress((K.P/'FLOW.json.gz').read_bytes());data=json.loads(raw)
    K.need(type(data['schema_version']) is int and data['schema_version']==1,'typed flow schema')
    flows=data['flows'];cut=K.checked_flow(arcs,flows,n)
    baseline=profile(S,model,[]);paid,helpers=S.M.invoice(model,[])
    K.need(dict(paid)=={1:2201,2:412,3:510,4:127,5:40,8:8} and dict(helpers)=={4:28,7:7,8:47,9:326},'complete baseline invoice')
    rng=random.Random(131305);node_by_index=list(variables)
    selections=[[],node_by_index]+[[row['node']] for row in model['owned_copies']]
    selections += [[node for node in node_by_index if rng.randrange(5)==0] for _ in range(8)]
    for chosen in selections:
        ids={variables[node] for node in chosen};objective=K.Z
        for i in ids: objective=K.add(objective,tuple(unary.get(i,K.Z)))
        for (a,b),v in pairs.items():
            if a in ids and b in ids:objective=K.add(objective,v)
        expected=K.sub(profile(S,model,chosen),baseline)
        K.need(objective[1:]==expected[1:],'source full invoice identity')
        side=lambda i: (i in ids if i<n else (i-n not in ids if i<2*n else i==src))
        actual=K.Z
        for a,j,b,cap in arcs:
            if side(a) and not side(b):actual=K.add(actual,cap)
        K.need(K.sub(actual,tuple(cut))[1:]==tuple(4*v for v in expected)[1:],'four-times invoice cut identity')
    # Actual witness mutations exercise capacity, conservation, omitted arcs, and types.
    changed=[row[:] for row in flows];changed[0][1]+=10**6
    rejected(lambda:K.checked_flow(arcs,changed,n),'capacity')
    changed=[row[:] for row in flows];changed[0][1]=True
    rejected(lambda:K.checked_flow(arcs,changed,n),'typed')
    rejected(lambda:K.checked_flow(arcs,flows[:-1],n),'all directed arcs')
    index=next(i for i,(a,j,b,c) in enumerate(arcs) if any(flows[i][1:]) and a!=src and b!=sink)
    changed=[row[:] for row in flows];changed[index]=list(K.Z)
    rejected(lambda:K.checked_flow(arcs,changed,n),'conservation')
    # Losing the center term or changing helper signs must change the source invoice.
    selected=[model['owned_copies'][0]['node']]
    K.need(profile(S,model,selected)!=baseline,'actual center contact changes complete invoice')
    result={'status':'PASS_EXACT_FUNCTIONAL1_WEAK_DUALITY','C':[K.C.numerator,K.C.denominator],'contacts':n,'pair_terms':len(pairs),'positive_pair_terms':sum(K.sign(v)>0 for v in pairs.values()),'directed_arcs':len(arcs),'baseline_paid':dict(paid),'baseline_helpers':dict(helpers),'all_helpers_productive':True,'owned_centers':8,'shared_late_maps':72,'preserved_prelude_lines':12,'flow_cut_coefficient_identity':cut,'power_intervals_scaled_10_60':[[str(a),str(b)] for a,b in K.bounds],'invoice_and_cut_controls':len(selections),'witness_mutations_rejected':4,'certificate_payload_sha256':hashlib.sha256(raw).hexdigest(),'minimum_invoice_delta':0,'new_kappa':False}
    if args.write_result:(K.P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: K.need(canonical(result)==canonical(json.loads((K.P/'RESULT.json').read_text())),'frozen typed receipt mismatch')
    print(canonical(result))
if __name__=='__main__':main()
