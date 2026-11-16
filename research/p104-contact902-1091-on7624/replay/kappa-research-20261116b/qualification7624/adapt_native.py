#!/usr/bin/env python3
"""Counted overlay of the freshly prepared #7624 native runner; never run here."""
from pathlib import Path
import gzip
import hashlib
import json

SOURCE_CAN='c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de'
SOURCE_GZ='bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887'
BASE_CAN='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
NATIVE_SHA='88de25922ac37156fcaee215467c0109cca9d4d2e326a49c0aa329ebb600e6e2'
INVOICE_SHA='e3f1c1bb9516eb141f2c51b8cd12a9a55026f5968082083bd8d9fdb793a2e486'

def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def read(p): return json.loads(Path(p).read_bytes())
def word(b): return json.loads(gzip.decompress(b))
def need(ok,msg):
    if not ok: raise ValueError(msg)
def routes(w):
    out={i:[] for i in range(w['public'])}
    for e in w['program']:
        if e[0]=='MOVE' and e[1]<w['public']: out[e[1]].append(tuple(e[2:4]))
    return out

def pair_evidence(base,source,candidate,pinned,candidate_can):
    b,s,c=map(routes,(base,source,candidate))
    source_fields=[i for i in b if b[i]!=s[i]]
    candidate_fields=[i for i in b if b[i]!=c[i]]
    splice_fields=[i for i in s if s[i]!=c[i]]
    source_pairs={p for i in source_fields for p in b[i]+s[i]}
    candidate_pairs={p for i in candidate_fields for p in b[i]+c[i]}
    splice_pairs={p for i in splice_fields for p in s[i]+c[i]}
    need(len(pinned)==1075 and len(source_fields)==201 and source_pairs==pinned,'source full pair census')
    need(splice_fields==[902,1091] and candidate_pairs and splice_pairs,'changed route inventory')
    union=pinned|source_pairs|candidate_pairs|splice_pairs
    return {'schema':'contact7624-native-pairs/v1','base7481_canonical_sha256':BASE_CAN,
      'source_canonical_sha256':SOURCE_CAN,'candidate_canonical_sha256':candidate_can,
      'source_affected_count':len(pinned),'pinned_source_pairs':[list(x) for x in sorted(pinned)],
      'source_changed_fields':source_fields,'candidate_changed_fields':candidate_fields,
      'splice_changed_fields':splice_fields,'source_vs7481_pairs':[list(x) for x in sorted(source_pairs)],
      'candidate_vs7481_pairs':[list(x) for x in sorted(candidate_pairs)],
      'splice_route_pairs':[list(x) for x in sorted(splice_pairs)],'full_validation_pairs':[list(x) for x in sorted(union)]}

