# SPDX-License-Identifier: Apache-2.0
"""Paired real Tape/Count/Machine protocol execution at reduced geometry.

Payload arrays and meters are test oracles. They never enter runtime control.
The binding is the retained complete tensor fixture, not production O73.
"""
from pathlib import Path
import sys, json
from types import SimpleNamespace
from hashlib import sha256
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE)); import runtime
runtime.cold()
A=runtime.module('protocol_adapter', HERE/'adapter.py')
R=runtime.module('protocol_resources', HERE/'resources.py')
from machine import Machine, transfer
from cardinal_counts import Count
from session import erase_marker, sealed_constructors
from records import Tape
from ordinary import Ordinary
from macro_code import Code
from fixture_binding import FixtureBinding
from root_layer import RootLayer
from selected_binding import Group
from words import BLANK, LEFT


def need(ok,msg):
    if not ok: raise ValueError(msg)


def native():
    return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),SimpleNamespace(families=0),
                    (Code((('unreachable',),),0),),capacity=64)


def raw(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
def encode(values,h):return bytes((x>>b)&1 for pair in values for x in pair for b in range(h))
def difference(a,b):return [x-y for x,y in zip(a,b)]


class Meter:
    """Literal primitive counters on a compiled, exhaustive fixed Tape inventory.

    Machine execution uses only its preallocated sealed pools. Allocation of a
    fresh Tape inside the measured interval is rejected, so a missed dynamic
    role cannot silently disappear from this total. Existing per-Tape meters
    count the source read/write/unit-step operations directly.
    """
    def __init__(self,tapes,codecs=()):
        self.tapes=tuple(dict.fromkeys(tapes));self.initial=None
        # BankParking's codec and two-tape interpreter are separate physical
        # counter banks. Shared primitive bundles must be counted exactly once.
        self.counter_banks=[];seen=set()
        for codec in codecs:
            for bank in (codec.codec_counts,codec.machine.counts):
                if id(bank) not in seen:
                    seen.add(id(bank));self.counter_banks.append(bank)
    def totals(self):
        return tuple(sum(getattr(t.meter,name) for t in self.tapes)+
                     sum(bank[name] for bank in self.counter_banks)
                     for name in ('reads','writes','moves'))
    def __enter__(self):
        self.initial=self.totals();self.original=Tape.__init__
        def forbidden(*args,**kwargs):raise ValueError('unmetered dynamic Tape allocation')
        Tape.__init__=forbidden
        return self
    def __exit__(self,*args):Tape.__init__=self.original
    def snapshot(self):return tuple(x-y for x,y in zip(self.totals(),self.initial))


def measured_codecs(parent):
    # Fixed controller identities only: no payload-dependent inventory discovery.
    own=parent.monomial.compact.binary.native.runtime.numerical
    child=getattr(parent,'native_child',None)
    return (own,) if child is None else (own,child.monomial.compact.binary.native.runtime.numerical)


def codec_meter_control():
    codec=native().runtime.numerical
    initial=(tuple(codec.machine.heads),tuple(dict(t) for t in codec.machine.tapes))
    with Meter((),codecs=(codec,codec)) as meter:
        codec._read(0);codec._write(0,'_')
        codec._move(0,1);codec._move(0,-1)
        codec._command('begin');codec._command('end')
        actions=meter.snapshot()
    need(actions==(7,3,4),'both actual numerical counter banks counted once')
    need(initial==(tuple(codec.machine.heads),tuple(dict(t) for t in codec.machine.tapes)),
         'actual matched codec control restores heads and symbols')
    return {'actions':list(actions),'codec_actions':[1,1,2],
            'interpreter_actions':[6,2,2],'duplicate_shared_codec_counted_once':True,
            'records_tapes':0,'matched_begin_end_restored':True}


def measured_roles(parent,source,descriptors):
    # resources.fixed_engine_tapes intentionally returns only controller roles;
    # include the complete original primitive bundle through the read-only
    # source graph walker retained below. No payload-dependent runtime use.
    seen=set();result=[]
    ignored={'binding','catalogue','codes','programs','program','recipe','recipes',
             'observe','retirement_tapes','primitive_bundle'}
    def walk(obj):
        if id(obj) in seen:return
        seen.add(id(obj))
        if isinstance(obj,Tape):result.append(obj);return
        if isinstance(obj,dict):
            for value in obj.values():walk(value)
        elif isinstance(obj,(tuple,list)):
            for value in obj:walk(value)
        elif hasattr(obj,'__dict__') and not isinstance(obj,type):
            for key,value in vars(obj).items():
                if key not in ignored:walk(value)
    walk(parent);walk(source);walk(descriptors)
    return tuple(result)


class BridgeBinding(FixtureBinding):
    """Reduced prefix/bridge/suffix fixture with the two exact source bridge legs.

    Original selected production control is separately authenticated/censused.
    This diagnostic control is not asserted to be a complete C decomposition.
    """
    families=4;slots=4
    events=('retained_prefix','both_bridge_legs','retained_later')
    def group_count(self,event):
        need(event in (0,1,2),'three reduced continuation events');return 1
    def group(self,event,subgroup,owner):
        need(subgroup==0,'one reduced continuation group')
        if event==1:
            return Group(((0,owner),(2,owner),(3,owner),(1,owner)),
                (('scalar',-1,0,1,('add',1,1)),('scalar',-1,2,3,('add',-1,1))),{})
        first=0 if event==0 else 2
        return Group(((first,owner),(first+1,owner)),
                     (('child',-1,0,1),('child',-1,1,1)),{})


def experiment(width=2, prefixes=1, front=0, back=0, coefficients=1, generations=2, binding_factory=FixtureBinding):
    """Same admitted row stock and complete external prepared packet for A/B/B*."""
    answers={}
    for variant in ('A','B','B_adopt'):
        binding=binding_factory()
        root=RootLayer(binding,native(),binding.catalogue)
        public=(root.current,root.output,root.plan)
        if variant=='A': parent=root.machine
        else: parent=A.install(root,native,adopt=variant=='B_adopt')
        need(public==(root.current,root.output,root.plan),'fixed actual RootLayer ports and plan')
        fixed_extra=parent.retirement_tapes if variant!='A' else ()
        root_output=parent.output
        # R=(families*cover)^depth makes all actual prepared children admissible.
        rows=(binding.families*binding.cover.size)**(width.bit_length()-1)
        descriptors={k:Count.literal(v) for k,v in dict(prefixes=prefixes,rows=rows,front=front,
            compact_bits=max(0,width//2-1),before=0,width=width,after=0,back=back,spacing=1,guard=1,residue=0,
            component_bits=24,coefficients=coefficients,root_width=width).items()}
        number=prefixes*rows*(1<<(front+width+back+3*max(0,width//2-1)))*coefficients
        values=[(256*((i*7)%19-9),256*((i*11)%23-11)) for i in range(number)]
        data=encode(values,24); source=Tape()
        for bit in data:source.append(bit)
        source.rewind();descriptor_images={k:raw(v.tape) for k,v in descriptors.items()}
        runs=[]
        for generation in range(generations):
            for tape in parent.private:
                # Closed owned dirty helper bodies must be erased by real group entry.
                for bit in (1,0,1,1):tape.append(bit)
                tape.rewind()
            pending=[];calls=[]
            original_prepare=parent.prepare_child
            original_return=parent.return_node
            original_enter=parent.enter_child
            with Meter(measured_roles(parent,source,descriptors),codecs=measured_codecs(parent)) as meter:
                def prepare(target,rank):
                    if parent.root:
                        start=meter.snapshot()
                        original_prepare(target,rank)
                        pending.append({'target':target,'rank':rank,'event':parent.event,
                            'subgroup':parent.subgroup,'owner':parent.cover_index,'pc':parent.pc,
                            'start':start,'prepared':meter.snapshot(),
                            'S':sum(len(raw(t)) for t in parent.parked),
                            'primitive_entry':R.primitive_history_fingerprint((parent.scalar,parent.leaf,parent.monomial)),
                            'missing_markers':sum(t.cells[0]!=LEFT for t in
                                (*(parent if variant=='A' else parent.native_child).parked,
                                 (parent if variant=='A' else parent.native_child).output)),
                            'C':sum(len(raw(t)) for t in parent.capsule.values()),
                            'r':len(parent.parked),'header':len(raw(parent.roles['header'])),
                            'capsule_hash':sha256(raw(parent.capsule['current'])).hexdigest(),
                            'protected_state':[(i,sha256(raw(t)).hexdigest(),t.head) for i,t in enumerate(parent.parked)
                                if t is not parent.packet(target) and t is not parent.roles['header']]})
                    else: original_prepare(target,rank)
                def returned():
                    result=original_return()
                    if parent.root and pending:
                        call=pending.pop();call['complete']=meter.snapshot()
                        call['return_hash']=sha256(raw(parent.packet(call['target']))).hexdigest()
                        call['primitive_return']=R.primitive_history_fingerprint((parent.scalar,parent.leaf,parent.monomial))
                        need(call['protected_state']==[(i,sha256(raw(t)).hexdigest(),t.head)
                            for i,t in enumerate(parent.parked) if t is not parent.packet(call['target'])
                            and t is not parent.roles['header']], 'live caller roles restored at next instruction')
                        calls.append(call)
                    return result
                def enter():
                    original_enter()
                    if variant!='A' and pending:
                        call=pending.pop();call['complete']=meter.snapshot()
                        call['return_hash']=sha256(raw(parent.packet(call['target']))).hexdigest()
                        call['primitive_return']=R.primitive_history_fingerprint((parent.scalar,parent.leaf,parent.monomial))
                        need(call['protected_state']==[(i,sha256(raw(t)).hexdigest(),t.head)
                            for i,t in enumerate(parent.parked) if t is not parent.packet(call['target'])
                            and t is not parent.roles['header']], 'live caller roles restored at next instruction')
                        calls.append(call)
                parent.prepare_child=prepare;parent.return_node=returned;parent.enter_child=enter
                try:
                    out=parent.run(source,descriptors)
                    total=meter.snapshot()
                finally:
                    parent.prepare_child=original_prepare;parent.return_node=original_return;parent.enter_child=original_enter
            need(out is root_output and parent.output is root_output,'fixed prepared/public Machine output')
            need(raw(source)==data and source.head==1 and all(raw(v.tape)==descriptor_images[k] and v.tape.head==1
                for k,v in descriptors.items()),'preserved borrowed payload descriptors and heads')
            need(parent.closed and not pending and parent.bank.state=='closed','complete parent closure')
            if variant!='A':
                need(parent.native_child.closed and raw(parent.native_child.output)==b'', 'dedicated child output consumed')
            runs.append({'actions':list(total),'sha256':sha256(raw(out)).hexdigest(),'calls':calls,
                         'generation':generation,'all_root_calls':len(calls)})
            out.clear()
        answers[variant]=runs
        source.clear()
        for v in descriptors.values():v.close()
        if fixed_extra:
            with Meter(fixed_extra) as terminal_meter:
                A.retire_installed(root)
            need(all(t.head==1 and all(b==BLANK for b in t.cells) for t in fixed_extra),
                 'complete added fixed Tape inventory finally erased at canonical heads')
            try:parent.run(None,{})
            except ValueError as exc:need('closed external caller' in str(exc),'retired controller reuse rejected')
            else:raise ValueError('retired controller reused')
            runs[-1]['terminal_added_inventory']={'tapes':len(fixed_extra),
                'tape_actions':list(terminal_meter.snapshot()),
                'shared_primitive_bundle_untouched':True}

    matched=[]
    for g in range(generations):
        aa,bb,cc=[answers[v][g] for v in ('A','B','B_adopt')]
        need(aa['sha256']==bb['sha256']==cc['sha256'],'identical actual complete C outputs')
        need(len(aa['calls'])==len(bb['calls'])==len(cc['calls']),'same source root occurrence count')
        details=[]
        for a,b,c in zip(aa['calls'],bb['calls'],cc['calls']):
            for key in ('target','rank','event','subgroup','owner','pc','S','C','r','header','capsule_hash','return_hash','primitive_entry','primitive_return'):
                need(a[key]==b[key]==c[key],'matched literal occurrence '+key)
            actual=difference(difference(b['complete'],b['prepared']),difference(a['complete'],a['prepared']))
            S,C,r=a['S'],a['C'],a['r'];k=15
            predicted=[2*C+3*k+3-18*S-10*r,-18*S-2*r-1,2*C+4*k+6-20*S-14*r]
            # Output marker is rearmed in the embedded return when its prior
            # transfer erased it; this finite context correction is recorded.
            residual=difference(actual,predicted)
            need(residual==[0,b['missing_markers']-a['missing_markers'],0],
                 'exact context-sensitive protocol action difference')
            saving=difference(difference(b['complete'],b['prepared']),difference(c['complete'],c['prepared']))
            n=len(data)//(prefixes*rows)*prefixes*(rows//(binding.families*binding.cover.size))
            need(saving==[5*n+2,2*n,4*n+2], 'exact guarded protected-return adoption saving')
            details.append({'event':a['event'],'owner':a['owner'],'pc':a['pc'],'target':a['target'],
                         'rank':a['rank'],'S':S,'C':C,'r':r,'header':a['header'],
                         'B_minus_A':actual,'protocol_prediction':predicted,'residual':residual,
                         'missing_marker_difference':b['missing_markers']-a['missing_markers'],
                         'copy_minus_adopt':saving,'packet_bits':n})
        need(difference(bb['actions'],aa['actions'])==
             [sum(row['B_minus_A'][j] for row in details)+(1 if j==0 else 0) for j in range(3)],
             'whole complete run equals occurrence sum plus charged entry check')
        need(difference(bb['actions'],cc['actions'])==
             [sum(row['copy_minus_adopt'][j] for row in details) for j in range(3)],
             'whole protected-return saving includes every call exactly once')
        matched.append({'generation':g,'output_sha256':aa['sha256'],
            'B_minus_A':difference(bb['actions'],aa['actions']),
            'B_minus_B_adopt':difference(bb['actions'],cc['actions']),
            'calls':details})
    return {'geometry':{'width':width,'prefixes':prefixes,'rows':rows,
              'front':front,'back':back,'coefficients':coefficients,'component_bits':24},
            'variants':answers,'matched':matched,'actual_source_endpoint':True,
            'scope':'Reduced complete tensor binding; no production O73 or complete RootLayer.run.'}


def nonleaf_cut():
    """Execute the real source prefix and first nested C child through return.

    Deliberately stops at the next parent instruction, preserving that cut for
    comparison, then invokes source exception cleanup. No completed root result
    is claimed by this reduced fixture.
    """
    class CutReached(Exception):pass
    results={}
    for variant in ('A','B','B_adopt'):
        binding=FixtureBinding();root=RootLayer(binding,native(),binding.catalogue)
        parent=root.machine if variant=='A' else A.install(root,native,adopt=variant=='B_adopt')
        descriptors={k:Count.literal(v) for k,v in dict(prefixes=1,rows=16,front=0,
            compact_bits=1,before=0,width=4,after=0,back=0,spacing=1,guard=1,residue=0,
            component_bits=8,coefficients=1,root_width=4).items()}
        data=encode([(4*((7*i)%5-2),4*((11*i)%7-3)) for i in range(2048)],8)
        source=Tape()
        for bit in data:source.append(bit)
        source.rewind();record={};nested=[0,0]
        old_prepare=parent.prepare_child;old_return=parent.return_node;old_enter=parent.enter_child
        backend=parent if variant=='A' else parent.native_child
        def observed(machine,event):
            if event=='enter':nested[0]+=1
            if event=='return':nested[1]+=1
        backend.observe=observed
        with Meter(measured_roles(parent,source,descriptors),codecs=measured_codecs(parent)) as meter:
            def prepare(target,rank):
                old_prepare(target,rank)
                if parent.root:
                    record.update(target=target,rank=rank,S=sum(len(raw(t)) for t in parent.parked),
                        C=sum(len(raw(t)) for t in parent.capsule.values()),r=len(parent.parked),
                        prepared=meter.snapshot(),primitive_entry=R.primitive_history_fingerprint((parent.scalar,parent.leaf,parent.monomial)),packet_bits=len(raw(parent.packet(target))),
                        missing=sum(t.cells[0]!=LEFT for t in (*backend.parked,backend.output)),
                        capsule=sha256(raw(parent.capsule['current'])).hexdigest(),
                        protected=[(i,sha256(raw(t)).hexdigest(),t.head) for i,t in enumerate(parent.parked)
                            if t is not parent.packet(target) and t is not parent.roles['header']])
            def finish():
                record['complete']=meter.snapshot();record['primitive_return']=R.primitive_history_fingerprint((parent.scalar,parent.leaf,parent.monomial));record['output']=sha256(raw(parent.packet(record['target']))).hexdigest()
                need(record['protected']==[(i,sha256(raw(t)).hexdigest(),t.head) for i,t in enumerate(parent.parked)
                    if t is not parent.packet(record['target']) and t is not parent.roles['header']],
                    'nonleaf return preserves all live nontarget caller roles and heads')
                need(parent.pc==5 and parent.group.code[parent.pc][0]=='scalar',
                     'nonleaf child returns to literal next source instruction')
                # Execute the actual next source instruction, not a callback-only endpoint.
                with sealed_constructors(), parent.scope.installed():parent.scalar_step(*parent.group.code[parent.pc][2:])
                parent.pc+=1
                record['next_instruction_output']=sha256(raw(parent.packet(1))).hexdigest()
                record['nested_events']=list(nested)
                raise CutReached()
            def returned():
                result=old_return()
                if parent.root and record:finish()
                return result
            def enter():
                old_enter()
                if variant!='A' and record:finish()
            parent.prepare_child=prepare;parent.return_node=returned;parent.enter_child=enter
            try:parent.run(source,descriptors)
            except CutReached:pass
            else:raise ValueError('nonleaf cut not reached')
        need(parent.closed and backend.closed and source.head==1 and raw(source)==data,
             'controlled cut closes original engines and preserves borrowed input')
        need(record['nested_events'][0]>0 and record['nested_events'][1]>0,
             'actual embedded descendants entered and returned')
        record['actions']=difference(record['complete'],record['prepared'])
        results[variant]=record
        source.clear()
        for value in descriptors.values():value.close()
    a,b,c=[results[v] for v in ('A','B','B_adopt')]
    for key in ('S','C','r','packet_bits','capsule','output','next_instruction_output','protected','primitive_entry','primitive_return'):
        need(a[key]==b[key]==c[key],'nonleaf same-boundary source match '+key)
    S,C,r=a['S'],a['C'],a['r'];eps=b['missing']-a['missing']
    expected=[2*C+48-18*S-10*r,-18*S-2*r-1+eps,2*C+66-20*S-14*r]
    need(difference(b['actions'],a['actions'])==expected,'nonleaf complete protocol formula')
    n=a['packet_bits']
    need(difference(b['actions'],c['actions'])==[5*n+2,2*n,4*n+2],
         'nonleaf guarded adoption formula')
    return {'variants':results,'B_minus_A':expected,'B_minus_B_adopt':[5*n+2,2*n,4*n+2],
        'scope':'Reduced reached first nonleaf child, actual nested returns and next scalar instruction; stopped before complete root.'}


def rejection_controls():
    rejected=[]
    for mutation in ('saved_pc','saved_target','saved_root','shared_bundle','active_child_lease','active_parent_reentry'):
        binding=FixtureBinding();root=RootLayer(binding,native(),binding.catalogue)
        parent=A.install(root,native,adopt=True)
        descriptors={k:Count.literal(v) for k,v in dict(prefixes=1,rows=4,front=0,
            compact_bits=0,before=0,width=2,after=0,back=0,spacing=1,guard=1,residue=0,
            component_bits=16,coefficients=1,root_width=2).items()}
        source=Tape();payload=encode([(32*(i-7),32*((3*i)%11-5)) for i in range(16)],16)
        for bit in payload:source.append(bit)
        source.rewind();original=parent.prepare_child
        def corrupted(target,rank):
            original(target,rank)
            if mutation=='shared_bundle':
                parent.primitive_bundle=(parent.scalar,parent.scalar,parent.monomial);return
            if mutation=='active_child_lease':
                parent.native_child.closed=False;return
            if mutation=='active_parent_reentry':
                parent.run(None,{});return
            fields=list(parent.header.read(parent.roles['header']))
            if mutation=='saved_pc':fields[4]+=1
            elif mutation=='saved_target':fields[5]=(fields[5]+1)%(binding.slots+binding.private)
            else:fields[0]^=1
            parent.roles['header'].clear();parent.header.write(parent.roles['header'],fields)
        parent.prepare_child=corrupted
        try:parent.run(source,descriptors)
        except ValueError as exc:
            expected={'saved_pc':'current source instruction','saved_root':'current source instruction',
                'saved_target':'target and rank','shared_bundle':'exact shared primitive bundle',
                'active_child_lease':'no simultaneous','active_parent_reentry':'closed external caller'}[mutation]
            need(expected in str(exc),
                 'specific continuation-header rejection')
            need(raw(source)==payload and source.head==1,'failed header preserves borrowed input')
            need(parent.closed and parent.native_child.closed,'controlled header failure closes engines')
            rejected.append(mutation)
        else:raise ValueError('accepted corrupted '+mutation)
        source.clear()
        for value in descriptors.values():value.close()
    binding=FixtureBinding();root=RootLayer(binding,native(),binding.catalogue)
    parent=A.install(root,native)
    parent.native_child.closed=False
    try:parent.run(None,{})
    except ValueError as exc:
        need('closed external caller' in str(exc),'premature backend reuse guard')
        rejected.append('premature_backend_reuse')
    else:raise ValueError('active dedicated backend accepted')
    finally:parent.native_child.closed=True
    guards=R.adoption_controls(A.machine_class(Machine,Count,transfer,erase_marker),Tape)
    history=R.primitive_history_control((parent.scalar,parent.leaf,parent.monomial))
    return {'actual_prepared_header_rejections':rejected,'adoption_guards':guards,
            'allocator_history_mutation':history,'two_tape_codec_meter':codec_meter_control()}


def run():
    return {'direct':experiment(), 'nonleaf':nonleaf_cut(),
            'same_output_zero_child_losing_case':experiment(width=1,generations=1),
            'spectators_and_coefficients':experiment(prefixes=2,front=1,coefficients=2,generations=1),
            'both_bridge_legs_and_later_calls':experiment(binding_factory=BridgeBinding,generations=1),
            'rejections':rejection_controls()}


if __name__=='__main__':
    try:print(json.dumps(run(),sort_keys=True))
    finally:runtime.cleanup()
