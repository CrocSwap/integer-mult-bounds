#!/usr/bin/env python3
"""Prepare counted, source-bound native adapter; execution delegated to root."""
from pathlib import Path
import gzip
import hashlib
import json

RUNNER_SHA='4e844230bdd80d3a895a8ea9a964aa830e6262a221b9f6bff04e52efb938cca2'
OLD7620_CAN='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
OLD7620_GZ='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
SOURCE_CAN='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
SOURCE_GZ='97391721ab7d30f8dd84c8d3c29a3c3ed2df2d65ca55e7ff8329bd09877681d2'
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


def pair_evidence(base,source,candidate,pinned,candidate_can):
    br,sr,cr=routes(base),routes(source),routes(candidate)
    bc=[i for i in br if br[i]!=sr[i]]
    bn={p for i in bc for p in br[i]+sr[i]}
    need(len(pinned)==964,'source #7623 affected pair census mismatch')
    changed=[i for i in br if br[i]!=cr[i]]
    direct={p for i in changed for p in br[i]+cr[i]}
    splice_changed=[i for i in sr if sr[i]!=cr[i]]
    need(splice_changed==[902,1091],'successor changed routes')
    route_extra={p for i in splice_changed for p in sr[i]+cr[i]}
    all_pairs=pinned|bn|direct|route_extra
    return {'schema':'compose7623-native-pairs/v1','base7481_canonical_sha256':BASE7481_CAN,
            'source_canonical_sha256':SOURCE_CAN,'candidate_canonical_sha256':candidate_can,
            'source_affected_count':len(pinned),'pinned_source_pairs':[list(x) for x in sorted(pinned)],'source_vs7481_pairs':[list(x) for x in sorted(bn)],'source_changed_fields':bc,
            'candidate_changed_fields':changed,'splice_changed_fields':splice_changed,
            'candidate_vs7481_pairs':[list(x) for x in sorted(direct)],
            'splice_route_pairs':[list(x) for x in sorted(route_extra)],
            'full_validation_pairs':[list(x) for x in sorted(all_pairs)]}


