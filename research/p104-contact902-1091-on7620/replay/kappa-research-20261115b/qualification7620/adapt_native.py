#!/usr/bin/env python3
"""Prepare counted, source-bound native adapter; execution delegated to root."""
from pathlib import Path
import gzip
import hashlib
import json

RUNNER_SHA='4e844230bdd80d3a895a8ea9a964aa830e6262a221b9f6bff04e52efb938cca2'
SOURCE_CAN='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
SOURCE_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
CANDIDATE_CAN='03da65fb97ffaf4d0e9756f3867df588b162975f6015d8458821d05b5fcb006b'
CANDIDATE_GZ='4d742e0b6e915cc3c3d31d18d5d2703c1f943c695c25d7c5a24f04626c1f5235'
MANIFEST_SHA='58fd6a8fb76f0dad335abab6973f0ceae29a1c687c47cb2d98d6d0c64e9ed1e7'
SOURCE_NATIVE_SHA='151e88d588d254d10fe8c9acc2201991ef8fc166990269f3863f270fffbceb0e'
SOURCE_INVOICE_SHA='61aaf72892d2bc2f9fac9dce37b3d62b01d15f4fa47e9f6fa2fceace7735b5ab'
CANDIDATE_INVOICE_SHA='82c4d37ebf48a43acd78aa8c3bc68b0972b90f03214a245734bc09201da8e10c'
BASE7481_CAN='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'


def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def readgz_bytes(b):return json.loads(gzip.decompress(b))
def need(ok,label):
    if not ok:raise ValueError(label)
def routes(w):
    out={i:[] for i in range(w['public'])}
    for e in w['program']:
        if e[0]=='MOVE' and e[1]<w['public']:out[e[1]].append(tuple(e[2:4]))
    return out


def pair_evidence(base,source,candidate):
    br,sr,cr=routes(base),routes(source),routes(candidate)
    bc=[i for i in br if br[i]!=sr[i]]
    bn={p for i in bc for p in br[i]+sr[i]}
    need(len(bn)==837,'source #7620 affected pair census mismatch')
    changed=[i for i in br if br[i]!=cr[i]]
    direct={p for i in changed for p in br[i]+cr[i]}
    splice_changed=[i for i in sr if sr[i]!=cr[i]]
    need(splice_changed==[902,1091],'successor changed routes')
    route_extra={p for i in splice_changed for p in sr[i]+cr[i]}
    all_pairs=direct|route_extra
    return {'schema':'compose7620-native-pairs/v1','base7481_canonical_sha256':BASE7481_CAN,
            'source_canonical_sha256':SOURCE_CAN,'candidate_canonical_sha256':CANDIDATE_CAN,
            'source_affected_count':len(bn),'source_changed_fields':bc,
            'candidate_changed_fields':changed,'splice_changed_fields':splice_changed,
            'candidate_vs7481_pairs':[list(x) for x in sorted(direct)],
            'splice_route_pairs':[list(x) for x in sorted(route_extra)],
            'full_validation_pairs':[list(x) for x in sorted(all_pairs)]}


