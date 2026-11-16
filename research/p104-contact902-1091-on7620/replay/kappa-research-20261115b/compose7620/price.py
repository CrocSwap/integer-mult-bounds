#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Provisional common-U declared-invoice comparison; no application admission.

Adapted from Clear1nsight's #7612 price.py and Ali Romman's #7605; retain the
notices and contributors of the unchanged directed integer-power comparator and
independent directed log/exp interval engine. Execute only under root's gate.
"""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import runpy
import sys

OLD_INVOICE_SHA='61aaf72892d2bc2f9fac9dce37b3d62b01d15f4fa47e9f6fa2fceace7735b5ab'
SOURCE_GZIP_SHA='2eb2cf1d29529c68a6cb1c0639de3065a805858d3492068e76b70c5a5e80a81c'
SOURCE_CANON_SHA='6c46ad38d812ae110392f1c977cc6f02665f8860e98ef1c21cb539ff3779533d'
ENGINE_SHA='52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad'
COMPARE_SHA='3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6'
INTERVAL_SHA='60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5'
DELTA_NATIVE={'1':-3,'2':1,'4':-1,'5':1}
DELTA_SIGNED={'1':-51,'2':17,'4':-17,'5':17}
CONFIG_SHA='3e6b52cb52f72d0663436b0c4c2f60f61a099578cc362541fbafacb12d16a0e8'
BIT_CAP=Q('0.00376669')


def need(ok,label):
    if not ok:raise ValueError(label)
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def read_json(path):return json.loads(Path(path).read_bytes())
def diff(old,new):
    return {k:new.get(k,0)-old.get(k,0) for k in sorted(old.keys()|new.keys(),key=int) if new.get(k,0)!=old.get(k,0)}
def write(path,obj):path.write_bytes(canon(obj)+b'\n')


def certify(root,built,exact,out):
    root=Path(root);built=Path(built);exact=Path(exact);out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    try:
        need(not sys.flags.optimize,'interval proof requires assertions enabled')
        word=root/'inputs/pr7620/data/word.json.gz';old_invoice=root/'inputs/pr7620/data/invoice.json'
        config_bytes=(root/'compose7620/CONFIG.json').read_bytes()
        need(sha(config_bytes)==CONFIG_SHA,'frozen config hash')
        config=json.loads(config_bytes);old_upper=Q(config['raw_bracket_source'][1])
        source_word=word.read_bytes();need(sha(source_word)==SOURCE_GZIP_SHA,'original word compressed pin')
        need(sha(canon(json.loads(gzip.decompress(source_word))))==SOURCE_CANON_SHA,'original word canonical pin')
        need(sha(old_invoice.read_bytes())==OLD_INVOICE_SHA,'original invoice pin')
        manifest_bytes=(built/'edit-manifest.json').read_bytes();manifest=json.loads(manifest_bytes)
        need(read_json(built/'status.json')['status']=='CANDIDATE_BUILT_UNQUALIFIED','builder status')
        candidate_bytes=(built/'candidate-word.json.gz').read_bytes()
        need(sha(candidate_bytes)==manifest['candidate_gzip_sha256'],'candidate compressed pin')
        need(sha(canon(json.loads(gzip.decompress(candidate_bytes))))==manifest['candidate_canonical_sha256'],'candidate canonical pin')
        need(manifest['source_gzip_sha256']==SOURCE_GZIP_SHA and manifest['source_canonical_sha256']==SOURCE_CANON_SHA,'manifest source pin')
        exact_bytes=(exact/'EXACT.json.gz').read_bytes(); exact_status=read_json(exact/'status.json')
        need(exact_status['status']=='U_CONDITIONAL_LITERAL_EXACT_ONLY' and sha(exact_bytes)==exact_status['exact_gzip_sha256'],'exact status or compressed pin')
        raw_exact=gzip.decompress(exact_bytes);need(sha(raw_exact)==exact_status['exact_sha256'],'exact content pin')
        X=json.loads(raw_exact);need(X['schema']=='compose7620-exact/v1','exact schema')
        src=X['source']
        need(src['original_canonical_sha256']==SOURCE_CANON_SHA and src['original_gzip_sha256']==SOURCE_GZIP_SHA,'exact source binding')
        need(src['candidate_canonical_sha256']==manifest['candidate_canonical_sha256'] and src['candidate_gzip_sha256']==manifest['candidate_gzip_sha256'] and src['manifest_sha256']==sha(manifest_bytes),'exact candidate/manifest binding')
        c=X['census'];oldc=c['original'];newc=c['candidate']
        need(diff(oldc['native_paid'],newc['native_paid'])==DELTA_NATIVE and c['native_delta_p']==DELTA_NATIVE,'native paid delta')
        need(diff(oldc['native_targets'],newc['native_targets'])=={} and c['native_delta_t']=={},'native target delta')
        need(c['seventeen_delta_p']==DELTA_SIGNED,'seventeen-call delta')
        need(oldc['owned_rises']==newc['owned_rises'] and all(oldc[k]==newc[k] for k in ('owned_moves','lifetimes','peak')),'owned census')
        need(oldc['lifetimes']==167 and len(X['original']['clears'])==167 and len(X['candidate']['clears'])==167,'167 CLEAR records')
        need(oldc['events']==77194 and newc['events']==77188,'event counts')
        retained=root.parent/'kappa-research-20261115/repo/research/p104-contact134-329-on7611/retained/pr7605/retained'
        engine_path=retained/'pricing/evaluate_recursive_power.py';compare_path=retained/'pricing/compare_recursive_invoices.py';interval_path=retained/'role902/engines/interval_gate.py'
        for path,pin in ((engine_path,ENGINE_SHA),(compare_path,COMPARE_SHA),(interval_path,INTERVAL_SHA)):
            need(sha(path.read_bytes())==pin,'directed engine source pin: '+str(path))
        need('compare_recursive_invoices' not in sys.modules,'preloaded comparator could bypass pinned source')
        engine=runpy.run_path(str(engine_path));interval=runpy.run_path(str(interval_path))
        need(Path(sys.modules['compare_recursive_invoices'].__file__).resolve()==compare_path.resolve(),'loaded comparator path')
        source_invoice=read_json(old_invoice)
        need(set(source_invoice)=={'paid','targets'},'source invoice shape')
        normalized={'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'mixed-target-unnormalized-power-v1',
              'rank_semantics':'H_r costs r^(1-C); debit surrendered productive fields',
              'ambient_rank':145,'boundary':'complete signed #7113 caller application with 17 native calls'},
            'paid':source_invoice['paid'],'targets':source_invoice['targets']}
        normalized_path=out/'invoice-source-normalized.json';write(normalized_path,normalized)
        old,old_pin=engine['load_invoice'](normalized_path)
        new=json.loads(json.dumps(old))
        for r,d in DELTA_SIGNED.items():
            new['paid'][r]=new['paid'].get(r,0)+d
            need(new['paid'][r]>=0,'negative paid count')
            if not new['paid'][r]:del new['paid'][r]
        invoice_path=out/'invoice-new.json';write(invoice_path,new)
        new_loaded,new_pin=engine['load_invoice'](invoice_path);need(new_loaded==new,'invoice roundtrip')
        comp=engine['compare_invoices'](old,new)
        need(comp['delta_paid']==DELTA_SIGNED and comp['delta_targets']=={},'complete declared invoice delta')
        need(comp['classification']=='uniformly_better','concave order')
        need(sum(old['paid'].values())==110145 and sum(new['paid'].values())==110111,'paid calls')
        need(sum(new['targets'].values())==22461,'productive calls')
        mass=lambda h:sum(int(r)*v for r,v in h.items())
        need(mass(new['targets'])-mass(new['paid'])==1424,'rank surplus')
        zero=dict(new,paid={},targets={})
        def signed(inv):return {int(r):inv['targets'].get(r,0)-inv['paid'].get(r,0) for r in inv['targets'].keys()|inv['paid'].keys()}
        def sign(inv,k):
            lo,hi=interval['moment'](signed(inv),k);need(lo>0 or hi<0,'interval sign unresolved')
            return 1 if lo>0 else -1
        def bracket(inv):
            lo,hi=Q('0.00365'),Q('0.00367')
            need(sign(inv,lo)==1 and sign(inv,hi)==-1,'crossing outside fixed bracket')
            for _ in range(24):
                mid=(lo+hi)/2
                if sign(inv,mid)>0:lo=mid
                else:hi=mid
            return lo,hi
        def point(label,inv,k,positive):
            power=engine['evaluate'](zero,inv,1-k,bits=256)
            need(power['classification']==('new_cost_lower' if positive else 'new_cost_higher'),label+' dyadic sign')
            lo,hi=interval['moment'](signed(inv),k)
            need(lo>0 if positive else hi<0,label+' interval sign')
            return {'point':str(k),'integer_power':power,'independent_moment':[str(Q(x,interval['B'])) for x in (lo,hi)]}
        def derivative(inv):
            total=(0,0)
            for rank,count in signed(inv).items():
                endpoint=BIT_CAP if count>=0 else Q(0)
                term=interval['mul'](interval['power'](rank,endpoint),interval['log'](rank))
                total=interval['add'](total,interval['smul'](term,-count))
            upper=Q(total[1],interval['B']);need(upper<0,'moment monotonicity on BIT interval')
            return str(upper)
        old_lo,old_hi=bracket(old);new_lo,new_hi=bracket(new)
        floor12=(new_lo.numerator*10**12)//new_lo.denominator
        claim=Q(floor12-1,10**12);tested=claim+Q(7,10**15)
        need(old_upper<claim<tested<new_lo<new_hi<BIT_CAP,'crossing, old upper or fixed claim ordering')
        checks={'old_lower':point('old lower',old,old_lo,True),
                'old_upper':point('old upper',old,old_hi,False),
                'old_published_upper_rejects':point('old published upper',old,old_upper,False),
                'candidate_at_old_published_upper':point('candidate at published upper',new,old_upper,True),
                'old_rejects_claim':point('old rejects claim',old,claim,False),
                'candidate_claim':point('candidate claim',new,claim,True),
                'candidate_tested':point('candidate tested',new,tested,True),
                'candidate_lower':point('candidate lower',new,new_lo,True),
                'candidate_upper':point('candidate upper',new,new_hi,False)}
        old_d,new_d=derivative(old),derivative(new)
        outer=interval['gate']({'T':new['targets'],'P':new['paid']},str(claim),str(tested),str(new_lo),str(new_hi),str(BIT_CAP))
        need(outer['outer']['strict_count']==54 and outer['outer']['functional_count']==4,'58 outer predicates')
        report={'status':'PROVISIONAL_UNDER_COMMON_U','claim':str(claim),'tested':str(tested),'BIT_cap':str(BIT_CAP),
            'old_published_raw_upper':str(old_upper),'old_invoice':old_pin,'candidate_invoice':new_pin,
            'source_invoice_normalization':'Pinned source paid/targets wrapped in the retained signed 17-call declared-invoice contract; not fresh caller reconstruction.',
            'native_delta_paid':DELTA_NATIVE,'seventeen_delta_paid':DELTA_SIGNED,'delta_targets':{},'comparison':comp,'checks':checks,
            'old_fixed_invoice_ceiling':{'raw_bracket':[str(old_lo),str(old_hi)],'derivative_upper':old_d,'unique_crossing':True},
            'candidate_fixed_invoice_ceiling':{'raw_bracket':[str(new_lo),str(new_hi)],'derivative_upper':new_d,'unique_crossing':True,
                'headroom_over_claim_lower':str(new_lo-claim),'headroom_over_claim_upper':str(new_hi-claim)},
            'gain_over_published_old_upper':str(claim-old_upper),'outer_gate':outer,
            'bindings':{'original_word_canonical_sha256':SOURCE_CANON_SHA,'candidate_canonical_sha256':manifest['candidate_canonical_sha256'],
                'exact_gzip_sha256':sha(exact_bytes),'manifest_sha256':sha(manifest_bytes),
                'old_invoice_sha256':OLD_INVOICE_SHA,'config_sha256':CONFIG_SHA,'integer_power_sha256':ENGINE_SHA,'comparison_sha256':COMPARE_SHA,'interval_gate_sha256':INTERVAL_SHA},
            'scope':'Declared invoice only; 17-call delta assumes unchanged caller and common U. Fresh native/signed reconstruction, physical and service qualification remain open. Not same-premise dominance.'}
        write(out/'PRICE.json',report);return report
    except Exception as exc:
        write(out/'PRICE.json',{'status':'INCOMPLETE','error_type':type(exc).__name__,'error':str(exc)})
        raise

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--built',required=True);ap.add_argument('--exact',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args();report=certify(a.root,a.built,a.exact,a.out);print(json.dumps({'status':report['status'],'claim':report['claim'],'tested':report['tested']},sort_keys=True),flush=True)
