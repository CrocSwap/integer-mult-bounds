"""Physical whole-word staging and chronological native global operations."""
from functools import lru_cache
from types import GeneratorType

from bitstream import copy_bits
from cardinal_counts import Count
from control import LocalState
from episode import xor_packet
from fresh_rows import family_rows
import oracle
from records import Tape
from routes import compile_route, copy_rows, inverse_rational, route_packet
from selection import gather, scatter
from sources import identity, product
from stream import Counter
from words import BLANK, ONE, ZERO, need


@lru_cache(None)
def inverse_chart(matrix):
    transposed=tuple(zip(*matrix))
    if product(matrix,transposed)==identity(len(matrix)):return transposed
    return inverse_rational(matrix)


@lru_cache(None)
def compile_owner(chart,common_low,codes):
    """Fixed-q source labels; no high matrix or precision reaches this stage."""
    inverse=inverse_chart(chart)
    native=tuple(map(tuple,oracle.multiply(common_low,oracle.reduce_rational(inverse,codes.q),codes.q)))
    forward=compile_route(native,chart,codes)
    backward=compile_route(common_low,inverse,codes)
    need(forward.target_low==common_low and backward.target_low==native,"exact owner/common inverse binding")
    return native,forward,backward


def clone_packet(source,context,old_count,fibre):
    result,outer=Tape(),Counter(old_count)
    source.rewind()
    try:
        while not outer.finished:
            copy_rows(source,result,context.highs,fibre);outer.decrement()
        need(source.read()==BLANK,"complete cloned packet")
        result.rewind()
        return result
    except ValueError:
        result.clear()
        raise
    finally:outer.close();source.rewind()


def xor_family(source,target,old_count,rows,fibre):
    result,outer=Tape(),Counter(old_count)
    source.rewind();target.rewind()
    try:
        while not outer.finished:
            records=Counter(rows)
            while not records.finished:
                bits=Counter(fibre)
                while not bits.finished:
                    a,b=source.read(),target.read()
                    need(a in (ZERO,ONE) and b in (ZERO,ONE),"aligned native Boolean family")
                    result.append(a^b);source.step(1);target.step(1);bits.decrement()
                bits.close();records.decrement()
            records.close();outer.decrement()
        need(source.read()==target.read()==BLANK,"complete native family XOR")
        result.rewind()
        return result
    except ValueError:
        result.clear()
        raise
    finally:outer.close();source.rewind();target.rewind()


