"""Source-level setup transaction for the retained PR2697 Consumer.

No physical allocator is claimed. Original runtime and notices remain unchanged.
JoyboyBrian with substantial OpenAI assistance. Apache-2.0.
"""
import weakref

_ACTIVE=False

class ContractViolation(RuntimeError):
    pass


def require(ok,message):
    if not ok:raise ContractViolation(message)


def home(tape,left):
    if tape.read()==left:tape.step(1)
    else:tape.rewind()


class SetupTransaction:
    def __init__(self,m,consumer,args):
        self.m,self.consumer=m,consumer
        self.arenas=(consumer.context.arena,consumer.indices)
        require(self.arenas[0] is not self.arenas[1],'distinct numerical arenas')
        self.protected=tuple(frozenset(a.live) for a in self.arenas)
        self.free_order=tuple(tuple(a.available) for a in self.arenas)
        self.allocated=tuple(len(a.words) for a in self.arenas)
        # Positional Consumer.apply ABI; optional observer is separately rejected.
        source,_,_,_,old,old_count,before,gap,suffix=args
        candidates=(source,old,consumer.program.tape,old_count.tape,before.tape,gap.tape,suffix.tape,
                    consumer.context.highs.tape)
        self.borrowed=tuple({id(t):t for t in candidates}.values())
        require(all(t.head==1 for t in self.borrowed),'canonical borrowed Tape heads')
        require(all(a.template.head==1 and all(a.words[k].head==1 for k in saved)
                    for a,saved in zip(self.arenas,self.protected)),'canonical borrowed Word heads')
        self.tapes=weakref.WeakValueDictionary();self.committed=False;self.max_tapes=0
        self.report={'state':'preparing','new_tapes_peak':0,'cleanup_ops':0,'cleanup_bound':0}

    def register(self,tape):
        self.tapes[id(tape)]=tape
        self.max_tapes=max(self.max_tapes,len(self.tapes))
        require(len(self.tapes)<=216,'bounded live setup Tape registry')

    def commit(self):
        self.committed=True
        self.report={'state':'handed_off','new_tapes_peak':self.max_tapes,'cleanup_ops':0,'cleanup_bound':0}
        self.tapes.clear()
        self.uninstall()

    def uninstall(self):
        if self.m.records.Tape.__init__ is self.new:self.m.records.Tape.__init__=self.original_init
        if self.m.packet_engine.run is self.handoff:self.m.packet_engine.run=self.original_packet

    def rollback(self):
        tapes=list(self.tapes.values())
        # No borrowed-byte snapshot. Protected identities must still be live.
        for a,saved in zip(self.arenas,self.protected):require(saved<=a.live,'borrowed ownership contract violation')
        all_tapes=list({id(t):t for t in (*tapes,*self.borrowed)}.values())
        meters=[a.meter for a in self.arenas]+[t.meter for t in all_tapes]
        def operations():return sum(x.reads+x.writes+x.moves for x in meters)
        before=operations()
        volume=sum(len(t.cells) for t in all_tapes)+sum((len(a.words)+1)*(a.bits+2) for a in self.arenas)
        for t in tapes:
            home(t,self.m.words.LEFT);t.clear()
        for a,saved,oldfree,n in zip(self.arenas,self.protected,self.free_order,self.allocated):
            a.rollback(saved)
            # Keep the entry free order; new erased backing remains allocated.
            a.available[:]=[*oldfree,*range(n,len(a.words))]
            require(set(a.available)==set(range(len(a.words)))-saved and len(a.available)==len(set(a.available)),
                    'canonical restored free partition')
            a.template.rewind()
        for t in self.borrowed:home(t,self.m.words.LEFT)
        cost=operations()-before;bound=10*(volume+len(all_tapes)+sum(len(a.words) for a in self.arenas)+1)
        require(cost<=bound,'charged cleanup bound')
        self.report={'state':'rejected','new_tapes_peak':self.max_tapes,'cleanup_ops':cost,'cleanup_bound':bound,
                     'erased_live_tapes':len(tapes),'retained_allocated_slots':[len(a.words) for a in self.arenas]}
        self.tapes.clear()

    def execute(self,call,args):
        global _ACTIVE
        require(not _ACTIVE,'one source transaction at a time')
        _ACTIVE=True;self.original_init=self.m.records.Tape.__init__;self.original_packet=self.m.packet_engine.run
        def new(tape):self.original_init(tape);self.register(tape)
        def handoff(*arguments,**keywords):
            self.commit()
            return self.original_packet(*arguments,**keywords)
        self.new,self.handoff=new,handoff
        self.m.records.Tape.__init__=new;self.m.packet_engine.run=handoff
        failure=None
        try:
            result=call(*args)
        except ValueError as error:
            if self.committed:raise
            self.rollback()
            failure=str(error)
        finally:
            self.uninstall();_ACTIVE=False
        # Outside the except suite: do not retain the failed source traceback,
        # its partially constructed owners or its full copied directory.
        if failure is not None:raise ValueError(failure) from None
        require(self.committed,'successful preparation must transfer to packet engine')
        return result


class GuardedConsumer:
    """Drop-in apply edge for canonical setup; post-handoff behavior is delegated."""
    def __init__(self,m,consumer):self.m,self.consumer=m,consumer;self.last_report=None
    def apply(self,source,request_id,common,low,old_directory,old_count,before,gap,suffix,observe=None):
        require(observe is None,'setup transaction excludes external observers')
        args=(source,request_id,common,low,old_directory,old_count,before,gap,suffix)
        transaction=SetupTransaction(self.m,self.consumer,args)
        try:return transaction.execute(self.consumer.apply,args)
        finally:self.last_report=dict(transaction.report)
