"""Paid original-coordinate gather, actual global consumer, and exact return.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Instantiate only inside physical_loader.opened(): every Count/Tape/owner is
the authenticated physical cohort, never a host payload callback.
"""
from cohort_sources import need


def owner(root,observe=None):
    from cardinal_counts import Count
    from compact_counts import append_bits,copy_bits,power_two
    from global_h_boundary import GlobalBoundary
    from physical_engine import FullPhysical,private_tapes,NullCounters
    from physical_controls import NAMES
    from router_metadata import owned
    from session import borrowed_count,borrowed_tape,erase_marker,sealed_constructors
    from words import BLANK

    class CohortPhysical(GlobalBoundary):
        def __init__(self):
            super().__init__(root,observe)
            self.full = FullPhysical(root,observe=observe)
            if observe is None:
                self.calls = NullCounters(self.calls)
            self.private = private_tapes(self)

        def idle(self):
            super().idle()
            if hasattr(self,'full'):
                self.full.idle()
                need(self.full.closed and self.full.current is None and
                     self.full.output.read() == BLANK,'consumed global Full child')

        def run(self,payload,forward,inverse,code,precision,support,*parameters):
            need(len(parameters) == len(NAMES),'complete outer Full metadata ports')
            ports = tuple(borrowed_tape(t) for t in (payload,forward,inverse,code))
            values = tuple(borrowed_count(x) for x in (precision,support,*parameters))
            need(len({id(t) for t in ports}) == len(ports)
                 and not any(t in self.private for t in ports)
                 and all(x.tape not in (*self.private,*ports) for x in values),
                 'distinct external outer payload controls and metadata')
            source,forward,inverse,code = ports
            precision,support,*full_parameters = values
            n,c,m,g,F,W,fw,cw,tw,F0,W0,rb,pw,stages,hc,dc = full_parameters
            self.rearm()
            succeeded = False
            for tape in ports:
                tape.rewind()
            try:
                with sealed_constructors(),self.scope.installed():
                    with owned(power_two(n),Count.literal(1)) as (records,one):
                        with owned(Count.product(records,W0)) as (input_bits,):
                            input_bits.multiply_small(2)
                            self.current = self.pool.acquire()
                            copy_bits(source,self.current,input_bits)
                        need(source.read() == BLANK,'complete original-coordinate input')
                        source.rewind()
                        self.current.rewind()
                        self.gather(forward,n,precision,support,pw,W0,one,one)
                        self.idle()
                        with self.scope.suspended():
                            returned = self.full.run(borrowed_tape(self.current),borrowed_tape(code),
                                *(borrowed_count(x) for x in full_parameters))
                        self.accept(returned)
                        self.gather(inverse,n,precision,support,pw,W,one,one)
                        self.idle()
                        append_bits(self.current,self.output)
                    self.current.clear()
                    self.current = None
                    self.pool.empty()
                    succeeded = True
            finally:
                for tape in ports:
                    tape.rewind()
                for value in values:
                    value.rewind()
                if self.current is not None:
                    self.current.clear()
                    self.current = None
                if not self.pool.live:
                    for tape in self.pool.tapes:
                        erase_marker(tape)
                self.output.rewind()
                if not succeeded:
                    self.output.clear()
                    erase_marker(self.output)
                self.closed = True
            return self.output

    return CohortPhysical()


class PreparedOuter:
    def __init__(self,program,physical,event_types):
        from cardinal_counts import Count
        from records import Tape
        from physical_controls import PreparedFull,emit_unsigned
        self.full = PreparedFull(program,Tape,Count,event_types)
        self.forward,self.inverse = Tape(),Tape()
        self.parameters = ()
        try:
            width = self.full.metadata['position_width']
            for tape,mapping in ((self.forward,program.layout.gather),
                                 (self.inverse,program.layout.inverse)):
                for old,new in sorted(mapping.items()):
                    emit_unsigned(tape,old,width)
                    emit_unsigned(tape,new,width)
                tape.rewind()
            self.parameters = (Count.literal(program.data_width+program.axes),
                               Count.literal(len(program.layout.gather)))
        except BaseException:
            self.close()
            raise

    def run(self,consumer,payload):
        return consumer.run(payload,self.forward,self.inverse,self.full.code,
                            *self.parameters,*self.full.parameters)

    def close(self):
        from session import erase_marker
        self.full.close()
        for tape in (self.forward,self.inverse):
            tape.clear()
            erase_marker(tape)
        for value in self.parameters:
            value.close()
            erase_marker(value.tape)
        self.parameters = ()
