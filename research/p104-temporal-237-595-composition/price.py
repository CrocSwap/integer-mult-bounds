"""Recompute both source invoices and two exact crossing engines.
Retains Rohan Arun's caller adapters and ToikY's attributed price engines.
Chart-595 adapter: dillona with OpenAI Codex. Three-way comparison:
Clear1nsight with Codex and ChatGPT Pro. Apache-2.0.
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
    with source.sources() as (vendor,archive,rank9,bundle,parent,word), source.frozen(7147) as peer:
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
        peer_word=read(peer/'WORD.json.gz');peer_result=read(peer/'NATIVE-RESULT.json')
        words=(old_word,new_word,peer_word)
        inventories=[ind.native(w) for w in words]
        for n,r,w in zip(inventories,(old_result,new_result,peer_result),words):
            assert normalized(n)==r['native'] and not n['bad_inputs']
            assert sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()==r['word_canonical_sha256']
        before,after,peer_invoice=[ind.invoices(w,C,n) for w,n in zip(words,inventories)]
        previous=read(previous_composition/'RESULT.json')['price']
        peer_price=read(peer/'RESULT.json')['price']
        assert normalized(before)==previous['after'],'Entire reconstructed chart-595 caller invoice'
        assert normalized(peer_invoice)==peer_price['after'],'Entire reconstructed chart-237 caller invoice'
        assert before['S']==after['S']==peer_invoice['S']==1424
        assert before['empty_root_credits']==after['empty_root_credits']==peer_invoice['empty_root_credits']==0
        def delta(new,old):
            return {r:new.get(r,0)-old.get(r,0) for r in sorted(new.keys()|old.keys())
                    if new.get(r,0)!=old.get(r,0)}
        assert delta(after['T'],before['T'])=={4:17,5:17,9:-17}
        assert delta(after['P'],before['P'])=={1:17,5:17,6:-17}
        assert delta(after['T'],peer_invoice['T'])=={1:17,8:17,9:-17}
        assert delta(after['P'],peer_invoice['P'])=={1:34,2:-17}
        G=load('composition_price_engine',bundle/'gate.py')
        gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
        peer_gate,peer_comparison=G.exact_price(vendor,archive,peer_invoice,after,{'gate':peer_price['gate']})
        assert gate==peer_gate and Q(gate['claim'])>Q(new_result['gate']['claim'])
        native_invoice={k:({int(r):v for r,v in value.items()} if k in ('T','P') else value) for k,value in new_result['invoice'].items()}
        directed=G.module('composition_native_comparator',vendor/'interval_gate.py')
        assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0,'The separately checked18-stage ingredient invoice rejects the17-stage claim'
        record=normalized(dict(before=before,after=after,gate=gate,price=price,peer_invoice=peer_invoice,
                               peer_comparison=peer_comparison,native_baseline_rejects_new_claim=True,
                               old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
        with (folder/'CURRENT-PRICE.json').open('x') as f:json.dump(record,f,indent=2)
        with (folder/'COHORT-PRICE.json').open('x') as f:json.dump(dict(target=after['T'],paid=after['P'],bracket=gate['raw_bracket']),f,indent=2)
        print('PASS three reconstructed invoices; both parents rejected at new claim, by two exact price engines',price['claim_decimal'],flush=True)

if __name__=='__main__':
    assert __debug__
    main(*map(Path,sys.argv[1:]))
