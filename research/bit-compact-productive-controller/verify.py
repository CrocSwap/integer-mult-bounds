#!/usr/bin/env python3
"""Rebuild a mixed-helper BIT controller and its charged ordinary supplier.

Apache-2.0. Prepared for ai-nanachi with substantial OpenAI Codex assistance.
Predecessor source code, word, frame, compiler and arithmetic are credited in
README.md and byte-pinned in SOURCES.json. No selected kappa is changed here.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
from contextlib import redirect_stdout
import argparse,copy,gzip,hashlib,io,json,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import local_word as L
import independent_native as I
import price
import global_word as G
import audit_stream as A

def need(c,m):
    if not c:raise ValueError(m)

def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_bytes())
    count=0
    for row in manifest['files']:
        if row['usage']!='input':continue
        p=ROOT/row['path'];raw=p.read_bytes()
        need(not p.is_symlink(),'No source alias')
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'Changed input '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
             'Changed Git blob '+row['path'])
        count+=1
    return count

def bit_main_controller():
    V,_=price.source_engines();C=V.C
    B,_=C.engines();p,a=16,7
    row=json.loads((price.THIN/'BIT-CONTROLLER.json').read_bytes())
    coeff,events,idles=B.physical_controller(p,C.keep_mask(p,a))
    coeff=C.specialize_bit(coeff,C.thick_stages(p))
    factor=B.simultaneous_monomial_factor(coeff)
    need(factor==row['boundaries'],'All main physical coefficients and actual binary boundaries')
    need(C.replay_events(row['physical_events'],p,'bit')==coeff,'Literal emitted native/query/idle events')
    need(price.encode(C.inventories('bit',p,a,factor['diagonal_monomials'],idles))==row['invoice'],
         'Literal source invoice, all main, idle, helper, and copied-query jobs')
    need(B.LOCAL==price.OLD_LOCAL,'Baseline local recursive calls')
    need(row['invoice']['thick_calls']==18,'Separate eighteen local invocations')
    # This is reuse of the existing phase, rational port and owned-query backend.
    # Its native algorithm is unchanged; the new local word gets its own audit.
    contact=V.native_contacts()
    return {'main_columns':32*111,'pairs':p,'prefix':a,'calls':18,'thin_queries':1665,
            'native_backend':contact,'main_source_abi_unchanged':True}

def mutations(word,frames,reference):
    controls={}
    def reject(name,w):
        try:I.verify(w,frames,reference)
        except (ValueError,KeyError,IndexError):controls[name]='REJECT';return
        raise ValueError('Unrejected actual native corruption: '+name)
    w=copy.deepcopy(word);w['start'][462]=1;reject('warm_partial_helper',w)
    w=copy.deepcopy(word);w['final'][462]=1;reject('unpaid_rank8_helper_credit',w)
    w=copy.deepcopy(word);w['start'][0]=0;reject('changed_SOURCE_version',w)
    w=copy.deepcopy(word);del w['records'][next(i for i,e in enumerate(w['records'])if e[0]==0)]
    reject('missing_paid_QUERY',w)
    w=copy.deepcopy(word);w['records'][next(i for i,e in enumerate(w['records'])if e[0]==1)][3]=0
    reject('changed_actual_ADD',w)
    w=copy.deepcopy(word);del w['records'][next(i for i,e in enumerate(w['records'])if e[0]==3)]
    reject('unreturned_owned_copy',w)
    return controls

def run():
    inputs=authenticate()
    with tempfile.TemporaryDirectory(prefix='compact-productive-')as temporary:
        out=Path(temporary)
        # Requalify the existing local word with its actual partial endpoints.
        with redirect_stdout(io.StringIO()):local=L.build(ROOT,out,True)
        word=json.loads(gzip.decompress((out/'WORD.json.gz').read_bytes()))
        payload=json.dumps(word,sort_keys=True,separators=(',',':')).encode()
        need(hashlib.sha256(payload).hexdigest()=='6f8516694bd0067897e91311fb16a749eea8fdd2eb3761bfa3f8eb2740d5c6a6',
             'Canonical regenerated local payload (not gzip container)')
        frames=json.loads((ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json').read_bytes())['frames']
        reference=json.loads(gzip.decompress((ROOT/'research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz').read_bytes()))
        forward=I.verify(word,frames,reference)
        reverse=I.verify(word,frames,reference,True)
        matchers=I.helper_matchers(word,frames)
        controls=mutations(word,frames,reference)
        global_dir=out/'global'
        global_result=G.build(ROOT,out,global_dir)
        stream=A.audit(ROOT,out,global_dir)
        stream_controls={}
        for name in ('duplicate_owner','full8_credit','omit_clear','wrong_nested_frame','source_write_in_lease'):
            try:A.audit(ROOT,out,global_dir,name)
            except ValueError:stream_controls[name]='REJECT'
            else:raise ValueError('Unrejected expanded-stream corruption '+name)
    main=bit_main_controller()
    local_paid={int(k):v for k,v in local['forward']['paid_profile'].items()}
    helpers={int(k):v for k,v in local['productive_helper_ranks'].items()}
    inv=price.invoice(local_paid,helpers)
    need(global_result['paid']==inv['paid']and global_result['targets']==inv['targets'],
         'Actual emitted global operator binds the complete price')
    certificate=price.certify(inv)
    # Whole-job matching is a proved identity at every positive multiplicity:
    # S diag(I4,0) S^-1=P; the generic complete-GL cover pays the routes.
    # It is not treated as a free same-ARRAY permutation or rank-only dispatch.
    majorant_bits=max(local[k]['cancellation_free_majorant_bits']for k in ('forward','reverse'))
    need(majorant_bits<=30,'New scalar majorant, not the predecessor21-bit bound')
    return price.encode({'schema':'compact-partial-productive-BIT/1','status':'PASS_CONDITIONAL_ORDINARY_BIT_0034597',
      'source_inputs_authenticated':inputs,'local':{'forward':forward,'inverse':reverse,
        'exact_signed_inverse_both_orders':local['signed_inverse_both_orders'],
        'helper_matchers':matchers,'canonical_payload_sha256':hashlib.sha256(payload).hexdigest(),
        'scalar_majorant_bits':majorant_bits,'old_scalar_threshold_reused':False},
      'main':main,'invoice':inv,'ordinary_BIT':certificate,
      'expanded':{k:global_result[k]for k in ('raw_scalar_columns','private_peak','private_episodes',
         'nonidentity_mainport_routes','additional_partial_outputmatcher_routes','event_counts',
         'expanded_event_count','expanded_event_sha256','cancellation_free_majorant_bits','raw_scalar_record_bound')},
      'separate_stream_interpreter':stream,'expanded_negative_controls':stream_controls,
      'negative_controls':controls,'new_complex_or_global_kappa':None,
      'scope':'Finite all-column native schematic and conditional ordinary BIT supplier. Paid tensor completion/splitting, delayed-cover/fallback and stock are retained. New fixed constants must be generated from this word; no massive uniform word or global multiplication theorem is materialized.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=run();target=HERE/'RESULT.json'
    if args.write:target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    else:need(result==json.loads(target.read_bytes()),'Deterministic complete receipt')
    print(json.dumps({'status':result['status'],'admitted_BIT':result['ordinary_BIT']['admitted'],
                      'original_fields':result['invoice']['original_fields'],
                      'native_controls':len(result['negative_controls'])}))
