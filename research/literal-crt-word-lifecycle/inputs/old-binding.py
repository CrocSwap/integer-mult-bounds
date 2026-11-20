"""Retained finite-source binder for one actual current-leaf divmod call.

No encoded value or width is decoded. Fixed64-slot control remains external
and separately charged. Every replacement numerical R/W/M runs literally.
"""
from contextlib import contextmanager
def need(x,s):
    if not x:raise ValueError(s)

class Binding:
    def __init__(self,program,hardware,observer=None):
        self.program,self.hardware,self.observer=program,hardware,observer
        self.iterator=self.selectors=None;self.phase=6;self.active=False
        self.replacements=self.invocations=self.boundary_actions=self.raw_calls=0
        self.finite_control_invoice=self.granted_extra_cells=0
        self.acquired=False;self.calls=[]
    def attach(self,iterator,private):
        """Explicit external grant8 on four newly acquired marker owners.

        The extension is a charged allocation service, not a graph opcode or
        free capacity inferred from Tape.step. ACQUIRE then clears all8 cells.
        """
        need(self.iterator is None and len(private)==4,'one four-owner acquisition')
        need(len({id(t.cells) for t in private})==4,'four distinct physical owners')
        granted=[]
        for tape in private:
            need(tape.head==0 and tape.cells==['_'],'exact fresh caller marker owner')
            tape.cells.extend(['_']*7)
            self.granted_extra_cells+=7
            granted.append(self.hardware.GrantedSelector(tape,granted_extent=8))
        self.iterator,self.selectors=iterator,tuple(granted)
        self.finite_control_invoice+=256
    def eligible(self):
        t=self.iterator.counters['half'];w=self.iterator.w
        need(t.read()==w.ONE,'actual nonempty current half');t.step(1)
        result=t.read()==w.RIGHT;t.rewind();self.boundary_actions+=8
        return result
    def reserve(self,arena,n,d):
        # This invoice includes a conservative bounded64-slot implementation
        # of all metadata predicates/reservations and the four setter choices.
        self.finite_control_invoice+=16384
        need(arena.capacity==64 and len(arena.words)==64,'current numerical inventory')
        need(len(arena.available)>=2 and len(set(arena.available))==len(arena.available),'two free owners')
        need(set(arena.available).isdisjoint(arena.live) and set(arena.available)|arena.live==set(range(64)),
             'complete live/free partition')
        need(set(range(8))<=arena.live,'protected borrowed owners remain live')
        for slot in range(64):
            word=arena.words[slot]
            need(word.slot==slot and word.arena is arena,'fixed slot and arena identity')
        need(n is not d and n.arena is arena and d.arena is arena and
             n.slot in arena.live and d.slot in arena.live and
             n is arena.words[n.slot] and d is arena.words[d.slot],'incoming bound live operands')
        out=[]
        for _ in range(2):
            slot=arena.available.pop();need(slot not in arena.live,'reserved owner free')
            arena.live.add(slot);arena.meter.allocations+=1
            arena.meter.peak_live=max(arena.meter.peak_live,len(arena.live));out.append(arena.words[slot])
        return tuple(out)
    def divide(self,raw,n,d):
        arena=raw.arena
        if self.observer:self.observer('before',self,arena,n,d,None)
        q,r=self.reserve(arena,n,d)
        ports=tuple(self.hardware.NumericPort(word) for word in arena.words)+self.selectors
        if not self.acquired:
            need(self.program.run(ports,'ACQUIRE')['status']=='READY','literal acquisition')
            self.acquired=True
        slots=(n.slot,d.slot,q.slot,r.slot)
        self.hardware.setters(self.program,ports,slots)
        result=self.program.run(ports,'DIVIDE')
        need(result['status']=='DONE','admitted current arithmetic accepts')
        self.calls.append({'slots':list(slots),'instructions':result['instructions'],
                           'numeric_actions':result['numeric_actions'],'selector_actions':result['selector_actions']})
        self.replacements+=1
        if self.observer:self.observer('after',self,arena,n,d,(q,r))
        return q,r
    @contextmanager
    def install(self,m):
        need(self.iterator is not None,'current iterator and descriptor grants')
        old_raw=m.w.Unsigned.divmod
        producers=(m.numeric,m.subtractive);old_produce=tuple(module.produce for module in producers)
        owner=self
        def raw(obj,n,d):
            owner.raw_calls+=1;owner.finite_control_invoice+=16
            if owner.active and owner.phase<6:
                owner.phase+=1
                if owner.phase==6:return owner.divide(obj,n,d)
            return old_raw(obj,n,d)
        def wrap(original):
            def produce(*args,**kwargs):
                need(not owner.active,'one sequential current producer')
                owner.finite_control_invoice+=32
                owner.invocations+=1;owner.active=owner.eligible();owner.phase=0 if owner.active else 6
                try:return original(*args,**kwargs)
                finally:owner.active=False;owner.phase=6
            return produce
        m.w.Unsigned.divmod=raw
        for module,original in zip(producers,old_produce):module.produce=wrap(original)
        try:yield self
        finally:
            m.w.Unsigned.divmod=old_raw
            for module,original in zip(producers,old_produce):module.produce=original

def join(previous_join,previous_caller,binding,caller_raw):
    function='def run_leg('+caller_raw.decode().split('def run_leg(',1)[1]
    for old,new in((previous_join.OLD_BUILD,previous_join.NEW_BUILD),(previous_join.OLD_RETIRE,previous_join.NEW_RETIRE)):
        need(function.count(old)==1,'authenticated B9 seam');function=function.replace(old,new)
    old='    private = tuple(m.join.Tape() for _ in range(14))\n'
    new=old+'    _divider_binding.attach(iterator, private[:4])\n'
    need(function.count(old)==1,'one marker acquisition seam');function=function.replace(old,new)
    old='    with base.seal_numerical_roles(m):\n'
    new='    with _divider_binding.install(m), base.seal_numerical_roles(m):\n'
    need(function.count(old)==1,'one numerical scope');function=function.replace(old,new)
    previous_caller._divider_binding=binding
    exec(compile(function,'<B9 caller plus two declared binding seams>','exec'),previous_caller.__dict__)
    return previous_caller,function
