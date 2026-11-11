# Successor: Rohan Arun/OpenAI Codex global output rechart; predecessor attribution retained.
"""Recompute both source invoices and two exact crossing engines.
Retains Rohan Arun's caller adapters and ToikY's attributed price engines.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import gzip,importlib.util,json,sys

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj

def read(path):
    raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)

def normalized(value):return json.loads(json.dumps(value,default=str))

def main(native,caller,previous_composition,folder):
    source=load('composition_native_source',native/'source.py')
    with source.sources() as (vendor,archive,rank9,bundle,parent,word):
        sys.path.insert(0,str(folder))
        model=load('composition_signed_model',folder/'signed_model.py');ind=model.signed_model()
        code=(folder/'independent.py').read_text();part=code[code.index('def invoices('):code.index('def ordinary(')]
        assert part.count('assert calls==18')==1
        part=part.replace('assert calls==18',"assert calls==C['stages']")
        old="elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports";assert part.count(old)==1
        part=part.replace(old,"elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports")
        exec(compile(part,str(folder/'independent.py'),'exec'),ind.__dict__)
        C=read(caller/'expected/ODD-TYPE-AB-CALLER.json')
        old_word=word;new_word=read(native/'WORD.json.gz')
        old_result=read(parent/'NATIVE-RESULT.json');new_result=read(native/'NATIVE-RESULT.json')
        inventories=[ind.native(w) for w in (old_word,new_word)]
        for n,r,w in zip(inventories,(old_result,new_result),(old_word,new_word)):
            assert normalized(n)==r['native'] and not n['bad_inputs']
            assert sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()==r['word_canonical_sha256']
        before,after=[ind.invoices(w,C,n) for w,n in zip((old_word,new_word),inventories)]
        previous=read(previous_composition/'RESULT.json')['price']
        assert normalized(before)==previous['after'],'Entire reconstructed current #7145 invoice'
        G=load('composition_price_engine',bundle/'gate.py')
        gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
        assert Q(gate['claim'])>Q(new_result['gate']['claim'])
        native_invoice={k:({int(r):v for r,v in value.items()} if k in ('T','P') else value) for k,value in new_result['invoice'].items()}
        directed=G.module('composition_native_comparator',vendor/'interval_gate.py')
        assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0,'The separately checked18-stage ingredient invoice rejects the17-stage claim'
        record=normalized(dict(before=before,after=after,gate=gate,price=price,native_baseline_rejects_new_claim=True,
                               old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
        with (folder/'CURRENT-PRICE.json').open('x') as f:json.dump(record,f,indent=2)
        with (folder/'COHORT-PRICE.json').open('x') as f:json.dump(dict(target=after['T'],paid=after['P'],bracket=gate['raw_bracket']),f,indent=2)
        print('PASS two reconstructed invoices and both exact price engines',price['claim_decimal'],flush=True)

if __name__=='__main__':
    assert __debug__
    main(*map(Path,sys.argv[1:]))