def adapt(rootwork:Path,roundroot:Path):
    rootwork=Path(rootwork);roundroot=Path(roundroot)
    runner=rootwork/'producer54/validation_native/run.py';raw=runner.read_bytes()
    gate=roundroot/'compose7624_completion/run/case'; result=read(gate/'RESULT.json')
    need(result['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','first gate status')
    for rel in ('built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/status.json','price/PRICE.json','price/invoice-new.json'):
        need(rel in result['receipt_hashes'] and sha((gate/rel).read_bytes())==result['receipt_hashes'][rel],'gate receipt '+rel)
    frozen=rootwork/'frozen-composition'; package=roundroot/'inputs/pr7624/research/p104-w2-primal-dual-bypass'
    source_bytes=(frozen/'7624-WORD.json.gz').read_bytes();candidate_bytes=(gate/'built/candidate-word.json.gz').read_bytes()
    need(sha(source_bytes)==SOURCE_GZ and source_bytes==(package/'data/word.json.gz').read_bytes(),'source bytes')
    source=word(source_bytes);candidate=word(candidate_bytes);c=sha(canonical(candidate))
    need(sha(canonical(source))==SOURCE_CAN,'source canonical')
    need((source['public'],source['owned_fields'],len(source['program']))==(1501,68,77372) and len(candidate['program'])==77371,'word shapes')
    for w in (source,candidate):
        need(sum(e[0]=='INIT' for e in w['program'])==sum(e[0]=='CLEAR' for e in w['program'])==204,'204 lifetimes')
    manifest_bytes=(gate/'built/edit-manifest.json').read_bytes();m=json.loads(manifest_bytes)
    need(m['source_canonical_sha256']==SOURCE_CAN and m['candidate_canonical_sha256']==c and m['candidate_gzip_sha256']==sha(candidate_bytes),'word manifest')
    need((frozen/'CONTACT7624-MANIFEST.json').read_bytes()==manifest_bytes,'frozen manifest')
    price=read(gate/'price/PRICE.json');need(price['status']=='PROVISIONAL_UNDER_COMMON_U' and price['bindings']['candidate_canonical_sha256']==c and price['bindings']['original_word_canonical_sha256']==SOURCE_CAN,'price binding')
    need((frozen/'CONTACT7624-PRICE.json').read_bytes()==(gate/'price/PRICE.json').read_bytes(),'frozen price')
    need(sha((frozen/'7624-INVOICE.json').read_bytes())==INVOICE_SHA,'source invoice')
    native_bytes=(package/'evidence/NATIVE.json').read_bytes();need(sha(native_bytes)==NATIVE_SHA,'source native evidence')
    source_native=json.loads(native_bytes);need(source_native['status']=='PASS_W3H_ADAPTED_COMPLETE_NATIVE' and source_native['word_canonical_sha256']==SOURCE_CAN,'source evidence identity')
    rows=source_native['charts']['all_affected_pairs']; pinned={tuple(x['pair']) for x in rows}
    need(len(rows)==len(pinned)==1075 and all(x['columns']==x['adjoint_columns']==512 and x['absolute_phase_verified'] for x in rows),'source physical census')
    base=word((frozen/'7481-WORD.json.gz').read_bytes());need(sha(canonical(base))==BASE_CAN,'base word')
    pairs=pair_evidence(base,source,candidate,pinned,c); pair_bytes=canonical(pairs)+b'\n';pair_sha=sha(pair_bytes)
    need(sha(canonical(word((rootwork/'producer54/reroute/WORD.json.gz').read_bytes())))==SOURCE_CAN,'prepared source reroute')
    need(sha(canonical(word((frozen/'CANDIDATE-WORD.json.gz').read_bytes())))==SOURCE_CAN,'prepared source frozen word')
    txt=raw.decode('utf-8').replace('\r\n','\n'); records=[{'label':'line_endings','original_sha256':sha(raw),'normalized_sha256':sha(txt.encode()),'crlf_count':raw.count(b'\r\n')}]
    def change(label,old,new,n=1):
        nonlocal txt
        count=txt.count(old);need(count==n,'anchor '+label+' count '+str(count));txt=txt.replace(old,new,n)
        records.append({'label':label,'occurrences':count,'old_sha256':sha(old.encode()),'new_sha256':sha(new.encode())})
    change('candidate_hash',"EXPECTED='"+SOURCE_CAN+"'","EXPECTED='"+c+"'")
    change('source_routes',"    old_routes,new_routes=routes(before),routes(word)","    source7624=read(ROOT/'frozen-composition/7624-WORD.json.gz')\n    need(sha256(canonical(source7624)).hexdigest()=='"+SOURCE_CAN+"','Exact #7624 source')\n    old_routes,new_routes=routes(before),routes(source7624)")
    # The #7624 adapter inserts the complete fixed literal pair set in exactly one record.
    pair_anchor=read(package/'adapters/native.json')[11]['after'];need(pair_anchor.startswith('need(affected==set('),'source pair anchor')
    change('pair_union',pair_anchor,"need(affected=={tuple(x) for x in pairs['pinned_source_pairs']},'Authenticated #7624 pair census')")
    change('pair_manifest',"    report=[]\n    for a,b in sorted(affected):", """    pair_path=ROOT/'frozen-composition/CONTACT7624-PAIRS.json'
    need(sha256(pair_path.read_bytes()).hexdigest()=='"""+pair_sha+"""','Exact candidate pair manifest')
    pairs=read(pair_path)
    source_routes=routes(source7624);candidate_routes=routes(word)
    source_fields=[i for i in old_routes if old_routes[i]!=source_routes[i]]
    candidate_fields=[i for i in old_routes if old_routes[i]!=candidate_routes[i]]
    splice_fields=[i for i in source_routes if source_routes[i]!=candidate_routes[i]]
    need(splice_fields==[902,1091] and candidate_fields==pairs['candidate_changed_fields'],'Exact changed fields')
    pinned={tuple(x) for x in pairs['pinned_source_pairs']}
    need(len(pinned)==1075,'Nonempty complete source pairs')
    affected=pinned | {p for i in source_fields for p in old_routes[i]+source_routes[i]} | {p for i in candidate_fields for p in old_routes[i]+candidate_routes[i]} | {p for i in splice_fields for p in source_routes[i]+candidate_routes[i]}
    need(affected=={tuple(x) for x in pairs['full_validation_pairs']},'Fresh full pair union')
    changed=candidate_fields
    report=[]
    for a,b in sorted(affected):""")
    # pair anchor now uses pairs before original report position; read it immediately after routes.
    change('pair_manifest_early',"    old_routes,new_routes=routes(before),routes(source7624)","    old_routes,new_routes=routes(before),routes(source7624)\n    pairs=read(ROOT/'frozen-composition/CONTACT7624-PAIRS.json')")
    change('source_then_splice',"        need(new==dict(helper_word,program=rebuilt_step1),'Literal W2+W3H-step1 reconstruction and unchanged metadata')", """        source7624=read(ROOT/'frozen-composition/7624-WORD.json.gz')
        need(sha256(canonical(source7624)).hexdigest()=='"""+SOURCE_CAN+"""' and source7624==dict(helper_word,program=rebuilt_step1),'Reconstructed exact #7624')
        manifest_path=ROOT/'frozen-composition/CONTACT7624-MANIFEST.json'
        need(sha256(manifest_path.read_bytes()).hexdigest()=='"""+sha(manifest_bytes)+"""','Exact splice manifest')
        contact=read(manifest_path);changes={e['original_index']:e for e in contact['edits']}
        need(len(changes)==len(contact['edits'])==5 and contact['source_canonical_sha256']=='"""+SOURCE_CAN+"""' and contact['candidate_canonical_sha256']==EXPECTED,'Five unique edits')
        successor=[];origins=[];reverse=[None]*len(source7624['program'])
        for i,event in enumerate(source7624['program']):
            if i in changes:
                edit=changes[i];need(event==edit['old'],'Exact original splice event');event=edit['new_or_null']
                if event is None:continue
            reverse[i]=len(successor);origins.append(i);successor.append(event)
        need(origins==contact['candidate_origins'] and reverse==contact['original_to_candidate'],'Complete origin mapping')
        need(new==dict(source7624,program=successor),'Literal candidate splice')""")
    change('peer_delta','=={1:-15,2:102,3:-205,4:81,5:8,6:9,8:1}','=={1:-17,2:104,3:-206,4:80,5:9,6:9,8:1}')
    change('old_delta','=={1:-20,2:96,3:-205,4:82,5:8,6:10,7:1,8:1}','=={1:-22,2:98,3:-206,4:81,5:9,6:10,7:1,8:1}')
    change('events',"len(old['program'])+900","len(old['program'])+899")
    change('paired_native',"        oldN,peerN,N=map(I.native,(old,peer,new))", """        oldN,peerN,N=map(I.native,(old,peer,new))
        sourceN=I.native(source7624)
        reference_path=ROOT/'frozen-composition/7624-NATIVE.json'
        need(sha256(reference_path.read_bytes()).hexdigest()=='"""+NATIVE_SHA+"""','Source native evidence hash')
        reference=read(reference_path)
        need(reference['word_canonical_sha256']=='"""+SOURCE_CAN+"""' and normalized(sourceN)==reference['native'],'Fresh source native inventory')
        need(not sourceN['bad_inputs'] and delta(N['paid'],sourceN['paid'])=={1:-2,2:2,3:-1,4:-1,5:1},'Fresh #7624 native paid delta')
        need(all(N[k]==sourceN[k] for k in ('public','helpers','rises','owned_peak','lifetimes')),'Candidate/source native boundary')""")
    change('paired_invoice',"        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)","        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)\n        source_invoice=I.invoices(source7624,C,sourceN)\n        need(normalized(source_invoice)==reference['invoice'],'Fresh source ingredient invoice')\n        need(normalized(source_invoice['T'])==normalized(invoice['T']),'Source/candidate target equality')")
    change('candidate_corruptions',"        need(all(controls.values()),'Every corruption control rejected')", """        def candidate_rejected(mutated):
            try: result=I.native(mutated)
            except (ValueError,AssertionError,KeyError,IndexError): return True
            return bool(result['bad_inputs'])
        contact=['ADD',1091,902,'1/2',373]
        need(new['program'].count(contact)==1,'Unique 902/1091 candidate contact')
        bad=deepcopy(new);i=bad['program'].index(contact);bad['program'][i][2]=1093
        controls['wrong_902_1091_contact_source']=candidate_rejected(bad)
        move=['MOVE',902,3,373,False]
        need(new['program'].count(move)==1,'Unique 902 paid movement')
        bad=deepcopy(new);bad['program'].remove(move)
        controls['missing_902_paid_move']=candidate_rejected(bad)
        need(all(controls.values()),'Every corruption control rejected')""")
    change('paired_ordinary',"        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')", """        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')
        source_ordinary=I.ordinary(source7624,C,sourceN)
        source_ordinary['caller_items']['B']['fused_routes']=routes
        for k in ('caller_total','raw_upper','conservative_total'):source_ordinary[k]+=route_delta
        source_ordinary['extra_B_scalar_surcharge']=surcharge;source_ordinary['conservative_total']+=surcharge
        source_ordinary['margin_to_billion']=10**9-source_ordinary['conservative_total']
        need(source_ordinary['margin_to_billion']>0,'Source full ordinary allowance')""")
    change('paired_precision',"        precision=base.precision(vendor,new,C,gate,manifest)","        source_gate,source_price=G.exact_price(vendor,archive,before,source_invoice,previous)\n        source_precision=base.precision(vendor,source7624,C,source_gate,manifest)\n        precision=base.precision(vendor,new,C,gate,manifest)\n        need(source_precision['context_c']==precision['context_c'],'Common ingredient precision context')")
    change('paired_receipt',"ordinary=ordinary,gate=gate,price=price,precision=precision", "ordinary=ordinary,paired_ordinary={'source_7624':source_ordinary,'candidate':ordinary,'common_U_incremental_tariff':'EXPLICIT_UNIMPLEMENTED_U_ENTIRE_EXISTING_ITEM_COVERS_ASSIGNED_SERVICE'},gate=gate,price=price,precision=precision,paired_precision={'source_7624':source_precision,'candidate':precision,'source_gate':source_gate,'source_price':source_price}")
    change('source_receipt',"native=N,forward=forward_receipt","native=N,source_native=sourceN,source_invoice=source_invoice,forward=forward_receipt")
    change('native_status',"status='PASS_W3H_ADAPTED_COMPLETE_NATIVE'","status='PASS_CONTACT7624_COMPLETE_NATIVE'")
    compile(txt,str(runner),'exec')
    p=frozen/'CONTACT7624-PAIRS.json';need(not p.exists(),'pair manifest must be new')
    p.write_bytes(pair_bytes)
    (rootwork/'producer54/reroute/WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-INVOICE.json').write_bytes((gate/'price/invoice-new.json').read_bytes())
    runner.write_bytes(txt.encode())
    return {'schema':'contact7624-native-adapter/v1','original_runner_sha256':sha(raw),'adapted_runner_sha256':sha(txt.encode()),'source_word_canonical_sha256':SOURCE_CAN,'candidate_word_canonical_sha256':c,'candidate_pair_manifest_sha256':pair_sha,'candidate_pair_count':len(pairs['full_validation_pairs']),'source_pair_count':len(pinned),'source_affected_pair_count':len(pinned),'candidate_vs7481_pair_count':len(pairs['candidate_vs7481_pairs']),'patches':records,'limitations':['Source resources are derived from this paired run; no standalone source native pass.','Common U and signed application require separate qualification.']}