def adapt(rootwork:Path,roundroot:Path):
    rootwork=Path(rootwork);roundroot=Path(roundroot)
    runner=rootwork/'producer54/validation_native/run.py'
    raw=runner.read_bytes();need(sha(raw)==RUNNER_SHA,'unmodified #7620 native runner pin')
    gate=roundroot/'compose7623/run/case';result=json.loads((gate/'RESULT.json').read_bytes())
    need(result['status']=='PASS_DIFFERENTIAL_ONLY_PROVISIONAL_UNDER_COMMON_U','first-gate status')
    required=['built/candidate-word.json.gz','built/edit-manifest.json','built/status.json','exact/EXACT.json.gz','exact/status.json','rankone/RANKONE.json','rankone/status.json','physical/PHYSICAL.json','physical/status.json','price/PRICE.json','price/invoice-new.json']
    for rel in required:
        need(rel in result['receipt_hashes'] and sha((gate/rel).read_bytes())==result['receipt_hashes'][rel],'first-gate receipt '+rel)
    CANDIDATE_GZ=result['receipt_hashes']['built/candidate-word.json.gz']
    MANIFEST_SHA=result['receipt_hashes']['built/edit-manifest.json']
    CANDIDATE_INVOICE_SHA=result['receipt_hashes']['price/invoice-new.json']
    frozen=rootwork/'frozen-composition'
    source_bytes=(frozen/'7623-WORD.json.gz').read_bytes()
    candidate_bytes=(gate/'built/candidate-word.json.gz').read_bytes()
    need(sha(source_bytes)==SOURCE_GZ and sha(candidate_bytes)==CANDIDATE_GZ,'source/candidate gzip pin')
    source=readgz_bytes(source_bytes);candidate=readgz_bytes(candidate_bytes)
    need(sha(canonical(source))==SOURCE_CAN,'source canonical pin')
    need((source['public'],source['owned_fields'],len(source['program']))==(1501,68,77277) and len(candidate['program'])==77271,'source and candidate shape')
    for word in (source,candidate):
        events=word['program'];need(sum(e[0]=='INIT' for e in events)==180 and sum(e[0]=='CLEAR' for e in events)==180 and sum(e[0]=='MOVE' and e[1]>=1501 for e in events)==47,'180 lifetimes and 47 owned moves')
    CANDIDATE_CAN=sha(canonical(candidate))
    manifest_bytes=(gate/'built/edit-manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
    need(manifest['candidate_canonical_sha256']==CANDIDATE_CAN and manifest['source_canonical_sha256']==SOURCE_CAN,'manifest word pins')
    exact=json.loads((gate/'exact/status.json').read_bytes());need(exact['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and exact['source']['candidate_canonical_sha256']==CANDIDATE_CAN,'exact gate status/binding')
    price=json.loads((gate/'price/PRICE.json').read_bytes());need(price['status']=='PROVISIONAL_UNDER_COMMON_U' and price['bindings']['candidate_canonical_sha256']==CANDIDATE_CAN and price['bindings']['original_word_canonical_sha256']==SOURCE_CAN,'price gate status/binding')
    need(price['candidate_invoice']['sha256']==CANDIDATE_INVOICE_SHA,'price invoice binding')
    existing=(rootwork/'producer54/reroute/WORD.json.gz').read_bytes();need(sha(canonical(readgz_bytes(existing)))==OLD7620_CAN,'prepared source W3 must be intact')
    baseline=readgz_bytes((frozen/'7481-WORD.json.gz').read_bytes())
    need(sha(canonical(baseline))==BASE7481_CAN,'7481 comparator canonical pin')
    source_package=roundroot/'inputs/pr7623/research/p104-loan-snapshot-engine-on7621/data'
    pinned_bytes=(source_package/'affected-pairs-loan.json').read_bytes()
    pinned_list=json.loads(pinned_bytes);pinned={tuple(x) for x in pinned_list}
    need(len(pinned)==len(pinned_list)==964,'unique 964 authenticated source pairs')
    pairs=pair_evidence(baseline,source,candidate,pinned,CANDIDATE_CAN);pair_bytes=canonical(pairs)+b'\n';pair_sha=sha(pair_bytes)
    source_native=(frozen/'7620-NATIVE.json').read_bytes();need(sha(source_native)==SOURCE_NATIVE_SHA,'7620 native receipt pin')
    old_source=(frozen/'7620-WORD.json.gz').read_bytes();need(sha(old_source)==OLD7620_GZ and sha(canonical(readgz_bytes(old_source)))==OLD7620_CAN,'7620 word pin')
    source_invoice=(frozen/'7620-INVOICE.json').read_bytes();need(sha(source_invoice)==SOURCE_INVOICE_SHA,'7620 invoice pin')
    candidate_invoice=(gate/'price/invoice-new.json').read_bytes();need(sha(candidate_invoice)==CANDIDATE_INVOICE_SHA,'candidate invoice pin')
    need(sha(canonical(readgz_bytes((frozen/'CANDIDATE-WORD.json.gz').read_bytes())))==OLD7620_CAN,'prepared 7620 frozen word binding')
    for name, package_file in (('7621-WORD.json.gz',roundroot/'inputs/pr7621/research/p104-courier-restop-on7620/data/word.json.gz'),('7621-EDITS.json',roundroot/'inputs/pr7621/research/p104-courier-restop-on7620/data/edits.json'),('7623-WORD.json.gz',source_package/'word.json.gz'),('7623-EDITS.json',source_package/'edits.json')):
        need((frozen/name).read_bytes()==package_file.read_bytes(),'exact authenticated package copy '+name)
    need((frozen/'CONTACT7623-MANIFEST.json').read_bytes()==manifest_bytes,'exact gate manifest copy')
    need((frozen/'CONTACT7623-PRICE.json').read_bytes()==(gate/'price/PRICE.json').read_bytes(),'exact gate price copy')
    need((frozen/'7623-PAIRS.json').read_bytes()==pinned_bytes,'exact source pair copy')
    need((frozen/'7623-INVOICE.json').read_bytes()==(source_package/'invoice-new.json').read_bytes(),'exact source invoice copy')
    need((frozen/'7623-NEW-CERTS.json').read_bytes()==(source_package/'clear-certificates.json').read_bytes(),'exact source clear certificate copy')
    need(raw.count(b'\r\n')==208 and raw.count(b'\n')==208 and raw.count(b'\r')==208,'source runner line ending pin')
    txt=raw.decode('utf-8').replace('\r\n','\n')
    records=[{'label':'source_CRLF_to_LF','occurrences':208,'original_runner_sha256':sha(raw),'normalized_sha256':sha(txt.encode())}]
    def change(label,old,new,expected_count=1):
        nonlocal txt
        count=txt.count(old);need(count==expected_count,'runner anchor occurrence mismatch: '+label)
        txt=txt.replace(old,new,expected_count);records.append({'label':label,'occurrences':count,'old_sha256':sha(old.encode()),'new_sha256':sha(new.encode())})
    change('candidate_hash',"EXPECTED='"+OLD7620_CAN+"'","EXPECTED='"+CANDIDATE_CAN+"'")
    change('preserve_source_pair_census',"    old_routes,new_routes=routes(before),routes(word)","    source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')\n    need(sha256(canonical(source7620)).hexdigest()=='"+OLD7620_CAN+"','Exact source 7620 for preserved physical census')\n    old_routes,new_routes=routes(before),routes(source7620)")
    change('candidate_pair_census',"    report=[]\n    for a,b in sorted(affected):", "    pairs_path=ROOT/'frozen-composition/CONTACT7623-PAIRS.json'\n    need(sha256(pairs_path.read_bytes()).hexdigest()=='"+pair_sha+"','Frozen full pair manifest')\n    pairs=read(pairs_path)\n    source7623=read(ROOT/'frozen-composition/7623-WORD.json.gz')\n    source_routes=routes(source7623);candidate_routes=routes(word)\n    source_fields=[i for i in old_routes if old_routes[i]!=source_routes[i]]\n    candidate_fields=[i for i in old_routes if old_routes[i]!=candidate_routes[i]]\n    splice_fields=[i for i in source_routes if source_routes[i]!=candidate_routes[i]]\n    need(splice_fields==[902,1091],'Exact splice route fields')\n    pinned={tuple(x) for x in pairs['pinned_source_pairs']}\n    need(len(pinned)==964,'964 protected source pairs')\n    affected=pinned | {p for i in source_fields for p in old_routes[i]+source_routes[i]} | {p for i in candidate_fields for p in old_routes[i]+candidate_routes[i]} | {p for i in splice_fields for p in source_routes[i]+candidate_routes[i]}\n    need(affected=={tuple(x) for x in pairs['full_validation_pairs']},'Complete fresh pair union')\n    need(candidate_fields==pairs['candidate_changed_fields'],'Fresh changed public fields')\n    changed=candidate_fields\n    report=[]\n    for a,b in sorted(affected):")
    change('retain_W3_reconstruction_then_splice',"        need(new==dict(helper_word,program=rebuilt),'Literal W2 reconstruction and unchanged metadata')", """        source7620=read(ROOT/'frozen-composition/7620-WORD.json.gz')
        need(sha256(canonical(source7620)).hexdigest()=='"""+OLD7620_CAN+"""' and source7620==dict(helper_word,program=rebuilt),'Original 7620 reconstructed')
        def apply_pinned(word,filename):
            E=read(ROOT/'frozen-composition'/filename);program=word['program']
            need(len(program)==E['base_events'],'edit base length')
            deletes={};inserts={}
            for i,event in E['delete']:
                need(type(i)==int and 0<=i<len(program) and i not in deletes and program[i]==event,'unique exact deletion');deletes[i]=event
            for i,events in E['insert_before']:
                need(type(i)==int and 0<=i<=len(program),'insertion position');inserts.setdefault(i,[]).extend(events)
            out=[]
            for i,event in enumerate(program):
                out.extend(inserts.get(i,[]))
                if i not in deletes:out.append(event)
            out.extend(inserts.get(len(program),[]));out.extend(E['append'])
            return dict(word,program=out)
        source7621=read(ROOT/'frozen-composition/7621-WORD.json.gz')
        need(apply_pinned(source7620,'7621-EDITS.json')==source7621,'Exact 7620 to 7621 reconstruction')
        source7623=read(ROOT/'frozen-composition/7623-WORD.json.gz')
        need(sha256(canonical(source7623)).hexdigest()=='"""+SOURCE_CAN+"""' and apply_pinned(source7621,'7623-EDITS.json')==source7623,'Exact 7621 to 7623 reconstruction')
        manifest_path=ROOT/'frozen-composition/CONTACT7623-MANIFEST.json'
        need(sha256(manifest_path.read_bytes()).hexdigest()=='"""+MANIFEST_SHA+"""','Frozen contact manifest')
        manifest=read(manifest_path);changes={e['original_index']:e for e in manifest['edits']}
        need(len(manifest['edits'])==len(changes)==10 and manifest['source_canonical_sha256']=='"""+SOURCE_CAN+"""' and manifest['candidate_canonical_sha256']==EXPECTED,'Exact ten edits')
        successor=[];origins=[];reverse=[None]*len(source7623['program'])
        for i,event in enumerate(source7623['program']):
            if i in changes:
                edit=changes[i];need(event==edit['old'],'Exact original splice literal');event=edit['new_or_null']
                if event is None:continue
            reverse[i]=len(successor);origins.append(i);successor.append(event)
        need(origins==manifest['candidate_origins'] and reverse==manifest['original_to_candidate'],'Complete origin map')
        need(new==dict(source7623,program=successor),'Exact successor and unchanged metadata')""")
    change('lifetime_envelope',"(life, peak, owned_count) == (167, 50, 68)","(life, peak, owned_count) == (180, 50, 68)",expected_count=2)
    change('owned_census',"need(owned.validate_word(new)['lifetimes']==167", "need(owned.validate_word(new)['lifetimes']==180")
    change('native_lifetimes',"N['lifetimes']==167", "N['lifetimes']==180")
    change('peer_delta',"{1: -12, 2: 76, 3: -148, 4: 55, 5: 8, 6: 6, 8: 1}","{1: -13, 2: 91, 3: -179, 4: 67, 5: 10, 6: 7, 8: 1}")
    change('source_delta',"{1: -17, 2: 70, 3: -148, 4: 56, 5: 8, 6: 7, 7: 1, 8: 1}","{1: -18, 2: 85, 3: -179, 4: 68, 5: 10, 6: 8, 7: 1, 8: 1}")
    change('event_count',"len(new['program'])==len(old['program'])+722","len(new['program'])==len(old['program'])+799")
    change('source_native_reconstruction',"        oldN,peerN,N=map(I.native,(old,peer,new))", """        oldN,peerN,N=map(I.native,(old,peer,new))
        source7620N=I.native(source7620)
        sourceN=I.native(source7623)
        reference_path=ROOT/'frozen-composition/7620-NATIVE.json'
        need(sha256(reference_path.read_bytes()).hexdigest()=='"""+SOURCE_NATIVE_SHA+"""','Exact source 7620 native receipt')
        reference=read(reference_path)
        need(reference['status']=='PASS_W3_ADAPTED_COMPLETE_NATIVE' and reference['word_canonical_sha256']=='"""+OLD7620_CAN+"""','Source native receipt binding')
        need(normalized(source7620N)==reference['native'] and not source7620N['bad_inputs'] and not sourceN['bad_inputs'],'Fresh original 7620 native inventory')
        need(delta(N['paid'],sourceN['paid'])=={1:-3,2:1,4:-1,5:1},'Exact candidate-versus-7623 native paid delta')
        need(all(N[k]==sourceN[k] for k in ('public','helpers','rises','owned_peak','lifetimes')),'Candidate versus 7623 native boundary')""")
    change('source_ingredient_invoice',"        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)","        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)\n        source_invoice=I.invoices(source7623,C,sourceN)\n        need(not sourceN['bad_inputs'],'Fresh 7623 native inventory')\n        need(normalized(source_invoice['T'])==normalized(invoice['T']),'Current source versus candidate ingredient target equality')")
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
        source_ordinary=I.ordinary(source7623,C,sourceN)
        source_ordinary['caller_items']['B']['fused_routes']=routes
        for k in ('caller_total','raw_upper','conservative_total'):source_ordinary[k]+=route_delta
        source_ordinary['extra_B_scalar_surcharge']=surcharge;source_ordinary['conservative_total']+=surcharge
        source_ordinary['margin_to_billion']=10**9-source_ordinary['conservative_total']
        need(source_ordinary['margin_to_billion']>0,'Source complete ordinary allowance')
""")
    change('fresh_source_precision',"        precision=base.precision(vendor,new,C,gate,manifest)","        source_gate,source_price=G.exact_price(vendor,archive,before,source_invoice,previous)\n        source_precision=base.precision(vendor,source7623,C,source_gate,manifest)\n        precision=base.precision(vendor,new,C,gate,manifest)\n        need(source_precision['context_c']==precision['context_c'],'Unequal precision contexts require explicit common cprec review')")
    change('paired_ordinary_receipt',"ordinary=ordinary,gate=gate,price=price,precision=precision", "ordinary=ordinary,paired_ordinary={'source_7623':source_ordinary,'candidate':ordinary,'formula':'same fresh 18-stage ingredient caller, route adjustment and scalar surcharge','common_U_incremental_tariff':'UNRESOLVED_NOT_INCLUDED'},gate=gate,price=price,precision=precision,paired_precision={'source_7623':source_precision,'candidate':precision,'source_gate':source_gate,'source_price':source_price,'context_comparison':{k:{'source':source_precision[k],'candidate':precision[k],'equal':source_precision[k]==precision[k]} for k in ('context_c','context_height','context_mass_bits')},'scope':'Fresh native ingredient envelopes on both words; signed precision/tape and common U service are separate.'}")
    change('source_head',"source_head='58a9d052143f5d85295ed2d0163591c47f89a331'","source_head='2ee2f0b61f7d123e8862482b966699cca578be6d',predecessor_source_head='58a9d052143f5d85295ed2d0163591c47f89a331'")
    change('common_U_limitation',"'The complete 17-stage signed application is checked separately.'","'The complete 17-stage signed application is checked separately.','Common U is a stronger unimplemented service; changed private states and its full numerical tariff remain unresolved.'")
    change('fresh_source_result_fields',"native=N,forward=forward_receipt","native=N,source_native=sourceN,source_invoice=source_invoice,forward=forward_receipt")
    change('candidate_native_status',"status='PASS_W3_ADAPTED_COMPLETE_NATIVE'","status='PASS_CONTACT7623_COMPLETE_NATIVE'")
    # Before any writes, compilation catches malformed source patches without running it.
    compile(txt,str(runner),'exec')
    prepared_pins={
        '7620-WORD.json.gz':OLD7620_GZ,
        '7620-NATIVE.json':SOURCE_NATIVE_SHA,
        '7620-INVOICE.json':SOURCE_INVOICE_SHA,
        'CONTACT7623-MANIFEST.json':MANIFEST_SHA,
    }
    for name,pin in prepared_pins.items():
        need(sha((frozen/name).read_bytes())==pin,'prepared frozen source pin '+name)
    need(not (frozen/'CONTACT7623-PAIRS.json').exists(),'candidate pair manifest already exists')
    (frozen/'CONTACT7623-PAIRS.json').write_bytes(pair_bytes)
    (rootwork/'producer54/reroute/WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-WORD.json.gz').write_bytes(candidate_bytes)
    (frozen/'CANDIDATE-INVOICE.json').write_bytes(candidate_invoice)
    runner.write_bytes(txt.encode('utf-8'))
    return {'schema':'contact7623-native-adapter/v1','original_runner_sha256':sha(raw),'adapted_runner_sha256':sha(txt.encode()),
            'source_word_canonical_sha256':SOURCE_CAN,'candidate_word_canonical_sha256':CANDIDATE_CAN,
            'historical_7620_native_receipt_sha256':SOURCE_NATIVE_SHA,'first_gate_result_sha256':sha((gate/'RESULT.json').read_bytes()),'source_pair_file_sha256':sha(pinned_bytes),'historical_7620_invoice_sha256':SOURCE_INVOICE_SHA,'source_7623_invoice_sha256':sha((frozen/'7623-INVOICE.json').read_bytes()),
            'candidate_declared_invoice_sha256':CANDIDATE_INVOICE_SHA,'manifest_sha256':MANIFEST_SHA,
            'candidate_overlays':{'producer54/reroute/WORD.json.gz':CANDIDATE_GZ,'frozen-composition/CANDIDATE-WORD.json.gz':CANDIDATE_GZ,'frozen-composition/CANDIDATE-INVOICE.json':CANDIDATE_INVOICE_SHA},
            'candidate_pair_manifest_sha256':pair_sha,'candidate_pair_count':len(pairs['full_validation_pairs']),
            'candidate_vs7481_pair_count':len(pairs['candidate_vs7481_pairs']),'source_pair_count':pairs['source_affected_count'],
            'patches':records,'limitations':['Common U requires separate full numerical service and accounting.',
             'Native result is not full signed caller qualification.']}
