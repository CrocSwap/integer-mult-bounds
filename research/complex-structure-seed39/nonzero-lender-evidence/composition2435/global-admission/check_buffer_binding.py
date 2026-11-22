#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent inverse-lowering and namespace audit of emitted private work.

No import of the binding emitter or invoice. Reads the actual emitted JSON,
reconstructs each original native event exactly, verifies all call families,
and checks the inherited route descriptors against literal owner records.
"""
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
E=HERE.parent
OLD=E.parent.parent/'anticipatory-stage-evidence'
LIVE=66304
EXPECTED_NS={'centers':[66304,66312],'reserved_tableau':[66312,66740],
             'coefficient':[66740,66742],'private_zero_buffers':[66742,66818]}


def need(ok, reason):
    if not ok:raise ValueError(reason)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def namespace(binding):
    need(binding['live']==66304 and binding['physical']==66818,'physical inventory')
    need(binding['private_namespace']==EXPECTED_NS,'private namespace overlap or omission')
    need(binding['all_calls_serialized'] is True,'private work reused by concurrent calls')


def unlower(program, original, labels):
    slots={int(k):v for k,v in program['slots'].items()}
    need(set(slots)==set(labels) and sorted(slots.values())==list(range(66742,66818)),'complete injective private zero slots')
    inv={v:k for k,v in slots.items()}
    events=program['events'];rebuilt=[];active=set();clears=0;i=0
    def ref(x):
        kind,r=x
        if kind=='L':
            need(0<=r<652,'local source range')
            return x
        need(kind=='F','unlowered private label')
        if r in inv:
            need(r in active,'private use outside allocation')
            return ['Z',inv[r]]
        need(66304<=r<66312 and not active,'private reference outside C/Z arenas')
        return ['C',r-66304]
    while i<len(events):
        e=copy.deepcopy(events[i])
        if e[0]=='private_zero':
            need(e[1]=='alloc' and e[2] in inv and e[2] not in active,'bad private allocation')
            need(i+1<len(events) and events[i+1]==['scalar',['clear',['F',e[2]]],1],'missing allocation CLEAR')
            active.add(e[2]);rebuilt.append(['zero_buffer','alloc',inv[e[2]]]);i+=2;clears+=1;continue
        if e[0]=='scalar' and e[1][0]=='clear' and e[1][1][0]=='F' and e[1][1][1] in inv:
            f=e[1][1][1]
            need(f in active and e==['scalar',['clear',['F',f]],1],'bad release CLEAR')
            need(i+1<len(events) and events[i+1]==['private_zero','free',f],'missing private release')
            active.remove(f);rebuilt.append(['zero_buffer','free',inv[f]]);i+=2;clears+=1;continue
        if e[0]=='scalar':
            g=e[1];g[1]=ref(g[1])
            if g[0] in ('add','copy'):g[2]=ref(g[2])
        elif e[0]=='warp':e[1]=ref(e[1])
        elif e[0] in ('adapter','residual_adapter','climb'):
            need(not active and e[2][0]=='L','private work overlaps adapter or child')
            e[2]=e[2][1]
        elif e[0]=='center':
            need(not active and e[1][0]=='F' and 66304<=e[1][1]<66312,'center family')
            e[1]=e[1][1]-66304
        else:need(e[0]=='phase','unknown lowered event')
        rebuilt.append(e);i+=1
    need(not active and clears==152,'complete CLEAR lifecycle')
    need(rebuilt==original,'lowered native event changed')
    need(digest(events)==program['lowered_program_sha256'],'lowered program hash')
    need(digest(original)==program['native_program_sha256'],'native program hash')
    return dict(native_events=len(original),lowered_events=len(events),explicit_CLEARs=clears,
                physical_zero_fields=76,complete_inverse_lowering=True)


def call_check(call, selected, parent, roles):
    need((call['stage'],call['replica'],call['time'],call['provider'],call['orientation'])==
         (selected['stage'],selected['replica'],selected['time'],selected['provider'],selected['orientation']),'call dispatch binding')
    owners=call['owners'];families=[x[0] for x in owners]
    need(len(families)==len(set(families))==652 and all(0<=f<66304 for f in families),'call family alias or private collision')
    need(owners[:224]==parent['owners'][:224],'data owner route changed')
    for helper,row in roles.items():
        f,route=owners[224+helper]
        need(f==row['family'],'helper family differs from literal owner')
        if row['width']==9:need(route==[3,row['child'],row['offset']],'width9 helper route')
        else:
            need(route[:4]==[4,row['child'],row['offset'],row['width']],'residual helper route')
            need(len(route)==5 and len(route[4])==9-row['width'] and len(set(route[4]))==len(route[4]),'residual spectator inventory')


def main():
    path=HERE/'GLOBAL-BUFFER-BINDING.json.gz';binding=read(path);namespace(binding)
    plan=read(E/'budget/PLAN.json');parent=read(OLD/'parent/GLOBAL-TEMPLATE.json.gz')
    oldcalls={(c['stage'],c['replica']):c for c in parent['calls']}
    roles={}
    for row in read(E/'budget/RESTRICTED-OWNERS.json.gz'):
        roles.setdefault((row['stage'],row['replica']),{})[row['helper']]=row
    need(len(binding['calls'])==666,'complete global call count')
    for call,selected in zip(binding['calls'],sorted(plan['provider_calls'],key=lambda c:c['time'])):
        key=call['stage'],call['replica'];call_check(call,selected,oldcalls[key],roles[key])
        need(call['lowered_program_sha256']==binding['providers'][call['provider']][call['orientation']]['lowered_program_sha256'],'call program hash binding')
    programs={};originals={};words={}
    for pid,tag in [('gauge44','base'),('extra','extra')]:
        p=E/'native-evidence'/tag
        words[pid]=read(p/'CANONICAL-WORD.json.gz');originals[pid]=read(p/'LOCAL-PROGRAMS.json.gz')
        replay=read(p/'INDEPENDENT-LOCAL-REPLAY.json')
        need(replay['canonical_word_sha256']==sha(p/'CANONICAL-WORD.json.gz') and replay['local_programs_sha256']==sha(p/'LOCAL-PROGRAMS.json.gz'),'native replay file binding')
        programs[pid]={}
        for orientation,original in originals[pid].items():
            need(replay['local'][orientation]['all_exact_columns']==652 and replay['local'][orientation]['zero_buffers_returned_to_zero']==76 and replay['local'][orientation]['private_work_erased'],'native zero endpoint')
            programs[pid][orientation]=unlower(binding['providers'][pid][orientation],original,words[pid]['zero_buffers'])
    controls=[]
    def rejected(label,action,reason):
        try:action()
        except ValueError as exc:need(str(exc)==reason,'unexpected control rejection: '+str(exc))
        else:raise ValueError('accepted mutation '+label)
        controls.append(label)
    bad=dict(binding,private_namespace=dict(binding['private_namespace'],private_zero_buffers=[66741,66817]))
    rejected('arena overlaps coefficient',lambda:namespace(bad),'private namespace overlap or omission')
    bad=copy.deepcopy(binding['providers']['gauge44']['forward']);ks=list(bad['slots']);bad['slots'][ks[1]]=bad['slots'][ks[0]]
    rejected('two Z labels alias',lambda:unlower(bad,originals['gauge44']['forward'],words['gauge44']['zero_buffers']),'complete injective private zero slots')
    bad=copy.deepcopy(binding['providers']['gauge44']['forward']);idx=next(i for i,e in enumerate(bad['events']) if e[0]=='private_zero');del bad['events'][idx+1]
    rejected('allocation CLEAR omitted',lambda:unlower(bad,originals['gauge44']['forward'],words['gauge44']['zero_buffers']),'missing allocation CLEAR')
    bad=copy.deepcopy(binding['providers']['gauge44']['forward']);idx=next(i for i,e in enumerate(bad['events']) if e[0]=='scalar' and e[1][0]=='add' and any(r[0]=='F' and r[1]>=66742 for r in e[1][1:3]));del bad['events'][idx]
    rejected('private scalar omitted',lambda:unlower(bad,originals['gauge44']['forward'],words['gauge44']['zero_buffers']),'lowered native event changed')
    selected=sorted(plan['provider_calls'],key=lambda c:c['time'])[0];bad=copy.deepcopy(binding['calls'][0]);bad['owners'][224][0]=bad['owners'][0][0];key=bad['stage'],bad['replica']
    rejected('helper aliases active data',lambda:call_check(bad,selected,oldcalls[key],roles[key]),'call family alias or private collision')
    out=dict(status='PASS_INDEPENDENT_666_CALL_PRIVATE_BINDING_AND_EXACT_INVERSE_LOWERING',
             calls=666,live_streams_per_call=652,helpers_per_call=428,private_zero_fields=76,physical=66818,
             programs=programs,controls=controls,binding_sha256=sha(path),checker_sha256=sha(Path(__file__)),
             source_sha256=dict(owner_map=sha(E/'budget/RESTRICTED-OWNERS.json.gz'),plan=sha(E/'budget/PLAN.json')),
             scope='Exact inverse lowering of every native event including zero cleanup; all 666 complete family maps and dispatches; explicit CLEAR lifecycle. Native endpoint algebra is inherited from hash-bound652-column receipts. Full controllerroute chart/prefix audit and outer admission remain separate.')
    (HERE/'BUFFER-BINDING-CHECK.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])


if __name__=='__main__':main()
