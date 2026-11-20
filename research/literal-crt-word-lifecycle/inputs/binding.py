"""Current-source binding for the combined literal arithmetic entries.

Finite owner metadata, flags and grants are explicitly retained and billed.
Observers, transcripts and counters are optional verifier instrumentation.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
from contextlib import contextmanager

def make_binding(old, all_divisions):
    Parent=all_divisions.make_binding(old)
    class Binding(Parent):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.simple_calls=[];self.simple_kind=None
        def reserve_simple(self,arena,a,b,output):
            self.finite_control_invoice+=16384
            old.need(arena.capacity==64 and len(arena.words)==64,'current64-role inventory')
            old.need(len(set(arena.available))==len(arena.available) and
                     set(arena.available).isdisjoint(arena.live) and
                     set(arena.available)|arena.live==set(range(64)),'complete live/free partition')
            old.need(set(range(8))<=arena.live,'eight protected physical guards')
            for slot in range(64):
                word=arena.words[slot]
                old.need(word.slot==slot and word.arena is arena,'exact slot and arena binding')
            for word in (a,b):
                old.need(word.arena is arena and word.slot in arena.live and
                         word is arena.words[word.slot],'bound live input')
            if not output:return None
            old.need(arena.available,'one fresh output owner')
            slot=arena.available.pop();arena.live.add(slot);arena.meter.allocations+=1
            arena.meter.peak_live=max(arena.meter.peak_live,len(arena.live))
            return arena.words[slot]
        def simple(self,raw,a,b,kind):
            arena=raw.arena;self.simple_kind=kind
            if self.observer:self.observer('arithmetic_before',self,arena,a,b,None)
            out=self.reserve_simple(arena,a,b,kind!='COMPARE')
            ports=tuple(self.hardware.NumericPort(word) for word in arena.words)+self.selectors
            if not self.acquired:
                old.need(self.program.run(ports,'ACQUIRE')['status']=='READY','literal acquisition')
                self.acquired=True
            slots=(a.slot,b.slot,a.slot,b.slot) if out is None else (a.slot,b.slot,out.slot,out.slot)
            self.hardware.setters(self.program,ports,slots)
            result=self.program.run(ports,kind)
            tags={'COMPARE':{'CMP_NEG':-1,'CMP_EQ':0,'CMP_POS':1},
                  'ADD':{'ADD_C0':0,'ADD_C1':1},'SUBTRACT':{'SUB_B0':0,'SUB_B1':1}}[kind]
            old.need(result['status'] in tags,'admitted current arithmetic accepts')
            flag=tags[result['status']];self.finite_control_invoice+=8
            self.simple_calls.append({'kind':kind,'slots':list(slots),'status':result['status'],
                                      'instructions':result['instructions'],'numeric_actions':result['numeric_actions'],
                                      'selector_actions':result['selector_actions']})
            answer=flag if out is None else (out,flag)
            if self.observer:self.observer('arithmetic_after',self,arena,a,b,answer)
            self.simple_kind=None
            return answer
        @contextmanager
        def install(self,m):
            names=('compare','add','subtract');original={name:getattr(m.w.Unsigned,name) for name in names}
            owner=self
            def wrap(kind):
                def primitive(raw,a,b):
                    owner.finite_control_invoice+=16
                    old.need(owner.active and raw.arena is owner.active_arena,
                             'raw arithmetic must belong to the active exact current producer')
                    return owner.simple(raw,a,b,kind)
                return primitive
            with super().install(m):
                for name,kind in zip(names,('COMPARE','ADD','SUBTRACT')):setattr(m.w.Unsigned,name,wrap(kind))
                try:yield self
                finally:
                    for name in names:setattr(m.w.Unsigned,name,original[name])
    return Binding
