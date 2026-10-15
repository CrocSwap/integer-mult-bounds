# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Concrete physical dispatch and independent inverse-lowering admission.

Inherited native programs remain immutable. The actual execution entry point
resolves L operands through each audited literal owner map. The validator
reconstructs every native event from physical lowering and its CLEAR lifecycle.
"""
import copy,gzip,hashlib,json
LIVE=66304
EXPECTED_NS={'centers':[66304,66312],'reserved_tableau':[66312,66740],
 'coefficient':[66740,66742],'private_zero_buffers':[66742,66818]}
DISPATCH='Execute buffer_runtime.iter_call_events(template, call) for each indivisible local_cover_sweep. The concrete lowered program resolves every L operand through the literal call owners, retains provider residual adapters and Clifford recipes, and explicitly clears all 76 private zero fields on allocation and release.'
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


def validate(template):
    binding=template['buffer_binding'];namespace(binding)
    need(template['private_namespace']==binding['private_namespace'] and template['live']==binding['live'] and template['physical']==binding['physical'],'global physical binding')
    need(template['provider_dispatch']==DISPATCH,'concrete lower dispatch missing')
    need(binding['source_sha256']['owners']==template['hosting']['owner_map_sha256'],'owner source binding')
    need(binding['source_sha256']['data_phases']==template['exact_data_phase_recipe_sha256'],'phase source binding')
    registry=template['local_providers']
    need(set(binding['providers'])==set(registry),'provider binding inventory')
    results={}
    for pid,reg in registry.items():
        pins=binding['source_sha256']['native'][pid]
        need(pins['CANONICAL-WORD.json.gz']==reg['canonical_word_sha256'] and pins['LOCAL-PROGRAMS.json.gz']==reg['local_programs_sha256'],'native file binding')
        need(set(binding['providers'][pid])==set(reg['local_programs'])=={'forward','backward'},'orientation inventory')
        results[pid]={}
        for orientation,original in reg['local_programs'].items():
            labels=[e[2] for e in original if e[0]=='zero_buffer' and e[1]=='alloc']
            need(len(labels)==len(set(labels))==76,'native zero allocation inventory')
            program=binding['providers'][pid][orientation]
            need(program['explicit_clear_macros']==152 and program['explicit_clear_real_components']==304 and program['native_columns']==652 and program['native_private_work_erased'],'lowered charge inventory')
            results[pid][orientation]=unlower(program,original,labels)
    need(len(binding['calls'])==len(template['calls'])==666,'complete dispatch count')
    for time,(actual,call) in enumerate(zip(binding['calls'],template['calls'])):
        wanted={k:call[k] for k in ('time','stage','replica','orientation','owners')}
        wanted['provider']=call['provider_id']
        wanted['lowered_program_sha256']=binding['providers'][call['provider_id']][call['orientation']]['lowered_program_sha256']
        need(actual==wanted and call['time']==time,'literal call lowering mismatch')
        families=[x[0] for x in actual['owners']]
        need(len(families)==len(set(families))==652 and all(0<=f<66304 for f in families),'call family namespace')
    return dict(calls=666,physical=66818,private_zero_fields=76,programs=results)


def iter_call_events(template,call):
    """Yield actual physical F operands; caller follows inherited route charts."""
    binding=template['buffer_binding']
    selected=binding['calls'][call['time']]
    need(selected['owners']==call['owners'] and selected['provider']==call['provider_id'] and selected['orientation']==call['orientation'],'dispatch call binding')
    for event in binding['providers'][selected['provider']][selected['orientation']]['events']:
        e=copy.deepcopy(event);tag=e[0]
        refs=([e[1][1]]+([e[1][2]] if e[1][0] in ('add','copy') else [])) if tag=='scalar' else ([e[1]] if tag in ('warp','center') else ([e[2]] if tag in ('adapter','residual_adapter','climb') else []))
        for ref in refs:
            if ref[0]=='L':ref[:]=['F',selected['owners'][ref[1]][0]]
            need(ref[0]=='F' and 0<=ref[1]<66818,'unbound physical operand')
        yield e


def mutation_controls(template):
    controls=[]
    def reject(label,mut):
        bad=copy.deepcopy(template);mut(bad)
        try:validate(bad)
        except (ValueError,KeyError,IndexError,TypeError):controls.append(label)
        else:raise ValueError('accepted buffer mutation '+label)
    def program(t):return t['buffer_binding']['providers']['gauge44']['forward']
    def omit_clear(t):
        events=program(t)['events'];idx=next(i for i,e in enumerate(events) if e[0]=='private_zero');del events[idx+1]
    def omit_release(t):
        events=program(t)['events'];idx=next(i for i,e in enumerate(events) if e[0]=='private_zero' and e[1]=='free');del events[idx-1]
    def alias(t):
        slots=program(t)['slots'];ks=list(slots);slots[ks[1]]=slots[ks[0]]
    reject('omit allocation CLEAR',omit_clear)
    reject('omit release CLEAR',omit_release)
    reject('alias private zero fields',alias)
    reject('wrong lower dispatch',lambda t:t.__setitem__('provider_dispatch','native-only'))
    reject('unbound lowered call family',lambda t:t['buffer_binding']['calls'][0]['owners'][0].__setitem__(0,66304))
    reject('stale lowered program digest',lambda t:program(t).__setitem__('lowered_program_sha256','0'*64))
    return controls
