#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Emit literal four-alias words with explicit A-phase compensation operations.

Uses the unchanged predecessor scalar builder for the original program. The
new prelude is explicit, and complete native transport checks both orientations.
"""
from collections import defaultdict
from fractions import Fraction as Q
import copy,gzip,importlib.util,json,sys
from pathlib import Path
import census as C
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('original_borrow_emitter',C.VENDOR/'vendor/pr2269/emit_word.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)

def emit(case):
    name=case['provider'];tag='base' if name=='gauge44' else 'extra';assert case['baseline']=='high48'
    w=C.read(C.VENDOR/'inputs'/f'{name}.canonical.json.gz');blocks=C.read(C.VENDOR/'inputs/blocks.json')['sources'][0]['blocks']
    full=C.read(C.VENDOR/'witness'/f'witness_80_{tag}.json')
    flags=next(x for x in C.read(HERE/'FLAG-FOUR.json')['cases'] if x['provider']==name and x['baseline']=='high48')
    inv=copy.deepcopy(case['witness']);original={p['register']:g for p,g in zip(full['pairs'],full['gaussian']['records'])}
    extra={r['register']:r for r in flags['records']}
    gauss=[]
    for op,p in enumerate(inv['pairs'],1):
        r=original.get(p['register'],extra.get(p['register']));assert r is not None
        gauss.append(dict(operator=op,G_columns=r['G_columns']))
    inv['gaussian']={'records':gauss}
    S=E.finish(E.build(w,blocks,inv));word=E.assemble(S,'seed39-four-lifted-'+name)
    del word['warp_order']
    # Preserve the original inverse history. The new source warp pairs below
    # are source-identity macros, with only target writes in between.
    v=S['v'];n=S['n'];restored=set(S['restored']);fullbasis=E.frame_basis(S['full'])
    bypos=defaultdict(list)
    for x in S['warps']:bypos[x[0]].append(x)
    forward=list(word['A'])
    for pos in range(len(word['B'])+1):
        for x in sorted(bypos[pos],key=lambda x:x[5]):forward.append(['warp',x[1],x[5]])
        if pos<len(word['B']):forward.append(word['B'][pos])
    forward+=word['restore'];recorded=[g for g in forward if g[0]=='warp' or not v<=g[1]<2*v]
    buf=lambda r:r+n if r in restored else r
    cleanup=[]
    for g in reversed(recorded):
        if g[0]=='warp':cleanup.append(['warp',buf(g[1]),-g[2],fullbasis])
        elif g[0]=='add':cleanup.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],fullbasis])
        else:cleanup.append(['scale',buf(g[1]),g[3],g[2],fullbasis])
    word['cleanup']=cleanup
    prelude=[]
    for t,f in inv['lifted_target_frames'].items():
        t=int(t);line=w['frames'][f]
        word['target_levels'][str(t-v)]=line
        prelude.append(['scale',t,1,1,line])
    groups=defaultdict(list)
    for term in inv['post_wrapper_corrections']:groups[(term['source'],term['operator'])].append(term)
    for (source,op),terms in sorted(groups.items()):
        old=w['frames'][w['start'][source]];line=w['frames'][inv['lifted_target_frames'][str(terms[0]['target'])]]
        prelude.append(['warp',source,op,old,line])
        for term in terms:
            q=Q(term['coefficient']);prelude.append(['add',term['target'],source,q.numerator,q.denominator,line])
        prelude.append(['warp',source,-op,line,old])
    word['A']=prelude+word['A'];word['report']['local_profile']=case['local_profile'];word['report']['width_inventory']=case['width_inventory']
    word['seed39']={'kind':'explicit_lifted_target_prelude','prelude_events':len(prelude),'source_flag_records':'FLAG-FOUR.json','native_and_global_admission':'separate obligations'}
    out=HERE/'words';out.mkdir(exist_ok=True)
    path=out/f'FOUR-{tag}.json.gz';payload=json.dumps(word,sort_keys=True,separators=(',',':')).encode();path.write_bytes(gzip.compress(payload,mtime=0))
    print(path, 'helpers',w['R']-len(word['removed']),'prelude',len(prelude),flush=True)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    C.check_sources()
    for case in C.read(HERE/'FOUR-CANDIDATE.json')['cases']:
        if case['baseline']=='high48':emit(case)
