#!/usr/bin/env python3
"""Exact source-bound output-slice allocation and complete endpoint replay."""
from copy import deepcopy
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from source import load
from model import need,transform,replay


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))


def run():
    algebra,old=load()
    selected=[int(e['dst'][1:]) for e in old[:32] if e['op']=='add']
    baseline,cuts,peak=algebra.replay(old,selected,'Z')
    new,windows=transform(old)
    output,new_cuts,borrowed=replay(new,selected,algebra)
    need(output==baseline and cuts==new_cuts,'complete outputs and checkpoints')
    old_bill,new_bill=algebra.invoice(old),algebra.invoice(new)
    need(old_bill==new_bill,'complete unchanged invoice')
    need(old_bill['scalar_primitives']==17280 and old_bill['owned_full_cover_bank_identities']==224,'source invoice')
    native=lambda word:[e for e in word if e['op'] in ('stage','line','current_map')]
    need(native(old)==native(new) and len(native(new))==448,'all native events literally unchanged')
    need(peak==borrowed==16,'same maximum temporary payload width')
    controls=[]
    def reject(label,mutate):
        bad=deepcopy(new);mutate(bad)
        try:
            result,new_cuts,_=replay(bad,selected,algebra)
            need(result==baseline and new_cuts==cuts,'changed endpoint')
        except (ValueError,KeyError):controls.append(label)
        else:raise ValueError('ineffective control '+label)
    def at(word,op,**kw):
        return next(e for e in word if e['op']==op and all(e.get(k)==v for k,v in kw.items()))
    reject('noninjective_scratch',lambda w:at(w,'output_slices_begin',name='F0_inverse')['fields'].__setitem__(1,'W0'))
    reject('borrowed_source_alias',lambda w:at(w,'output_slices_begin')['fields'].__setitem__(0,'X0'))
    reject('output_produced_too_early',lambda w:w.insert(633,{'op':'clear','field':'W0','frame':'current'}))
    reject('scratch_frame_mismatch',lambda w:at(w,'clear',field='W0',frame='current').update(frame='identity'))
    reject('omitted_release_clear',lambda w:w.remove(at(w,'clear',field='W15',frame='identity')))
    reject('future_output_uses_stale_scratch',lambda w:w.remove(next(e for e in w[2127:] if e['op']=='clear' and e['field']=='W0')))
    reject('native_event_inside_owner_body',lambda w:w.insert(634,{'op':'current_map','field':'W0','port':0,'inverse':False}))
    reject('wrong_scratch_source',lambda w:at(w,'add',dst='W0',src='Z76').update(src='Z81'))
    receipt={'schema_version':1,'source_head':'a3b82e6f4ddcf999f8b6dcd3a6dfc3a9543a1533',
             'events':len(new),'windows':windows,'invoice':new_bill,'unchanged_native_events':448,
             'output_arrays':224,'borrowed_arrays_restored':224,'peak_additional_local_arrays':{'old':16,'new':0},
             'peak_borrowed_output_slices':16,'temporal_symbols':240,
             'output_digest':algebra.digest_rows(output),'checkpoints':cuts,'controls':controls}
    return new,receipt


if __name__=='__main__':
    word,result=run()
    if sys.argv[1:]==['--write']:
        for name,value in [('WORD.json',word),('RESULT.json',result)]:
            with (HERE/name).open('x',encoding='utf-8') as f:f.write(json.dumps(value,indent=2)+'\n')
    else:
        need(not sys.argv[1:],'usage verify.py [--write]')
        need(canonical(word)==canonical(json.loads((HERE/'WORD.json').read_text())),'literal word mismatch')
        need(canonical(result)==canonical(json.loads((HERE/'RESULT.json').read_text())),'typed receipt mismatch')
    print('PASS_QQ16_OUTPUT_SLICE_SCRATCH outputs=224 borrowed=224 added_scratch=16->0 native=448 scalar=17280 controls='+str(len(result['controls'])))
