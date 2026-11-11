"""Exact source, native operator, complete invoice and two price engines.

This gate alone does not certify the full physical/precision application.
Rohan Arun with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import sys,json,gzip,copy,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import HERE,read,sources,canonical,need,load
from construct import construct
from packing_reference import packing
from fractions import Fraction as Q
def normalized(x):return json.loads(json.dumps(x,default=str))
def run():
    need(__debug__,'Do not disable proof assertions')
    with sources() as (vendor,archive,rank9,bundle,parent,old):
        new=construct(old);need(canonical(new)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Entire regenerated word')
        I=load('rechart_early_independent',vendor/'independent.py');before,after=map(I.native,(old,new))
        need(not before['bad_inputs'] and not after['bad_inputs'],'Exact arbitrary-input adjoint')
        need(normalized(before)==read(parent/'NATIVE-RESULT.json')['native'],'Entire source inventory')
        need(after['lifetimes']==before['lifetimes']+2 and new['owned_fields']==old['owned_fields']+1,'Both caches counted, one reused label')
        need(after['rises']==before['rises'],'Owned ascent inventory unchanged')
        base=read(parent/'RESULT.json')['price'];old_invoice={k:({int(r):v for r,v in x.items()} if k in ('T','P') else x) for k,x in base['after'].items()}
        invoice=copy.deepcopy(old_invoice);deltas={}
        for ik,nk in (('T','helpers'),('P','paid')):
            d=Counter(after[nk]);d.subtract(before[nk]);d={r:v for r,v in d.items() if v};deltas[ik]=d
            for r,v in d.items():invoice[ik][r]=invoice[ik].get(r,0)+17*v
        invoice['S']=sum(r*(invoice['T'].get(r,0)-invoice['P'].get(r,0)) for r in invoice['T'].keys()|invoice['P'].keys())
        need(deltas=={'T':{9:-1,4:1},'P':{6:-1,1:1}},'Complete paid split and return debit')
        need(invoice['S']==old_invoice['S']==1424,'Same signed rank surplus')
        for k in ('raw_crossing','no_E_credit_crossing'):invoice.pop(k,None)
        G=load('rechart_early_price',bundle/'gate.py');gate,price=G.exact_price(vendor,archive,old_invoice,invoice,{'gate':base['gate']})
        ceiling=packing(invoice,after,G.module('two_cut_packing',vendor/'interval_gate.py'),Q(gate['claim']))
        return normalized(dict(packing=ceiling,status='PASS_EXACT_NATIVE_AND_PRICE_ONLY',word_sha256=sha256(canonical(new)).hexdigest(),native=after,native_delta=deltas,invoice=invoice,gate=gate,price=price,pending=['fresh integer grid','all affected physical chart maps','complete caller replay','ordinary and precision bounds','full source application']))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()
    r=run()
    if args.out:
        with args.out.open('x') as out:json.dump(r,out,sort_keys=True,indent=2);out.write('\n')
    else:need(r==read(HERE/'EARLY-RESULT.json'),'Every frozen early receipt field')
    print(r['status'],r['price']['claim_decimal'],flush=True)