class Driver:
    def __init__(self,context,topology,consumer,old_directory,old_count,before,gap,suffix,fibre,observe=None,child_stock=None,child_before=None):
        self.child_stock,self.child_before=child_stock,child_before
        self.context,self.topology,self.consumer=context,topology,consumer
        self.old_directory,self.old_count=old_directory,old_count
        self.before,self.gap,self.suffix,self.fibre=before,gap,suffix,fibre
        self.observe=observe

    def event(self,kind,*labels):
        if self.observe is not None:self.observe(kind,*labels)

    def residual(self,source,identifier,common,low):
        self.event("residual",identifier,common)
        if getattr(self.consumer,"recursive",False):
            result=self.consumer.apply(source,identifier,common,low,self.old_directory,self.old_count,
                                       self.before,self.gap,self.suffix,child_stock=self.child_stock,
                                       child_before=self.child_before)
        else:
            result=self.consumer.apply(source,identifier,common,low,self.old_directory,self.old_count,
                                       self.before,self.gap,self.suffix)
        if isinstance(result,GeneratorType):return (yield from result)
        return result

    def commit(self,families,family,low,packet):
        """Merge into the latest family state, including earlier role returns."""
        previous=families[family]
        families[family]=scatter(previous,packet,self.context,self.old_count,low,self.fibre)
        previous.clear()

    def local(self,families,call,common_low):
        context=self.context
        slots,buffers={},{}
        state=LocalState(call);private=state.private
        try:
            seen=set()
            for role,owner in enumerate(call.owners):
                chart=self.topology.matrix(owner.chart)
                native,forward,backward=compile_owner(chart,common_low,context.codes)
                key=(owner.family,native)
                need(key not in seen,"disjoint complete owned low packets")
                seen.add(key)
                local=gather(families[owner.family],context,self.old_count,native,self.fibre)
                try:buffers[role]=route_packet(local,forward,context,self.old_count,self.fibre)
                finally:local.clear()
                slots[role]=(owner.family,native,backward)
            for position,event in enumerate(call.events):
                op,role=state.accept(position)
                self.event("literal",call.stage,call.replica,position,op)
                if op==0:
                    changed=yield from self.residual(buffers[role],call.requests[position],True,common_low)
                    buffers[role].clear();buffers[role]=changed
                elif op==1:
                    source=event[2]
                    need(source in buffers,"live XOR payload role")
                    changed=xor_packet(buffers[source],buffers[role],context,self.old_count,self.fibre)
                    buffers[role].clear();buffers[role]=changed
                elif op==2:
                    need(private not in buffers,"fresh private payload role")
                    copied=clone_packet(buffers[role],context,self.old_count,self.fibre)
                    try:buffers[private]=yield from self.residual(copied,call.requests[position],True,common_low)
                    finally:copied.clear()
                else:
                    need(op==3 and private in buffers,"live transported private payload")
                    buffers.pop(private).clear()
            state.finish()
            # Every role returns, including helpers with a changed physical frame.
            for role in range(private):
                family,native,backward=slots[role]
                returned=route_packet(buffers[role],backward,context,self.old_count,self.fibre)
                try:self.commit(families,family,native,returned)
                finally:returned.clear()
        finally:
            for tape in buffers.values():tape.clear()
            self.old_directory.rewind()

    def idle(self,families,identifier,replica):
        family=self.topology.idle_family(identifier,replica)
        for low in self.topology.catalogue.low_classes():
            selected=gather(families[family],self.context,self.old_count,low,self.fibre)
            changed=None
            try:
                changed=yield from self.residual(selected,identifier,False,low)
                self.commit(families,family,low,changed)
            finally:
                if changed is not None:changed.clear()
                selected.clear()

    def global_word(self,families):
        topology=self.topology
        rows=family_rows(self.context)
        try:
            for event in topology.schedule:
                kind=event["kind"]
                self.event("global",kind)
                if kind=="local_cover_sweep":
                    for replica in range(topology.replicas):
                        call=topology.call(event["stage"],replica)
                        for low in topology.catalogue.low_classes():
                            yield from self.local(families,call,low)
                elif kind=="idle":
                    for replica in range(topology.replicas):
                        for identifier in topology.idles[event["idx"]]:yield from self.idle(families,identifier,replica)
                elif kind=="bridge":
                    need(event["coefficient"] in (-1,1) and event["dst"]!=event["src"],"native bridge scalar")
                    for replica in range(topology.replicas):
                        for port in range(topology.ports):
                            for target,source,side in ((event["dst"],event["src"],0),
                                                       (event["src"],event["dst"],1)):
                                a=topology.family(replica,target,side,port)
                                b=topology.family(replica,source,side,port)
                                changed=xor_family(families[b],families[a],self.old_count,rows,self.fibre)
                                families[a].clear();families[a]=changed
                                self.event("bridge",a,b,event["coefficient"])
                else:
                    need(kind=="exchange","closed global opcode")
                    for replica in range(topology.replicas):
                        for pair in range(topology.pairs):
                            for port in range(topology.ports):
                                a=topology.family(replica,pair,0,port);b=topology.family(replica,pair,1,port)
                                families[a],families[b]=families[b],families[a]
                                self.event("exchange",a,b)
                self.event("global_return",kind,event.get("stage",event.get("idx",-1)))
        finally:rows.close()