def adapt(rootwork:Path,roundroot:Path):
    rootwork=Path(rootwork);roundroot=Path(roundroot)
    runner=rootwork/'producer54/validation_native/run.py'
    raw=runner.read_bytes();need(sha(raw)==RUNNER_SHA,'unmodified #7620 native runner pin')
    gate=roundroot/'compose7620/run/case';result=json.loads((gate/'RESULT.json').read_bytes())
    need(result['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','first-gate status')
    required=['built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/EXACT.json.gz','exact/status.json','rankone/RANKONE.json','rankone/status.json','physical/PHYSICAL.json','physical/status.json','price/PRICE.json','price/invoice-new.json']
    for rel in required:
        need(rel in result['receipt_hashes'] and sha((gate/rel).read_bytes())==result['receipt_hashes'][rel],'first-gate receipt '+rel)
    need(result['receipt_hashes']['built/candidate-word.json.gz']==CANDIDATE_GZ and result['receipt_hashes']['built/edit-manifest.json']==MANIFEST_SHA,'fixed first-gate artifact pins')
    exact=json.loads((gate/'exact/status.json').read_bytes());need(exact['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and exact['source']['candidate_canonical_sha256']==CANDIDATE_CAN,'exact gate status/binding')
    price=json.loads((gate/'price/PRICE.json').read_bytes());need(price['status']=='PROVISIONAL_UNDER_COMMON_U' and price['bindings']['candidate_canonical_sha256']==CANDIDATE_CAN,'price gate status/binding')
    source_bytes=(roundroot/'inputs/pr7620/data/word.json.gz').read_bytes();candidate_bytes=(gate/'built/candidate-word.json.gz').read_bytes()
    need(sha(source_bytes)==SOURCE_GZ and sha(candidate_bytes)==CANDIDATE_GZ,'source/candidate gzip pin')
    source=readgz_bytes(source_bytes);candidate=readgz_bytes(candidate_bytes)
    need(sha(canonical(source))==SOURCE_CAN and sha(canonical(candidate))==CANDIDATE_CAN,'source/candidate canonical pin')
    manifest_bytes=(gate/'built/edit-manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
    need(manifest['candidate_canonical_sha256']==CANDIDATE_CAN and manifest['source_canonical_sha256']==SOURCE_CAN,'manifest word pins')
    existing=(rootwork/'producer54/reroute/WORD.json.gz').read_bytes();need(sha(canonical(readgz_bytes(existing)))==SOURCE_CAN,'prepared source W3 must be intact')
    frozen=rootwork/'frozen-composition';baseline_bytes=(frozen/'7481-WORD.json.gz').read_bytes();baseline=readgz_bytes(baseline_bytes)
    need(sha(canonical(baseline))==BASE7481_CAN,'7481 comparator canonical pin')
    pairs=pair_evidence(baseline,source,candidate);pair_bytes=canonical(pairs)+b'\n';pair_sha=sha(pair_bytes)
    source_native=(roundroot/'inputs/pr7620/evidence/FULL-NATIVE-RESULT.json').read_bytes();need(sha(source_native)==SOURCE_NATIVE_SHA,'7620 native receipt pin')
    source_invoice=(roundroot/'inputs/pr7620/data/invoice.json').read_bytes();need(sha(source_invoice)==SOURCE_INVOICE_SHA,'7620 signed invoice pin')
    candidate_invoice=(gate/'price/invoice-new.json').read_bytes();need(sha(candidate_invoice)==CANDIDATE_INVOICE_SHA,'candidate declared invoice pin')
    prior_invoice=(frozen/'CANDIDATE-INVOICE.json').read_bytes();si=json.loads(source_invoice);pi=json.loads(prior_invoice)
    need(pi['paid']==si['paid'] and pi['targets']==si['targets'],'prepared source signed invoice binding')
    need(sha(canonical(readgz_bytes((frozen/'CANDIDATE-WORD.json.gz').read_bytes())))==SOURCE_CAN,'prepared source frozen word binding')
    need(raw.count(b'\r\n')==208 and raw.count(b'\n')==208 and raw.count(b'\r')==208,'source runner line ending pin')
    txt=raw.decode('utf-8').replace('\r\n','\n')
    records=[{'label':'source_CRLF_to_LF','occurrences':208,'original_runner_sha256':sha(raw),'normalized_sha256':sha(txt.encode())}]
    def change(label,old,new):
        nonlocal txt
        count=txt.count(old);need(count==1,'nonunique runner anchor: '+label)
        txt=txt.replace(old,new,1);records.append({'label':label,'occurrences':count,'old_sha256':sha(old.encode()),'new_sha256':sha(new.encode())})
    change('candidate_hash',"EXPECTED='"+SOURCE_CAN+"'","EXPECTED='"+CANDIDATE_CAN+"'")
    change('preserve_source_pair_census',"    old_routes,new_routes=routes(before),routes(word)","    source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')\n    need(sha256(canonical(source7620)).hexdigest()=='"+SOURCE_CAN+"','Exact source 7620 for preserved physical census')\n    old_routes,new_routes=routes(before),routes(source7620)")
    change('candidate_pair_census',"    report=[]\n    for a,b in sorted(affected):", "    pairs_path=ROOT/'frozen-composition/CONTACT7620-PAIRS.json'\n    need(sha256(pairs_path.read_bytes()).hexdigest()=='"+pair_sha+"','Exact independently frozen candidate-pair manifest')\n    pairs=read(pairs_path)\n    candidate_routes=routes(word)\n    changed=[i for i in old_routes if old_routes[i]!=candidate_routes[i]]\n    affected={pair for i in changed for pair in old_routes[i]+candidate_routes[i]}\n    splice_changed=[i for i in new_routes if new_routes[i]!=candidate_routes[i]]\n    need(splice_changed==[902,1091],'Exact splice route fields')\n    affected |= {pair for i in splice_changed for pair in new_routes[i]+candidate_routes[i]}\n    need(affected=={tuple(x) for x in pairs['full_validation_pairs']},'Complete fresh candidate affected pairs')\n    need(changed==pairs['candidate_changed_fields'],'Fresh changed public fields')\n    report=[]\n    for a,b in sorted(affected):")
    change('retain_W3_reconstruction_then_splice',"        need(new==dict(helper_word,program=rebuilt),'Literal W2 reconstruction and unchanged metadata')", """        source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')
        need(sha256(canonical(source7620)).hexdigest()=='"""+SOURCE_CAN+"""','Exact original 7620 source')
        need(source7620==dict(helper_word,program=rebuilt),'Literal original W3 reconstruction and unchanged metadata')
        manifest_path=ROOT/'frozen-composition/CONTACT7620-MANIFEST.json'
        need(sha256(manifest_path.read_bytes()).hexdigest()=='"""+MANIFEST_SHA+"""','Exact frozen successor edit manifest')
        manifest=read(manifest_path); changes={e['original_index']:e for e in manifest['edits']}
        need(len(changes)==10 and manifest['source_canonical_sha256']=='"""+SOURCE_CAN+"""' and manifest['candidate_canonical_sha256']==EXPECTED,'Exact successor source/candidate edit contract')
        successor=[];origins=[];reverse=[None]*len(rebuilt)
        for i,event in enumerate(rebuilt):
            if i in changes:
                edit=changes[i];need(event==edit['old'],'Exact original splice literal')
                event=edit['new_or_null']
                if event is None:continue
            reverse[i]=len(successor);origins.append(i);successor.append(event)
        need(origins==manifest['candidate_origins'] and reverse==manifest['original_to_candidate'],'Complete successor origin map')
        need(new==dict(helper_word,program=successor),'Exact successor word and unchanged full metadata')""")
    change('peer_delta',"{1: -12, 2: 76, 3: -148, 4: 55, 5: 8, 6: 6, 8: 1}","{1: -15, 2: 77, 3: -148, 4: 54, 5: 9, 6: 6, 8: 1}")
    change('source_delta',"{1: -17, 2: 70, 3: -148, 4: 56, 5: 8, 6: 7, 7: 1, 8: 1}","{1: -20, 2: 71, 3: -148, 4: 55, 5: 9, 6: 7, 7: 1, 8: 1}")
    change('event_count',"len(new['program'])==len(old['program'])+722","len(new['program'])==len(old['program'])+716")
    change('source_native_reconstruction',"        oldN,peerN,N=map(I.native,(old,peer,new))", """        oldN,peerN,N=map(I.native,(old,peer,new))
        sourceN=I.native(source7620)
        reference_path=ROOT/'frozen-composition/7620-NATIVE.json'
        need(sha256(reference_path.read_bytes()).hexdigest()=='"""+SOURCE_NATIVE_SHA+"""','Exact source 7620 native receipt')
        reference=read(reference_path)
        need(reference['status']=='PASS_W3_ADAPTED_COMPLETE_NATIVE' and reference['word_canonical_sha256']=='"""+SOURCE_CAN+"""','Source native receipt binding')
        need(normalized(sourceN)==reference['native'] and not sourceN['bad_inputs'],'Fresh original 7620 native inventory')
        need(delta(N['paid'],sourceN['paid'])=={1:-3,2:1,4:-1,5:1},'Exact candidate-versus-7620 native paid delta')
        need(all(N[k]==sourceN[k] for k in ('public','helpers','rises','owned_peak','lifetimes')),'Candidate versus 7620 native boundary')""")
    change('source_ingredient_invoice',"        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)","        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)\n        source_invoice=I.invoices(source7620,C,sourceN)\n        need(normalized(source_invoice)==reference['invoice'],'Fresh complete 7620 native ingredient invoice')")
    change('new_corruption_controls',"        need(all(controls.values()),'Every corruption control rejected')", """        def candidate_rejected(mutated):
            try:
                result=I.native(mutated)
            except (ValueError,AssertionError,KeyError,IndexError):
                return True
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
    change('paired_source_ordinary',"        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')", """        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')
        source_ordinary=I.ordinary(source7620,C,sourceN)
        source_ordinary['caller_items']['B']['fused_routes']=routes
        for k in ('caller_total','raw_upper','conservative_total'):source_ordinary[k]+=route_delta
        source_ordinary['extra_B_scalar_surcharge']=surcharge;source_ordinary['conservative_total']+=surcharge
        source_ordinary['margin_to_billion']=10**9-source_ordinary['conservative_total']
        need(source_ordinary['margin_to_billion']>0,'Source complete ordinary allowance')
        need(source_ordinary['conservative_total']==863312128,'Source 7620 ingredient ordinary total')
        need(normalized(source_ordinary)==reference['ordinary'],'Fresh source ordinary with identical caller route and scalar surcharge')""")
    change('fresh_source_precision',"        precision=base.precision(vendor,new,C,gate,manifest)","        source_gate,source_price=G.exact_price(vendor,archive,before,source_invoice,previous)\n        source_precision=base.precision(vendor,source7620,C,source_gate,manifest)\n        need(normalized(source_precision)==reference['precision'],'Fresh full 7620 precision equals deterministic pinned reference')\n        precision=base.precision(vendor,new,C,gate,manifest)")
    change('paired_ordinary_receipt',"ordinary=ordinary,gate=gate,price=price,precision=precision", "ordinary=ordinary,paired_ordinary={'source_7620':source_ordinary,'candidate':ordinary,'formula':'same fresh 18-stage ingredient caller, route adjustment and scalar surcharge','common_U_incremental_tariff':'UNRESOLVED_NOT_INCLUDED'},gate=gate,price=price,precision=precision,paired_precision={'source_7620':source_precision,'candidate':precision,'source_gate':source_gate,'source_price':source_price,'scope':'Fresh native ingredient envelopes on both words; signed precision/tape and common U service are separate.'}")
    change('source_head',"source_head='58a9d052143f5d85295ed2d0163591c47f89a331'","source_head='b1356c84a0733843ce59855f02511c49c6a44133',predecessor_source_head='58a9d052143f5d85295ed2d0163591c47f89a331'")
    change('common_U_limitation',"'The complete 17-stage signed application is checked separately.'","'The complete 17-stage signed application is checked separately.','Common U is a stronger unimplemented service; changed private states and its full numerical tariff remain unresolved.'")
    change('fresh_source_result_fields',"native=N,forward=forward_receipt","native=N,source_native=sourceN,source_invoice=source_invoice,forward=forward_receipt")
    change('candidate_native_status',"status='PASS_W3_ADAPTED_COMPLETE_NATIVE'","status='PASS_CONTACT7620_COMPLETE_NATIVE'")
    # Before any writes, compilation catches malformed source patches without running it.
    compile(txt,str(runner),'exec')
    prepared_pins={
        '7620-WORD.json.gz':SOURCE_GZ,
        '7620-NATIVE.json':SOURCE_NATIVE_SHA,
        '7620-INVOICE.json':SOURCE_INVOICE_SHA,
        'CONTACT7620-MANIFEST.json':MANIFEST_SHA,
    }
    for name,pin in prepared_pins.items():
        need(sha((frozen/name).read_bytes())==pin,'prepared frozen source pin '+name)
    need(not (frozen/'CONTACT7620-PAIRS.json').exists(),'candidate pair manifest already exists')
    (frozen/'CONTACT7620-PAIRS.json').write_bytes(pair_bytes)
    (rootwork/'producer54/reroute/WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-INVOICE.json').write_bytes(candidate_invoice)
    runner.write_bytes(txt.encode('utf-8'))
    return {'schema':'contact7620-native-adapter/v1','original_runner_sha256':sha(raw),'adapted_runner_sha256':sha(txt.encode()),
            'source_word_canonical_sha256':SOURCE_CAN,'candidate_word_canonical_sha256':CANDIDATE_CAN,
            'source_native_receipt_sha256':SOURCE_NATIVE_SHA,'source_invoice_sha256':SOURCE_INVOICE_SHA,
            'candidate_declared_invoice_sha256':CANDIDATE_INVOICE_SHA,'manifest_sha256':MANIFEST_SHA,
            'candidate_overlays':{'producer54/reroute/WORD.json.gz':CANDIDATE_GZ,'frozen-composition/CANDIDATE-WORD.json.gz':CANDIDATE_GZ,'frozen-composition/CANDIDATE-INVOICE.json':CANDIDATE_INVOICE_SHA},
            'candidate_pair_manifest_sha256':pair_sha,'candidate_pair_count':len(pairs['full_validation_pairs']),
            'candidate_vs7481_pair_count':len(pairs['candidate_vs7481_pairs']),'source_pair_count':pairs['source_affected_count'],
            'patches':records,'limitations':['Common U requires separate full numerical service and accounting.',
             'Native result is not full signed caller qualification.']}
